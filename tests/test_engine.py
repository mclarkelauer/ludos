"""Tests for GameEngine."""

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from gamify.engine import EngineConfig, GameEngine
from gamify.errors import InitializationError
from gamify.input.events import InputEvent, InputType
from gamify.scenes.base import BaseScene
from gamify.scenes.menu import MenuConfig, MenuItem, MenuScene
from gamify.state.base import BaseGameState


class StubScene(BaseScene):
    def __init__(self):
        self.input_count = 0
        self.update_count = 0
        self.render_count = 0

    def handle_input(self, event, state):
        self.input_count += 1

    def update(self, dt, state):
        self.update_count += 1

    def render(self, surface, state):
        self.render_count += 1


class TestEngineConfig:
    def test_defaults(self):
        cfg = EngineConfig()
        assert cfg.width == 800
        assert cfg.height == 600
        assert cfg.title == "Gamify"
        assert cfg.fps == 60
        assert cfg.bg_color == (0, 0, 0)

    def test_custom(self):
        cfg = EngineConfig(width=1024, height=768, title="Test", fps=30)
        assert cfg.width == 1024
        assert cfg.fps == 30


class TestGameEngine:
    def test_init_defaults(self):
        engine = GameEngine()
        assert engine.state_manager is not None
        assert engine.scene_manager is not None
        assert engine.input_handler is not None
        assert engine.window is None  # not initialized until run()

    def test_init_with_custom_state(self):
        @dataclass
        class MyState(BaseGameState):
            score: int = 0

        state = MyState(score=42)
        engine = GameEngine(initial_state=state)
        assert engine.state_manager.state.score == 42

    def test_stop_sets_not_running(self):
        engine = GameEngine()
        assert engine.state_manager.state.is_running is True
        engine.stop()
        assert engine.state_manager.state.is_running is False

    @patch("gamify.engine.pygame")
    def test_run_initializes_and_shuts_down(self, mock_pg):
        mock_pg.display.set_mode.return_value = MagicMock()
        mock_clock = MagicMock()
        mock_clock.tick.return_value = 16  # ~60fps
        mock_pg.time.Clock.return_value = mock_clock
        mock_pg.event.get.return_value = []

        engine = GameEngine()
        # Stop after first frame
        frame = [0]
        original_poll = engine._input_handler.poll

        def stop_after_one():
            frame[0] += 1
            if frame[0] >= 2:
                engine.stop()
            return []

        with patch.object(engine._input_handler, "poll", side_effect=stop_after_one):
            engine.run()

        mock_pg.init.assert_called_once()
        mock_pg.quit.assert_called_once()

    @patch("gamify.engine.pygame")
    def test_quit_event_stops_engine(self, mock_pg):
        mock_pg.display.set_mode.return_value = MagicMock()
        mock_clock = MagicMock()
        mock_clock.tick.return_value = 16
        mock_pg.time.Clock.return_value = mock_clock
        mock_pg.QUIT = 256

        quit_event = InputEvent(type=InputType.QUIT)

        engine = GameEngine()
        call_count = [0]

        def poll_with_quit():
            call_count[0] += 1
            if call_count[0] == 1:
                return [quit_event]
            return []

        with patch.object(engine._input_handler, "poll", side_effect=poll_with_quit):
            engine.run()

        assert engine.state_manager.state.is_running is False

    @patch("gamify.engine.pygame")
    def test_scene_receives_events(self, mock_pg):
        mock_pg.display.set_mode.return_value = MagicMock()
        mock_clock = MagicMock()
        mock_clock.tick.return_value = 16
        mock_pg.time.Clock.return_value = mock_clock

        scene = StubScene()
        engine = GameEngine(initial_scene=scene)

        key_event = InputEvent(type=InputType.KEY_DOWN, key=42, action="test")
        call_count = [0]

        def poll_events():
            call_count[0] += 1
            if call_count[0] == 1:
                return [key_event]
            engine.stop()
            return []

        with patch.object(engine._input_handler, "poll", side_effect=poll_events):
            engine.run()

        assert scene.input_count >= 1
        assert scene.update_count >= 1
        assert scene.render_count >= 1

    @patch("gamify.scenes.menu.pygame")
    @patch("gamify.display.window.pygame")
    @patch("gamify.engine.pygame")
    def test_integration_menu_scene(self, mock_pg, mock_window_pg, mock_menu_pg):
        """Integration test: engine runs with a MenuScene."""
        mock_surface = MagicMock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600
        mock_window_pg.display.set_mode.return_value = mock_surface

        mock_clock = MagicMock()
        mock_clock.tick.return_value = 16
        mock_pg.time.Clock.return_value = mock_clock

        mock_font = MagicMock()
        mock_font.render.return_value = MagicMock()
        mock_font.render.return_value.get_rect.return_value = MagicMock()
        mock_menu_pg.font.Font.return_value = mock_font

        quit_called = []
        menu = MenuScene(
            items=[
                MenuItem("Start", lambda: None),
                MenuItem("Quit", lambda: quit_called.append(True)),
            ],
            config=MenuConfig(title="Test Menu"),
        )

        @dataclass
        class GameState(BaseGameState):
            score: int = 0

        engine = GameEngine(
            config=EngineConfig(title="Test"),
            initial_state=GameState(),
            initial_scene=menu,
        )

        call_count = [0]

        def poll_events():
            call_count[0] += 1
            if call_count[0] >= 2:
                engine.stop()
            return []

        with patch.object(engine._input_handler, "poll", side_effect=poll_events):
            engine.run()

        assert engine.state_manager.state.frame_count >= 1
