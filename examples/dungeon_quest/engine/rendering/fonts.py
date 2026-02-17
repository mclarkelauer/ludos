"""Font cache with lazy loading."""

from __future__ import annotations

import pygame

_cache: dict[tuple[str | None, int], pygame.font.Font] = {}


def get_font(size: int, name: str | None = None) -> pygame.font.Font:
    """Get a cached font. Uses pygame's default font if name is None."""
    key = (name, size)
    if key not in _cache:
        _cache[key] = pygame.font.SysFont(name, size)
    return _cache[key]


def small() -> pygame.font.Font:
    return get_font(16)


def normal() -> pygame.font.Font:
    return get_font(20)


def large() -> pygame.font.Font:
    return get_font(28)


def title() -> pygame.font.Font:
    return get_font(48)


def clear_cache() -> None:
    _cache.clear()
