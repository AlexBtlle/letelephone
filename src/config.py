import json
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG = _BASE_DIR / "config" / "config.default.json"
_EVENT_CONFIG = _BASE_DIR / "config" / "config.event.json"


def load() -> dict:
    with open(_DEFAULT_CONFIG) as f:
        cfg = json.load(f)

    if _EVENT_CONFIG.exists():
        with open(_EVENT_CONFIG) as f:
            event_override = json.load(f)
        _deep_merge(cfg, event_override)

    return cfg


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
