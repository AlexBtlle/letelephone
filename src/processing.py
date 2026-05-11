import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

_VOICE_FILTERS = "highpass=f=300,lowpass=f=3500,afftdn=nf=-25"


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
        log.warning("Normalisation échouée pour %s : %s", wav_path.name, exc.stderr.decode("utf-8", errors="replace")[-200:] if exc.stderr else "")
        tmp.unlink(missing_ok=True)
    except subprocess.TimeoutExpired:
        log.warning("Normalisation timeout pour %s", wav_path.name)
        tmp.unlink(missing_ok=True)
    except FileNotFoundError:
        log.warning("ffmpeg introuvable — normalisation ignorée")


def compress_to_mp3(wav_path: Path, quality: int = 0) -> Path | None:
    """Convert WAV to MP3 HD using libmp3lame VBR. Deletes the WAV on success.

    quality: VBR level 0 (best, ~245 kbps) to 9 (smallest). Default 0.
    Returns the MP3 Path on success, None on failure (WAV preserved).
    """
    if not wav_path.exists():
        log.warning("compress_to_mp3: fichier introuvable %s", wav_path)
        return None
    mp3_path = wav_path.with_suffix(".mp3")
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(wav_path),
                "-codec:a", "libmp3lame", "-q:a", str(quality),
                str(mp3_path),
            ],
            capture_output=True,
            timeout=120,
            check=True,
        )
        wav_path.unlink()
        log.info("MP3 HD : %s (%.1f ko)", mp3_path.name, mp3_path.stat().st_size / 1024)
        return mp3_path
    except subprocess.CalledProcessError as exc:
        log.warning("Compression MP3 échouée pour %s : %s", wav_path.name, exc.stderr.decode("utf-8", errors="replace")[-200:] if exc.stderr else "")
        mp3_path.unlink(missing_ok=True)
        return None
    except subprocess.TimeoutExpired:
        log.warning("Compression MP3 timeout pour %s", wav_path.name)
        mp3_path.unlink(missing_ok=True)
        return None
    except FileNotFoundError:
        log.warning("ffmpeg introuvable — compression MP3 ignorée")
        return None


def isolate_voice(wav_path: Path) -> Path | None:
    """Apply FFmpeg voice-frequency filters and save result as <stem>_vocal.wav.

    Keeps the original wav_path untouched.
    Returns the vocal Path on success, None on failure.
    """
    if not wav_path.exists():
        log.warning("isolate_voice: fichier introuvable %s", wav_path)
        return None
    vocal_path = wav_path.with_stem(wav_path.stem + "_vocal")
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(wav_path),
                "-af", _VOICE_FILTERS,
                "-ar", "44100",
                str(vocal_path),
            ],
            capture_output=True,
            timeout=120,
            check=True,
        )
        log.info("Isolation voix : %s", vocal_path.name)
        return vocal_path
    except subprocess.CalledProcessError as exc:
        log.warning("Isolation voix échouée pour %s : %s", wav_path.name, exc.stderr.decode("utf-8", errors="replace")[-200:] if exc.stderr else "")
        vocal_path.unlink(missing_ok=True)
        return None
    except subprocess.TimeoutExpired:
        log.warning("Isolation voix timeout pour %s", wav_path.name)
        vocal_path.unlink(missing_ok=True)
        return None
    except FileNotFoundError:
        log.warning("ffmpeg introuvable — isolation voix ignorée")
        return None
