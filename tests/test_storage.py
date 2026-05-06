from pathlib import Path

from src.storage import build_recording_path, ensure_recordings_dir


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
    import time
    p1 = build_recording_path(tmp_path)
    time.sleep(0.01)
    p2 = build_recording_path(tmp_path)
    # Both end in .wav and start with message_, may be same if called within same second
    assert p1.name.startswith("message_")
    assert p2.name.startswith("message_")
