"""Abstract base scene."""

from abc import ABC, abstractmethod

import pygame

from gamify.input.events import InputEvent
from gamify.state.base import BaseGameState


class BaseScene(ABC):
    """Abstract base class for all game scenes.

    Subclass and implement handle_input, update, and render.
    Optionally override on_enter and on_exit for lifecycle hooks.
    """

    @abstractmethod
    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        """Process a single input event."""

    @abstractmethod
    def update(self, dt: float, state: BaseGameState) -> None:
        """Update scene logic. dt is seconds since last frame."""

    @abstractmethod
    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        """Draw the scene to the surface."""

    def on_enter(self, state: BaseGameState) -> None:
        """Called when this scene becomes the active scene."""

    def on_exit(self, state: BaseGameState) -> None:
        """Called when this scene is no longer the active scene."""
