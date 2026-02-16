"""Base game state dataclass."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaseGameState:
    """Base state that all game states should extend.

    Users subclass this and add their own fields:

        @dataclass
        class MyState(BaseGameState):
            score: int = 0
            player_x: float = 100.0
    """

    is_running: bool = True
    frame_count: int = 0
    elapsed_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
