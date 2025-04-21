import os
import pytest
import logging
import audio

class DummyPopen:
    def __init__(self, poll_return=None):
        self._poll = poll_return
        self.terminated = False
        self.waited = False
    def poll(self):
        return self._poll
    def terminate(self):
        self.terminated = True
    def wait(self):
        self.waited = True


def test_play_announcement_nonexistent(monkeypatch, caplog):
    path = 'nonexistent.mp3'
    # Forcer isfile à False
    monkeypatch.setattr(audio.os.path, 'isfile', lambda p: False)
    caplog.set_level(logging.ERROR)
    audio.play_announcement(path)
    assert 'Annonce non trouvée' in caplog.text


def test_play_announcement_mp3(monkeypatch):
    path = 'file.mp3'
    monkeypatch.setattr(audio.os.path, 'isfile', lambda p: True)
    calls = []
    def fake_run(cmd, check=True):
        calls.append(cmd)
    monkeypatch.setattr(audio.subprocess, 'run', fake_run)
    audio.play_announcement(path)
    assert calls == [['omxplayer', '--no-keys', path]]


def test_play_announcement_wav(monkeypatch):
    path = 'file.wav'
    monkeypatch.setattr(audio.os.path, 'isfile', lambda p: True)
    calls = []
    def fake_run(cmd, check=True):
        calls.append(cmd)
    monkeypatch.setattr(audio.subprocess, 'run', fake_run)
    audio.play_announcement(path)
    assert calls == [['aplay', path]]


def test_start_recording_no_duration(monkeypatch, tmp_path):
    audio.en_rec_process = None
    output = str(tmp_path / 'out.wav')
    popen_args = []
    def fake_popen(cmd):
        popen_args.append(cmd)
        return DummyPopen(poll_return=None)
    monkeypatch.setattr(audio.subprocess, 'Popen', fake_popen)
    audio.start_recording(output, max_duration=None)
    assert popen_args == [['arecord', '-f', 'cd', output]]
    assert isinstance(audio.en_rec_process, DummyPopen)


def test_start_recording_with_duration(monkeypatch, tmp_path):
    audio.en_rec_process = None
    output = str(tmp_path / 'out.wav')
    popen_args = []
    def fake_popen(cmd):
        popen_args.append(cmd)
        return DummyPopen(poll_return=None)
    monkeypatch.setattr(audio.subprocess, 'Popen', fake_popen)
    audio.start_recording(output, max_duration=5)
    # Vérifier la commande incluant '-d' et '5'
    assert popen_args == [['arecord', '-f', '-d', '5', 'cd', output]]
    assert isinstance(audio.en_rec_process, DummyPopen)


def test_start_recording_already(monkeypatch, caplog):
    dummy = DummyPopen(poll_return=None)
    audio.en_rec_process = dummy
    caplog.set_level(logging.WARNING)
    audio.start_recording('out.wav', max_duration=None)
    assert 'Un enregistrement est déjà en cours' in caplog.text
    assert audio.en_rec_process is dummy


def test_stop_recording_none(caplog):
    audio.en_rec_process = None
    caplog.set_level(logging.WARNING)
    audio.stop_recording()
    assert 'Aucun enregistrement en cours à arrêter' in caplog.text


def test_stop_recording_active():
    dummy = DummyPopen(poll_return=None)
    audio.en_rec_process = dummy
    audio.stop_recording()
    assert dummy.terminated is True
    assert dummy.waited is True
    assert audio.en_rec_process is None


def test_stop_recording_inactive():
    dummy = DummyPopen(poll_return=1)
    audio.en_rec_process = dummy
    audio.stop_recording()
    # Si poll != None, terminate n'a pas été appelé
    assert dummy.terminated is False
    assert audio.en_rec_process is None
