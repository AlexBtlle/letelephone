"""OLED display driver (SSD1306 128×64 via I2C).

Optional — if luma.oled is not installed or the display is not connected,
all methods silently no-op so the rest of the system is unaffected.

Layout (128×64 px):
  ┌────────────────────────┐
  │ Alice & Bob            │  couple name  (y=4,  small)
  │                        │
  │ EN ATTENTE             │  status       (y=22, medium)
  │  ● ENREGISTREMENT      │
  │                        │
  │ Messages : 3           │  counter      (y=50, small)
  └────────────────────────┘
"""

import logging
from typing import Protocol

log = logging.getLogger(__name__)

try:
    from luma.core.interface.serial import i2c as _i2c
    from luma.oled.device import ssd1306 as _ssd1306
    from luma.core.render import canvas
except ImportError:
    _i2c = None       # type: ignore[assignment]
    _ssd1306 = None   # type: ignore[assignment]
    canvas = None     # type: ignore[assignment]


class _DisplayProtocol(Protocol):
    def show_idle(self, couple_name: str, message_count: int) -> None: ...
    def show_recording(self, couple_name: str, message_count: int) -> None: ...
    def clear(self) -> None: ...


class _NoOpDisplay:
    """Used when luma.oled is unavailable or the display is not found."""
    def show_idle(self, couple_name: str, message_count: int) -> None: pass
    def show_recording(self, couple_name: str, message_count: int) -> None: pass
    def clear(self) -> None: pass


class OledDisplay:
    def __init__(self, i2c_port: int = 1, i2c_address: int = 0x3C) -> None:
        if _i2c is None:
            raise ImportError("luma.oled n'est pas installé")
        serial = _i2c(port=i2c_port, address=i2c_address)
        self._device = _ssd1306(serial)
        log.info("Afficheur OLED initialisé (I2C 0x%02X)", i2c_address)

    def show_idle(self, couple_name: str, message_count: int) -> None:
        self._draw(couple_name, "EN ATTENTE", message_count)

    def show_recording(self, couple_name: str, message_count: int) -> None:
        self._draw(couple_name, "* ENREGISTREMENT", message_count)

    def clear(self) -> None:
        self._device.clear()

    def _draw(self, couple_name: str, status: str, message_count: int) -> None:
        with canvas(self._device) as draw:
            if couple_name:
                draw.text((2, 4), couple_name[:20], fill="white")
            draw.text((2, 22), status, fill="white")
            draw.text((2, 50), f"Messages : {message_count}", fill="white")


def build(i2c_port: int = 1, i2c_address: int = 0x3C) -> _DisplayProtocol:
    """Return a real OledDisplay, or a no-op fallback on any error."""
    try:
        return OledDisplay(i2c_port=i2c_port, i2c_address=i2c_address)
    except ImportError:
        log.info("luma.oled non installé — afficheur désactivé")
    except Exception as exc:
        log.warning("Afficheur OLED non disponible : %s", exc)
    return _NoOpDisplay()
