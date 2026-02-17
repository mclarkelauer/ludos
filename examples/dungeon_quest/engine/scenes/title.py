"""Title scene — main menu."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.menu_renderer import draw_menu
from ..rendering.sprites import SpriteCache
from ..state import DungeonQuestState

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext

MENU_ITEMS = ["New Game", "Quit"]


class TitleScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx: GameContext, state_factory=None) -> None:
        self._engine = engine
        self._ctx = ctx
        self._state_factory = state_factory  # callable that builds fresh DungeonQuestState
        self._cursor = 0
        self._layout: Layout | None = None

    def on_enter(self, state: BaseGameState) -> None:
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)
        self._bg_surface = SpriteCache.get_title_illustration()

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        if event.action == "move_up":
            self._cursor = (self._cursor - 1) % len(MENU_ITEMS)
        elif event.action == "move_down":
            self._cursor = (self._cursor + 1) % len(MENU_ITEMS)
        elif event.action == "confirm":
            self._select(state)

    def update(self, dt: float, state: BaseGameState) -> None:
        pass

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        if not self._layout:
            return

        # Background illustration (dimmed)
        if self._bg_surface:
            bg_rect = self._bg_surface.get_rect(
                center=(self._layout.width // 2, self._layout.height // 3)
            )
            dimmed = self._bg_surface.copy()
            dimmed.set_alpha(100)
            surface.blit(dimmed, bg_rect)

        # Title
        title_font = fonts.title()
        title_surf = title_font.render("Dungeon Quest", True, colors.YELLOW)
        title_rect = title_surf.get_rect(center=(self._layout.width // 2, self._layout.height // 3))
        surface.blit(title_surf, title_rect)

        # Quest name subtitle
        subtitle_font = fonts.normal()
        subtitle = self._ctx.quest_pack.name
        sub_surf = subtitle_font.render(subtitle, True, colors.LIGHT_GRAY)
        sub_rect = sub_surf.get_rect(center=(self._layout.width // 2, self._layout.height // 3 + 50))
        surface.blit(sub_surf, sub_rect)

        # Menu
        menu_w, menu_h = 200, 100
        menu_rect = self._layout.centered(menu_w, menu_h)
        menu_rect.y = self._layout.height // 2 + 20
        draw_menu(surface, menu_rect, MENU_ITEMS, self._cursor, font=fonts.large())

    def _select(self, state: BaseGameState) -> None:
        action = MENU_ITEMS[self._cursor]
        if action == "New Game":
            # Build fresh state if factory provided
            if self._state_factory:
                new_state = self._state_factory()
                self._engine.state_manager.update(lambda s: self._copy_state(s, new_state))
                state = self._engine.state_manager.state

            s = state
            assert isinstance(s, DungeonQuestState)

            from .overworld import OverworldScene
            scene = OverworldScene(self._engine, self._ctx)
            self._engine.scene_manager.replace(scene, s)

        elif action == "Quit":
            self._engine.stop()

    def _copy_state(self, target: DungeonQuestState, source: DungeonQuestState) -> None:
        """Copy all fields from source to target."""
        target.party = source.party
        target.gold = source.gold
        target.inventory = list(source.inventory)
        target.combat = source.combat
        target.exploration = source.exploration
        target.dialogue = source.dialogue
        target.quest = source.quest
        target.message_log = list(source.message_log)
        target.notification = source.notification
        target.show_intro = source.show_intro
        target.intro_text = source.intro_text
        target.game_won = source.game_won
        target.victory_text = source.victory_text
