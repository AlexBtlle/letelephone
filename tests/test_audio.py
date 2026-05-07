import subprocess
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from src.audio import AudioController, _detect_usb_alsa_device


@pytest.fixture
def audio():
    with patch("src.audio._detect_usb_alsa_device", return_value="default"):
        return AudioController(sample_rate=44100, channels=1, max_duration_sec=60)


# ── Detection ────────────────────────────────────────────────────────────────

def test_init_detects_devices(monkeypatch):
    monkeypatch.setattr("src.audio._detect_usb_alsa_device", lambda _: "hw:1,0")
    ctrl = AudioController()
    assert ctrl.playback_device == "hw:1,0"
    assert ctrl.capture_device == "hw:1,0"


def test_explicit_devices_skip_detection():
    ctrl = AudioController(playback_device="hw:2,0", capture_device="hw:3,0")
    assert ctrl.playback_device == "hw:2,0"
    assert ctrl.capture_device == "hw:3,0"


def test_detect_alsa_finds_usb():
    fake_output = "card 2: Device [USB Audio Device], device 0: USB Audio [USB Audio]\n"
    mock_result = MagicMock()
    mock_result.stdout = fake_output
    with patch("subprocess.run", return_value=mock_result):
        assert _detect_usb_alsa_device("capture") == "hw:2,0"


def test_detect_alsa_fallback_on_no_usb():
    mock_result = MagicMock()
    mock_result.stdout = "card 0: bcm2835 [bcm2835 ALSA], device 0: ...\n"
    with patch("subprocess.run", return_value=mock_result):
        assert _detect_usb_alsa_device("capture") == "default"


def test_detect_alsa_fallback_when_command_not_found():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert _detect_usb_alsa_device("capture") == "default"


def test_detect_alsa_fallback_on_timeout():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="arecord", timeout=5)):
        assert _detect_usb_alsa_device("capture") == "default"


# ── Playback ─────────────────────────────────────────────────────────────────

def test_play_audio_missing_file(audio, tmp_path):
    with pytest.raises(FileNotFoundError):
        audio.play_audio(tmp_path / "nonexistent.wav")


def test_play_audio_calls_aplay(audio, tmp_path):
    wav = tmp_path / "beep.wav"
    wav.write_bytes(b"\x00" * 44)
    with patch("subprocess.run") as mock_run:
        audio.play_audio(wav)
        args = mock_run.call_args[0][0]
        assert "aplay" in args
        assert str(wav) in args


def test_play_audio_propagates_called_process_error(audio, tmp_path):
    wav = tmp_path / "beep.wav"
    wav.write_bytes(b"\x00" * 44)
    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "aplay")):
        with pytest.raises(subprocess.CalledProcessError):
            audio.play_audio(wav)


def test_play_audio_propagates_file_not_found_for_aplay(audio, tmp_path):
    wav = tmp_path / "beep.wav"
    wav.write_bytes(b"\x00" * 44)
    with patch("subprocess.run", side_effect=FileNotFoundError("aplay not found")):
        with pytest.raises(FileNotFoundError):
            audio.play_audio(wav)


# ── Recording ────────────────────────────────────────────────────────────────

def test_start_recording_launches_arecord(audio, tmp_path):
    out = tmp_path / "test.wav"
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        audio.start_recording(out)
        args = mock_popen.call_args[0][0]
        assert "arecord" in args
        assert str(out) in args


def test_start_recording_creates_parent_dir(audio, tmp_path):
    out = tmp_path / "subdir" / "test.wav"
    with patch("subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        audio.start_recording(out)
        assert out.parent.exists()


def test_start_recording_raises_if_already_recording(audio, tmp_path):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    audio._recording_process = mock_proc
    with pytest.raises(RuntimeError):
        audio.start_recording(tmp_path / "test.wav")


def test_start_recording_propagates_arecord_not_found(audio, tmp_path):
    with patch("subprocess.Popen", side_effect=FileNotFoundError("arecord not found")):
        with pytest.raises(FileNotFoundError):
            audio.start_recording(tmp_path / "test.wav")


# ── Stop recording ───────────────────────────────────────────────────────────

def test_stop_recording_terminates_process(audio):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_proc.wait.return_value = 0
    audio._recording_process = mock_proc
    audio.stop_recording()
    mock_proc.terminate.assert_called_once()
    assert audio._recording_process is None


def test_stop_recording_noop_when_idle(audio):
    audio._recording_process = None
    audio.stop_recording()  # must not raise


def test_stop_recording_kills_if_terminate_times_out(audio):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_proc.wait.side_effect = [subprocess.TimeoutExpired(cmd="arecord", timeout=5), None]
    audio._recording_process = mock_proc
    audio.stop_recording()
    mock_proc.kill.assert_called_once()
    assert audio._recording_process is None


def test_stop_recording_logs_error_if_kill_also_times_out(audio):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_proc.wait.side_effect = subprocess.TimeoutExpired(cmd="arecord", timeout=5)
    audio._recording_process = mock_proc
    # Must not raise even if kill+wait also times out
    audio.stop_recording()
    assert audio._recording_process is None


def test_stop_recording_noop_if_process_already_finished(audio):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 0  # already exited
    audio._recording_process = mock_proc
    audio.stop_recording()
    mock_proc.terminate.assert_not_called()
    assert audio._recording_process is None


# ── is_recording ─────────────────────────────────────────────────────────────

def test_is_recording_true_when_active(audio):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    audio._recording_process = mock_proc
    assert audio.is_recording() is True


def test_is_recording_false_when_finished(audio):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 0
    audio._recording_process = mock_proc
    assert audio.is_recording() is False


def test_is_recording_false_when_no_process(audio):
    audio._recording_process = None
    assert audio.is_recording() is False
