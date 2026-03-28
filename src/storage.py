from datetime import datetime
from pathlib import Path


def ensure_recordings_dir(base_dir: Path) -> Path:
    recordings_dir = base_dir / "recordings"
    recordings_dir.mkdir(parents=True, exist_ok=True)
    return recordings_dir


def build_recording_path(recordings_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return recordings_dir / f"message_{timestamp}.wav"