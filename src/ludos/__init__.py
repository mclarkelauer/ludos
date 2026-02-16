"""Ludos - Pygame abstraction framework for rapid game development."""

from ludos.display.window import Window
from ludos.engine import EngineConfig, GameEngine
from ludos.errors import (
    LudosError,
    InitializationError,
    InputError,
    RenderError,
    SceneError,
    StateError,
)
from ludos.input.bindings import KeyBindings
from ludos.input.events import InputEvent, InputType
from ludos.input.handler import InputHandler
from ludos.scenes.base import BaseScene
from ludos.scenes.manager import SceneManager
from ludos.scenes.menu import MenuConfig, MenuItem, MenuScene
from ludos.state.base import BaseGameState
from ludos.state.manager import StateManager

__all__ = [
    "BaseGameState",
    "BaseScene",
    "EngineConfig",
    "GameEngine",
    "LudosError",
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
