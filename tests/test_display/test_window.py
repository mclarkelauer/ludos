"""Tests for Window."""

from unittest.mock import MagicMock, patch

import pygame
import pytest

from gamify.display.window import Window
from gamify.errors import InitializationError, RenderError


class TestWindow:
    @patch("gamify.display.window.pygame.display")
    def test_creates_display(self, mock_display):
        mock_surface = MagicMock()
        mock_display.set_mode.return_value = mock_surface

        window = Window(1024, 768, "Test Game")
        mock_display.set_mode.assert_called_once_with((1024, 768), 0)
        mock_display.set_caption.assert_called_once_with("Test Game")
        assert window.surface is mock_surface
        assert window.width == 1024
        assert window.height == 768
        assert window.title == "Test Game"

    @patch("gamify.display.window.pygame.display")
    def test_default_values(self, mock_display):
        mock_display.set_mode.return_value = MagicMock()
        window = Window()
        assert window.width == 800
        assert window.height == 600
        assert window.title == "Gamify"

    @patch("gamify.display.window.pygame.display")
    def test_clear_fills_surface(self, mock_display):
        mock_surface = MagicMock()
        mock_display.set_mode.return_value = mock_surface
        window = Window()
        window.clear((255, 0, 0))
        mock_surface.fill.assert_called_once_with((255, 0, 0))

    @patch("gamify.display.window.pygame.display")
    def test_clear_default_black(self, mock_display):
        mock_surface = MagicMock()
        mock_display.set_mode.return_value = mock_surface
        window = Window()
        window.clear()
        mock_surface.fill.assert_called_once_with((0, 0, 0))

    @patch("gamify.display.window.pygame.display")
    def test_flip_calls_display_flip(self, mock_display):
        mock_display.set_mode.return_value = MagicMock()
        window = Window()
        window.flip()
        mock_display.flip.assert_called_once()

    @patch("gamify.display.window.pygame.display")
    def test_init_error_wraps(self, mock_display):
        mock_display.set_mode.side_effect = pygame.error("no display")
        with pytest.raises(InitializationError, match="Failed to create window"):
            Window()

    @patch("gamify.display.window.pygame.display")
    def test_flip_error_wraps(self, mock_display):
        mock_display.set_mode.return_value = MagicMock()
        window = Window()
        mock_display.flip.side_effect = pygame.error("flip failed")
        with pytest.raises(RenderError, match="Display flip failed"):
            window.flip()
