import time
from pathlib import Path

from src.storage import build_recording_path, count_recordings, ensure_recordings_dir


def test_ensure_recordings_dir_creates_directory(tmp_path):
    d = ensure_recordings_dir(tmp_path)
    assert d.exists()
    assert d.is_dir()
    assert d == tmp_path / "recordings"


def test_ensure_recordings_dir_idempotent(tmp_path):
    ensure_recordings_dir(tmp_path)
    d = ensure_recordings_dir(tmp_path)
    assert d.exists()


def test_build_recording_path_format(tmp_path):
    path = build_recording_path(tmp_path)
    assert path.parent == tmp_path
    assert path.suffix == ".wav"
    assert path.name.startswith("message_")


def test_build_recording_path_unique(tmp_path):
    p1 = build_recording_path(tmp_path)
    time.sleep(0.01)
    p2 = build_recording_path(tmp_path)
    assert p1.name.startswith("message_")
    assert p2.name.startswith("message_")


def test_count_recordings_empty_dir(tmp_path):
    assert count_recordings(tmp_path) == 0


def test_count_recordings_nonexistent_dir(tmp_path):
    assert count_recordings(tmp_path / "absent") == 0


def test_count_recordings_counts_only_message_wavs(tmp_path):
    (tmp_path / "message_2026-06-15_12-00-00.wav").write_bytes(b"\x00")
    (tmp_path / "message_2026-06-15_12-01-00.wav").write_bytes(b"\x00")
    (tmp_path / "other.wav").write_bytes(b"\x00")  # not counted
    (tmp_path / "message_test.txt").write_bytes(b"\x00")  # not counted
    assert count_recordings(tmp_path) == 2
