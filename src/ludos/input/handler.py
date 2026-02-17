"""Input handler that polls pygame events and converts them."""

from collections.abc import Callable

import pygame

from ludos.input.bindings import KeyBindings
from ludos.input.events import InputEvent, InputType


class InputHandler:
    """Polls pygame events, converts to InputEvents, and dispatches callbacks.

    Example:
        handler = InputHandler(bindings)
        handler.on("confirm", lambda event: print("confirmed!"))

        # In game loop:
        for event in handler.poll():
            scene.handle_input(event)
    """

    _PG_TYPE_MAP = {
        pygame.QUIT: InputType.QUIT,
        pygame.KEYDOWN: InputType.KEY_DOWN,
        pygame.KEYUP: InputType.KEY_UP,
        pygame.MOUSEBUTTONDOWN: InputType.MOUSE_DOWN,
        pygame.MOUSEBUTTONUP: InputType.MOUSE_UP,
        pygame.MOUSEMOTION: InputType.MOUSE_MOTION,
    }

    def __init__(self, bindings: KeyBindings | None = None) -> None:
        self._bindings = bindings or KeyBindings.defaults()
        self._callbacks: dict[str, list[Callable[[InputEvent], None]]] = {}

    @property
    def bindings(self) -> KeyBindings:
        return self._bindings

    def on(self, action: str, callback: Callable[[InputEvent], None]) -> None:
        """Register a callback for a semantic action."""
        self._callbacks.setdefault(action, []).append(callback)

    def off(self, action: str, callback: Callable[[InputEvent], None]) -> None:
        """Unregister a callback for a semantic action."""
        if action in self._callbacks:
            try:
                self._callbacks[action].remove(callback)
            except ValueError:
                pass

    def poll(self) -> list[InputEvent]:
        """Poll all pending pygame events and return as InputEvents."""
        events: list[InputEvent] = []
        for pg_event in pygame.event.get():
            converted = self._convert(pg_event)
            if converted is not None:
                events.append(converted)
                if converted.action:
                    self._dispatch(converted)
        return events

    def _convert(self, pg_event: pygame.event.Event) -> InputEvent | None:
        """Convert a pygame event to an InputEvent."""
        input_type = self._PG_TYPE_MAP.get(pg_event.type)
        if input_type is None:
            return None

        key = getattr(pg_event, "key", None)
        button = getattr(pg_event, "button", None)
        pos = getattr(pg_event, "pos", None)

        action = None
        if key is not None and input_type == InputType.KEY_DOWN:
            action = self._bindings.get_key_action(key)
        elif button is not None and input_type == InputType.MOUSE_DOWN:
            action = self._bindings.get_mouse_action(button)

        return InputEvent(type=input_type, key=key, button=button, pos=pos, action=action)

    def _dispatch(self, event: InputEvent) -> None:
        """Call registered callbacks for this event's action."""
        if event.action and event.action in self._callbacks:
            for cb in self._callbacks[event.action]:
                cb(event)
