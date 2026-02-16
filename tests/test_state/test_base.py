"""Tests for BaseGameState."""

from dataclasses import dataclass

from ludos.state.base import BaseGameState


class TestBaseGameState:
    def test_default_values(self):
        state = BaseGameState()
        assert state.is_running is True
        assert state.frame_count == 0
        assert state.elapsed_time == 0.0
        assert state.metadata == {}

    def test_metadata_independent_per_instance(self):
        s1 = BaseGameState()
        s2 = BaseGameState()
        s1.metadata["key"] = "val"
        assert "key" not in s2.metadata

    def test_subclassing(self):
        @dataclass
        class MyState(BaseGameState):
            score: int = 0
            name: str = "player"

        state = MyState()
        assert state.score == 0
        assert state.name == "player"
        assert state.is_running is True

    def test_subclass_with_custom_defaults(self):
        @dataclass
        class MyState(BaseGameState):
            health: int = 100

        state = MyState(is_running=False, health=50)
        assert state.is_running is False
        assert state.health == 50
