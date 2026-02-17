"""Inventory scene — item list + equip/use."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..characters.inventory import equip_item, use_consumable
from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.text import draw_text
from ..rendering.menu_renderer import draw_menu
from ..state import DungeonQuestState
from ...content.types import ItemType

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext


class InventoryScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx: GameContext) -> None:
        self._engine = engine
        self._ctx = ctx
        self._layout: Layout | None = None
        self._cursor = 0
        self._char_cursor = 0  # For equip target
        self._mode = "list"  # "list" or "equip_target"
        self._notification = ""
        self._notif_timer = 0.0

    def on_enter(self, state: BaseGameState) -> None:
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)
        self._cursor = 0
        self._mode = "list"

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)

        if self._mode == "equip_target":
            alive = [c for c in s.party if not c.is_dead]
            if event.action == "move_up":
                self._char_cursor = (self._char_cursor - 1) % max(1, len(alive))
            elif event.action == "move_down":
                self._char_cursor = (self._char_cursor + 1) % max(1, len(alive))
            elif event.action == "confirm":
                self._equip_to_char(s)
            elif event.action == "cancel":
                self._mode = "list"
            return

        items = self._unique_items(s)
        if event.action == "move_up":
            self._cursor = (self._cursor - 1) % max(1, len(items))
        elif event.action == "move_down":
            self._cursor = (self._cursor + 1) % max(1, len(items))
        elif event.action == "confirm":
            self._use_item(s)
        elif event.action == "cancel":
            self._engine.scene_manager.pop(s)

    def update(self, dt: float, state: BaseGameState) -> None:
        if self._notif_timer > 0:
            self._notif_timer -= dt
            if self._notif_timer <= 0:
                self._notification = ""

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        s = self._cast(state)
        if not self._layout:
            return

        # Semi-transparent backdrop
        overlay = pygame.Surface((self._layout.width, self._layout.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel = self._layout.centered(500, 400)
        inner = draw_panel(surface, panel, title=f"Inventory (Gold: {s.gold})")

        items = self._unique_items(s)
        if not items:
            draw_text(surface, "No items.", inner, colors.LIGHT_GRAY)
        else:
            # Item list
            list_rect = pygame.Rect(inner.x, inner.y, inner.width // 2, inner.height)
            item_names = []
            for item_id, count in items:
                item = self._ctx.items.get(item_id)
                name = item.name if item else item_id
                suffix = f" x{count}" if count > 1 else ""
                item_names.append(f"{name}{suffix}")
            draw_menu(surface, list_rect, item_names, self._cursor)

            # Item details
            if self._cursor < len(items):
                detail_rect = pygame.Rect(inner.x + inner.width // 2 + 8, inner.y, inner.width // 2 - 8, inner.height)
                item_id = items[self._cursor][0]
                item = self._ctx.items.get(item_id)
                if item:
                    y = detail_rect.y
                    font = fonts.normal()
                    small = fonts.small()

                    name_surf = font.render(item.name, True, colors.YELLOW)
                    surface.blit(name_surf, (detail_rect.x, y))
                    y += 28

                    draw_text(surface, item.description, pygame.Rect(detail_rect.x, y, detail_rect.width, 60), colors.LIGHT_GRAY, small)
                    y += 65

                    type_surf = small.render(f"Type: {item.item_type.name}", True, colors.WHITE)
                    surface.blit(type_surf, (detail_rect.x, y))
                    y += 20

                    if item.item_type == ItemType.EQUIPMENT and item.slot:
                        slot_surf = small.render(f"Slot: {item.slot.name}", True, colors.WHITE)
                        surface.blit(slot_surf, (detail_rect.x, y))
                        y += 20
                        if item.attack_bonus:
                            surface.blit(small.render(f"ATK +{item.attack_bonus}", True, colors.BUFF_COLOR), (detail_rect.x, y))
                            y += 18
                        if item.defense_bonus:
                            surface.blit(small.render(f"DEF +{item.defense_bonus}", True, colors.BUFF_COLOR), (detail_rect.x, y))
                            y += 18

                    elif item.item_type == ItemType.CONSUMABLE:
                        if item.heal_amount:
                            surface.blit(small.render(f"Heals {item.heal_amount} HP", True, colors.HEAL_COLOR), (detail_rect.x, y))
                            y += 18
                        if item.mp_restore:
                            surface.blit(small.render(f"Restores {item.mp_restore} MP", True, colors.MP_BLUE), (detail_rect.x, y))
                            y += 18

        # Equip target selection
        if self._mode == "equip_target":
            alive = [c for c in s.party if not c.is_dead]
            char_panel = self._layout.centered(250, 200)
            char_panel.x += 200
            char_inner = draw_panel(surface, char_panel, title="Equip to:")
            char_names = [c.name for c in alive]
            draw_menu(surface, char_inner, char_names, self._char_cursor)

        # Notification
        if self._notification:
            notif = fonts.small().render(self._notification, True, colors.YELLOW)
            surface.blit(notif, (panel.centerx - notif.get_width() // 2, panel.bottom - 24))

        # Controls
        controls = "[Enter] Use/Equip  [Esc] Close"
        hint = fonts.small().render(controls, True, colors.LIGHT_GRAY)
        surface.blit(hint, (panel.centerx - hint.get_width() // 2, panel.bottom + 4))

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state

    def _unique_items(self, s: DungeonQuestState) -> list[tuple[str, int]]:
        """Get unique items with counts."""
        counts: dict[str, int] = {}
        order: list[str] = []
        for item_id in s.inventory:
            if item_id not in counts:
                order.append(item_id)
                counts[item_id] = 0
            counts[item_id] += 1
        return [(iid, counts[iid]) for iid in order]

    def _use_item(self, s: DungeonQuestState) -> None:
        items = self._unique_items(s)
        if not items or self._cursor >= len(items):
            return
        item_id = items[self._cursor][0]
        item = self._ctx.items.get(item_id)
        if not item:
            return

        if item.item_type == ItemType.CONSUMABLE:
            # Use on first alive party member
            alive = [c for c in s.party if not c.is_dead]
            if alive:
                msg = use_consumable(alive[0], item_id, s, self._ctx)
                if msg:
                    self._notification = msg
                    self._notif_timer = 2.0

        elif item.item_type == ItemType.EQUIPMENT:
            alive = [c for c in s.party if not c.is_dead]
            if alive:
                self._mode = "equip_target"
                self._char_cursor = 0

    def _equip_to_char(self, s: DungeonQuestState) -> None:
        items = self._unique_items(s)
        if not items or self._cursor >= len(items):
            self._mode = "list"
            return
        item_id = items[self._cursor][0]
        alive = [c for c in s.party if not c.is_dead]
        if self._char_cursor >= len(alive):
            self._mode = "list"
            return
        char = alive[self._char_cursor]
        msg = equip_item(char, item_id, s, self._ctx)
        if msg:
            self._notification = msg
            self._notif_timer = 2.0
        self._mode = "list"
