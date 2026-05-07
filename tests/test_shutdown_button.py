from unittest.mock import MagicMock, patch

from src.shutdown_button import ShutdownButton, _NoOpShutdownButton, build


def test_noop_shutdown_button_close():
    btn = _NoOpShutdownButton()
    btn.close()


def test_build_returns_noop_when_disabled():
    btn = build({"shutdown_button": {"enabled": False}})
    assert isinstance(btn, _NoOpShutdownButton)


def test_build_returns_noop_when_no_config():
    btn = build({})
    assert isinstance(btn, _NoOpShutdownButton)


def test_build_returns_noop_on_gpio_error():
    with patch("src.shutdown_button.Button", side_effect=Exception("GPIO busy")):
        btn = build({"shutdown_button": {"enabled": True, "pin": 27}})
    assert isinstance(btn, _NoOpShutdownButton)


def test_shutdown_button_held_calls_callback_and_shutdown():
    callback = MagicMock()
    mock_button_instance = MagicMock()

    with patch("src.shutdown_button.Button", return_value=mock_button_instance):
        btn = ShutdownButton(gpio_pin=27, hold_duration=3.0, on_shutdown=callback)

    # Retrieve and invoke the when_held callback directly
    held_fn = mock_button_instance.when_held
    with patch("src.shutdown_button.subprocess.run") as mock_run:
        held_fn()
    callback.assert_called_once()
    mock_run.assert_called_once_with(["shutdown", "-h", "now"], check=False)


def test_shutdown_button_held_no_callback():
    mock_button_instance = MagicMock()
    with patch("src.shutdown_button.Button", return_value=mock_button_instance):
        btn = ShutdownButton(gpio_pin=27, hold_duration=3.0, on_shutdown=None)

    held_fn = mock_button_instance.when_held
    with patch("src.shutdown_button.subprocess.run"):
        held_fn()  # should not raise


def test_shutdown_button_callback_exception_does_not_prevent_shutdown():
    callback = MagicMock(side_effect=RuntimeError("boom"))
    mock_button_instance = MagicMock()

    with patch("src.shutdown_button.Button", return_value=mock_button_instance):
        btn = ShutdownButton(gpio_pin=27, on_shutdown=callback)

    held_fn = mock_button_instance.when_held
    with patch("src.shutdown_button.subprocess.run") as mock_run:
        held_fn()
    mock_run.assert_called_once()


def test_shutdown_button_close():
    mock_button_instance = MagicMock()
    with patch("src.shutdown_button.Button", return_value=mock_button_instance):
        btn = ShutdownButton(gpio_pin=27)
    btn.close()
    mock_button_instance.close.assert_called_once()


def test_build_creates_shutdown_button_with_correct_params():
    mock_button_instance = MagicMock()
    with patch("src.shutdown_button.Button", return_value=mock_button_instance) as mock_cls:
        btn = build({"shutdown_button": {"enabled": True, "pin": 27, "hold_duration_sec": 5.0}})
    assert isinstance(btn, ShutdownButton)
    mock_cls.assert_called_once_with(pin=27, hold_time=5.0, pull_up=True)
