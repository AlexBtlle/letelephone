import json
import pytest
from pathlib import Path

import src.config as cfg_module
from src.config import ConfigError


def _setup(tmp_path, default, override=None):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.default.json").write_text(json.dumps(default))
    cfg_module._DEFAULT_CONFIG = config_dir / "config.default.json"
    cfg_module._EVENT_CONFIG = config_dir / "config.event.json"
    if override is not None:
        (config_dir / "config.event.json").write_text(override if isinstance(override, str) else json.dumps(override))


_DEFAULT = {
    "hook_pin": 17,
    "poll_interval_sec": 0.05,
    "pre_beep_delay_sec": 2.0,
    "max_duration_sec": 180,
    "audio": {"sample_rate": 44100, "channels": 1},
}


def test_load_defaults(tmp_path):
    _setup(tmp_path, _DEFAULT)
    cfg = cfg_module.load()
    assert cfg["hook_pin"] == 17
    assert cfg["audio"]["sample_rate"] == 44100


def test_override_top_level_key(tmp_path):
    _setup(tmp_path, _DEFAULT, override={"max_duration_sec": 240})
    cfg = cfg_module.load()
    assert cfg["max_duration_sec"] == 240
    assert cfg["hook_pin"] == 17


def test_override_nested_key(tmp_path):
    _setup(tmp_path, _DEFAULT, override={"audio": {"sample_rate": 48000, "channels": 1}})
    cfg = cfg_module.load()
    assert cfg["audio"]["sample_rate"] == 48000


def test_no_override_file(tmp_path):
    _setup(tmp_path, _DEFAULT)
    cfg = cfg_module.load()
    assert cfg["max_duration_sec"] == 180


def test_missing_default_config_raises(tmp_path):
    cfg_module._DEFAULT_CONFIG = tmp_path / "nonexistent.json"
    cfg_module._EVENT_CONFIG = tmp_path / "config.event.json"
    with pytest.raises(ConfigError, match="introuvable"):
        cfg_module.load()


def test_malformed_default_json_raises(tmp_path):
    _setup(tmp_path, _DEFAULT)
    cfg_module._DEFAULT_CONFIG.write_text("{invalid json")
    with pytest.raises(ConfigError, match="malformé"):
        cfg_module.load()


def test_missing_required_key_raises(tmp_path):
    incomplete = {k: v for k, v in _DEFAULT.items() if k != "hook_pin"}
    _setup(tmp_path, incomplete)
    with pytest.raises(ConfigError, match="hook_pin"):
        cfg_module.load()


def test_malformed_override_json_is_ignored(tmp_path):
    _setup(tmp_path, _DEFAULT, override="{bad json")
    # Should not raise — override file is optional
    cfg = cfg_module.load()
    assert cfg["hook_pin"] == 17
