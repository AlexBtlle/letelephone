from unittest.mock import MagicMock, patch

from src.playback_button import PlaybackButton, _NoOpPlaybackButton, build


def test_noop_playback_button_close():
    btn = _NoOpPlaybackButton()
    btn.close()


def test_build_returns_noop_when_disabled():
    btn = build({"playback_button": {"enabled": False}})
    assert isinstance(btn, _NoOpPlaybackButton)


def test_build_returns_noop_when_no_config():
    btn = build({})
    assert isinstance(btn, _NoOpPlaybackButton)


def test_build_returns_noop_on_gpio_error():
    with patch("src.playback_button.Button", side_effect=Exception("GPIO busy")):
        btn = build({"playback_button": {"enabled": True, "pin": 25}})
    assert isinstance(btn, _NoOpPlaybackButton)


def test_playback_button_pressed_calls_callback():
    callback = MagicMock()
    mock_button_instance = MagicMock()

    with patch("src.playback_button.Button", return_value=mock_button_instance):
        btn = PlaybackButton(gpio_pin=25, on_press=callback)

    pressed_fn = mock_button_instance.when_pressed
    pressed_fn()
    callback.assert_called_once()


def test_playback_button_pressed_no_callback():
    mock_button_instance = MagicMock()
    with patch("src.playback_button.Button", return_value=mock_button_instance):
        btn = PlaybackButton(gpio_pin=25, on_press=None)

    pressed_fn = mock_button_instance.when_pressed
    pressed_fn()  # must not raise


def test_playback_button_callback_exception_does_not_propagate():
    callback = MagicMock(side_effect=RuntimeError("boom"))
    mock_button_instance = MagicMock()

    with patch("src.playback_button.Button", return_value=mock_button_instance):
        btn = PlaybackButton(gpio_pin=25, on_press=callback)

    pressed_fn = mock_button_instance.when_pressed
    pressed_fn()  # must not raise
    callback.assert_called_once()


def test_playback_button_close():
    mock_button_instance = MagicMock()
    with patch("src.playback_button.Button", return_value=mock_button_instance):
        btn = PlaybackButton(gpio_pin=25)
    btn.close()
    mock_button_instance.close.assert_called_once()


def test_build_creates_playback_button_with_correct_params():
    mock_button_instance = MagicMock()
    with patch("src.playback_button.Button", return_value=mock_button_instance) as mock_cls:
        btn = build({"playback_button": {"enabled": True, "pin": 25}})
    assert isinstance(btn, PlaybackButton)
    mock_cls.assert_called_once_with(pin=25, pull_up=True)
