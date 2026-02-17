"""Bordered panel drawing."""

from __future__ import annotations

import pygame

from . import colors, fonts


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg: tuple[int, int, int] = colors.PANEL_BG,
    border: tuple[int, int, int] = colors.PANEL_BORDER,
    border_width: int = 2,
    title: str = "",
) -> pygame.Rect:
    """Draw a bordered panel. Returns the inner content Rect."""
    pygame.draw.rect(surface, bg, rect)
    pygame.draw.rect(surface, border, rect, border_width)

    inner = rect.inflate(-8, -8)

    if title:
        font = fonts.small()
        title_surf = font.render(title, True, colors.YELLOW)
        # Draw title bar
        title_rect = pygame.Rect(rect.x, rect.y, rect.width, 24)
        pygame.draw.rect(surface, border, title_rect)
        surface.blit(title_surf, (rect.x + 6, rect.y + 3))
        inner = pygame.Rect(inner.x, inner.y + 20, inner.width, inner.height - 20)

    return inner
