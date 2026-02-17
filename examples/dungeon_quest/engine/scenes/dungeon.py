"""Dungeon scene — tile grid movement + HUD."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..exploration.dungeon import (
    exit_dungeon,
    get_current_tile,
    go_deeper,
    move_player,
)
from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.map_renderer import draw_dungeon
from ..rendering.panels import draw_panel
from ..rendering.hud import draw_party_summary
from ..rendering.text import draw_text
from ..state import DungeonQuestState
from ...content.types import TileType

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext


class DungeonScene(BaseScene):
    input_repeat_delay = 0.12

    def __init__(self, engine: GameEngine, ctx: GameContext) -> None:
        self._engine = engine
        self._ctx = ctx
        self._layout: Layout | None = None
        self._notification = ""
        self._notif_timer = 0.0

    def on_enter(self, state: BaseGameState) -> None:
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)

        dx, dy = 0, 0
        if event.action in ("move_up", "w"):
            dy = -1
        elif event.action in ("move_down", "s"):
            dy = 1
        elif event.action in ("move_left", "a"):
            dx = -1
        elif event.action in ("move_right", "d"):
            dx = 1
        elif event.action == "cancel":
            # Check if on entrance/stairs_up — exit dungeon
            tile = get_current_tile(s, self._ctx)
            if tile in (TileType.ENTRANCE, TileType.STAIRS_UP):
                exit_dungeon(s)
                self._engine.scene_manager.pop(s)
            return
        elif event.action == "inventory":
            from .inventory import InventoryScene
            self._engine.scene_manager.push(InventoryScene(self._engine, self._ctx), s)
            return
        elif event.action == "party":
            from .party import PartyScene
            self._engine.scene_manager.push(PartyScene(self._engine, self._ctx), s)
            return

        if dx == 0 and dy == 0:
            return

        enc_id, dlg_id, msg = move_player(dx, dy, s, self._ctx)

        if msg:
            self._notification = msg
            self._notif_timer = 2.0

        # Check tile-based actions after movement
        tile = get_current_tile(s, self._ctx)
        if tile == TileType.STAIRS_DOWN and not enc_id:
            err = go_deeper(s, self._ctx)
            if err:
                self._notification = err
                self._notif_timer = 2.0
            else:
                # Refresh scene
                level = self._ctx.dungeon_levels.get(s.exploration.dungeon_level_id or "")
                if level:
                    self._notification = f"Descended to {level.name}"
                    self._notif_timer = 2.0

        if enc_id:
            from .combat import CombatScene
            scene = CombatScene(self._engine, self._ctx, enc_id)
            self._engine.scene_manager.push(scene, s)

        if dlg_id:
            from .dialogue import DialogueScene
            scene = DialogueScene(self._engine, self._ctx, dlg_id)
            self._engine.scene_manager.push(scene, s)

    def update(self, dt: float, state: BaseGameState) -> None:
        if self._notif_timer > 0:
            self._notif_timer -= dt
            if self._notif_timer <= 0:
                self._notification = ""

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        s = self._cast(state)
        if not self._layout:
            return

        level_id = s.exploration.dungeon_level_id
        if not level_id or level_id not in self._ctx.dungeon_levels:
            return

        level = self._ctx.dungeon_levels[level_id]

        # Map area
        map_rect = self._layout.dungeon_map()
        draw_panel(surface, map_rect, title=level.name)
        inner_map = map_rect.inflate(-8, -28)
        player_class = s.party[0].char_class.name if s.party else ""
        draw_dungeon(
            surface,
            inner_map,
            level.tiles,
            s.exploration.player_x,
            s.exploration.player_y,
            player_class=player_class,
        )

        # HUD sidebar
        hud_rect = self._layout.dungeon_hud()
        inner = draw_panel(surface, hud_rect, title="Party")
        draw_party_summary(surface, inner, s.party)

        # Notification
        if self._notification:
            font = fonts.small()
            notif_surf = font.render(self._notification, True, colors.YELLOW)
            x = map_rect.centerx - notif_surf.get_width() // 2
            surface.blit(notif_surf, (x, map_rect.bottom - 24))

        # Controls hint
        hint = fonts.small().render("[WASD/Arrows] Move  [Esc] Exit  [I] Items  [P] Party", True, colors.LIGHT_GRAY)
        surface.blit(hint, (self._layout.width // 2 - hint.get_width() // 2, self._layout.height - 20))

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state
