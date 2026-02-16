"""Generic state manager."""

from collections.abc import Callable
from typing import Generic, TypeVar

from gamify.errors import StateError
from gamify.state.base import BaseGameState

T = TypeVar("T", bound=BaseGameState)


class StateManager(Generic[T]):
    """Manages game state with explicit mutation tracking.

    Generic over the user's BaseGameState subclass for type safety.

        manager = StateManager(MyState())
        manager.update(lambda s: setattr(s, 'score', s.score + 1))
    """

    def __init__(self, initial_state: T) -> None:
        if not isinstance(initial_state, BaseGameState):
            raise StateError(
                f"State must be a BaseGameState subclass, got {type(initial_state).__name__}"
            )
        self._state = initial_state
        self._dirty = False

    @property
    def state(self) -> T:
        return self._state

    @property
    def dirty(self) -> bool:
        return self._dirty

    def update(self, mutator: Callable[[T], None]) -> None:
        """Apply a mutation to the state.

        The mutator receives the state and should modify it in place.
        """
        try:
            mutator(self._state)
            self._dirty = True
        except Exception as e:
            raise StateError(f"State mutation failed: {e}") from e

    def mark_clean(self) -> None:
        """Reset the dirty flag after rendering."""
        self._dirty = False
