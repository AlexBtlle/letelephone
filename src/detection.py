#!/usr/bin/env python3
"""
detection.py

Module de gestion du hook switch (décrochage/raccrochage) du combiné.
Exporte :
  - setup_hook(pin: int)
  - is_hooked() -> bool
  - cleanup_hook()
"""
import time
import RPi.GPIO as GPIO

# Numéro de la broche BCM utilisée pour le hook switch
HOOK_PIN = None

# Durée de debounce (secondes)
_DEBOUNCE_DELAY = 0.05


def setup_hook(pin: int) -> None:
    """
    Initialise la détection du hook switch sur la broche BCM spécifiée.
    Doit être appelé avant is_hooked().
    """
    global HOOK_PIN
    HOOK_PIN = pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(HOOK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def is_hooked() -> bool:
    """
    Retourne True si le combiné est décroché (INPUT HIGH deux fois),
    False si raccroché ou en cas de rebond.
    Implémente un simple debounce.
    """
    if HOOK_PIN is None:
        raise RuntimeError("Hook switch non initialisé, appeler setup_hook(pin) d'abord.")
    # Lecture initiale
    first = GPIO.input(HOOK_PIN)
    # Petit délai pour debounce
    time.sleep(_DEBOUNCE_DELAY)
    # Relecture pour validation
    second = GPIO.input(HOOK_PIN)
    # Retourne un booléen explicite
    return bool(first and second)


def cleanup_hook() -> None:
    """
    Libère les ressources GPIO associées au hook switch.
    """
    if HOOK_PIN is not None:
        GPIO.cleanup(HOOK_PIN)
    else:
        GPIO.cleanup()
