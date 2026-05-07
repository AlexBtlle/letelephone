import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import src.selftest as st


@pytest.fixture(autouse=True)
def patch_base(tmp_path, monkeypatch):
    """Redirect selftest paths to tmp_path."""
    assets = tmp_path / "assets"
    assets.mkdir()
    config = tmp_path / "config"
    config.mkdir()
    monkeypatch.setattr(st, "_BASE_DIR", tmp_path)
    monkeypatch.setattr(st, "_ASSETS_DIR", assets)
    return tmp_path


# ── check_config ─────────────────────────────────────────────────────────────

def test_check_config_ok(patch_base):
    cfg = {"hook_pin": 17, "poll_interval_sec": 0.05, "pre_beep_delay_sec": 2.0,
           "max_duration_sec": 180, "audio": {"sample_rate": 44100, "channels": 1}}
    (patch_base / "config" / "config.default.json").write_text(json.dumps(cfg))
    assert st.check_config() is True


def test_check_config_missing_file(patch_base):
    assert st.check_config() is False


def test_check_config_malformed_json(patch_base):
    (patch_base / "config" / "config.default.json").write_text("{bad")
    assert st.check_config() is False


# ── check_beep_file ───────────────────────────────────────────────────────────

def test_check_beep_file_present(patch_base):
    (patch_base / "assets" / "beep.wav").write_bytes(b"\x00")
    assert st.check_beep_file() is True


def test_check_beep_file_missing(patch_base):
    assert st.check_beep_file() is False


# ── check_audio_devices ───────────────────────────────────────────────────────

def test_check_audio_devices_ok():
    result = MagicMock(returncode=0, stdout="card 2: USB Audio Device\n")
    with patch("subprocess.run", return_value=result):
        assert st.check_audio_devices() is True


def test_check_audio_devices_no_card():
    result = MagicMock(returncode=0, stdout="no sound device found\n")
    with patch("subprocess.run", return_value=result):
        assert st.check_audio_devices() is False


def test_check_audio_devices_aplay_fails():
    result = MagicMock(returncode=1, stdout="")
    with patch("subprocess.run", return_value=result):
        assert st.check_audio_devices() is False


def test_check_audio_devices_aplay_not_installed():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert st.check_audio_devices() is False


def test_check_audio_devices_timeout():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="aplay", timeout=5)):
        assert st.check_audio_devices() is False


# ── check_usb_writable ────────────────────────────────────────────────────────

def test_check_usb_no_media_dir(monkeypatch):
    monkeypatch.setattr("src.usb._MEDIA_BASE", "/nonexistent_path_xyz")
    # Should return True (non-critical)
    assert st.check_usb_writable() is True


def test_check_usb_writable_ok(tmp_path, monkeypatch):
    import getpass
    usb = tmp_path / getpass.getuser() / "MYKEY"
    usb.mkdir(parents=True)
    with patch.object(Path, "is_mount", return_value=True):
        assert st.check_usb_writable() is True


# ── run() ─────────────────────────────────────────────────────────────────────

def test_run_returns_false_on_critical_failure(patch_base):
    # No config, no beep — both critical checks fail
    with patch("src.selftest.check_audio_devices", return_value=True), \
         patch("src.selftest._play_error"):
        result = st.run()
    assert result is False


def test_run_returns_true_when_all_ok(patch_base):
    (patch_base / "assets" / "beep.wav").write_bytes(b"\x00")
    cfg = {"hook_pin": 17, "poll_interval_sec": 0.05, "pre_beep_delay_sec": 2.0,
           "max_duration_sec": 180, "audio": {"sample_rate": 44100, "channels": 1}}
    (patch_base / "config" / "config.default.json").write_text(json.dumps(cfg))
    with patch("src.selftest.check_audio_devices", return_value=True), \
         patch("src.selftest.check_usb_writable", return_value=True):
        assert st.run() is True
