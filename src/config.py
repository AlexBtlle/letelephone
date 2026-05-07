import json
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG = _BASE_DIR / "config" / "config.default.json"
_EVENT_CONFIG = _BASE_DIR / "config" / "config.event.json"

_REQUIRED_KEYS = ["hook_pin", "poll_interval_sec", "pre_beep_delay_sec", "max_duration_sec", "audio"]


class ConfigError(Exception):
    pass


def load() -> dict:
    try:
        with open(_DEFAULT_CONFIG) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Fichier de configuration introuvable : {_DEFAULT_CONFIG}")
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config.default.json invalide (JSON malformé) : {exc}")

    missing = [k for k in _REQUIRED_KEYS if k not in cfg]
    if missing:
        raise ConfigError(f"Clés manquantes dans la configuration : {missing}")

    if _EVENT_CONFIG.exists():
        try:
            with open(_EVENT_CONFIG) as f:
                event_override = json.load(f)
            _deep_merge(cfg, event_override)
        except json.JSONDecodeError as exc:
            # Override file is optional — warn and continue with defaults
            import logging
            logging.getLogger(__name__).warning(
                "config.event.json invalide, ignoré : %s", exc
            )

    return cfg


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
