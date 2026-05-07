import os


def _configure_pin_factory() -> None:
    # Pi 5 uses the RP1 GPIO controller, which requires the lgpio backend.
    # Set the env var before gpiozero creates any pin factory instance.
    try:
        with open("/proc/cpuinfo") as f:
            if "Raspberry Pi 5" in f.read():
                os.environ.setdefault("GPIOZERO_PIN_FACTORY", "lgpio")
    except OSError:
        pass


_configure_pin_factory()

from gpiozero import DigitalInputDevice  # noqa: E402


class HookSwitch:
    def __init__(self, gpio_pin: int, pull_up: bool = True, bounce_time: float = 0.05):
        self.device = DigitalInputDevice(
            pin=gpio_pin,
            pull_up=pull_up,
            bounce_time=bounce_time,
        )

    def is_off_hook(self) -> bool:
        return self.device.value == 1

    def close(self) -> None:
        self.device.close()
