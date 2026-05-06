import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.audio import AudioController, _detect_usb_alsa_device


@pytest.fixture
def audio():
    with patch("src.audio._detect_usb_alsa_device", return_value="default"):
        return AudioController(sample_rate=44100, channels=1, max_duration_sec=60)


def test_init_detects_devices(monkeypatch):
    monkeypatch.setattr("src.audio._detect_usb_alsa_device", lambda _: "hw:1,0")
    ctrl = AudioController()
    assert ctrl.playback_device == "hw:1,0"
    assert ctrl.capture_device == "hw:1,0"


def test_explicit_devices_skip_detection():
    ctrl = AudioController(playback_device="hw:2,0", capture_device="hw:3,0")
    assert ctrl.playback_device == "hw:2,0"
    assert ctrl.capture_device == "hw:3,0"


def test_play_audio_missing_file(audio, tmp_path):
    with pytest.raises(FileNotFoundError):
        audio.play_audio(tmp_path / "nonexistent.wav")


def test_play_audio_calls_aplay(audio, tmp_path):
    wav = tmp_path / "beep.wav"
    wav.write_bytes(b"\x00" * 44)  # fake WAV header
    with patch("subprocess.run") as mock_run:
        audio.play_audio(wav)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "aplay" in args
        assert str(wav) in args


def test_start_recording_launches_arecord(audio, tmp_path):
    out = tmp_path / "test.wav"
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        audio.start_recording(out)
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert "arecord" in args
        assert str(out) in args


def test_start_recording_raises_if_already_recording(audio, tmp_path):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    audio._recording_process = mock_proc
    with pytest.raises(RuntimeError):
        audio.start_recording(tmp_path / "test.wav")


def test_stop_recording_terminates_process(audio):
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    audio._recording_process = mock_proc
    audio.stop_recording()
    mock_proc.terminate.assert_called_once()
    assert audio._recording_process is None


def test_stop_recording_noop_when_idle(audio):
    audio._recording_process = None
    audio.stop_recording()  # must not raise


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


def test_detect_alsa_finds_usb(monkeypatch):
    fake_output = "card 2: Device [USB Audio Device], device 0: USB Audio [USB Audio]\n"
    mock_result = MagicMock()
    mock_result.stdout = fake_output
    with patch("subprocess.run", return_value=mock_result):
        device = _detect_usb_alsa_device("capture")
    assert device == "hw:2,0"


def test_detect_alsa_fallback_on_no_usb(monkeypatch):
    mock_result = MagicMock()
    mock_result.stdout = "card 0: bcm2835 [bcm2835 ALSA], device 0: ...\n"
    with patch("subprocess.run", return_value=mock_result):
        device = _detect_usb_alsa_device("capture")
    assert device == "default"
