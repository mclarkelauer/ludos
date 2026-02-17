"""Combat screen layout and rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..state import CombatState, Character
from .layout import Layout
from . import colors, fonts, panels, text as text_mod
from .hud import draw_party_summary, draw_enemy_list
from .menu_renderer import draw_menu
from .sprites import SpriteCache

if TYPE_CHECKING:
    from .effects import EffectManager


def draw_combat_screen(
    surface: pygame.Surface,
    layout: Layout,
    combat: CombatState,
    party: list[Character],
    action_items: list[str] | None = None,
    action_cursor: int = 0,
    sub_items: list[str] | None = None,
    sub_cursor: int = 0,
    show_targets: bool = False,
    effects: EffectManager | None = None,
) -> None:
    """Draw the full combat screen."""
    # Party panel
    party_rect = layout.combat_party()
    inner = panels.draw_panel(surface, party_rect, title="Party")
    draw_party_summary(surface, inner, party)

    # Enemy panel
    enemy_rect = layout.combat_enemies()
    inner = panels.draw_panel(surface, enemy_rect, title="Enemies")
    target_cursor = combat.target_cursor if show_targets else -1
    draw_enemy_list(surface, inner, combat.enemies, target_cursor)

    # Combat arena (center area between party/enemy panels and log)
    _draw_combat_arena(surface, layout, combat, party)

    # Combat log
    log_rect = layout.combat_log()
    inner = panels.draw_panel(surface, log_rect, title="Battle")
    font = fonts.small()
    y = inner.y
    # Show last N lines that fit
    line_h = font.get_linesize() + 2
    max_lines = inner.height // line_h
    visible_log = combat.combat_log[-max_lines:]
    for line in visible_log:
        if y + line_h > inner.bottom:
            break
        line_surf = font.render(line, True, colors.LIGHT_GRAY)
        surface.blit(line_surf, (inner.x, y))
        y += line_h

    # Action menu
    if action_items:
        action_rect = layout.combat_actions()
        inner = panels.draw_panel(surface, action_rect, title="Actions")
        draw_menu(surface, inner, action_items, action_cursor)

    # Sub-menu (abilities, items, targets)
    if sub_items:
        info_rect = layout.combat_info()
        inner = panels.draw_panel(surface, info_rect)
        draw_menu(surface, inner, sub_items, sub_cursor)

    # Render effects last (on top of everything)
    if effects:
        effects.render(surface)


def _draw_combat_arena(
    surface: pygame.Surface,
    layout: Layout,
    combat: CombatState,
    party: list[Character],
) -> None:
    """Draw character and enemy sprites facing each other in the arena area."""
    # Arena spans the full width, sits between the top panels and the log
    top_y = layout.height // 3
    log_top = layout.height // 3
    # Use the combat log area as the arena background (overlay sprites on it)
    arena_rect = pygame.Rect(8, top_y, layout.width - 16, log_top)

    if arena_rect.height < 40:
        return

    # Draw party characters on the left side
    alive_party = [c for c in party if not c.is_dead]
    party_x_start = arena_rect.x + 20
    party_spacing = min(70, (arena_rect.width // 3) // max(1, len(alive_party)))

    for i, char in enumerate(alive_party):
        sprite = SpriteCache.get_character_large(char.char_class.name)
        x = party_x_start + i * party_spacing
        y = arena_rect.y + (arena_rect.height - sprite.get_height()) // 2
        surface.blit(sprite, (x, y))

    # Draw enemies on the right side (facing left = flipped)
    alive_enemies = [e for e in combat.enemies if not e.is_dead]
    enemy_x_end = arena_rect.right - 20
    enemy_spacing = min(70, (arena_rect.width // 3) // max(1, len(alive_enemies)))

    for i, enemy in enumerate(alive_enemies):
        sprite = SpriteCache.get_enemy_large(enemy.enemy_id)
        # Flip horizontally so they face the party
        flipped = pygame.transform.flip(sprite, True, False)
        x = enemy_x_end - (i + 1) * enemy_spacing
        y = arena_rect.y + (arena_rect.height - flipped.get_height()) // 2
        surface.blit(flipped, (x, y))
