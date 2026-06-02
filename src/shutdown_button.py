import logging
import subprocess
from typing import Callable, Protocol

from gpiozero import Button

log = logging.getLogger(__name__)


class _ShutdownButtonProtocol(Protocol):
    def close(self) -> None: ...


class _NoOpShutdownButton:
    def close(self) -> None:
        pass


class ShutdownButton:
    def __init__(
        self,
        gpio_pin: int,
        hold_duration: float = 3.0,
        on_shutdown: Callable[[], None] | None = None,
    ) -> None:
        def _held() -> None:
            log.info("Bouton d'arrêt maintenu — extinction en cours…")
            if on_shutdown:
                try:
                    on_shutdown()
                except Exception as exc:
                    log.error("Erreur callback arrêt : %s", exc)
            subprocess.run(["shutdown", "-h", "now"], check=False)

        self._button = Button(pin=gpio_pin, hold_time=hold_duration, pull_up=True)
        self._button.when_held = _held

    def close(self) -> None:
        try:
            self._button.close()
        except Exception:
            pass


def build(
    cfg: dict,
    on_shutdown: Callable[[], None] | None = None,
) -> _ShutdownButtonProtocol:
    btn_cfg = cfg.get("shutdown_button", {})
    if not btn_cfg.get("enabled", False):
        return _NoOpShutdownButton()
    try:
        return ShutdownButton(
            gpio_pin=btn_cfg["pin"],
            hold_duration=btn_cfg.get("hold_duration_sec", 3.0),
            on_shutdown=on_shutdown,
        )
    except ImportError:
        log.info("gpiozero non disponible — bouton d'arrêt désactivé")
    except Exception as exc:
        log.warning("Bouton d'arrêt non disponible : %s", exc)
    return _NoOpShutdownButton()
