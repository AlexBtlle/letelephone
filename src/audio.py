#!/usr/bin/env python3
"""
audio.py

Module de gestion de la lecture d'annonces et de l'enregistrement audio.
Exporte :
  - play_announcement(path: str) -> None
  - start_recording(output_path: str) -> None
  - stop_recording() -> None
"""
import subprocess
import logging
import datetime
import os

# Processus d'enregistrement en cours
en_rec_process = None


def play_announcement(path: str) -> None:
    """
    Joue un fichier audio (MP3/WAV) en mode bloquant.
    Utilise omxplayer ou aplay selon le format.
    """
    if not os.path.isfile(path):
        logging.error(f"Annonce non trouvée : {path}")
        return
    logging.info(f"Lecture de l'annonce : {path}")
    # Choix du lecteur selon l'extension
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in ['.mp3']:
            subprocess.run(['omxplayer', '--no-keys', path], check=True)
        else:
            subprocess.run(['aplay', path], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de la lecture de l'annonce : {e}")


def start_recording(output_path: str, max_duration: int = None) -> None:
    """
    Démarre l'enregistrement audio dans un fichier WAV.
    Si max_duration est défini, utilise arecord -d pour limiter la durée.
    """
    global en_rec_process
    if en_rec_process is not None and en_rec_process.poll() is None:
        logging.warning("Un enregistrement est déjà en cours.")
        return
    # Prépare la commande arecord
    cmd = ['arecord', '-f', 'cd', output_path]
    if max_duration:
        cmd.insert(2, '-d')
        cmd.insert(3, str(max_duration))
    logging.info(f"Démarrage de l'enregistrement : {output_path}")
    try:
        en_rec_process = subprocess.Popen(cmd)
    except Exception as e:
        logging.error(f"Impossible de démarrer l'enregistrement : {e}")
        en_rec_process = None


def stop_recording() -> None:
    """
    Stoppe l'enregistrement en cours s'il existe.
    """
    global en_rec_process
    if en_rec_process is None:
        logging.warning("Aucun enregistrement en cours à arrêter.")
        return
    if en_rec_process.poll() is None:
        logging.info("Arrêt de l'enregistrement.")
        en_rec_process.terminate()
        en_rec_process.wait()
    en_rec_process = None
