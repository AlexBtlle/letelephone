import os
import json
import logging
import subprocess
import pytest
import utils

def test_find_mount_point_no_base(monkeypatch, caplog):
    # Base /media/<user> does not exist
    caplog.set_level(logging.ERROR)
    monkeypatch.setattr(utils.os.path, 'isdir', lambda p: False)
    result = utils.find_mount_point()
    assert result is None
    assert "introuvable" in caplog.text


def test_find_mount_point_empty(monkeypatch, caplog):
    # Base exists but no mount point under it
    caplog.set_level(logging.ERROR)
    monkeypatch.setattr(utils.os.path, 'isdir', lambda p: True)
    monkeypatch.setattr(utils.os, 'listdir', lambda p: ['foo', 'bar'])
    monkeypatch.setattr(utils.os.path, 'ismount', lambda p: False)
    monkeypatch.setattr(utils.getpass, 'getuser', lambda: 'user1')
    result = utils.find_mount_point()
    assert result is None
    assert "Aucun périphérique USB monté" in caplog.text


def test_find_mount_point_success(monkeypatch):
    # Base exists and one mount
    monkeypatch.setattr(utils.os.path, 'isdir', lambda p: True)
    monkeypatch.setattr(utils.os, 'listdir', lambda p: ['USBKEY', 'other'])
    def fake_ismount(path):
        return path.endswith('USBKEY')
    monkeypatch.setattr(utils.os.path, 'ismount', fake_ismount)
    monkeypatch.setattr(utils.getpass, 'getuser', lambda: 'user1')
    result = utils.find_mount_point()
    assert result == '/media/user1/USBKEY'


def test_ensure_usb_available(monkeypatch):
    # When mount point found
    monkeypatch.setattr(utils, 'find_mount_point', lambda: '/media/user1/USBKEY')
    result = utils.ensure_usb_available()
    assert result == '/media/user1/USBKEY'
    # When not found
    monkeypatch.setattr(utils, 'find_mount_point', lambda: None)
    result = utils.ensure_usb_available()
    assert result is None


def test_load_config_success(tmp_path):
    # Create a valid config.json
    cfg = {'key': 'value'}
    path = tmp_path / 'config.json'
    path.write_text(json.dumps(cfg))
    result = utils.load_config(str(tmp_path))
    assert result == cfg


def test_load_config_error(tmp_path, caplog):
    # Missing config.json
    caplog.set_level(logging.ERROR)
    result = utils.load_config(str(tmp_path))
    assert result == {}
    assert "Erreur chargement config" in caplog.text


def test_unmount_usb_success(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    # subprocess.check_call does not raise
    monkeypatch.setattr(utils.subprocess, 'check_call', lambda args: 0)
    result = utils.unmount_usb('/media/user1/USBKEY')
    assert result is True
    assert "démontée" in caplog.text


def test_unmount_usb_fail(monkeypatch, caplog):
    caplog.set_level(logging.ERROR)
    # simulate failure
    def fake_call(args):
        raise subprocess.CalledProcessError(1, args)
    monkeypatch.setattr(utils.subprocess, 'check_call', fake_call)
    result = utils.unmount_usb('/media/user1/USBKEY')
    assert result is False
    assert "Erreur démontage USB" in caplog.text
