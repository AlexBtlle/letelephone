import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.audio import AudioController
from src.config import load as load_config
from src.hook import HookSwitch
from src.storage import build_recording_path, ensure_recordings_dir
from src.usb import UsbStorage

_BASE_DIR = Path(__file__).resolve().parent.parent
_ASSETS_DIR = _BASE_DIR / "assets"
_BEEP_FILE = _ASSETS_DIR / "beep.wav"
_ERROR_FILE = _ASSETS_DIR / "error.wav"


def _setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(
        log_dir / "letelephone.log", maxBytes=10 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


def main() -> None:
    cfg = load_config()

    usb = UsbStorage()
    recordings_dir = usb.recordings_dir() if usb.is_available() else ensure_recordings_dir(_BASE_DIR)
    log_dir = usb.log_dir() if usb.is_available() else _BASE_DIR / "logs"

    _setup_logging(log_dir)
    log = logging.getLogger(__name__)

    log.info("Démarrage. Enregistrements → %s", recordings_dir)
    if not usb.is_available():
        log.warning("Clé USB non détectée — enregistrements en local.")

    # welcome.wav à la racine de la clé USB, sinon beep par défaut
    welcome_file = usb.welcome_file() or _BEEP_FILE
    log.info("Message d'accueil : %s", welcome_file.name)

    audio = AudioController(
        sample_rate=cfg["audio"]["sample_rate"],
        channels=cfg["audio"]["channels"],
        max_duration_sec=cfg["max_duration_sec"],
    )
    hook = HookSwitch(gpio_pin=cfg["hook_pin"], pull_up=True, bounce_time=0.05)

    poll = cfg["poll_interval_sec"]
    pre_beep_delay = cfg["pre_beep_delay_sec"]

    log.info("Système prêt. En attente du décrochage...")

    try:
        while True:
            if hook.is_off_hook():
                log.info("Décroché détecté.")
                time.sleep(pre_beep_delay)

                try:
                    audio.play_audio(welcome_file)
                except Exception as exc:
                    log.error("Erreur lecture message d'accueil : %s", exc)
                    _try_play_error(audio)
                    _wait_for_hangup(hook, poll)
                    continue

                output_file = build_recording_path(recordings_dir)
                try:
                    audio.start_recording(output_file)
                except Exception as exc:
                    log.error("Erreur démarrage enregistrement : %s", exc)
                    _try_play_error(audio)
                    _wait_for_hangup(hook, poll)
                    continue

                while hook.is_off_hook() and audio.is_recording():
                    time.sleep(poll)

                audio.stop_recording()

                if output_file.exists() and output_file.stat().st_size > 0:
                    log.info("Message enregistré : %s (%.1f ko)", output_file.name, output_file.stat().st_size / 1024)
                else:
                    log.warning("Fichier enregistré vide ou absent : %s", output_file.name)

                _wait_for_hangup(hook, poll)
                log.info("Retour en attente.")

            time.sleep(poll)

    except KeyboardInterrupt:
        log.info("Arrêt demandé.")
    finally:
        audio.stop_recording()
        hook.close()


def _wait_for_hangup(hook: HookSwitch, poll: float) -> None:
    while hook.is_off_hook():
        time.sleep(poll)


def _try_play_error(audio: AudioController) -> None:
    if _ERROR_FILE.exists():
        try:
            audio.play_audio(_ERROR_FILE)
        except Exception:
            pass


if __name__ == "__main__":
    main()
