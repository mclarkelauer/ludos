"""Tests for KeyBindings."""

import pygame
import pytest

from ludos.errors import InputError
from ludos.input.bindings import KeyBindings


class TestKeyBindings:
    def test_empty_bindings(self):
        bindings = KeyBindings()
        assert bindings.get_key_action(pygame.K_UP) is None

    def test_bind_and_get_key(self):
        bindings = KeyBindings()
        bindings.bind_key(pygame.K_w, "move_up")
        assert bindings.get_key_action(pygame.K_w) == "move_up"

    def test_bind_and_get_mouse(self):
        bindings = KeyBindings()
        bindings.bind_mouse(1, "click")
        assert bindings.get_mouse_action(1) == "click"

    def test_unbind_key(self):
        bindings = KeyBindings()
        bindings.bind_key(pygame.K_w, "move_up")
        bindings.unbind_key(pygame.K_w)
        assert bindings.get_key_action(pygame.K_w) is None

    def test_unbind_mouse(self):
        bindings = KeyBindings()
        bindings.bind_mouse(1, "click")
        bindings.unbind_mouse(1)
        assert bindings.get_mouse_action(1) is None

    def test_unbind_nonexistent_key_no_error(self):
        bindings = KeyBindings()
        bindings.unbind_key(pygame.K_z)  # no error

    def test_defaults_has_arrows(self):
        bindings = KeyBindings.defaults()
        assert bindings.get_key_action(pygame.K_UP) == "move_up"
        assert bindings.get_key_action(pygame.K_DOWN) == "move_down"
        assert bindings.get_key_action(pygame.K_LEFT) == "move_left"
        assert bindings.get_key_action(pygame.K_RIGHT) == "move_right"

    def test_defaults_has_confirm_cancel(self):
        bindings = KeyBindings.defaults()
        assert bindings.get_key_action(pygame.K_RETURN) == "confirm"
        assert bindings.get_key_action(pygame.K_ESCAPE) == "cancel"

    def test_defaults_has_mouse(self):
        bindings = KeyBindings.defaults()
        assert bindings.get_mouse_action(1) == "click"
        assert bindings.get_mouse_action(3) == "right_click"

    def test_rebind_overwrites(self):
        bindings = KeyBindings()
        bindings.bind_key(pygame.K_w, "move_up")
        bindings.bind_key(pygame.K_w, "jump")
        assert bindings.get_key_action(pygame.K_w) == "jump"

    def test_bind_key_rejects_empty_action(self):
        bindings = KeyBindings()
        with pytest.raises(InputError):
            bindings.bind_key(pygame.K_w, "")

    def test_bind_mouse_rejects_non_string(self):
        bindings = KeyBindings()
        with pytest.raises(InputError):
            bindings.bind_mouse(1, 42)  # type: ignore
