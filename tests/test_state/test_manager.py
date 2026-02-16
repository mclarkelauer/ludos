"""Tests for StateManager."""

from dataclasses import dataclass

import pytest

from ludos.errors import StateError
from ludos.state.base import BaseGameState
from ludos.state.manager import StateManager


@dataclass
class SampleState(BaseGameState):
    score: int = 0
    player_x: float = 100.0


class SampleStateManager:
    def test_initial_state(self):
        state = SampleState()
        manager = StateManager(state)
        assert manager.state is state
        assert manager.dirty is False

    def test_update_mutates_state(self):
        manager = StateManager(SampleState())
        manager.update(lambda s: setattr(s, "score", s.score + 10))
        assert manager.state.score == 10

    def test_update_sets_dirty(self):
        manager = StateManager(SampleState())
        manager.update(lambda s: setattr(s, "score", 1))
        assert manager.dirty is True

    def test_mark_clean(self):
        manager = StateManager(SampleState())
        manager.update(lambda s: setattr(s, "score", 1))
        manager.mark_clean()
        assert manager.dirty is False

    def test_multiple_updates(self):
        manager = StateManager(SampleState())
        manager.update(lambda s: setattr(s, "score", s.score + 5))
        manager.update(lambda s: setattr(s, "score", s.score + 3))
        assert manager.state.score == 8

    def test_update_base_fields(self):
        manager = StateManager(SampleState())
        manager.update(lambda s: setattr(s, "frame_count", s.frame_count + 1))
        assert manager.state.frame_count == 1

    def test_rejects_non_base_state(self):
        with pytest.raises(StateError, match="BaseGameState subclass"):
            StateManager("not a state")  # type: ignore

    def test_mutation_error_wraps_in_state_error(self):
        manager = StateManager(SampleState())
        with pytest.raises(StateError, match="State mutation failed"):
            manager.update(lambda s: (_ for _ in ()).throw(ValueError("boom")))
