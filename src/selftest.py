"""Boot self-test. Executed by systemd ExecStartPre before main.py.

Exits 0 if all checks pass, 1 if a critical check fails (systemd will not start main).
Plays error.wav on critical failure so the operator hears the problem.
"""

import getpass
import json
import logging
import subprocess
import sys
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_ASSETS_DIR = _BASE_DIR / "assets"

log = logging.getLogger(__name__)


def _play_error() -> None:
    error_file = _ASSETS_DIR / "error.wav"
    if error_file.exists():
        try:
            subprocess.run(["aplay", str(error_file)], timeout=10)
        except Exception:
            pass


def check_audio_devices() -> bool:
    try:
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            log.error("selftest: aplay -l a échoué")
            return False
        # At least one card must be present
        if "card" not in result.stdout:
            log.error("selftest: aucune carte audio détectée")
            return False
        return True
    except FileNotFoundError:
        log.error("selftest: aplay introuvable (alsa-utils non installé ?)")
        return False
    except subprocess.TimeoutExpired:
        log.error("selftest: timeout aplay -l")
        return False


def check_beep_file() -> bool:
    beep = _ASSETS_DIR / "beep.wav"
    if not beep.exists():
        log.error("selftest: assets/beep.wav introuvable")
        return False
    return True


def check_config() -> bool:
    config_path = _BASE_DIR / "config" / "config.default.json"
    if not config_path.exists():
        log.error("selftest: config/config.default.json introuvable")
        return False
    try:
        with open(config_path) as f:
            json.load(f)
        return True
    except Exception as exc:
        log.error("selftest: config invalide : %s", exc)
        return False


def _is_pi_zero2() -> bool:
    try:
        with open("/proc/cpuinfo") as f:
            return "Zero 2" in f.read()
    except OSError:
        return False


def check_codec_zero() -> bool:
    """Critical: on Pi Zero 2 W, IQaudio Codec Zero must appear in aplay -l."""
    if not _is_pi_zero2():
        return True
    try:
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=5)
        if any(kw in result.stdout for kw in ("IQaudIO", "DA7212")):
            log.info("selftest: IQaudio Codec Zero détecté OK")
            return True
        log.error(
            "selftest: Pi Zero 2 W détecté mais Codec Zero absent. "
            "Vérifiez que dtoverlay=iqaudio-codec est dans /boot/firmware/config.txt "
            "et redémarrez le Pi."
        )
        return False
    except FileNotFoundError:
        log.error("selftest: aplay introuvable — alsa-utils non installé ?")
        return False
    except subprocess.TimeoutExpired:
        log.error("selftest: timeout aplay -l (check_codec_zero)")
        return False


def check_usb_writable() -> bool:
    """Non-blocking: warns but doesn't fail if USB absent."""
    base = Path("/media") / getpass.getuser()
    if not base.is_dir():
        log.warning("selftest: %s introuvable, pas de clé USB détectée", base)
        return True  # non-critical
    for entry in base.iterdir():
        if entry.is_mount():
            test_file = entry / ".letelephone_test"
            try:
                test_file.write_text("ok")
                test_file.unlink()
                log.info("selftest: clé USB OK (%s)", entry)
                return True
            except OSError as exc:
                log.error("selftest: clé USB non accessible en écriture : %s", exc)
                return True  # warn only, not critical
    log.warning("selftest: aucune clé USB montée, enregistrements en local")
    return True


def run() -> bool:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )
    log.info("=== Démarrage selftest ===")
    ok = True
    ok &= check_config()
    ok &= check_beep_file()
    ok &= check_audio_devices()
    ok &= check_codec_zero()
    check_usb_writable()  # warning only
    if ok:
        log.info("selftest: tous les contrôles OK")
    else:
        log.error("selftest: échec — arrêt du service")
        _play_error()
    return ok


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
