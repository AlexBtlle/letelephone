import pytest
import detection

def test_setup_hook(monkeypatch):
    # Patch GPIO methods
    class DummyGPIO:
        BCM = 'BCM'
        IN = 'IN'
        PUD_DOWN = 'PUD_DOWN'
        def __init__(self):
            self.mode_set = False
            self.setup_called = False
        def setmode(self, mode):
            self.mode_set = True
        def setup(self, pin, mode, pull_up_down=None):
            self.setup_called = True
            self.pin = pin
            self.mode = mode
            self.pull = pull_up_down
    dummy = DummyGPIO()
    monkeypatch.setattr(detection, 'GPIO', dummy)
    detection.setup_hook(5)
    assert detection.HOOK_PIN == 5
    assert dummy.mode_set is True
    assert dummy.setup_called is True
    assert dummy.pin == 5


def test_is_hooked_without_setup():
    # Calling is_hooked before setup should raise
    detection.HOOK_PIN = None
    with pytest.raises(RuntimeError):
        detection.is_hooked()


def test_is_hooked_debounce(monkeypatch):
    # Patch GPIO and time.sleep
    class DummyGPIO:
        def __init__(self, inputs):
            self.inputs = inputs
        def input(self, pin):
            return self.inputs.pop(0)
    dummy_gpio = DummyGPIO([1, 1])
    monkeypatch.setattr(detection, 'GPIO', dummy_gpio)
    monkeypatch.setattr(detection, 'time', type('t', (), {'sleep': lambda x: None}))
    # Setup hook
    detection.HOOK_PIN = 3
    # Should return True when both reads are 1
    assert detection.is_hooked() is True


def test_is_hooked_debounce_false_initial(monkeypatch):
    class DummyGPIO:
        def __init__(self, inputs):
            self.inputs = inputs
        def input(self, pin):
            return self.inputs.pop(0)
    dummy_gpio = DummyGPIO([0, 1])
    monkeypatch.setattr(detection, 'GPIO', dummy_gpio)
    monkeypatch.setattr(detection, 'time', type('t', (), {'sleep': lambda x: None}))
    detection.HOOK_PIN = 4
    # Should return False when first read is 0
    assert detection.is_hooked() is False


def test_is_hooked_debounce_false_second(monkeypatch):
    class DummyGPIO:
        def __init__(self, inputs):
            self.inputs = inputs
        def input(self, pin):
            return self.inputs.pop(0)
    dummy_gpio = DummyGPIO([1, 0])
    monkeypatch.setattr(detection, 'GPIO', dummy_gpio)
    monkeypatch.setattr(detection, 'time', type('t', (), {'sleep': lambda x: None}))
    detection.HOOK_PIN = 6
    # Should return False when second read is 0
    assert detection.is_hooked() is False


def test_cleanup_hook(monkeypatch):
    # Patch GPIO.cleanup to capture call
    class DummyGPIO:
        def __init__(self):
            self.cleaned = False
            self.cleaned_pin = None
        def cleanup(self, pin=None):
            self.cleaned = True
            self.cleaned_pin = pin
    dummy = DummyGPIO()
    monkeypatch.setattr(detection, 'GPIO', dummy)
    detection.HOOK_PIN = 7
    detection.cleanup_hook()
    assert dummy.cleaned is True
    assert dummy.cleaned_pin == 7
