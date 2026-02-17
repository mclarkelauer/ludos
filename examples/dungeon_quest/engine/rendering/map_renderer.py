"""Dungeon tile grid and overworld node rendering."""

from __future__ import annotations

import pygame

from ...content.types import TileType
from . import colors, fonts
from .sprites import SpriteCache

TILE_SIZE = 24

TILE_COLORS: dict[TileType, tuple[int, int, int]] = {
    TileType.FLOOR: colors.FLOOR_COLOR,
    TileType.WALL: colors.WALL_COLOR,
    TileType.DOOR: colors.DOOR_COLOR,
    TileType.STAIRS_DOWN: colors.STAIRS_COLOR,
    TileType.STAIRS_UP: colors.STAIRS_COLOR,
    TileType.CHEST: colors.CHEST_COLOR,
    TileType.TRAP: colors.TRAP_COLOR,
    TileType.NPC: colors.NPC_COLOR,
    TileType.ENTRANCE: colors.ENTRANCE_COLOR,
}

TILE_SYMBOLS: dict[TileType, str] = {
    TileType.STAIRS_DOWN: "v",
    TileType.STAIRS_UP: "^",
    TileType.CHEST: "$",
    TileType.TRAP: "!",
    TileType.NPC: "?",
    TileType.DOOR: "+",
    TileType.ENTRANCE: "E",
}


def draw_dungeon(
    surface: pygame.Surface,
    rect: pygame.Rect,
    tiles: tuple[tuple[TileType, ...], ...],
    player_x: int,
    player_y: int,
    view_radius: int = 8,
    player_class: str = "",
) -> None:
    """Draw the dungeon tile grid centered on the player."""
    map_height = len(tiles)
    map_width = len(tiles[0]) if tiles else 0

    # Calculate viewport offset to center on player
    tiles_x = rect.width // TILE_SIZE
    tiles_y = rect.height // TILE_SIZE
    offset_x = player_x - tiles_x // 2
    offset_y = player_y - tiles_y // 2

    for sy in range(tiles_y):
        for sx in range(tiles_x):
            mx = offset_x + sx
            my = offset_y + sy

            px = rect.x + sx * TILE_SIZE
            py = rect.y + sy * TILE_SIZE
            tile_rect = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)

            if mx < 0 or my < 0 or mx >= map_width or my >= map_height:
                pygame.draw.rect(surface, colors.BLACK, tile_rect)
                continue

            tile = tiles[my][mx]
            dist = abs(mx - player_x) + abs(my - player_y)

            if dist > view_radius:
                pygame.draw.rect(surface, colors.FOG_COLOR, tile_rect)
                continue

            # Distance-based dimming (quantized to 0.1 steps)
            dim = max(0.3, 1.0 - dist / (view_radius + 1))
            dim = round(dim, 1)
            tile_sprite = SpriteCache.get_tile(tile, dim)
            surface.blit(tile_sprite, (px, py))

            # Player marker
            if mx == player_x and my == player_y:
                if player_class:
                    token = SpriteCache.get_player_token(player_class)
                    token_rect = token.get_rect(center=tile_rect.center)
                    surface.blit(token, token_rect)
                else:
                    player_inner = pygame.Rect(px + 4, py + 4, TILE_SIZE - 8, TILE_SIZE - 8)
                    pygame.draw.rect(surface, colors.PLAYER_COLOR, player_inner)

    # Grid lines (subtle)
    for sx in range(tiles_x + 1):
        x = rect.x + sx * TILE_SIZE
        pygame.draw.line(surface, (40, 40, 50), (x, rect.y), (x, rect.y + tiles_y * TILE_SIZE))
    for sy in range(tiles_y + 1):
        y = rect.y + sy * TILE_SIZE
        pygame.draw.line(surface, (40, 40, 50), (rect.x, y), (rect.x + tiles_x * TILE_SIZE, y))
