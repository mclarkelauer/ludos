"""HUD elements: HP/MP bars, party summary, enemy list."""

from __future__ import annotations

import pygame

from ...content.types import AbilityEffect
from ..state import Character, Enemy
from . import colors, fonts
from .sprites import SpriteCache


def draw_hp_bar(
    surface: pygame.Surface,
    x: int,
    y: int,
    width: int,
    current: int,
    maximum: int,
    height: int = 12,
) -> None:
    """Draw an HP bar."""
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, colors.HP_BG, bg_rect)
    if maximum > 0:
        ratio = max(0, min(1, current / maximum))
        fill_w = int(width * ratio)
        bar_color = colors.HP_GREEN if ratio > 0.3 else colors.HP_RED
        fill_rect = pygame.Rect(x, y, fill_w, height)
        pygame.draw.rect(surface, bar_color, fill_rect)
    pygame.draw.rect(surface, colors.PANEL_BORDER, bg_rect, 1)

    font = fonts.small()
    text = f"{current}/{maximum}"
    text_surf = font.render(text, True, colors.WHITE)
    surface.blit(text_surf, (x + width + 4, y - 1))


def draw_mp_bar(
    surface: pygame.Surface,
    x: int,
    y: int,
    width: int,
    current: int,
    maximum: int,
    height: int = 10,
) -> None:
    """Draw an MP bar."""
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, colors.MP_BG, bg_rect)
    if maximum > 0:
        ratio = max(0, min(1, current / maximum))
        fill_rect = pygame.Rect(x, y, int(width * ratio), height)
        pygame.draw.rect(surface, colors.MP_BLUE, fill_rect)
    pygame.draw.rect(surface, colors.PANEL_BORDER, bg_rect, 1)


def draw_party_summary(
    surface: pygame.Surface,
    rect: pygame.Rect,
    party: list[Character],
) -> None:
    """Draw compact party summary with HP/MP bars."""
    font = fonts.small()
    y = rect.y
    bar_width = min(100, rect.width - 120)

    sprite_offset = 20

    for char in party:
        name_color = colors.DISABLED_COLOR if char.is_dead else colors.WHITE
        class_name = char.char_class.name
        class_color = colors.CLASS_COLORS.get(class_name, colors.WHITE)

        # Mini sprite
        sprite = SpriteCache.get_character_mini(class_name)
        surface.blit(sprite, (rect.x, y))

        # Name + class (shifted right for sprite)
        name_surf = font.render(f"{char.name}", True, name_color)
        surface.blit(name_surf, (rect.x + sprite_offset, y))
        cls_surf = font.render(f"Lv{char.level} {class_name[:3]}", True, class_color)
        surface.blit(cls_surf, (rect.x + sprite_offset + 90, y))

        # HP bar
        y += 22
        draw_hp_bar(surface, rect.x + sprite_offset, y, bar_width, char.current_hp, char.max_hp)
        y += 14
        draw_mp_bar(surface, rect.x + sprite_offset, y, bar_width, char.current_mp, char.max_mp)
        y += 16

        if y > rect.bottom - 20:
            break


def draw_enemy_list(
    surface: pygame.Surface,
    rect: pygame.Rect,
    enemies: list[Enemy],
    target_cursor: int = -1,
) -> None:
    """Draw enemy list with HP bars."""
    font = fonts.small()
    y = rect.y
    bar_width = min(100, rect.width - 100)

    sprite_offset = 20

    for i, enemy in enumerate(enemies):
        if enemy.is_dead:
            color = colors.DISABLED_COLOR
        elif i == target_cursor:
            color = colors.HIGHLIGHT
        else:
            color = colors.ENEMY_COLOR

        # Mini enemy sprite
        sprite = SpriteCache.get_enemy_mini(enemy.enemy_id)
        surface.blit(sprite, (rect.x, y))

        prefix = "> " if i == target_cursor else "  "
        name_surf = font.render(f"{prefix}{enemy.name}", True, color)
        surface.blit(name_surf, (rect.x + sprite_offset, y))
        y += 22

        if not enemy.is_dead:
            draw_hp_bar(surface, rect.x + sprite_offset + 20, y, bar_width, enemy.current_hp, enemy.max_hp)
        y += 16

        if y > rect.bottom - 20:
            break
