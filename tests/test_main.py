"""Tests for the main event loop helpers and startup resilience."""
import json
import logging
import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

import src.main as main_module
from src.main import _run_playback, _try_play_error, _wait_for_hangup


# ── Fixture: full main() environment ─────────────────────────────────────────

@pytest.fixture
def env(tmp_path, monkeypatch):
    """Patch all external dependencies so main() can run in-process."""
    assets = tmp_path / "assets"
    assets.mkdir()
    beep = assets / "beep.wav"
    beep.write_bytes(b"\x00")
    error = assets / "error.wav"
    error.write_bytes(b"\x00")

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "config.default.json").write_text(json.dumps({
        "hook_pin": 17, "poll_interval_sec": 0, "pre_beep_delay_sec": 0,
        "max_duration_sec": 60, "audio": {"sample_rate": 44100, "channels": 1},
    }))

    monkeypatch.setattr(main_module, "_BASE_DIR", tmp_path)
    monkeypatch.setattr(main_module, "_ASSETS_DIR", assets)
    monkeypatch.setattr(main_module, "_BEEP_FILE", beep)
    monkeypatch.setattr(main_module, "_ERROR_FILE", error)

    import src.config as cfg_mod
    monkeypatch.setattr(cfg_mod, "_DEFAULT_CONFIG", cfg_dir / "config.default.json")
    monkeypatch.setattr(cfg_mod, "_EVENT_CONFIG", cfg_dir / "config.event.json")

    recordings = tmp_path / "recordings"
    recordings.mkdir()

    usb = MagicMock()
    usb.is_available.return_value = False
    usb.welcome_file.return_value = None
    usb.log_dir.side_effect = OSError
    usb.recordings_dir.side_effect = OSError

    audio = MagicMock()
    audio.is_recording.return_value = False
    audio.stop_recording.return_value = None

    hook = MagicMock()
    hook.close.return_value = None

    return {
        "tmp_path": tmp_path,
        "recordings": recordings,
        "assets": assets,
        "beep": beep,
        "error": error,
        "usb": usb,
        "audio": audio,
        "hook": hook,
    }


def _run_main(env):
    with patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.build_playback_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.compress_to_mp3"), \
         patch("src.main.time.sleep", return_value=None):
        main_module.main()


# ── _try_play_error ───────────────────────────────────────────────────────────

def test_try_play_error_plays_when_file_exists(tmp_path, monkeypatch):
    error_file = tmp_path / "error.wav"
    error_file.write_bytes(b"\x00")
    monkeypatch.setattr(main_module, "_ERROR_FILE", error_file)
    audio = MagicMock()
    _try_play_error(audio)
    audio.play_audio.assert_called_once_with(error_file)


def test_try_play_error_silent_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module, "_ERROR_FILE", tmp_path / "nonexistent.wav")
    audio = MagicMock()
    _try_play_error(audio)
    audio.play_audio.assert_not_called()


def test_try_play_error_swallows_exception(tmp_path, monkeypatch):
    error_file = tmp_path / "error.wav"
    error_file.write_bytes(b"\x00")
    monkeypatch.setattr(main_module, "_ERROR_FILE", error_file)
    audio = MagicMock()
    audio.play_audio.side_effect = subprocess.CalledProcessError(1, "aplay")
    _try_play_error(audio)  # must not raise


# ── _wait_for_hangup ──────────────────────────────────────────────────────────

def test_wait_for_hangup_returns_when_hung_up():
    hook = MagicMock()
    hook.is_off_hook.side_effect = [True, True, False]
    _wait_for_hangup(hook, poll=0)
    assert hook.is_off_hook.call_count == 3


def test_wait_for_hangup_immediate_return():
    hook = MagicMock()
    hook.is_off_hook.return_value = False
    _wait_for_hangup(hook, poll=0)
    hook.is_off_hook.assert_called_once()


# ── main() startup resilience ─────────────────────────────────────────────────

def test_main_falls_back_to_defaults_on_bad_config(env, caplog):
    from src.config import ConfigError
    env["hook"].is_off_hook.side_effect = KeyboardInterrupt

    with patch("src.main.load_config", side_effect=ConfigError("JSON invalide")), \
         patch("src.main.time.sleep", return_value=None):
        with caplog.at_level(logging.ERROR, logger="src.main"):
            _run_main(env)

    assert any("configuration" in r.message.lower() for r in caplog.records)


