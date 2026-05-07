import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.usb import UsbStorage, _find_mount_point


def test_is_available_false_when_no_usb(monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: None)
    usb = UsbStorage()
    assert usb.is_available() is False


def test_is_available_true_when_mounted(tmp_path, monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True):
        usb = UsbStorage()
        assert usb.is_available() is True


def test_recordings_dir_created(tmp_path, monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True):
        usb = UsbStorage()
        d = usb.recordings_dir()
        assert d == tmp_path / "enregistrements"
        assert d.exists()


def test_log_dir_created(tmp_path, monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True):
        usb = UsbStorage()
        d = usb.log_dir()
        assert d == tmp_path / "logs"
        assert d.exists()


def test_welcome_file_found(tmp_path, monkeypatch):
    (tmp_path / "welcome.wav").write_bytes(b"\x00")
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True):
        usb = UsbStorage()
        assert usb.welcome_file() == tmp_path / "welcome.wav"


def test_welcome_file_absent(tmp_path, monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True):
        usb = UsbStorage()
        assert usb.welcome_file() is None


def test_welcome_file_no_usb(monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: None)
    usb = UsbStorage()
    assert usb.welcome_file() is None


def test_find_mount_point_returns_none_if_no_media(monkeypatch, tmp_path):
    monkeypatch.setattr("src.usb._MEDIA_BASE", str(tmp_path / "nonexistent"))
    assert _find_mount_point() is None


def test_find_mount_point_returns_none_if_nothing_mounted(monkeypatch, tmp_path):
    import getpass
    fake_base = tmp_path / getpass.getuser()
    fake_base.mkdir(parents=True)
    (fake_base / "MYKEY").mkdir()
    monkeypatch.setattr("src.usb._MEDIA_BASE", str(tmp_path))
    assert _find_mount_point() is None


def test_eject_calls_umount(tmp_path, monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True), patch("subprocess.run") as mock_run:
        usb = UsbStorage()
        usb.eject()
        mock_run.assert_called_once()
        assert "umount" in mock_run.call_args[0][0]


def test_eject_logs_error_on_umount_failure(tmp_path, monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True), \
         patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "umount")):
        usb = UsbStorage()
        usb.eject()  # must not raise


def test_eject_logs_error_on_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: tmp_path)
    with patch.object(Path, "is_mount", return_value=True), \
         patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="umount", timeout=10)):
        usb = UsbStorage()
        usb.eject()  # must not raise


def test_eject_noop_when_no_usb(monkeypatch):
    monkeypatch.setattr("src.usb._find_mount_point", lambda: None)
    usb = UsbStorage()
    usb.eject()  # must not raise
