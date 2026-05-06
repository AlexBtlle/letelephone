import getpass
import logging
import os
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

_MEDIA_BASE = "/media"


class UsbStorage:
    def __init__(self) -> None:
        self._mount_point: Path | None = _find_mount_point()
        if self._mount_point:
            log.info("Clé USB détectée : %s", self._mount_point)
        else:
            log.warning("Aucune clé USB montée sous %s/%s/", _MEDIA_BASE, getpass.getuser())

    def is_available(self) -> bool:
        return self._mount_point is not None and self._mount_point.is_mount()

    def recordings_dir(self) -> Path:
        assert self._mount_point is not None
        d = self._mount_point / "enregistrements"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def log_dir(self) -> Path:
        assert self._mount_point is not None
        d = self._mount_point / "logs"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def eject(self) -> None:
        if not self.is_available():
            return
        try:
            subprocess.run(["umount", str(self._mount_point)], check=True, timeout=10)
            log.info("Clé USB éjectée : %s", self._mount_point)
        except subprocess.CalledProcessError as exc:
            log.error("Échec éjection USB : %s", exc)
        except subprocess.TimeoutExpired:
            log.error("Timeout éjection USB")


def _find_mount_point() -> Path | None:
    user = getpass.getuser()
    base = Path(_MEDIA_BASE) / user
    if not base.is_dir():
        return None
    for entry in base.iterdir():
        if entry.is_mount():
            return entry
    return None
