"""Built-in customizable menu scene."""

from collections.abc import Callable
from dataclasses import dataclass, field

import pygame

from gamify.input.events import InputEvent
from gamify.scenes.base import BaseScene
from gamify.state.base import BaseGameState


@dataclass
class MenuItem:
    """A single menu item."""

    label: str
    action: Callable[[], None]


@dataclass
class MenuConfig:
    """Configuration for MenuScene appearance."""

    font_size: int = 36
    font_name: str | None = None
    text_color: tuple[int, int, int] = (255, 255, 255)
    highlight_color: tuple[int, int, int] = (255, 255, 0)
    bg_color: tuple[int, int, int] = (0, 0, 0)
    title: str = ""
    title_font_size: int = 48
    item_spacing: int = 10


class MenuScene(BaseScene):
    """A customizable menu scene with keyboard navigation.

    Example:
        menu = MenuScene(
            items=[
                MenuItem("Start Game", start_game),
                MenuItem("Quit", quit_game),
            ],
            config=MenuConfig(title="Main Menu"),
        )
    """

    def __init__(
        self,
        items: list[MenuItem],
        config: MenuConfig | None = None,
    ) -> None:
        self._items = items
        self._config = config or MenuConfig()
        self._selected = 0
        self._font: pygame.font.Font | None = None
        self._title_font: pygame.font.Font | None = None

    @property
    def items(self) -> list[MenuItem]:
        return self._items

    @property
    def selected(self) -> int:
        return self._selected

    @selected.setter
    def selected(self, value: int) -> None:
        if self._items:
            self._selected = value % len(self._items)

    def _ensure_fonts(self) -> None:
        if self._font is None:
            self._font = pygame.font.Font(
                self._config.font_name, self._config.font_size
            )
        if self._title_font is None:
            self._title_font = pygame.font.Font(
                self._config.font_name, self._config.title_font_size
            )

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        if event.action == "move_up":
            self.selected -= 1
        elif event.action == "move_down":
            self.selected += 1
        elif event.action == "confirm":
            if self._items:
                self._items[self._selected].action()

    def update(self, dt: float, state: BaseGameState) -> None:
        pass

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        self._ensure_fonts()
        assert self._font is not None
        assert self._title_font is not None

        surface.fill(self._config.bg_color)
        center_x = surface.get_width() // 2
        y = surface.get_height() // 4

        if self._config.title:
            title_surf = self._title_font.render(
                self._config.title, True, self._config.text_color
            )
            title_rect = title_surf.get_rect(center=(center_x, y))
            surface.blit(title_surf, title_rect)
            y += self._config.title_font_size + self._config.item_spacing * 2

        for i, item in enumerate(self._items):
            color = (
                self._config.highlight_color
                if i == self._selected
                else self._config.text_color
            )
            text_surf = self._font.render(item.label, True, color)
            text_rect = text_surf.get_rect(center=(center_x, y))
            surface.blit(text_surf, text_rect)
            y += self._config.font_size + self._config.item_spacing
