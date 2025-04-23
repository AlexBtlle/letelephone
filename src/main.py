#!/usr/bin/env python3
"""
main.py

Script principal pour :
- Détection du point de montage de la clé USB
- Chargement de la configuration depuis la clé USB
- Configuration de la journalisation sur console et fichier sur la clé USB
- Détection du hook switch et gestion audio
- Lecture d'un message d'erreur en cas d'échec critique
- Démontage de la clé USB à l'arrêt
"""
import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler

import detection
import audio
import utils


def setup_logging(log_file_path: str):
    """
    Configure le logger pour la console et un fichier rotatif.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler with rotation
    log_dir = os.path.dirname(log_file_path)
    os.makedirs(log_dir, exist_ok=True)
    fh = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)


def main():
    # Base directory of project for relative paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Default error announcement on local RPi
    default_error = os.path.join(base_dir, 'audio', 'annonces', 'error.wav')

    # 1. Vérifier la clé USB auto-montée
    mount_point = utils.ensure_usb_available()
    if not mount_point:
        # Critical error: play error message then exit
        audio.play_announcement(default_error)
        print("Erreur critique : clé USB non trouvée. Arrêt.")
        sys.exit(1)

    # Prepare logs on USB
    logs_dir = os.path.join(mount_point, 'logs')
    log_file = os.path.join(logs_dir, 'system.log')

    # 2. Configure logging
    setup_logging(log_file)
    logging.info(f"Clé USB disponible sur {mount_point}")

    # 3. Charger la configuration depuis la clé USB
    config = utils.load_config(mount_point)
    if not config:
        audio.play_announcement(default_error)
        logging.critical("Impossible de charger config.json depuis la clé USB. Arrêt.")
        sys.exit(1)
    logging.info("Configuration chargée avec succès.")

    # 4. Lecture des paramètres
    hook_pin       = config.get('hook_pin', 17)
    poll_interval  = config.get('poll_interval', 0.1)
    announce_path  = config.get('announce_path')
    beep_path      = config.get('beep_path')
    record_dir     = config.get('record_dir')
    max_duration   = config.get('max_duration')
    pre_beep_delay = config.get('pre_beep_delay', 1)
    # Optional error path in config, fallback to default
    error_path     = config.get('error_path') or default_error

    # Adapter chemins relatifs (annonce & enregistrements sur USB)
    if announce_path and not os.path.isabs(announce_path):
        announce_path = os.path.join(mount_point, announce_path.lstrip("/"))
    if record_dir and not os.path.isabs(record_dir):
        record_dir = os.path.join(mount_point, record_dir.lstrip("/"))
    # beep_path & error_path locaux
    if beep_path and not os.path.isabs(beep_path):
        beep_path = os.path.join(base_dir, beep_path)
    if error_path and not os.path.isabs(error_path):
        error_path = error_path  # error_path already absolute (default_error)

    logging.info(
        f"Paramètres: hook_pin={hook_pin}, poll_interval={poll_interval}, "
        f"announce_path={announce_path}, beep_path={beep_path}, "
        f"record_dir={record_dir}, max_duration={max_duration}, pre_beep_delay={pre_beep_delay}, "
        f"error_path={error_path}"
    )

    # 5. Préparer répertoire d'enregistrements
    if record_dir and not os.path.exists(record_dir):
        os.makedirs(record_dir, exist_ok=True)
        logging.info(f"Répertoire d'enregistrements créé: {record_dir}")

    # 6. Initialiser GPIO hook
    detection.setup_hook(hook_pin)
    last_state = False

    # 7. Boucle principale
    try:
        while True:
            state = detection.is_hooked()

            # Décroché
            if state and not last_state:
                logging.info("Événement: décroché détecté")

                if announce_path and os.path.isfile(announce_path):
                    audio.play_announcement(announce_path)
                else:
                    logging.warning(f"Annonce absente: {announce_path}")

                logging.info(f"Attente de {pre_beep_delay}s avant bip et enregistrement")
                time.sleep(pre_beep_delay)

                audio.play_announcement(beep_path)

                timestamp = time.strftime("%Y%m%d_%H%M%S")
                outfile = os.path.join(record_dir, f"message_{timestamp}.wav")
                audio.start_recording(outfile, max_duration)

            # Raccroché
            elif not state and last_state:
                logging.info("Événement: raccroché détecté")
                audio.stop_recording()

            last_state = state
            time.sleep(poll_interval)

    except Exception as e:
        logging.error(f"Erreur inattendue: {e}", exc_info=True)
        # Play error announcement
        audio.play_announcement(error_path)
    except KeyboardInterrupt:
        logging.info("Arrêt manuel de l'application")
    finally:
        detection.cleanup_hook()
        # Démonter la clé USB
        if mount_point:
            utils.unmount_usb(mount_point)
        logging.info("GPIO libérés, clé USB démontée, sortie du programme")


if __name__ == '__main__':
    main()
