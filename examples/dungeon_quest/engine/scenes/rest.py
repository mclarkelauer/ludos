"""Rest scene — heal confirmation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.menu_renderer import draw_menu
from ..rendering.text import draw_text
from ..state import DungeonQuestState

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext


class RestScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx: GameContext) -> None:
        self._engine = engine
        self._ctx = ctx
        self._layout: Layout | None = None
        self._cursor = 0
        self._rested = False

    def on_enter(self, state: BaseGameState) -> None:
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)
        self._cursor = 0
        self._rested = False

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)

        if self._rested:
            if event.action == "confirm":
                self._engine.scene_manager.pop(s)
            return

        if event.action == "move_up":
            self._cursor = (self._cursor - 1) % 2
        elif event.action == "move_down":
            self._cursor = (self._cursor + 1) % 2
        elif event.action == "confirm":
            if self._cursor == 0:  # Rest
                for char in s.party:
                    if not char.is_dead:
                        char.current_hp = char.max_hp
                        char.current_mp = char.max_mp
                self._rested = True
            else:  # Cancel
                self._engine.scene_manager.pop(s)
        elif event.action == "cancel":
            self._engine.scene_manager.pop(s)

    def update(self, dt: float, state: BaseGameState) -> None:
        pass

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        if not self._layout:
            return

        overlay = pygame.Surface((self._layout.width, self._layout.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel = self._layout.centered(350, 200)
        inner = draw_panel(surface, panel, title="Rest")

        if self._rested:
            draw_text(surface, "The party rests and recovers fully.", inner, colors.HEAL_COLOR)
            prompt = fonts.small().render("[Enter] to continue", True, colors.LIGHT_GRAY)
            surface.blit(prompt, (panel.centerx - prompt.get_width() // 2, panel.bottom - 30))
        else:
            draw_text(surface, "Rest here and recover HP/MP?", inner, colors.WHITE)
            menu_rect = pygame.Rect(inner.x, inner.y + 40, inner.width, inner.height - 40)
            draw_menu(surface, menu_rect, ["Rest", "Cancel"], self._cursor)

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state
