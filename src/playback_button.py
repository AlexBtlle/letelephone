import logging
from typing import Callable, Protocol

from gpiozero import Button

log = logging.getLogger(__name__)


class _PlaybackButtonProtocol(Protocol):
    def close(self) -> None: ...


class _NoOpPlaybackButton:
    def close(self) -> None:
        pass


class PlaybackButton:
    def __init__(
        self,
        gpio_pin: int,
        on_press: Callable[[], None] | None = None,
    ) -> None:
        def _pressed() -> None:
            log.info("Bouton lecture pressé.")
            if on_press:
                try:
                    on_press()
                except Exception as exc:
                    log.error("Erreur callback lecture : %s", exc)

        self._button = Button(pin=gpio_pin, pull_up=True)
        self._button.when_pressed = _pressed

    def close(self) -> None:
        try:
            self._button.close()
        except Exception:
            pass


def build(
    cfg: dict,
    on_press: Callable[[], None] | None = None,
) -> _PlaybackButtonProtocol:
    btn_cfg = cfg.get("playback_button", {})
    if not btn_cfg.get("enabled", False):
        return _NoOpPlaybackButton()
    try:
        return PlaybackButton(
            gpio_pin=btn_cfg["pin"],
            on_press=on_press,
        )
    except ImportError:
        log.info("gpiozero non disponible — bouton lecture désactivé")
    except Exception as exc:
        log.warning("Bouton lecture non disponible : %s", exc)
    return _NoOpPlaybackButton()
