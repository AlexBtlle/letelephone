import logging
import re
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def _detect_usb_alsa_device(stream: str) -> str:
    """Return the first USB Audio card/device found via aplay/arecord -l, or 'default'."""
    try:
        result = subprocess.run(
            ["arecord" if stream == "capture" else "aplay", "-l"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.splitlines():
            if "USB Audio" in line or "USB-Audio" in line:
                m = re.search(r"card (\d+):.*device (\d+):", line)
                if m:
                    return f"hw:{m.group(1)},{m.group(2)}"
    except Exception as exc:
        log.warning("Impossible de détecter le périphérique ALSA (%s): %s", stream, exc)
    return "default"


class AudioController:
    def __init__(
        self,
        sample_rate: int = 44100,
        channels: int = 1,
        max_duration_sec: int = 180,
        playback_device: str | None = None,
        capture_device: str | None = None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration_sec = max_duration_sec
        self.playback_device = playback_device or _detect_usb_alsa_device("playback")
        self.capture_device = capture_device or _detect_usb_alsa_device("capture")
        self._recording_process: subprocess.Popen | None = None
        log.info(
            "AudioController: playback=%s capture=%s",
            self.playback_device, self.capture_device,
        )

    def play_audio(self, audio_file: Path) -> None:
        if not audio_file.exists():
            raise FileNotFoundError(f"Fichier audio introuvable : {audio_file}")
        log.debug("Lecture : %s", audio_file.name)
        subprocess.run(
            ["aplay", "-D", self.playback_device, str(audio_file)],
            check=True,
            timeout=self.max_duration_sec + 10,
        )

    def start_recording(self, output_file: Path) -> None:
        if self._recording_process is not None and self._recording_process.poll() is None:
            raise RuntimeError("Un enregistrement est déjà en cours.")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        log.info("Démarrage enregistrement : %s", output_file.name)
        self._recording_process = subprocess.Popen(
            [
                "arecord",
                "-D", self.capture_device,
                "-f", "S16_LE",
                "-r", str(self.sample_rate),
                "-c", str(self.channels),
                "-d", str(self.max_duration_sec),
                str(output_file),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def stop_recording(self) -> None:
        if self._recording_process is None:
            return
        if self._recording_process.poll() is None:
            self._recording_process.terminate()
            try:
                self._recording_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._recording_process.kill()
                try:
                    self._recording_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pid = self._recording_process.pid
                    self._recording_process = None
                    raise RuntimeError(f"Processus arecord impossible à tuer (PID {pid})")
            log.info("Enregistrement arrêté.")
        self._recording_process = None

    def is_recording(self) -> bool:
        return self._recording_process is not None and self._recording_process.poll() is None
