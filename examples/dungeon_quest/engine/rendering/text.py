"""Text rendering with word-wrap and typewriter effect."""

from __future__ import annotations

import pygame

from . import fonts


def word_wrap(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Split text into lines that fit within max_width."""
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def draw_text(
    surface: pygame.Surface,
    text: str,
    rect: pygame.Rect,
    color: tuple[int, int, int] = (255, 255, 255),
    font: pygame.font.Font | None = None,
    line_spacing: int = 4,
) -> int:
    """Draw word-wrapped text in a rect. Returns y position after last line."""
    if font is None:
        font = fonts.normal()
    lines = word_wrap(text, font, rect.width)
    y = rect.y
    line_h = font.get_linesize()
    for line in lines:
        if y + line_h > rect.bottom:
            break
        rendered = font.render(line, True, color)
        surface.blit(rendered, (rect.x, y))
        y += line_h + line_spacing
    return y


def draw_typewriter(
    surface: pygame.Surface,
    text: str,
    rect: pygame.Rect,
    progress: float,
    color: tuple[int, int, int] = (255, 255, 255),
    font: pygame.font.Font | None = None,
    line_spacing: int = 4,
) -> bool:
    """Draw text with typewriter effect. progress is 0.0-1.0+.

    Returns True if all text is displayed.
    """
    char_count = int(progress * len(text))
    visible = text[:char_count]
    done = char_count >= len(text)
    draw_text(surface, visible, rect, color, font, line_spacing)
    return done
