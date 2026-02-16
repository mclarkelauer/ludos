"""Tests for SceneManager."""

import pytest

from ludos.errors import SceneError
from ludos.scenes.base import BaseScene
from ludos.scenes.manager import SceneManager
from ludos.state.base import BaseGameState


class FakeScene(BaseScene):
    def __init__(self, name=""):
        self.name = name
        self.entered = False
        self.exited = False

    def handle_input(self, event, state): pass
    def update(self, dt, state): pass
    def render(self, surface, state): pass

    def on_enter(self, state):
        self.entered = True

    def on_exit(self, state):
        self.exited = True


class TestSceneManager:
    def setup_method(self):
        self.manager = SceneManager()
        self.state = BaseGameState()

    def test_initially_empty(self):
        assert self.manager.active is None
        assert self.manager.depth == 0

    def test_push(self):
        scene = FakeScene("main")
        self.manager.push(scene, self.state)
        assert self.manager.active is scene
        assert self.manager.depth == 1
        assert scene.entered

    def test_push_calls_exit_on_previous(self):
        s1 = FakeScene("s1")
        s2 = FakeScene("s2")
        self.manager.push(s1, self.state)
        self.manager.push(s2, self.state)
        assert s1.exited
        assert s2.entered
        assert self.manager.active is s2

    def test_pop(self):
        s1 = FakeScene("s1")
        s2 = FakeScene("s2")
        self.manager.push(s1, self.state)
        s1.entered = False  # reset
        self.manager.push(s2, self.state)
        popped = self.manager.pop(self.state)
        assert popped is s2
        assert s2.exited
        assert s1.entered  # re-entered
        assert self.manager.active is s1

    def test_pop_empty_raises(self):
        with pytest.raises(SceneError, match="empty"):
            self.manager.pop(self.state)

    def test_replace(self):
        s1 = FakeScene("s1")
        s2 = FakeScene("s2")
        self.manager.push(s1, self.state)
        old = self.manager.replace(s2, self.state)
        assert old is s1
        assert s1.exited
        assert s2.entered
        assert self.manager.active is s2
        assert self.manager.depth == 1

    def test_replace_empty_raises(self):
        with pytest.raises(SceneError, match="empty"):
            self.manager.replace(FakeScene(), self.state)

    def test_push_rejects_non_scene(self):
        with pytest.raises(SceneError, match="BaseScene"):
            self.manager.push("not a scene", self.state)  # type: ignore

    def test_clear(self):
        self.manager.push(FakeScene("s1"), self.state)
        self.manager.push(FakeScene("s2"), self.state)
        self.manager.clear(self.state)
        assert self.manager.depth == 0
        assert self.manager.active is None
