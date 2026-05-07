import json
import pytest
from pathlib import Path

import src.config as cfg_module


def _write_configs(tmp_path, default, override=None):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.default.json").write_text(json.dumps(default))
    cfg_module.__dict__["_DEFAULT_CONFIG"] = config_dir / "config.default.json"
    cfg_module.__dict__["_EVENT_CONFIG"] = config_dir / "config.event.json"
    if override is not None:
        (config_dir / "config.event.json").write_text(json.dumps(override))


_DEFAULT = {
    "hook_pin": 17,
    "poll_interval_sec": 0.05,
    "pre_beep_delay_sec": 2.0,
    "max_duration_sec": 180,
    "audio": {"sample_rate": 44100, "channels": 1},
}


def test_load_defaults(tmp_path, monkeypatch):
    _write_configs(tmp_path, _DEFAULT)
    cfg = cfg_module.load()
    assert cfg["hook_pin"] == 17
    assert cfg["audio"]["sample_rate"] == 44100


def test_override_top_level_key(tmp_path, monkeypatch):
    _write_configs(tmp_path, _DEFAULT, override={"max_duration_sec": 240})
    cfg = cfg_module.load()
    assert cfg["max_duration_sec"] == 240
    assert cfg["hook_pin"] == 17  # default preserved


def test_override_nested_key(tmp_path, monkeypatch):
    _write_configs(tmp_path, _DEFAULT, override={"audio": {"sample_rate": 48000, "channels": 1}})
    cfg = cfg_module.load()
    assert cfg["audio"]["sample_rate"] == 48000


def test_no_override_file(tmp_path, monkeypatch):
    _write_configs(tmp_path, _DEFAULT)
    cfg = cfg_module.load()
    assert cfg["max_duration_sec"] == 180
