"""Tests for the display module."""
from unittest.mock import MagicMock, patch

import pytest

from src.display import OledDisplay, _NoOpDisplay, build


# ── _NoOpDisplay ──────────────────────────────────────────────────────────────

def test_noop_display_does_not_raise():
    d = _NoOpDisplay()
    d.show_idle("Alice & Bob", 0)
    d.show_recording("Alice & Bob", 3)
    d.clear()


# ── build() fallback ─────────────────────────────────────────────────────────

def test_build_returns_noop_when_luma_not_installed():
    with patch("src.display.OledDisplay.__init__", side_effect=ImportError("luma.oled not found")):
        d = build()
    assert isinstance(d, _NoOpDisplay)


def test_build_returns_noop_when_display_not_connected():
    with patch("src.display.OledDisplay.__init__", side_effect=Exception("No device found")):
        d = build()
    assert isinstance(d, _NoOpDisplay)


def test_build_returns_oled_when_available():
    with patch("src.display.OledDisplay.__init__", return_value=None) as mock_init:
        d = build(i2c_port=1, i2c_address=0x3C)
    assert isinstance(d, OledDisplay)
    mock_init.assert_called_once_with(i2c_port=1, i2c_address=0x3C)


# ── OledDisplay rendering ─────────────────────────────────────────────────────

@pytest.fixture
def oled():
    """OledDisplay with mocked luma.oled device."""
    mock_device = MagicMock()
    with patch("src.display.OledDisplay.__init__", return_value=None):
        d = OledDisplay.__new__(OledDisplay)
        d._device = mock_device
    return d, mock_device


def test_show_idle_calls_canvas(oled):
    d, mock_device = oled
    mock_ctx = MagicMock()
    mock_device.__class__ = MagicMock
    with patch("src.display.canvas") as mock_canvas:
        mock_canvas.return_value.__enter__ = lambda s: mock_ctx
        mock_canvas.return_value.__exit__ = MagicMock(return_value=False)
        d.show_idle("Alice & Bob", 2)
    mock_canvas.assert_called_once_with(d._device)


def test_show_recording_calls_canvas(oled):
    d, mock_device = oled
    with patch("src.display.canvas") as mock_canvas:
        mock_canvas.return_value.__enter__ = lambda s: MagicMock()
        mock_canvas.return_value.__exit__ = MagicMock(return_value=False)
        d.show_recording("Alice & Bob", 5)
    mock_canvas.assert_called_once_with(d._device)


def test_clear_calls_device_clear(oled):
    d, mock_device = oled
    d.clear()
    mock_device.clear.assert_called_once()


def test_show_idle_draws_couple_name_and_status(oled):
    d, _ = oled
    drawn = []
    mock_draw = MagicMock()
    mock_draw.text.side_effect = lambda pos, text, **kw: drawn.append(text)
    with patch("src.display.canvas") as mock_canvas:
        mock_canvas.return_value.__enter__ = lambda s: mock_draw
        mock_canvas.return_value.__exit__ = MagicMock(return_value=False)
        d.show_idle("Alice & Bob", 7)
    assert any("Alice" in t for t in drawn)
    assert any("ATTENTE" in t for t in drawn)
    assert any("7" in t for t in drawn)


def test_show_recording_draws_enregistrement(oled):
    d, _ = oled
    drawn = []
    mock_draw = MagicMock()
    mock_draw.text.side_effect = lambda pos, text, **kw: drawn.append(text)
    with patch("src.display.canvas") as mock_canvas:
        mock_canvas.return_value.__enter__ = lambda s: mock_draw
        mock_canvas.return_value.__exit__ = MagicMock(return_value=False)
        d.show_recording("Alice & Bob", 7)
    assert any("ENREGISTREMENT" in t for t in drawn)


def test_show_idle_empty_couple_name(oled):
    """Empty couple name must not draw anything for that field."""
    d, _ = oled
    drawn_calls = []
    mock_draw = MagicMock()
    mock_draw.text.side_effect = lambda pos, text, **kw: drawn_calls.append((pos, text))
    with patch("src.display.canvas") as mock_canvas:
        mock_canvas.return_value.__enter__ = lambda s: mock_draw
        mock_canvas.return_value.__exit__ = MagicMock(return_value=False)
        d.show_idle("", 0)
    # couple_name line must not have been drawn (condition: if couple_name)
    assert all(text for _, text in drawn_calls)  # all drawn texts are non-empty
