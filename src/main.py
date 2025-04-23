#!/usr/bin/env python3
"""
main.py

Script principal pour :
- Détection du point de montage de la clé USB
- Chargement de la configuration depuis la clé USB
- Détection du hook switch et gestion audio
- Démontage de la clé USB à l'arrêt
"""
import os
import sys
import time
import logging

import detection
import audio
import utils


def setup_logging():
    """
    Configure le logger pour la console avec horodatage.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )


def main():
    setup_logging()

    # 1. Vérifier la clé USB auto-montée
    mount_point = utils.ensure_usb_available()
    if not mount_point:
        logging.critical("Clé USB non trouvée. Arrêt du programme.")
        sys.exit(1)
    logging.info(f"Clé USB disponible sur {mount_point}")

    # 2. Charger la configuration
    config = utils.load_config(mount_point)
    if not config:
        logging.critical("Impossible de charger config.json depuis la clé USB. Arrêt.")
        sys.exit(1)
    logging.info("Configuration chargée avec succès.")

    # 3. Lecture des paramètres
    hook_pin       = config.get('hook_pin', 17)
    poll_interval  = config.get('poll_interval', 0.1)
    announce_path  = config.get('announce_path')
    beep_path      = config.get('beep_path')
    record_dir     = config.get('record_dir')
    max_duration   = config.get('max_duration')
    pre_beep_delay = config.get('pre_beep_delay', 1)

    # Adapter chemins relatifs (annonce & enregistrements sur USB)
    if announce_path and not os.path.isabs(announce_path):
        announce_path = os.path.join(mount_point, announce_path.lstrip("/"))
    if record_dir and not os.path.isabs(record_dir):
        record_dir = os.path.join(mount_point, record_dir.lstrip("/"))
    # beep_path reste local
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if beep_path and not os.path.isabs(beep_path):
        beep_path = os.path.join(base_dir, beep_path)

    logging.info(
        f"Paramètres: hook_pin={hook_pin}, poll_interval={poll_interval}, "
        f"announce_path={announce_path}, beep_path={beep_path}, "
        f"record_dir={record_dir}, max_duration={max_duration}, pre_beep_delay={pre_beep_delay}"
    )

    # 4. Préparer répertoire d'enregistrements
    if record_dir and not os.path.exists(record_dir):
        os.makedirs(record_dir)
        logging.info(f"Répertoire d'enregistrements créé: {record_dir}")

    # 5. Initialiser GPIO hook
    detection.setup_hook(hook_pin)
    last_state = False

    # 6. Boucle principale
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