def test_main_falls_back_to_local_recordings_on_usb_error(env):
    env["usb"].is_available.return_value = True
    env["usb"].recordings_dir.side_effect = OSError("lecture seule")
    env["usb"].log_dir.side_effect = OSError("lecture seule")
    env["hook"].is_off_hook.side_effect = KeyboardInterrupt

    with patch("src.main.ensure_recordings_dir", return_value=env["recordings"]) as mock_ensure, \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"):
        main_module.main()

    mock_ensure.assert_called()


# ── main() event loop ─────────────────────────────────────────────────────────

def test_main_happy_path_records_message(env, tmp_path):
    """Pickup → welcome → record → hang up → idle → KeyboardInterrupt."""
    wav = env["recordings"] / "message_2026-06-15_12-00-00.wav"
    wav.write_bytes(b"\x00" * 100)

    env["audio"].is_recording.side_effect = [True, True, False]  # recording, then done
    # Sequence: off-hook × 3 (recording loop), on-hook, on-hook (wait hangup), idle, stop
    env["hook"].is_off_hook.side_effect = [
        True,   # main loop: detected
        True, True, False,  # recording while-loop
        False,  # wait_for_hangup
        KeyboardInterrupt,
    ]

    with patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.normalize_audio"):
        main_module.main()

    env["audio"].play_audio.assert_called_once()
    env["audio"].start_recording.assert_called_once_with(wav)
    env["audio"].stop_recording.assert_called()


def test_main_gpio_error_retries(env, caplog):
    """GPIO read error must not crash the loop — it logs and retries."""
    env["hook"].is_off_hook.side_effect = [
        OSError("GPIO error"),
        KeyboardInterrupt,
    ]

    with caplog.at_level(logging.ERROR, logger="src.main"):
        _run_main(env)

    assert any("GPIO" in r.message for r in caplog.records)
    env["audio"].play_audio.assert_not_called()


def test_main_welcome_audio_error_plays_error_sound(env, caplog):
    """If welcome audio fails, play error sound and wait for hangup."""
    env["audio"].play_audio.side_effect = subprocess.CalledProcessError(1, "aplay")
    env["hook"].is_off_hook.side_effect = [
        True,   # detected off-hook
        False,  # wait_for_hangup: already hung up
        KeyboardInterrupt,
    ]

    with caplog.at_level(logging.ERROR, logger="src.main"):
        _run_main(env)

    assert any("accueil" in r.message for r in caplog.records)
    env["audio"].start_recording.assert_not_called()


def test_main_recording_start_error_plays_error_sound(env, caplog):
    """If arecord fails to start, play error sound and wait for hangup."""
    env["audio"].play_audio.return_value = None  # welcome OK
    env["audio"].start_recording.side_effect = FileNotFoundError("arecord not found")
    env["hook"].is_off_hook.side_effect = [
        True,   # detected off-hook
        False,  # wait_for_hangup
        KeyboardInterrupt,
    ]

    with caplog.at_level(logging.ERROR, logger="src.main"), \
         patch("src.main.build_recording_path", return_value=env["recordings"] / "test.wav"), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"):
        main_module.main()

    assert any("enregistrement" in r.message.lower() for r in caplog.records)
    env["audio"].stop_recording.assert_called()


def test_main_logs_warning_on_empty_recording(env, caplog):
    """If the recorded file is empty (but long enough), log a warning."""
    wav = env["recordings"] / "message_empty.wav"
    wav.write_bytes(b"")  # exists but empty (0 bytes)

    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [
        True,
        False,  # wait_for_hangup
        KeyboardInterrupt,
    ]

    with caplog.at_level(logging.WARNING, logger="src.main"), \
         patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"):
        main_module.main()

    assert any("vide" in r.message for r in caplog.records)


def test_main_short_recording_discarded(env, caplog):
    """Recording shorter than min_duration_sec must be deleted and not counted."""
    wav = env["recordings"] / "message_short.wav"
    wav.write_bytes(b"\x00" * 100)

    env["audio"].is_recording.return_value = False
    env["hook"].is_off_hook.side_effect = [
        True,   # off-hook
        False,  # wait_for_hangup
        KeyboardInterrupt,
    ]

    with caplog.at_level(logging.INFO, logger="src.main"), \
         patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 0.3]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"):
        main_module.main()

    assert not wav.exists(), "Le fichier court doit être supprimé"
    assert any("court" in r.message for r in caplog.records)


def test_main_display_updated_on_recording(env):
    """Display must switch to show_recording on pickup and back to show_idle after."""
    mock_display = MagicMock()
    wav = env["recordings"] / "message_ok.wav"
    wav.write_bytes(b"\x00" * 100)

    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [
        True,
        False,  # wait_for_hangup
        KeyboardInterrupt,
    ]

    with patch("src.main.build_display", return_value=mock_display), \
         patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.normalize_audio"):
        main_module.main()

    mock_display.show_recording.assert_called()
    mock_display.show_idle.assert_called()


