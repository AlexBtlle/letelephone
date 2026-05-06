import json
import pytest
from pathlib import Path


def test_load_defaults(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.default.json").write_text(json.dumps({
        "hook_pin": 17,
        "poll_interval_sec": 0.05,
        "pre_beep_delay_sec": 2.0,
        "max_duration_sec": 180,
        "audio": {"sample_rate": 44100, "channels": 1},
        "event": {"couple_name": "", "date": "", "welcome_audio": ""},
    }))

    import src.config as cfg_module
    monkeypatch.setattr(cfg_module, "_DEFAULT_CONFIG", config_dir / "config.default.json")
    monkeypatch.setattr(cfg_module, "_EVENT_CONFIG", config_dir / "config.event.json")

    cfg = cfg_module.load()
    assert cfg["hook_pin"] == 17
    assert cfg["audio"]["sample_rate"] == 44100


def test_event_override_merged(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.default.json").write_text(json.dumps({
        "hook_pin": 17,
        "poll_interval_sec": 0.05,
        "pre_beep_delay_sec": 2.0,
        "max_duration_sec": 180,
        "audio": {"sample_rate": 44100, "channels": 1},
        "event": {"couple_name": "", "date": "", "welcome_audio": ""},
    }))
    (config_dir / "config.event.json").write_text(json.dumps({
        "event": {"couple_name": "Alice & Bob", "date": "2026-06-15", "welcome_audio": "welcome.wav"}
    }))

    import src.config as cfg_module
    monkeypatch.setattr(cfg_module, "_DEFAULT_CONFIG", config_dir / "config.default.json")
    monkeypatch.setattr(cfg_module, "_EVENT_CONFIG", config_dir / "config.event.json")

    cfg = cfg_module.load()
    assert cfg["event"]["couple_name"] == "Alice & Bob"
    assert cfg["hook_pin"] == 17  # default preserved


def test_event_override_does_not_affect_defaults(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.default.json").write_text(json.dumps({
        "hook_pin": 17, "max_duration_sec": 180,
        "audio": {"sample_rate": 44100, "channels": 1},
        "event": {},
        "poll_interval_sec": 0.05, "pre_beep_delay_sec": 2.0,
    }))
    (config_dir / "config.event.json").write_text(json.dumps({
        "max_duration_sec": 240
    }))

    import src.config as cfg_module
    monkeypatch.setattr(cfg_module, "_DEFAULT_CONFIG", config_dir / "config.default.json")
    monkeypatch.setattr(cfg_module, "_EVENT_CONFIG", config_dir / "config.event.json")

    cfg = cfg_module.load()
    assert cfg["max_duration_sec"] == 240
    assert cfg["hook_pin"] == 17
