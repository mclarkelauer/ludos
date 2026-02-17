"""Generic cursor-based vertical menu renderer."""

from __future__ import annotations

import pygame

from . import colors, fonts


def draw_menu(
    surface: pygame.Surface,
    rect: pygame.Rect,
    items: list[str],
    cursor: int,
    font: pygame.font.Font | None = None,
    text_color: tuple[int, int, int] = colors.WHITE,
    cursor_color: tuple[int, int, int] = colors.CURSOR_COLOR,
    disabled: set[int] | None = None,
) -> None:
    """Draw a vertical menu with cursor highlight."""
    if font is None:
        font = fonts.normal()
    disabled = disabled or set()
    line_h = font.get_linesize() + 4
    y = rect.y

    for i, item in enumerate(items):
        if y + line_h > rect.bottom:
            break
        if i in disabled:
            color = colors.DISABLED_COLOR
        elif i == cursor:
            color = cursor_color
        else:
            color = text_color

        prefix = "> " if i == cursor else "  "
        text_surf = font.render(f"{prefix}{item}", True, color)
        surface.blit(text_surf, (rect.x, y))
        y += line_h
