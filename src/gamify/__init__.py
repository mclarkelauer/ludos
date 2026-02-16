"""Gamify - Pygame abstraction framework for rapid game development."""

from gamify.display.window import Window
from gamify.engine import EngineConfig, GameEngine
from gamify.errors import (
    GamifyError,
    InitializationError,
    InputError,
    RenderError,
    SceneError,
    StateError,
)
from gamify.input.bindings import KeyBindings
from gamify.input.events import InputEvent, InputType
from gamify.input.handler import InputHandler
from gamify.scenes.base import BaseScene
from gamify.scenes.manager import SceneManager
from gamify.scenes.menu import MenuConfig, MenuItem, MenuScene
from gamify.state.base import BaseGameState
from gamify.state.manager import StateManager

__all__ = [
    "BaseGameState",
    "BaseScene",
    "EngineConfig",
    "GameEngine",
    "GamifyError",
    "InitializationError",
    "InputError",
    "InputEvent",
    "InputHandler",
    "InputType",
    "KeyBindings",
    "MenuConfig",
    "MenuItem",
    "MenuScene",
    "RenderError",
    "SceneError",
    "SceneManager",
    "StateError",
    "StateManager",
    "Window",
]
