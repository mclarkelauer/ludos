"""Tests for BaseScene."""

import pytest

from gamify.input.events import InputEvent, InputType
from gamify.scenes.base import BaseScene
from gamify.state.base import BaseGameState


class ConcreteScene(BaseScene):
    """Minimal concrete scene for testing."""

    def __init__(self):
        self.inputs = []
        self.updates = []
        self.renders = []
        self.entered = False
        self.exited = False

    def handle_input(self, event, state):
        self.inputs.append(event)

    def update(self, dt, state):
        self.updates.append(dt)

    def render(self, surface, state):
        self.renders.append(surface)

    def on_enter(self, state):
        self.entered = True

    def on_exit(self, state):
        self.exited = True


class TestBaseScene:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BaseScene()

    def test_concrete_scene_works(self):
        scene = ConcreteScene()
        state = BaseGameState()
        event = InputEvent(type=InputType.KEY_DOWN, key=42)
        scene.handle_input(event, state)
        assert len(scene.inputs) == 1

    def test_lifecycle_hooks_optional(self):
        # on_enter and on_exit have default no-op implementations
        class MinimalScene(BaseScene):
            def handle_input(self, event, state): pass
            def update(self, dt, state): pass
            def render(self, surface, state): pass

        scene = MinimalScene()
        state = BaseGameState()
        scene.on_enter(state)  # no error
        scene.on_exit(state)  # no error
