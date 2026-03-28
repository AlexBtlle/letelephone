from gpiozero import DigitalInputDevice


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