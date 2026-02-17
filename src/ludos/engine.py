"""Game engine - composition root and main loop."""

import time
from dataclasses import dataclass

import pygame

from ludos.display.window import Window
from ludos.errors import InitializationError, SceneError
from ludos.input.bindings import KeyBindings
from ludos.input.events import InputEvent, InputType
from ludos.input.handler import InputHandler
from ludos.scenes.base import BaseScene
from ludos.scenes.manager import SceneManager
from ludos.state.base import BaseGameState
from ludos.state.manager import StateManager


@dataclass
class EngineConfig:
    """Configuration for the game engine."""

    width: int = 800
    height: int = 600
    title: str = "Ludos"
    fps: int = 60
    bg_color: tuple[int, int, int] = (0, 0, 0)
    display_flags: int = 0


class GameEngine:
    """Main engine that ties everything together.

    Example:
        engine = GameEngine(
            config=EngineConfig(title="My Game"),
            initial_state=MyState(),
            initial_scene=MyScene(),
        )
        engine.run()
    """

    def __init__(
        self,
        config: EngineConfig | None = None,
        initial_state: BaseGameState | None = None,
        initial_scene: BaseScene | None = None,
        bindings: KeyBindings | None = None,
    ) -> None:
        self._config = config or EngineConfig()
        self._state_manager: StateManager = StateManager(
            initial_state or BaseGameState()
        )
        self._scene_manager = SceneManager()
        self._input_handler = InputHandler(bindings)
        self._window: Window | None = None
        self._clock: pygame.time.Clock | None = None
        self._initial_scene = initial_scene
        self._action_timestamps: dict[str, float] = {}
        self._active_scene_id: int = 0

    @property
    def state_manager(self) -> StateManager:
        return self._state_manager

    @property
    def scene_manager(self) -> SceneManager:
        return self._scene_manager

    @property
    def input_handler(self) -> InputHandler:
        return self._input_handler

    @property
    def window(self) -> Window | None:
        return self._window

    def run(self) -> None:
        """Initialize pygame and start the game loop."""
        try:
            pygame.init()
            pygame.font.init()
        except pygame.error as e:
            raise InitializationError(f"Pygame initialization failed: {e}") from e

        self._window = Window(
            self._config.width,
            self._config.height,
            self._config.title,
            self._config.display_flags,
        )
        self._clock = pygame.time.Clock()

        if self._initial_scene:
            self._scene_manager.push(self._initial_scene, self._state_manager.state)

        try:
            self._loop()
        finally:
            self._shutdown()

    def stop(self) -> None:
        """Signal the engine to stop after the current frame."""
        self._state_manager.update(lambda s: setattr(s, "is_running", False))

    def _should_deliver(self, event: InputEvent, scene: BaseScene) -> bool:
        """Check whether an input event should be delivered to the scene.

        Throttles repeated KEY_DOWN events with a resolved action based on
        the scene's input_repeat_delay. All other events pass through.
        """
        if scene.input_repeat_delay <= 0:
            return True
        if event.type != InputType.KEY_DOWN:
            return True
        if event.action is None:
            return True

        now = time.monotonic()
        last = self._action_timestamps.get(event.action, 0.0)
        if now - last < scene.input_repeat_delay:
            return False
        self._action_timestamps[event.action] = now
        return True

    def _loop(self) -> None:
        """Main game loop: input → update → render."""
        state = self._state_manager.state
        assert self._clock is not None
        assert self._window is not None

        while state.is_running:
            dt = self._clock.tick(self._config.fps) / 1000.0

            self._state_manager.update(lambda s: setattr(s, "frame_count", s.frame_count + 1))
            self._state_manager.update(lambda s: setattr(s, "elapsed_time", s.elapsed_time + dt))

            # Input
            events = self._input_handler.poll()
            scene = self._scene_manager.active

            # Reset throttle timestamps when the active scene changes
            if scene is not None and id(scene) != self._active_scene_id:
                self._active_scene_id = id(scene)
                self._action_timestamps.clear()

            for event in events:
                if event.type == InputType.QUIT:
                    self.stop()
                    break
                if scene and self._should_deliver(event, scene):
                    scene.handle_input(event, state)

            if not state.is_running:
                break

            # Update
            if scene:
                scene.update(dt, state)

            # Render
            self._window.clear(self._config.bg_color)
            if scene:
                scene.render(self._window.surface, state)
            self._window.flip()

            self._state_manager.mark_clean()

    def _shutdown(self) -> None:
        """Clean up pygame."""
        self._scene_manager.clear(self._state_manager.state)
        pygame.quit()
