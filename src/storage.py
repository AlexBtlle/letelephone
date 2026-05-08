from datetime import datetime
from pathlib import Path


def ensure_recordings_dir(base_dir: Path) -> Path:
    recordings_dir = base_dir / "recordings"
    recordings_dir.mkdir(parents=True, exist_ok=True)
    return recordings_dir


def build_recording_path(recordings_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return recordings_dir / f"message_{timestamp}.wav"


def count_recordings(recordings_dir: Path) -> int:
    if not recordings_dir.exists():
        return 0
    return sum(
        1 for f in recordings_dir.iterdir()
        if f.stem.startswith("message_") and f.suffix in (".wav", ".mp3")
    )