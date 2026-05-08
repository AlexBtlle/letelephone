import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.audio import AudioController
from src.config import ConfigError, load as load_config
from src.display import build as build_display
from src.hook import HookSwitch
from src.processing import compress_to_mp3, normalize_audio
from src.shutdown_button import build as build_shutdown_button
from src.storage import build_recording_path, count_recordings, ensure_recordings_dir
from src.usb import UsbStorage

_BASE_DIR = Path(__file__).resolve().parent.parent
_ASSETS_DIR = _BASE_DIR / "assets"
_BEEP_FILE = _ASSETS_DIR / "beep.wav"
_ERROR_FILE = _ASSETS_DIR / "error.wav"

_DEFAULTS = {
    "hook_pin": 17,
    "poll_interval_sec": 0.05,
    "pre_beep_delay_sec": 2.0,
    "max_duration_sec": 180,
    "min_duration_sec": 1.0,
    "couple_name": "",
    "audio": {"sample_rate": 44100, "channels": 1},
    "normalize_audio": True,
    "compress_mp3": {"enabled": True, "quality": 0},
    "shutdown_button": {"enabled": False},
}


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
    usb = UsbStorage()

    log_dir = _BASE_DIR / "logs"
    try:
        log_dir = usb.log_dir() if usb.is_available() else _BASE_DIR / "logs"
    except OSError:
        pass
    _setup_logging(log_dir)
    log = logging.getLogger(__name__)

    try:
        cfg = load_config()
    except ConfigError as exc:
        log.error("Erreur de configuration : %s — utilisation des valeurs par défaut", exc)
        import copy
        cfg = copy.deepcopy(_DEFAULTS)

    try:
        recordings_dir = usb.recordings_dir() if usb.is_available() else ensure_recordings_dir(_BASE_DIR)
    except (OSError, RuntimeError) as exc:
        log.error("Impossible d'accéder au dossier USB (%s) — fallback local", exc)
        recordings_dir = ensure_recordings_dir(_BASE_DIR)

    log.info("Démarrage. Enregistrements → %s", recordings_dir)
    if not usb.is_available():
        log.warning("Clé USB non détectée — enregistrements en local.")

    welcome_file = usb.welcome_file() or _BEEP_FILE
    log.info("Message d'accueil : %s", welcome_file.name)

    couple_name = usb.couple_name() or cfg.get("couple_name", "")
    if couple_name:
        log.info("Événement : %s", couple_name)

    audio = AudioController(
        sample_rate=cfg["audio"]["sample_rate"],
        channels=cfg["audio"]["channels"],
        max_duration_sec=cfg["max_duration_sec"],
    )
    hook = HookSwitch(gpio_pin=cfg["hook_pin"], pull_up=True, bounce_time=0.05)
    display = build_display()
    shutdown_btn = build_shutdown_button(cfg, on_shutdown=lambda: log.info("Arrêt demandé via bouton."))

    poll = cfg["poll_interval_sec"]
    pre_beep_delay = cfg["pre_beep_delay_sec"]
    min_duration = cfg.get("min_duration_sec", 1.0)
    do_normalize = cfg.get("normalize_audio", True)
    mp3_cfg = cfg.get("compress_mp3", {})
    do_compress = mp3_cfg.get("enabled", True)
    mp3_quality = mp3_cfg.get("quality", 0)

    message_count = count_recordings(recordings_dir)
    log.info("Système prêt (%d message(s) existant(s)).", message_count)
    display.show_idle(couple_name, message_count)

    try:
        while True:
            try:
                off_hook = hook.is_off_hook()
            except Exception as exc:
                log.error("Erreur lecture GPIO : %s — nouvelle tentative dans 1s", exc)
                time.sleep(1)
                continue

            if off_hook:
                log.info("Décroché détecté.")
                display.show_recording(couple_name, message_count)
                time.sleep(pre_beep_delay)

                try:
                    audio.play_audio(welcome_file)
                except Exception as exc:
                    log.error("Erreur lecture message d'accueil : %s", exc)
                    _try_play_error(audio)
                    display.show_idle(couple_name, message_count)
                    _wait_for_hangup(hook, poll)
                    continue

                output_file = build_recording_path(recordings_dir)
                record_start = time.monotonic()
                try:
                    audio.start_recording(output_file)
                except Exception as exc:
                    log.error("Erreur démarrage enregistrement : %s", exc)
                    _try_play_error(audio)
                    display.show_idle(couple_name, message_count)
                    _wait_for_hangup(hook, poll)
                    continue

                while hook.is_off_hook() and audio.is_recording():
                    time.sleep(poll)

                audio.stop_recording()
                duration = time.monotonic() - record_start

                if duration < min_duration:
                    output_file.unlink(missing_ok=True)
                    log.info("Message ignoré (trop court : %.1fs)", duration)
                    display.show_idle(couple_name, message_count)
                    _wait_for_hangup(hook, poll)
                    continue

                try:
                    file_size = output_file.stat().st_size
                except OSError:
                    file_size = 0
                if file_size > 0:
                    message_count += 1
                    log.info(
                        "Message #%d enregistré : %s (%.1f ko)",
                        message_count,
                        output_file.name,
                        file_size / 1024,
                    )
                    if do_normalize:
                        normalize_audio(output_file)
                    if do_compress:
                        compress_to_mp3(output_file, quality=mp3_quality)
                else:
                    log.warning("Fichier enregistré vide ou absent : %s", output_file.name)

                display.show_idle(couple_name, message_count)
                _wait_for_hangup(hook, poll)
                log.info("Retour en attente.")

            time.sleep(poll)

    except KeyboardInterrupt:
        log.info("Arrêt demandé.")
    finally:
        audio.stop_recording()
        hook.close()
        display.clear()
        shutdown_btn.close()


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
