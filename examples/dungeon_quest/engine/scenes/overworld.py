"""Overworld scene — area description + action menu."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..exploration.overworld import get_area_actions, travel_to_area, get_locked_text
from ..exploration.dungeon import enter_dungeon
from ..quests.tracker import update_quests
from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.text import draw_text
from ..rendering.menu_renderer import draw_menu
from ..rendering.sprites import SpriteCache
from ..state import DungeonQuestState

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext


class OverworldScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx: GameContext) -> None:
        self._engine = engine
        self._ctx = ctx
        self._layout: Layout | None = None
        self._actions: list[str] = []
        self._notification = ""
        self._notif_timer = 0.0

    def on_enter(self, state: BaseGameState) -> None:
        s = self._cast(state)
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)
        self._rebuild_actions(s)

        # Update quests
        quest_msgs = update_quests(s, self._ctx)
        if quest_msgs:
            self._notification = " | ".join(quest_msgs)
            self._notif_timer = 3.0

        # Check victory condition
        victory_flag = self._ctx.quest_pack.victory_flag
        if victory_flag in s.quest.flags and not s.game_won:
            s.game_won = True
            s.victory_text = self._ctx.quest_pack.victory_text
            from .game_over import GameOverScene
            scene = GameOverScene(self._engine, self._ctx, victory=True)
            self._engine.scene_manager.replace(scene, s)

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)

        # Handle intro text
        if s.show_intro:
            if event.action == "confirm":
                s.show_intro = False
            return

        if event.action == "move_up":
            s.exploration.overworld_cursor = (s.exploration.overworld_cursor - 1) % max(1, len(self._actions))
        elif event.action == "move_down":
            s.exploration.overworld_cursor = (s.exploration.overworld_cursor + 1) % max(1, len(self._actions))
        elif event.action == "confirm":
            self._select_action(s)

    def update(self, dt: float, state: BaseGameState) -> None:
        if self._notif_timer > 0:
            self._notif_timer -= dt
            if self._notif_timer <= 0:
                self._notification = ""

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        s = self._cast(state)
        if not self._layout:
            return

        area = self._ctx.areas.get(s.exploration.current_area_id)
        if not area:
            return

        # Handle intro overlay
        if s.show_intro:
            panel = self._layout.centered(500, 300)
            inner = draw_panel(surface, panel, title=self._ctx.quest_pack.name)
            draw_text(surface, s.intro_text, inner, colors.WHITE, fonts.normal())
            prompt = fonts.small().render("[Enter] to continue", True, colors.LIGHT_GRAY)
            surface.blit(prompt, (panel.centerx - prompt.get_width() // 2, panel.bottom - 30))
            return

        # Description panel
        desc_rect = self._layout.overworld_description()
        inner = draw_panel(surface, desc_rect, title=area.name)

        # Area vignette illustration
        vignette = SpriteCache.get_area_vignette(
            s.exploration.current_area_id, area.name
        )
        vignette_w = min(vignette.get_width(), inner.width)
        vignette_h = vignette.get_height()
        vx = inner.x + (inner.width - vignette_w) // 2
        vy = inner.y
        surface.blit(vignette, (vx, vy), (0, 0, vignette_w, vignette_h))

        # Shift description text down below the vignette
        text_rect = pygame.Rect(inner.x, vy + vignette_h + 4, inner.width, inner.height - vignette_h - 4)
        draw_text(surface, area.description, text_rect, colors.WHITE, fonts.normal())

        # Notification
        if self._notification:
            font = fonts.small()
            notif_surf = font.render(self._notification, True, colors.YELLOW)
            surface.blit(notif_surf, (inner.x, inner.bottom - 20))

        # Action menu
        action_rect = self._layout.overworld_actions()
        inner = draw_panel(surface, action_rect, title="Actions")
        # Mark locked actions
        disabled = set()
        for i, action in enumerate(self._actions):
            if action.startswith("Travel: [Locked]"):
                disabled.add(i)
        draw_menu(surface, inner, self._actions, s.exploration.overworld_cursor, disabled=disabled)

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state

    def _rebuild_actions(self, s: DungeonQuestState) -> None:
        area = self._ctx.areas.get(s.exploration.current_area_id)
        if area:
            self._actions = get_area_actions(area, s, self._ctx)
        else:
            self._actions = []

    def _select_action(self, s: DungeonQuestState) -> None:
        if not self._actions:
            return
        action = self._actions[s.exploration.overworld_cursor]

        if action.startswith("Travel: [Locked]"):
            # Find locked text
            area = self._ctx.areas.get(s.exploration.current_area_id)
            if area:
                conn_idx = 0
                for i, a in enumerate(self._actions):
                    if a == action:
                        # Count travel actions up to this index
                        for conn in area.connections:
                            if conn_idx == i:
                                self._notification = conn.locked_text
                                self._notif_timer = 2.0
                                break
                            conn_idx += 1
            return

        if action.startswith("Travel: "):
            label = action[8:]
            area = self._ctx.areas.get(s.exploration.current_area_id)
            if area:
                for conn in area.connections:
                    if conn.label == label:
                        err = travel_to_area(conn.target_area_id, s, self._ctx)
                        if err:
                            self._notification = err
                            self._notif_timer = 2.0
                        else:
                            # Replace with new overworld scene
                            scene = OverworldScene(self._engine, self._ctx)
                            self._engine.scene_manager.replace(scene, s)
                        return

        elif action == "Enter Dungeon":
            err = enter_dungeon(s.exploration.current_area_id, s, self._ctx)
            if err:
                self._notification = err
                self._notif_timer = 2.0
            else:
                from .dungeon import DungeonScene
                scene = DungeonScene(self._engine, self._ctx)
                self._engine.scene_manager.push(scene, s)

        elif action.startswith("Talk: "):
            speaker = action[6:]
            area = self._ctx.areas.get(s.exploration.current_area_id)
            if area:
                for dlg_id in area.npcs:
                    dlg = self._ctx.dialogues.get(dlg_id)
                    if dlg and dlg.nodes and dlg.nodes[0].speaker == speaker:
                        from .dialogue import DialogueScene
                        scene = DialogueScene(self._engine, self._ctx, dlg_id)
                        self._engine.scene_manager.push(scene, s)
                        return

        elif action == "Rest":
            from .rest import RestScene
            scene = RestScene(self._engine, self._ctx)
            self._engine.scene_manager.push(scene, s)

        elif action == "Party":
            from .party import PartyScene
            scene = PartyScene(self._engine, self._ctx)
            self._engine.scene_manager.push(scene, s)

        elif action == "Inventory":
            from .inventory import InventoryScene
            scene = InventoryScene(self._engine, self._ctx)
            self._engine.scene_manager.push(scene, s)
