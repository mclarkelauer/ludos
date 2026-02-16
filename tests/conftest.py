"""Shared test fixtures for gamify tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_surface():
    """Create a mock pygame surface."""
    surface = MagicMock()
    surface.get_size.return_value = (800, 600)
    surface.get_width.return_value = 800
    surface.get_height.return_value = 600
    return surface


@pytest.fixture
def mock_pygame(monkeypatch):
    """Mock pygame module to avoid needing a display."""
    mock_pg = MagicMock()
    mock_pg.display.set_mode.return_value = MagicMock()
    mock_pg.display.get_surface.return_value = MagicMock()
    mock_pg.time.Clock.return_value = MagicMock()
    mock_pg.QUIT = 256
    mock_pg.KEYDOWN = 768
    mock_pg.KEYUP = 769
    mock_pg.MOUSEBUTTONDOWN = 1025
    mock_pg.MOUSEBUTTONUP = 1026
    mock_pg.MOUSEMOTION = 1024
    mock_pg.K_UP = 273
    mock_pg.K_DOWN = 274
    mock_pg.K_LEFT = 276
    mock_pg.K_RIGHT = 275
    mock_pg.K_RETURN = 13
    mock_pg.K_ESCAPE = 27
    mock_pg.K_SPACE = 32
    return mock_pg
