"""Tests for InputHandler."""

from unittest.mock import MagicMock, patch

import pygame

from gamify.input.bindings import KeyBindings
from gamify.input.events import InputType
from gamify.input.handler import InputHandler


def _make_pg_event(event_type, **attrs):
    """Create a mock pygame event."""
    event = MagicMock()
    event.type = event_type
    for attr in ("key", "button", "pos"):
        setattr(event, attr, attrs.get(attr))
    return event


class TestInputHandler:
    def test_creates_default_bindings(self):
        handler = InputHandler()
        assert handler.bindings is not None

    def test_accepts_custom_bindings(self):
        bindings = KeyBindings()
        handler = InputHandler(bindings)
        assert handler.bindings is bindings

    @patch("gamify.input.handler.pygame.event.get")
    def test_poll_converts_key_down(self, mock_get):
        mock_get.return_value = [_make_pg_event(pygame.KEYDOWN, key=pygame.K_UP)]
        handler = InputHandler(KeyBindings.defaults())
        events = handler.poll()
        assert len(events) == 1
        assert events[0].type == InputType.KEY_DOWN
        assert events[0].key == pygame.K_UP
        assert events[0].action == "move_up"

    @patch("gamify.input.handler.pygame.event.get")
    def test_poll_converts_quit(self, mock_get):
        mock_get.return_value = [_make_pg_event(pygame.QUIT)]
        handler = InputHandler()
        events = handler.poll()
        assert len(events) == 1
        assert events[0].type == InputType.QUIT

    @patch("gamify.input.handler.pygame.event.get")
    def test_poll_converts_mouse_down(self, mock_get):
        mock_get.return_value = [
            _make_pg_event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 200))
        ]
        handler = InputHandler(KeyBindings.defaults())
        events = handler.poll()
        assert len(events) == 1
        assert events[0].type == InputType.MOUSE_DOWN
        assert events[0].button == 1
        assert events[0].pos == (100, 200)
        assert events[0].action == "click"

    @patch("gamify.input.handler.pygame.event.get")
    def test_poll_ignores_unknown_event_types(self, mock_get):
        unknown = MagicMock()
        unknown.type = 99999
        mock_get.return_value = [unknown]
        handler = InputHandler()
        events = handler.poll()
        assert len(events) == 0

    @patch("gamify.input.handler.pygame.event.get")
    def test_callback_dispatched(self, mock_get):
        mock_get.return_value = [_make_pg_event(pygame.KEYDOWN, key=pygame.K_RETURN)]
        handler = InputHandler(KeyBindings.defaults())
        received = []
        handler.on("confirm", lambda e: received.append(e))
        handler.poll()
        assert len(received) == 1
        assert received[0].action == "confirm"

    @patch("gamify.input.handler.pygame.event.get")
    def test_off_removes_callback(self, mock_get):
        mock_get.return_value = [_make_pg_event(pygame.KEYDOWN, key=pygame.K_RETURN)]
        handler = InputHandler(KeyBindings.defaults())
        received = []
        cb = lambda e: received.append(e)
        handler.on("confirm", cb)
        handler.off("confirm", cb)
        handler.poll()
        assert len(received) == 0

    @patch("gamify.input.handler.pygame.event.get")
    def test_unbound_key_has_no_action(self, mock_get):
        mock_get.return_value = [_make_pg_event(pygame.KEYDOWN, key=pygame.K_z)]
        handler = InputHandler(KeyBindings())
        events = handler.poll()
        assert len(events) == 1
        assert events[0].action is None

    @patch("gamify.input.handler.pygame.event.get")
    def test_mouse_motion(self, mock_get):
        mock_get.return_value = [
            _make_pg_event(pygame.MOUSEMOTION, pos=(50, 75))
        ]
        handler = InputHandler()
        events = handler.poll()
        assert len(events) == 1
        assert events[0].type == InputType.MOUSE_MOTION
        assert events[0].pos == (50, 75)
