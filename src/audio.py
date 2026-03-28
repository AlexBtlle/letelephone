import subprocess
from pathlib import Path


class AudioController:
    def __init__(
        self,
        playback_device: str = "hw:2,0",
        capture_device: str = "hw:3,0",
        sample_rate: int = 48000,
        channels: int = 1,
        max_duration_sec: int = 180,
    ):
        self.playback_device = playback_device
        self.capture_device = capture_device
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_duration_sec = max_duration_sec
        self.recording_process = None

    def play_beep(self, beep_file: Path) -> None:
        subprocess.run(
            [
                "aplay",
                "-D",
                self.playback_device,
                str(beep_file),
            ],
            check=True,
        )

    def start_recording(self, output_file: Path) -> None:
        if self.recording_process is not None and self.recording_process.poll() is None:
            raise RuntimeError("Un enregistrement est déjà en cours.")

        self.recording_process = subprocess.Popen(
            [
                "arecord",
                "-D",
                self.capture_device,
                "-f",
                "S16_LE",
                "-r",
                str(self.sample_rate),
                "-c",
                str(self.channels),
                "-d",
                str(self.max_duration_sec),
                str(output_file),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def stop_recording(self) -> None:
        if self.recording_process is None:
            return

        if self.recording_process.poll() is None:
            self.recording_process.terminate()
            try:
                self.recording_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.recording_process.kill()
                self.recording_process.wait(timeout=3)

        self.recording_process = None

    def is_recording(self) -> bool:
        return self.recording_process is not None and self.recording_process.poll() is None