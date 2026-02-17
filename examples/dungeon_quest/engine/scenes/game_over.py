"""Game over scene — death/victory screen."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.text import draw_text
from ..rendering.menu_renderer import draw_menu
from ..state import DungeonQuestState

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext


class GameOverScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx: GameContext, victory: bool = False) -> None:
        self._engine = engine
        self._ctx = ctx
        self._victory = victory
        self._layout: Layout | None = None
        self._cursor = 0

    def on_enter(self, state: BaseGameState) -> None:
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)
        if event.action == "move_up":
            self._cursor = (self._cursor - 1) % 2
        elif event.action == "move_down":
            self._cursor = (self._cursor + 1) % 2
        elif event.action == "confirm":
            if self._cursor == 0:  # Retry / Title
                from .title import TitleScene
                self._engine.scene_manager.clear(s)
                scene = TitleScene(self._engine, self._ctx)
                self._engine.scene_manager.push(scene, s)
            else:  # Quit
                self._engine.stop()

    def update(self, dt: float, state: BaseGameState) -> None:
        pass

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        s = self._cast(state)
        if not self._layout:
            return

        if self._victory:
            title = "VICTORY!"
            title_color = colors.YELLOW
            message = s.victory_text or self._ctx.quest_pack.victory_text
        else:
            title = "GAME OVER"
            title_color = colors.HP_RED
            message = "Your party has fallen..."

        # Title
        title_font = fonts.title()
        title_surf = title_font.render(title, True, title_color)
        title_rect = title_surf.get_rect(center=(self._layout.width // 2, self._layout.height // 4))
        surface.blit(title_surf, title_rect)

        # Message
        msg_rect = pygame.Rect(
            self._layout.width // 4,
            self._layout.height // 3,
            self._layout.width // 2,
            self._layout.height // 4,
        )
        draw_text(surface, message, msg_rect, colors.WHITE, fonts.normal())

        # Menu
        menu_rect = self._layout.centered(200, 80)
        menu_rect.y = self._layout.height * 2 // 3
        items = ["Title Screen", "Quit"]
        draw_menu(surface, menu_rect, items, self._cursor, font=fonts.large())

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state