def test_main_message_counter_increments(env):
    """message_count must increment after a successful recording."""
    wav = env["recordings"] / "message_ok.wav"
    wav.write_bytes(b"\x00" * 100)
    mock_display = MagicMock()

    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [True, False, KeyboardInterrupt]

    with patch("src.main.build_display", return_value=mock_display), \
         patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.count_recordings", return_value=3), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.normalize_audio"):
        main_module.main()

    # Final show_idle call must carry count=4 (3 existing + 1 new)
    final_idle_call = mock_display.show_idle.call_args_list[-1]
    assert final_idle_call.args[1] == 4


def test_main_normalize_called_after_recording(env):
    """normalize_audio must be called once after a valid recording."""
    wav = env["recordings"] / "message_ok.wav"
    wav.write_bytes(b"\x00" * 100)

    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [True, False, KeyboardInterrupt]

    with patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.normalize_audio") as mock_normalize:
        main_module.main()

    mock_normalize.assert_called_once_with(wav)


def test_main_normalize_skipped_when_disabled(env):
    """normalize_audio must not be called when normalize_audio=false in config."""
    import src.config as cfg_mod
    cfg_dir = env["tmp_path"] / "config"
    import json
    (cfg_dir / "config.default.json").write_text(json.dumps({
        "hook_pin": 17, "poll_interval_sec": 0, "pre_beep_delay_sec": 0,
        "max_duration_sec": 60, "audio": {"sample_rate": 44100, "channels": 1},
        "normalize_audio": False,
    }))

    wav = env["recordings"] / "message_ok.wav"
    wav.write_bytes(b"\x00" * 100)
    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [True, False, KeyboardInterrupt]

    with patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.normalize_audio") as mock_normalize:
        main_module.main()

    mock_normalize.assert_not_called()


def test_main_compress_called_after_recording(env):
    """compress_to_mp3 must be called once on the raw file after a valid recording."""
    wav = env["recordings"] / "message_ok.wav"
    wav.write_bytes(b"\x00" * 100)

    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [True, False, KeyboardInterrupt]

    with patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.compress_to_mp3") as mock_compress:
        main_module.main()

    mock_compress.assert_called_once_with(wav, quality=0)


def test_main_compress_skipped_when_disabled(env):
    """compress_to_mp3 must not be called when compress_mp3.enabled=false."""
    import json
    cfg_dir = env["tmp_path"] / "config"
    (cfg_dir / "config.default.json").write_text(json.dumps({
        "hook_pin": 17, "poll_interval_sec": 0, "pre_beep_delay_sec": 0,
        "max_duration_sec": 60, "audio": {"sample_rate": 44100, "channels": 1},
        "compress_mp3": {"enabled": False},
    }))

    wav = env["recordings"] / "message_ok.wav"
    wav.write_bytes(b"\x00" * 100)
    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [True, False, KeyboardInterrupt]

    with patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"), \
         patch("src.main.isolate_voice", return_value=None), \
         patch("src.main.compress_to_mp3") as mock_compress:
        main_module.main()

    mock_compress.assert_not_called()


def test_main_isolate_voice_compressed_when_present(env):
    """When isolate_voice succeeds, the vocal file is also compressed."""
    wav = env["recordings"] / "message_ok.wav"
    wav.write_bytes(b"\x00" * 100)
    vocal_wav = env["recordings"] / "vocal" / "message_ok.wav"
    vocal_wav.parent.mkdir(parents=True, exist_ok=True)
    vocal_wav.write_bytes(b"\x00" * 80)

    env["audio"].is_recording.side_effect = [False]
    env["hook"].is_off_hook.side_effect = [True, False, KeyboardInterrupt]

    with patch("src.main.build_recording_path", return_value=wav), \
         patch("src.main.time.monotonic", side_effect=[0.0, 5.0]), \
         patch("src.main.time.sleep", return_value=None), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()), \
         patch("src.main.normalize_audio"), \
         patch("src.main.isolate_voice", return_value=vocal_wav), \
         patch("src.main.compress_to_mp3") as mock_compress:
        main_module.main()

    assert mock_compress.call_count == 2
    mock_compress.assert_any_call(wav, quality=0)
    mock_compress.assert_any_call(vocal_wav, quality=0)


# ── _run_playback ─────────────────────────────────────────────────────────────

