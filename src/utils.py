#!/usr/bin/env python3
"""
utils.py

Module utilitaire pour :
  - détection du point de montage automatique de la clé USB
  - chargement de la configuration depuis la clé USB
  - démonter la clé USB à l'arrêt du programme
"""
import os
import json
import logging
import getpass
import subprocess

# Base des montages automatiques sous Raspberry Pi OS
AUTO_MEDIA_BASE = '/media'


def find_mount_point() -> str:
    """
    Retourne le chemin du premier répertoire monté sous /media/<user>/
    ou None s'il n'y en a pas.
    """
    user = getpass.getuser()
    base = os.path.join(AUTO_MEDIA_BASE, user)
    if not os.path.isdir(base):
        logging.error(f"Répertoire {base} introuvable.")
        return None
    for entry in os.listdir(base):
        candidate = os.path.join(base, entry)
        if os.path.ismount(candidate):
            logging.info(f"Clé USB détectée sur {candidate}")
            return candidate
    logging.error("Aucun périphérique USB monté sous /media/<user>.")
    return None


def ensure_usb_available() -> str:
    """
    Vérifie la présence de la clé USB montée et retourne son chemin,
    ou None si aucune clé détectée.
    """
    return find_mount_point()


def load_config(mount_point: str) -> dict:
    """
    Charge config.json depuis la racine de la clé USB.
    Retourne un dictionnaire vide en cas d'erreur.
    """
    config_path = os.path.join(mount_point, 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logging.info(f"Configuration chargée depuis {config_path}")
        return config
    except Exception as e:
        logging.error(f"Erreur chargement config depuis {config_path}: {e}")
        return {}


def unmount_usb(mount_point: str) -> bool:
    """
    Démonte la clé USB montée sur mount_point.
    """
    try:
        subprocess.check_call(['umount', mount_point])
        logging.info(f"Clé USB démontée: {mount_point}")
        return True
    except Exception as e:
        logging.error(f"Erreur démontage USB {mount_point}: {e}")
        return False
