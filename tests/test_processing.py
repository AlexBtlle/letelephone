import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.processing import normalize_audio


def test_normalize_audio_success(tmp_path):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    tmp = tmp_path / "test.tmp.wav"

    def fake_run(*args, **kwargs):
        tmp.write_bytes(b"\x00" * 200)
        return MagicMock(returncode=0)

    with patch("src.processing.subprocess.run", side_effect=fake_run):
        normalize_audio(wav)

    assert wav.exists()
    assert not tmp.exists()


def test_normalize_audio_missing_file(tmp_path, caplog):
    normalize_audio(tmp_path / "nonexistent.wav")
    assert "introuvable" in caplog.text


def test_normalize_audio_ffmpeg_failure(tmp_path, caplog):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    exc = subprocess.CalledProcessError(1, "ffmpeg", stderr=b"error details")
    with patch("src.processing.subprocess.run", side_effect=exc):
        normalize_audio(wav)
    assert "Normalisation échouée" in caplog.text
    assert wav.exists()


def test_normalize_audio_timeout(tmp_path, caplog):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    with patch("src.processing.subprocess.run", side_effect=subprocess.TimeoutExpired("ffmpeg", 120)):
        normalize_audio(wav)
    assert "timeout" in caplog.text
    assert wav.exists()


def test_normalize_audio_ffmpeg_not_found(tmp_path, caplog):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    with patch("src.processing.subprocess.run", side_effect=FileNotFoundError):
        normalize_audio(wav)
    assert "ffmpeg introuvable" in caplog.text
    assert wav.exists()


def test_normalize_audio_cleans_tmp_on_failure(tmp_path):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    tmp = tmp_path / "test.tmp.wav"
    tmp.write_bytes(b"\x00" * 50)
    exc = subprocess.CalledProcessError(1, "ffmpeg", stderr=b"")
    with patch("src.processing.subprocess.run", side_effect=exc):
        normalize_audio(wav)
    assert not tmp.exists()
