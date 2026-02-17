"""Party scene — character stat cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..characters.stats import effective_attack, effective_defense, effective_speed
from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.hud import draw_hp_bar, draw_mp_bar
from ..state import DungeonQuestState

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext


class PartyScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx: GameContext) -> None:
        self._engine = engine
        self._ctx = ctx
        self._layout: Layout | None = None
        self._cursor = 0

    def on_enter(self, state: BaseGameState) -> None:
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)
        if event.action == "move_left":
            self._cursor = (self._cursor - 1) % max(1, len(s.party))
        elif event.action == "move_right":
            self._cursor = (self._cursor + 1) % max(1, len(s.party))
        elif event.action == "cancel":
            self._engine.scene_manager.pop(s)

    def update(self, dt: float, state: BaseGameState) -> None:
        pass

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        s = self._cast(state)
        if not self._layout or not s.party:
            return

        # Backdrop
        overlay = pygame.Surface((self._layout.width, self._layout.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        char = s.party[self._cursor % len(s.party)]
        panel = self._layout.centered(400, 420)
        class_name = char.char_class.name
        inner = draw_panel(surface, panel, title=f"{char.name} — {class_name}")

        font = fonts.normal()
        small = fonts.small()
        y = inner.y

        # Level + XP
        lvl_surf = font.render(f"Level {char.level}  XP: {char.xp}/{char.level * 100 + 100}", True, colors.WHITE)
        surface.blit(lvl_surf, (inner.x, y))
        y += 30

        # HP bar
        hp_label = small.render("HP", True, colors.WHITE)
        surface.blit(hp_label, (inner.x, y + 1))
        draw_hp_bar(surface, inner.x + 30, y, 180, char.current_hp, char.max_hp)
        y += 20

        # MP bar
        mp_label = small.render("MP", True, colors.WHITE)
        surface.blit(mp_label, (inner.x, y + 1))
        draw_mp_bar(surface, inner.x + 30, y, 180, char.current_mp, char.max_mp)
        y += 28

        # Stats
        atk = effective_attack(char, self._ctx)
        dfn = effective_defense(char, self._ctx)
        spd = effective_speed(char, self._ctx)

        stats = [
            ("ATK", atk, char.base_attack),
            ("DEF", dfn, char.base_defense),
            ("SPD", spd, char.base_speed),
        ]
        for label, eff, base in stats:
            color = colors.BUFF_COLOR if eff > base else colors.WHITE
            stat_surf = small.render(f"{label}: {eff} (base {base})", True, color)
            surface.blit(stat_surf, (inner.x, y))
            y += 20

        y += 10

        # Equipment
        equip_label = font.render("Equipment", True, colors.YELLOW)
        surface.blit(equip_label, (inner.x, y))
        y += 26
        for slot, item_id in char.equipment.items():
            if item_id and item_id in self._ctx.items:
                item = self._ctx.items[item_id]
                eq_surf = small.render(f"  {slot.name}: {item.name}", True, colors.WHITE)
            else:
                eq_surf = small.render(f"  {slot.name}: (empty)", True, colors.DISABLED_COLOR)
            surface.blit(eq_surf, (inner.x, y))
            y += 18

        y += 10

        # Abilities
        if char.abilities:
            ab_label = font.render("Abilities", True, colors.YELLOW)
            surface.blit(ab_label, (inner.x, y))
            y += 26
            for ability in char.abilities[:5]:
                ab_surf = small.render(f"  {ability.name} ({ability.cost}MP) - {ability.description}", True, colors.LIGHT_GRAY)
                surface.blit(ab_surf, (inner.x, y))
                y += 18

        # Navigation hint
        nav = f"< {self._cursor + 1}/{len(s.party)} >  [Left/Right] Switch  [Esc] Close"
        hint = fonts.small().render(nav, True, colors.LIGHT_GRAY)
        surface.blit(hint, (panel.centerx - hint.get_width() // 2, panel.bottom + 4))

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state
