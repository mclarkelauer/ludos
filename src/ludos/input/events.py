"""Input event types."""

from dataclasses import dataclass
from enum import Enum, auto


class InputType(Enum):
    """Categories of input events."""

    KEY_DOWN = auto()
    KEY_UP = auto()
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()
    MOUSE_MOTION = auto()
    QUIT = auto()


@dataclass(frozen=True)
class InputEvent:
    """Unified input event with optional semantic action.

    Attributes:
        type: The kind of input event.
        key: Pygame key constant (for keyboard events).
        button: Mouse button number (for mouse events).
        pos: Mouse position tuple (for mouse events).
        action: Semantic action string resolved from KeyBindings (e.g. "move_up").
    """

    type: InputType
    key: int | None = None
    button: int | None = None
    pos: tuple[int, int] | None = None
    action: str | None = None
