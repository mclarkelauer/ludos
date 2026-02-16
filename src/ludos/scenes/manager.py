"""Stack-based scene manager."""

from ludos.errors import SceneError
from ludos.scenes.base import BaseScene
from ludos.state.base import BaseGameState


class SceneManager:
    """Manages a stack of scenes with push/pop/replace operations.

    The topmost scene is the active scene that receives input, updates, and renders.
    """

    def __init__(self) -> None:
        self._stack: list[BaseScene] = []

    @property
    def active(self) -> BaseScene | None:
        """The currently active (topmost) scene."""
        return self._stack[-1] if self._stack else None

    @property
    def depth(self) -> int:
        """Number of scenes on the stack."""
        return len(self._stack)

    def push(self, scene: BaseScene, state: BaseGameState) -> None:
        """Push a scene onto the stack, calling lifecycle hooks."""
        if not isinstance(scene, BaseScene):
            raise SceneError(f"Expected BaseScene, got {type(scene).__name__}")
        if self._stack:
            self._stack[-1].on_exit(state)
        self._stack.append(scene)
        scene.on_enter(state)

    def pop(self, state: BaseGameState) -> BaseScene:
        """Pop the active scene and return it."""
        if not self._stack:
            raise SceneError("Cannot pop from empty scene stack")
        scene = self._stack.pop()
        scene.on_exit(state)
        if self._stack:
            self._stack[-1].on_enter(state)
        return scene

    def replace(self, scene: BaseScene, state: BaseGameState) -> BaseScene:
        """Replace the active scene with a new one."""
        if not isinstance(scene, BaseScene):
            raise SceneError(f"Expected BaseScene, got {type(scene).__name__}")
        if not self._stack:
            raise SceneError("Cannot replace on empty scene stack")
        old = self._stack.pop()
        old.on_exit(state)
        self._stack.append(scene)
        scene.on_enter(state)
        return old

    def clear(self, state: BaseGameState) -> None:
        """Pop all scenes from the stack."""
        while self._stack:
            scene = self._stack.pop()
            scene.on_exit(state)
