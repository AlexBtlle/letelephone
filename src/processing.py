import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def normalize_audio(wav_path: Path) -> None:
    """Normalize loudness to -16 LUFS with ffmpeg loudnorm. Replaces the file in-place."""
    if not wav_path.exists():
        log.warning("normalize_audio: fichier introuvable %s", wav_path)
        return
    tmp = wav_path.with_suffix(".tmp.wav")
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(wav_path),
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                "-ar", "44100",
                str(tmp),
            ],
            capture_output=True,
            timeout=120,
            check=True,
        )
        tmp.replace(wav_path)
        log.info("Audio normalisé : %s", wav_path.name)
    except subprocess.CalledProcessError as exc:
        log.warning("Normalisation échouée pour %s : %s", wav_path.name, exc.stderr[-200:] if exc.stderr else "")
        tmp.unlink(missing_ok=True)
    except subprocess.TimeoutExpired:
        log.warning("Normalisation timeout pour %s", wav_path.name)
        tmp.unlink(missing_ok=True)
    except FileNotFoundError:
        log.warning("ffmpeg introuvable — normalisation ignorée")
