#!/usr/bin/env python3
"""
main.py

Script principal pour la détection du hook switch et gestion audio :
- Lecture de l'annonce si elle existe (MP3/WAV)
- Lecture du bip obligatoire (beep.wav) après un délai
- Lancement et arrêt de l'enregistrement audio
"""
import os
import time
import logging
import detection
import audio

# --- CONFIGURATION ---
HOOK_PIN = 17  # BCM
POLL_INTERVAL = 0.1  # secondes
ANNOUNCE_PATH = os.path.join("audio", "annonces", "accueil.mp3")
BEEP_PATH = os.path.join("audio", "annonces", "beep.wav")
RECORD_DIR = os.path.join("audio", "enregistrements")
MAX_DURATION = None  # en secondes, ou None pour illimité
PRE_BEEP_DELAY = 1  # secondes de délai avant le bip et l'enregistrement
# ----------------------


def setup_logging():
    """
    Configure le logger pour la console avec timestamp.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )


def ensure_directories():
    """
    Crée le répertoire d'enregistrements si nécessaire.
    """
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)


def main():
    setup_logging()
    ensure_directories()

    logging.info(f"Démarrage détection hook sur GPIO {HOOK_PIN}")
    detection.setup_hook(HOOK_PIN)
    last_state = False

    try:
        while True:
            state = detection.is_hooked()
            # Transition "raccroché" -> "décroché"
            if state and not last_state:
                logging.info("Événement : décroché détecté")
                # Lecture annonce si disponible
                if os.path.isfile(ANNOUNCE_PATH):
                    audio.play_announcement(ANNOUNCE_PATH)
                else:
                    logging.info(f"Annonce absente : {ANNOUNCE_PATH}")

                # Délai avant le bip et le début de l'enregistrement
                logging.info(f"Attente de {PRE_BEEP_DELAY} secondes avant le bip et l'enregistrement")
                time.sleep(PRE_BEEP_DELAY)

                # Lecture du bip obligatoire
                audio.play_announcement(BEEP_PATH)

                # Démarrage enregistrement
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                outfile = os.path.join(RECORD_DIR, f"message_{timestamp}.wav")
                audio.start_recording(outfile, MAX_DURATION)

            # Transition "décroché" -> "raccroché"
            elif not state and last_state:
                logging.info("Événement : raccroché détecté")
                audio.stop_recording()

            last_state = state
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logging.info("Arrêt manuel de l'application")
    finally:
        detection.cleanup_hook()
        logging.info("GPIO nettoyés, fin du programme")


if __name__ == '__main__':
    main()