def test_run_playback_plays_messages_newest_first(tmp_path):
    raw_dir = tmp_path / "brut"
    raw_dir.mkdir()
    f1 = raw_dir / "message_2026-01-01_10-00-00.mp3"
    f2 = raw_dir / "message_2026-01-01_11-00-00.mp3"
    f1.write_bytes(b"\x00")
    f2.write_bytes(b"\x00")

    audio = MagicMock()
    audio.is_playing.side_effect = [True, False, True, False]
    hook = MagicMock()
    # True: before f2 / True: inner loop f2 / True: before f1 / True: inner loop f1 / False: hangup
    hook.is_off_hook.side_effect = [True, True, True, True, False]
    display = MagicMock()

    with patch("src.main.time.sleep"):
        _run_playback(audio, raw_dir, hook, poll=0)

    assert audio.start_playback.call_count == 2
    assert audio.start_playback.call_args_list[0].args[0] == f2
    assert audio.start_playback.call_args_list[1].args[0] == f1
    assert audio.stop_playback.call_count == 2


def test_run_playback_no_messages_waits_for_hangup(tmp_path):
    raw_dir = tmp_path / "brut"
    raw_dir.mkdir()
    audio = MagicMock()
    hook = MagicMock()
    hook.is_off_hook.return_value = False
    display = MagicMock()

    with patch("src.main.time.sleep"):
        _run_playback(audio, raw_dir, hook, poll=0)

    audio.start_playback.assert_not_called()


def test_run_playback_stops_on_hangup(tmp_path):
    raw_dir = tmp_path / "brut"
    raw_dir.mkdir()
    f1 = raw_dir / "message_2026-01-01_10-00-00.mp3"
    f1.write_bytes(b"\x00")

    audio = MagicMock()
    audio.is_playing.return_value = True
    hook = MagicMock()
    # True: before f1 / False: during inner loop → exits / False: hangup
    hook.is_off_hook.side_effect = [True, False, False]

    with patch("src.main.time.sleep"):
        _run_playback(audio, raw_dir, hook, poll=0)

    audio.start_playback.assert_called_once_with(f1)
    audio.stop_playback.assert_called_once()


def test_run_playback_skips_file_on_error(tmp_path):
    raw_dir = tmp_path / "brut"
    raw_dir.mkdir()
    f1 = raw_dir / "message_2026-01-01_10-00-00.mp3"
    f2 = raw_dir / "message_2026-01-01_11-00-00.mp3"
    f1.write_bytes(b"\x00")
    f2.write_bytes(b"\x00")

    audio = MagicMock()
    audio.start_playback.side_effect = [FileNotFoundError("aplay missing"), None]
    audio.is_playing.side_effect = [True, False]
    hook = MagicMock()
    hook.is_off_hook.side_effect = [True, True, True, False]

    with patch("src.main.time.sleep"):
        _run_playback(audio, raw_dir, hook, poll=0)

    assert audio.start_playback.call_count == 2


# ── main() playback mode ──────────────────────────────────────────────────────

def test_main_playback_mode_triggered_by_button(env):
    """Button press sets playback_requested; next off-hook triggers playback not recording."""
    captured = {}

    def fake_build_playback(cfg, on_press=None):
        captured["on_press"] = on_press
        return MagicMock()

    slept = [0]

    def fake_sleep(_):
        slept[0] += 1
        if slept[0] == 1 and "on_press" in captured:
            captured["on_press"]()  # simulate button press during idle

    env["hook"].is_off_hook.side_effect = [
        False,          # idle: not off-hook → sleep → callback fires
        True,           # playback_requested + off-hook → playback mode
        False,          # _wait_for_hangup inside _run_playback (no messages)
        KeyboardInterrupt,
    ]
    mock_display = MagicMock()
    (env["recordings"] / "brut").mkdir(parents=True, exist_ok=True)

    with patch("src.main.build_display", return_value=mock_display), \
         patch("src.main.build_playback_button", side_effect=fake_build_playback), \
         patch("src.main.time.sleep", side_effect=fake_sleep), \
         patch("src.main.UsbStorage", return_value=env["usb"]), \
         patch("src.main.AudioController", return_value=env["audio"]), \
         patch("src.main.HookSwitch", return_value=env["hook"]), \
         patch("src.main.ensure_recordings_dir", return_value=env["recordings"]), \
         patch("src.main.build_shutdown_button", return_value=MagicMock()):
        main_module.main()

    mock_display.show_playback.assert_called_once()
    mock_display.show_idle.assert_called()
    env["audio"].start_recording.assert_not_called()
