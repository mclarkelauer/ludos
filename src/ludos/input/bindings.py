"""Key and mouse bindings that map raw inputs to semantic actions."""

import pygame

from ludos.errors import InputError


class KeyBindings:
    """Maps pygame keys/buttons to semantic action strings.

    Example:
        bindings = KeyBindings.defaults()
        bindings.bind_key(pygame.K_w, "move_up")
        action = bindings.get_key_action(pygame.K_w)  # "move_up"
    """

    def __init__(self) -> None:
        self._key_map: dict[int, str] = {}
        self._mouse_map: dict[int, str] = {}

    @classmethod
    def defaults(cls) -> "KeyBindings":
        """Create bindings with sensible defaults."""
        bindings = cls()
        bindings.bind_key(pygame.K_UP, "move_up")
        bindings.bind_key(pygame.K_DOWN, "move_down")
        bindings.bind_key(pygame.K_LEFT, "move_left")
        bindings.bind_key(pygame.K_RIGHT, "move_right")
        bindings.bind_key(pygame.K_RETURN, "confirm")
        bindings.bind_key(pygame.K_ESCAPE, "cancel")
        bindings.bind_key(pygame.K_SPACE, "action")
        bindings.bind_mouse(1, "click")
        bindings.bind_mouse(3, "right_click")
        return bindings

    def bind_key(self, key: int, action: str) -> None:
        """Bind a pygame key constant to a semantic action."""
        if not isinstance(action, str) or not action:
            raise InputError("Action must be a non-empty string")
        self._key_map[key] = action

    def unbind_key(self, key: int) -> None:
        """Remove a key binding."""
        self._key_map.pop(key, None)

    def bind_mouse(self, button: int, action: str) -> None:
        """Bind a mouse button number to a semantic action."""
        if not isinstance(action, str) or not action:
            raise InputError("Action must be a non-empty string")
        self._mouse_map[button] = action

    def unbind_mouse(self, button: int) -> None:
        """Remove a mouse button binding."""
        self._mouse_map.pop(button, None)

    def get_key_action(self, key: int) -> str | None:
        """Look up the action for a key, or None if unbound."""
        return self._key_map.get(key)

    def get_mouse_action(self, button: int) -> str | None:
        """Look up the action for a mouse button, or None if unbound."""
        return self._mouse_map.get(button)
