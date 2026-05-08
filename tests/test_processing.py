import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.processing import compress_to_mp3, normalize_audio


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


# ── compress_to_mp3 ───────────────────────────────────────────────────────────

def test_compress_to_mp3_success(tmp_path):
    wav = tmp_path / "message_2026-01-01_12-00-00.wav"
    wav.write_bytes(b"\x00" * 100)
    mp3 = tmp_path / "message_2026-01-01_12-00-00.mp3"

    def fake_run(*args, **kwargs):
        mp3.write_bytes(b"\xff\xfb" + b"\x00" * 50)  # minimal MP3 header
        return MagicMock(returncode=0)

    with patch("src.processing.subprocess.run", side_effect=fake_run):
        result = compress_to_mp3(wav)

    assert result == mp3
    assert mp3.exists()
    assert not wav.exists()


def test_compress_to_mp3_missing_file(tmp_path, caplog):
    result = compress_to_mp3(tmp_path / "nonexistent.wav")
    assert result is None
    assert "introuvable" in caplog.text


def test_compress_to_mp3_ffmpeg_failure(tmp_path, caplog):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    exc = subprocess.CalledProcessError(1, "ffmpeg", stderr=b"codec error")
    with patch("src.processing.subprocess.run", side_effect=exc):
        result = compress_to_mp3(wav)
    assert result is None
    assert wav.exists()
    assert "MP3 échouée" in caplog.text


def test_compress_to_mp3_timeout(tmp_path, caplog):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    with patch("src.processing.subprocess.run", side_effect=subprocess.TimeoutExpired("ffmpeg", 120)):
        result = compress_to_mp3(wav)
    assert result is None
    assert wav.exists()
    assert "timeout" in caplog.text


def test_compress_to_mp3_ffmpeg_not_found(tmp_path, caplog):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    with patch("src.processing.subprocess.run", side_effect=FileNotFoundError):
        result = compress_to_mp3(wav)
    assert result is None
    assert wav.exists()
    assert "ffmpeg introuvable" in caplog.text


def test_compress_to_mp3_cleans_partial_mp3_on_failure(tmp_path):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    mp3 = tmp_path / "test.mp3"
    mp3.write_bytes(b"\x00" * 20)  # partial file left by failed ffmpeg
    exc = subprocess.CalledProcessError(1, "ffmpeg", stderr=b"")
    with patch("src.processing.subprocess.run", side_effect=exc):
        compress_to_mp3(wav)
    assert not mp3.exists()


def test_compress_to_mp3_uses_quality_param(tmp_path):
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"\x00" * 100)
    mp3 = tmp_path / "test.mp3"
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        mp3.write_bytes(b"\x00" * 10)
        return MagicMock(returncode=0)

    with patch("src.processing.subprocess.run", side_effect=fake_run):
        compress_to_mp3(wav, quality=2)

    assert "-q:a" in captured["cmd"]
    assert "2" in captured["cmd"]
