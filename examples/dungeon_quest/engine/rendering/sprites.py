"""Procedural pixel-art sprite generation and caching.

All sprites are generated at runtime using pygame draw calls — no external
image files required.
"""

from __future__ import annotations

import math

import pygame

from . import colors


class SpriteCache:
    """Dict-based cache keyed by (type, name, variant) tuples."""

    _cache: dict[tuple, pygame.Surface] = {}

    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()

    @classmethod
    def _get(cls, key: tuple, factory) -> pygame.Surface:
        if key not in cls._cache:
            cls._cache[key] = factory()
        return cls._cache[key]

    # ------------------------------------------------------------------
    # Tile sprites (24x24)
    # ------------------------------------------------------------------

    @classmethod
    def get_tile(cls, tile_type, dim_level: float = 1.0) -> pygame.Surface:
        """Return a 24x24 tile sprite with quantized dimming."""
        # Quantize dim to 0.1 steps for bounded cache
        dim = round(max(0.3, min(1.0, dim_level)), 1)
        key = ("tile", tile_type.name, dim)
        return cls._get(key, lambda: _make_tile(tile_type, dim))

    # ------------------------------------------------------------------
    # Character sprites
    # ------------------------------------------------------------------

    @classmethod
    def get_character(cls, class_name: str, width: int = 24, height: int = 32, frame: int = 0) -> pygame.Surface:
        """Return a character sprite (idle frame 0 or 1)."""
        key = ("char", class_name, width, height, frame)
        return cls._get(key, lambda: _make_character(class_name, width, height, frame))

    @classmethod
    def get_character_large(cls, class_name: str, frame: int = 0) -> pygame.Surface:
        """48x64 combat-sized character sprite."""
        return cls.get_character(class_name, 48, 64, frame)

    @classmethod
    def get_character_mini(cls, class_name: str) -> pygame.Surface:
        """16x20 HUD-sized character sprite."""
        return cls.get_character(class_name, 16, 20, 0)

    # ------------------------------------------------------------------
    # Enemy sprites
    # ------------------------------------------------------------------

    @classmethod
    def get_enemy(cls, enemy_id: str, width: int = 24, height: int = 32, frame: int = 0) -> pygame.Surface:
        """Return an enemy sprite."""
        key = ("enemy", enemy_id, width, height, frame)
        return cls._get(key, lambda: _make_enemy(enemy_id, width, height, frame))

    @classmethod
    def get_enemy_large(cls, enemy_id: str) -> pygame.Surface:
        """48x64 combat-sized enemy sprite (chief gets 64x80)."""
        if "chief" in enemy_id.lower() or "boss" in enemy_id.lower():
            return cls.get_enemy(enemy_id, 64, 80, 0)
        return cls.get_enemy(enemy_id, 48, 64, 0)

    @classmethod
    def get_enemy_mini(cls, enemy_id: str) -> pygame.Surface:
        """16x20 HUD-sized enemy sprite."""
        return cls.get_enemy(enemy_id, 16, 20, 0)

    # ------------------------------------------------------------------
    # Player dungeon token (16x16)
    # ------------------------------------------------------------------

    @classmethod
    def get_player_token(cls, class_name: str) -> pygame.Surface:
        key = ("token", class_name)
        return cls._get(key, lambda: _make_player_token(class_name))

    # ------------------------------------------------------------------
    # Scene illustrations
    # ------------------------------------------------------------------

    @classmethod
    def get_title_illustration(cls) -> pygame.Surface:
        key = ("scene", "title", 0)
        return cls._get(key, _make_title_illustration)

    @classmethod
    def get_area_vignette(cls, area_id: str, area_name: str = "") -> pygame.Surface:
        key = ("scene", "vignette", area_id)
        return cls._get(key, lambda: _make_area_vignette(area_id, area_name))


# ======================================================================
# Internal sprite generators
# ======================================================================

def _dim(color: tuple[int, ...], d: float) -> tuple[int, ...]:
    """Apply dimming factor to a color."""
    return tuple(int(c * d) for c in color)


def _px(surf: pygame.Surface, x: int, y: int, color: tuple[int, ...]) -> None:
    """Draw a single pixel (safely)."""
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)


def _rect(surf: pygame.Surface, color: tuple[int, ...], x: int, y: int, w: int, h: int) -> None:
    """Draw a filled rect."""
    pygame.draw.rect(surf, color, (x, y, w, h))


# ------------------------------------------------------------------
# Tiles
# ------------------------------------------------------------------

def _make_tile(tile_type, dim: float) -> pygame.Surface:
    from ...content.types import TileType

    s = pygame.Surface((24, 24))
    s.fill((0, 0, 0))

    if tile_type == TileType.FLOOR:
        base = _dim(colors.FLOOR_COLOR, dim)
        s.fill(base)
        dot = _dim((80, 75, 65), dim)
        for dx, dy in [(5, 5), (17, 3), (3, 15), (19, 17), (11, 10), (8, 20), (15, 13)]:
            _px(s, dx, dy, dot)

    elif tile_type == TileType.WALL:
        base = _dim(colors.WALL_COLOR, dim)
        s.fill(base)
        mortar = _dim((70, 60, 50), dim)
        # Horizontal mortar lines
        for y in [6, 12, 18]:
            pygame.draw.line(s, mortar, (0, y), (23, y))
        # Vertical brick offsets
        for y_start, offset in [(0, 0), (6, 6), (12, 0), (18, 6)]:
            for x in range(offset, 24, 12):
                pygame.draw.line(s, mortar, (x, y_start), (x, min(y_start + 6, 23)))

    elif tile_type == TileType.DOOR:
        base = _dim(colors.FLOOR_COLOR, dim)
        s.fill(base)
        wood = _dim(colors.DOOR_COLOR, dim)
        dark_wood = _dim(colors.BROWN, dim)
        # Door planks
        _rect(s, wood, 4, 2, 16, 20)
        # Plank lines
        for x in [8, 12, 16]:
            pygame.draw.line(s, dark_wood, (x, 2), (x, 21))
        # Handle
        handle = _dim(colors.SILVER, dim)
        _rect(s, handle, 15, 10, 2, 3)

    elif tile_type in (TileType.STAIRS_DOWN, TileType.STAIRS_UP):
        base = _dim(colors.FLOOR_COLOR, dim)
        s.fill(base)
        step = _dim(colors.STAIRS_COLOR, dim)
        dark_step = _dim((140, 140, 40), dim)
        going_down = tile_type == TileType.STAIRS_DOWN
        for i in range(5):
            y = 2 + i * 4 if going_down else 18 - i * 4
            w = 20 - i * 3 if going_down else 8 + i * 3
            x = (24 - w) // 2
            _rect(s, step, x, y, w, 3)
            _rect(s, dark_step, x, y + 2, w, 1)

    elif tile_type == TileType.CHEST:
        base = _dim(colors.FLOOR_COLOR, dim)
        s.fill(base)
        chest = _dim(colors.CHEST_COLOR, dim)
        dark_chest = _dim(colors.BROWN, dim)
        # Box body
        _rect(s, chest, 5, 10, 14, 10)
        # Lid
        _rect(s, chest, 4, 7, 16, 4)
        _rect(s, dark_chest, 4, 10, 16, 1)
        # Clasp
        clasp = _dim(colors.SILVER, dim)
        _rect(s, clasp, 10, 8, 4, 4)
        _rect(s, dark_chest, 11, 9, 2, 2)

    elif tile_type == TileType.TRAP:
        base = _dim(colors.FLOOR_COLOR, dim)
        s.fill(base)
        trap = _dim(colors.TRAP_COLOR, dim)
        # Red X
        pygame.draw.line(s, trap, (6, 6), (18, 18), 2)
        pygame.draw.line(s, trap, (18, 6), (6, 18), 2)
        # Corner dots
        for dx, dy in [(6, 6), (18, 6), (6, 18), (18, 18)]:
            _px(s, dx, dy, trap)

    elif tile_type == TileType.NPC:
        base = _dim(colors.FLOOR_COLOR, dim)
        s.fill(base)
        npc = _dim(colors.NPC_COLOR, dim)
        # Green diamond
        pts = [(12, 4), (20, 12), (12, 20), (4, 12)]
        pygame.draw.polygon(s, npc, pts)
        outline = _dim(colors.DARK_GREEN, dim)
        pygame.draw.polygon(s, outline, pts, 1)

    elif tile_type == TileType.ENTRANCE:
        base = _dim(colors.FLOOR_COLOR, dim)
        s.fill(base)
        arch = _dim(colors.ENTRANCE_COLOR, dim)
        dark = _dim((60, 100, 140), dim)
        # Archway
        _rect(s, arch, 4, 4, 4, 18)
        _rect(s, arch, 16, 4, 4, 18)
        _rect(s, arch, 4, 2, 16, 4)
        # Dark interior
        _rect(s, dark, 8, 6, 8, 16)
        # Arch curve
        pygame.draw.arc(s, arch, (4, 0, 16, 12), 0, math.pi, 2)

    else:
        s.fill(_dim(colors.FLOOR_COLOR, dim))

    return s


# ------------------------------------------------------------------
# Characters
# ------------------------------------------------------------------

def _make_character(class_name: str, w: int, h: int, frame: int) -> pygame.Surface:
    """Draw a class-specific character sprite."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)

    # Scale factors relative to 24x32
    sx = w / 24
    sy = h / 32

    # Breathing offset
    body_offset = 1 if frame == 1 else 0

    skin = colors.SKIN_COLOR
    dark_skin = colors.DARK_SKIN
    class_upper = class_name.upper()
    class_color = colors.CLASS_COLORS.get(class_upper, (150, 150, 150))

    # Head
    head_w = max(2, int(8 * sx))
    head_h = max(2, int(8 * sy))
    head_x = (w - head_w) // 2
    head_y = int(2 * sy) + body_offset
    _rect(s, skin, head_x, head_y, head_w, head_h)
    # Eyes
    eye_y = head_y + max(1, int(3 * sy))
    _px(s, head_x + max(1, int(2 * sx)), eye_y, (0, 0, 0))
    _px(s, head_x + head_w - max(1, int(2 * sx)) - 1, eye_y, (0, 0, 0))

    # Body
    body_w = max(2, int(10 * sx))
    body_h = max(2, int(12 * sy))
    body_x = (w - body_w) // 2
    body_y = head_y + head_h
    _rect(s, class_color, body_x, body_y, body_w, body_h)

    # Legs
    leg_w = max(1, int(3 * sx))
    leg_h = max(2, int(8 * sy))
    leg_y = body_y + body_h
    # Left leg
    _rect(s, dark_skin, body_x + max(1, int(1 * sx)), leg_y, leg_w, leg_h)
    # Right leg
    _rect(s, dark_skin, body_x + body_w - leg_w - max(1, int(1 * sx)), leg_y, leg_w, leg_h)

    # Class-specific details
    if class_upper == "WARRIOR":
        _draw_warrior_details(s, w, h, sx, sy, body_x, body_y, body_w, head_y, body_offset)
    elif class_upper == "ROGUE":
        _draw_rogue_details(s, w, h, sx, sy, body_x, body_y, body_w, head_x, head_y, head_w, body_offset)
    elif class_upper == "CLERIC":
        _draw_cleric_details(s, w, h, sx, sy, body_x, body_y, body_w, head_x, head_y, head_w, body_offset)
    elif class_upper == "MAGE":
        _draw_mage_details(s, w, h, sx, sy, body_x, body_y, body_w, head_x, head_y, head_w, body_offset)

    return s


def _draw_warrior_details(s, w, h, sx, sy, body_x, body_y, body_w, head_y, offset):
    """Sword on right + shield on left."""
    silver = colors.SILVER
    brown = colors.BROWN
    # Sword (right side)
    sword_x = body_x + body_w + max(1, int(1 * sx))
    sword_y = body_y + max(1, int(2 * sy)) + offset
    sword_h = max(3, int(10 * sy))
    _rect(s, silver, sword_x, sword_y, max(1, int(2 * sx)), sword_h)
    # Hilt
    _rect(s, brown, sword_x - max(1, int(1 * sx)), sword_y + sword_h, max(2, int(4 * sx)), max(1, int(2 * sy)))
    # Shield (left side)
    shield_x = body_x - max(2, int(4 * sx))
    shield_y = body_y + max(1, int(2 * sy)) + offset
    shield_w = max(2, int(4 * sx))
    shield_h = max(3, int(6 * sy))
    _rect(s, silver, shield_x, shield_y, shield_w, shield_h)
    # Shield cross
    cross_color = colors.CLASS_COLORS.get("WARRIOR", (200, 80, 40))
    cx = shield_x + shield_w // 2
    cy = shield_y + shield_h // 2
    _rect(s, cross_color, cx, shield_y + 1, max(1, int(1 * sx)), shield_h - 2)
    _rect(s, cross_color, shield_x + 1, cy, shield_w - 2, max(1, int(1 * sy)))


def _draw_rogue_details(s, w, h, sx, sy, body_x, body_y, body_w, head_x, head_y, head_w, offset):
    """Hood + dagger + cape."""
    dark = (40, 60, 40)
    # Hood
    hood_w = max(3, int(10 * sx))
    hood_h = max(2, int(4 * sy))
    hood_x = (w - hood_w) // 2
    hood_y = head_y - max(1, int(1 * sy))
    _rect(s, dark, hood_x, hood_y, hood_w, hood_h)
    # Cape
    cape_x = body_x + body_w - max(1, int(1 * sx))
    cape_y = body_y + max(1, int(1 * sy)) + offset
    cape_h = max(3, int(14 * sy))
    _rect(s, dark, cape_x, cape_y, max(2, int(3 * sx)), cape_h)
    # Dagger
    dagger_x = body_x - max(1, int(2 * sx))
    dagger_y = body_y + max(2, int(4 * sy)) + offset
    _rect(s, colors.SILVER, dagger_x, dagger_y, max(1, int(1 * sx)), max(2, int(6 * sy)))


def _draw_cleric_details(s, w, h, sx, sy, body_x, body_y, body_w, head_x, head_y, head_w, offset):
    """Robes bottom + staff + cross."""
    robe = (200, 190, 160)
    # Robe extension
    robe_y = body_y + max(2, int(8 * sy))
    robe_w = max(3, int(12 * sx))
    robe_x = (w - robe_w) // 2
    _rect(s, robe, robe_x, robe_y, robe_w, max(2, int(6 * sy)))
    # Staff (right)
    staff_x = body_x + body_w + max(1, int(2 * sx))
    staff_y = head_y + offset
    _rect(s, colors.BROWN, staff_x, staff_y, max(1, int(1 * sx)), max(5, int(20 * sy)))
    # Cross on staff top
    cross_color = colors.YELLOW
    _rect(s, cross_color, staff_x - max(1, int(1 * sx)), staff_y, max(2, int(3 * sx)), max(1, int(1 * sy)))
    _rect(s, cross_color, staff_x, staff_y - max(1, int(1 * sy)), max(1, int(1 * sx)), max(2, int(3 * sy)))


def _draw_mage_details(s, w, h, sx, sy, body_x, body_y, body_w, head_x, head_y, head_w, offset):
    """Wizard hat + staff + star."""
    hat_color = colors.CLASS_COLORS.get("MAGE", (100, 80, 220))
    # Wizard hat (triangle)
    hat_base_y = head_y
    hat_top_y = hat_base_y - max(3, int(6 * sy))
    hat_cx = w // 2
    hat_w = max(3, int(10 * sx))
    pts = [
        (hat_cx, hat_top_y),
        (hat_cx - hat_w // 2, hat_base_y),
        (hat_cx + hat_w // 2, hat_base_y),
    ]
    pygame.draw.polygon(s, hat_color, pts)
    # Hat brim
    brim_w = max(4, int(12 * sx))
    _rect(s, hat_color, (w - brim_w) // 2, hat_base_y, brim_w, max(1, int(1 * sy)))
    # Staff (left)
    staff_x = body_x - max(1, int(3 * sx))
    staff_y = head_y + offset
    _rect(s, colors.BROWN, staff_x, staff_y, max(1, int(1 * sx)), max(5, int(20 * sy)))
    # Star at staff top
    star_color = colors.TORCH_YELLOW
    star_x = staff_x
    star_y = staff_y - max(1, int(2 * sy))
    _px(s, star_x, star_y, star_color)
    _px(s, star_x - 1, star_y, star_color)
    _px(s, star_x + 1, star_y, star_color)
    _px(s, star_x, star_y - 1, star_color)
    _px(s, star_x, star_y + 1, star_color)


# ------------------------------------------------------------------
# Enemies
# ------------------------------------------------------------------

def _make_enemy(enemy_id: str, w: int, h: int, frame: int) -> pygame.Surface:
    """Draw an enemy sprite based on enemy_id keywords."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    eid = enemy_id.lower()

    if "bat" in eid:
        _draw_bat(s, w, h, frame)
    elif "spider" in eid:
        _draw_spider(s, w, h, frame)
    elif "chief" in eid or "boss" in eid:
        _draw_goblin_chief(s, w, h, frame)
    elif "shaman" in eid:
        _draw_goblin_shaman(s, w, h, frame)
    elif "archer" in eid:
        _draw_goblin_archer(s, w, h, frame)
    elif "goblin" in eid:
        _draw_goblin(s, w, h, frame)
    else:
        # Generic enemy - red-tinted humanoid
        _draw_generic_enemy(s, w, h, frame)

    return s


def _draw_goblin(s, w, h, frame):
    sx, sy = w / 24, h / 32
    g = colors.GOBLIN_GREEN
    dark_g = (50, 100, 30)
    offset = 1 if frame == 1 else 0

    # Head
    head_w, head_h = max(2, int(8 * sx)), max(2, int(7 * sy))
    head_x = (w - head_w) // 2
    head_y = int(4 * sy) + offset
    _rect(s, g, head_x, head_y, head_w, head_h)
    # Pointy ears
    _rect(s, g, head_x - max(1, int(2 * sx)), head_y + max(1, int(1 * sy)), max(1, int(2 * sx)), max(1, int(3 * sy)))
    _rect(s, g, head_x + head_w, head_y + max(1, int(1 * sy)), max(1, int(2 * sx)), max(1, int(3 * sy)))
    # Eyes (red)
    eye_y = head_y + max(1, int(2 * sy))
    _px(s, head_x + max(1, int(2 * sx)), eye_y, (255, 0, 0))
    _px(s, head_x + head_w - max(1, int(2 * sx)) - 1, eye_y, (255, 0, 0))
    # Body
    body_w = max(2, int(8 * sx))
    body_h = max(2, int(10 * sy))
    body_x = (w - body_w) // 2
    body_y = head_y + head_h
    _rect(s, dark_g, body_x, body_y, body_w, body_h)
    # Legs
    leg_y = body_y + body_h
    _rect(s, g, body_x + 1, leg_y, max(1, int(2 * sx)), max(2, int(6 * sy)))
    _rect(s, g, body_x + body_w - max(1, int(2 * sx)) - 1, leg_y, max(1, int(2 * sx)), max(2, int(6 * sy)))
    # Club
    brown = colors.BROWN
    club_x = body_x + body_w + max(1, int(1 * sx))
    club_y = body_y + offset
    _rect(s, brown, club_x, club_y, max(1, int(2 * sx)), max(3, int(8 * sy)))
    _rect(s, brown, club_x - 1, club_y, max(2, int(4 * sx)), max(2, int(3 * sy)))


def _draw_goblin_archer(s, w, h, frame):
    sx, sy = w / 24, h / 32
    g = colors.GOBLIN_GREEN
    dark_g = (50, 100, 30)
    offset = 1 if frame == 1 else 0

    # Same base as goblin
    head_w, head_h = max(2, int(8 * sx)), max(2, int(7 * sy))
    head_x = (w - head_w) // 2
    head_y = int(4 * sy) + offset
    _rect(s, g, head_x, head_y, head_w, head_h)
    _rect(s, g, head_x - max(1, int(2 * sx)), head_y + max(1, int(1 * sy)), max(1, int(2 * sx)), max(1, int(3 * sy)))
    _rect(s, g, head_x + head_w, head_y + max(1, int(1 * sy)), max(1, int(2 * sx)), max(1, int(3 * sy)))
    eye_y = head_y + max(1, int(2 * sy))
    _px(s, head_x + max(1, int(2 * sx)), eye_y, (255, 0, 0))
    _px(s, head_x + head_w - max(1, int(2 * sx)) - 1, eye_y, (255, 0, 0))
    body_w = max(2, int(8 * sx))
    body_h = max(2, int(10 * sy))
    body_x = (w - body_w) // 2
    body_y = head_y + head_h
    _rect(s, dark_g, body_x, body_y, body_w, body_h)
    leg_y = body_y + body_h
    _rect(s, g, body_x + 1, leg_y, max(1, int(2 * sx)), max(2, int(6 * sy)))
    _rect(s, g, body_x + body_w - max(1, int(2 * sx)) - 1, leg_y, max(1, int(2 * sx)), max(2, int(6 * sy)))
    # Bow (arc on left)
    bow_color = colors.BROWN
    bow_x = body_x - max(2, int(4 * sx))
    bow_y = body_y + offset
    bow_h = max(4, int(10 * sy))
    pygame.draw.arc(s, bow_color, (bow_x, bow_y, max(2, int(4 * sx)), bow_h), -1.2, 1.2, 2)
    # Bowstring
    pygame.draw.line(s, colors.LIGHT_GRAY, (bow_x + max(1, int(2 * sx)), bow_y), (bow_x + max(1, int(2 * sx)), bow_y + bow_h), 1)


def _draw_goblin_shaman(s, w, h, frame):
    sx, sy = w / 24, h / 32
    g = colors.GOBLIN_GREEN
    offset = 1 if frame == 1 else 0

    head_w, head_h = max(2, int(8 * sx)), max(2, int(7 * sy))
    head_x = (w - head_w) // 2
    head_y = int(4 * sy) + offset
    _rect(s, g, head_x, head_y, head_w, head_h)
    _rect(s, g, head_x - max(1, int(2 * sx)), head_y + max(1, int(1 * sy)), max(1, int(2 * sx)), max(1, int(3 * sy)))
    _rect(s, g, head_x + head_w, head_y + max(1, int(1 * sy)), max(1, int(2 * sx)), max(1, int(3 * sy)))
    # Headdress (feathers)
    feather = (200, 60, 60)
    _rect(s, feather, head_x, head_y - max(2, int(3 * sy)), head_w, max(2, int(3 * sy)))
    _rect(s, colors.YELLOW, head_x + 1, head_y - max(1, int(2 * sy)), max(1, int(2 * sx)), max(1, int(2 * sy)))
    # Purple eyes
    eye_y = head_y + max(1, int(2 * sy))
    _px(s, head_x + max(1, int(2 * sx)), eye_y, (200, 0, 200))
    _px(s, head_x + head_w - max(1, int(2 * sx)) - 1, eye_y, (200, 0, 200))
    # Robe body
    body_w = max(2, int(10 * sx))
    body_h = max(2, int(14 * sy))
    body_x = (w - body_w) // 2
    body_y = head_y + head_h
    _rect(s, (80, 40, 120), body_x, body_y, body_w, body_h)
    # Orb (floating)
    orb_x = body_x + body_w + max(1, int(2 * sx))
    orb_y = body_y + max(1, int(2 * sy)) + offset
    orb_r = max(2, int(3 * sx))
    pygame.draw.circle(s, (160, 60, 220), (orb_x, orb_y), orb_r)
    pygame.draw.circle(s, (220, 140, 255), (orb_x - 1, orb_y - 1), max(1, orb_r // 2))


def _draw_bat(s, w, h, frame):
    sx, sy = w / 20, h / 16
    body_color = (60, 40, 60)
    wing_color = (80, 50, 80)

    cx, cy = w // 2, h // 2
    # Body (small oval)
    body_w = max(2, int(6 * sx))
    body_h = max(2, int(6 * sy))
    pygame.draw.ellipse(s, body_color, (cx - body_w // 2, cy - body_h // 2, body_w, body_h))
    # Eyes
    _px(s, cx - max(1, int(1 * sx)), cy - max(1, int(1 * sy)), (255, 0, 0))
    _px(s, cx + max(1, int(1 * sx)), cy - max(1, int(1 * sy)), (255, 0, 0))
    # Wings
    wing_spread = max(3, int(6 * sx)) + (1 if frame == 1 else 0)
    # Left wing
    pts_l = [(cx - 2, cy), (cx - 2 - wing_spread, cy - max(2, int(4 * sy))), (cx - 2 - wing_spread, cy + 1)]
    pygame.draw.polygon(s, wing_color, pts_l)
    # Right wing
    pts_r = [(cx + 2, cy), (cx + 2 + wing_spread, cy - max(2, int(4 * sy))), (cx + 2 + wing_spread, cy + 1)]
    pygame.draw.polygon(s, wing_color, pts_r)


def _draw_spider(s, w, h, frame):
    sx, sy = w / 24, h / 16
    body_color = colors.SPIDER_BROWN
    dark = (60, 40, 20)

    cx, cy = w // 2, h // 2
    # Body (oval)
    body_w = max(3, int(10 * sx))
    body_h = max(2, int(6 * sy))
    pygame.draw.ellipse(s, body_color, (cx - body_w // 2, cy - body_h // 2, body_w, body_h))
    # Head (smaller oval)
    head_w = max(2, int(5 * sx))
    head_h = max(2, int(4 * sy))
    pygame.draw.ellipse(s, body_color, (cx - head_w // 2, cy - body_h // 2 - head_h + 1, head_w, head_h))
    # Eyes (cluster)
    eye_y = cy - body_h // 2 - head_h // 2
    for dx in [-1, 0, 1]:
        _px(s, cx + dx, eye_y, (255, 0, 0))
    # 8 legs (4 per side)
    leg_color = dark
    for i in range(4):
        angle_l = 0.4 + i * 0.4
        angle_r = math.pi - 0.4 - i * 0.4
        leg_len = max(3, int(6 * sx))
        for angle, side in [(angle_l, -1), (angle_r, 1)]:
            lx = cx + int(math.cos(angle) * leg_len * side)
            ly = cy + int(math.sin(angle) * leg_len)
            pygame.draw.line(s, leg_color, (cx + side * (body_w // 4), cy), (lx, ly), 1)


def _draw_goblin_chief(s, w, h, frame):
    """Bigger goblin with crown and axe."""
    sx, sy = w / 32, h / 40
    g = colors.GOBLIN_GREEN
    dark_g = (50, 100, 30)
    offset = 1 if frame == 1 else 0

    # Head (bigger)
    head_w, head_h = max(3, int(12 * sx)), max(3, int(10 * sy))
    head_x = (w - head_w) // 2
    head_y = int(6 * sy) + offset
    _rect(s, g, head_x, head_y, head_w, head_h)
    # Ears
    _rect(s, g, head_x - max(1, int(3 * sx)), head_y + max(1, int(2 * sy)), max(1, int(3 * sx)), max(1, int(4 * sy)))
    _rect(s, g, head_x + head_w, head_y + max(1, int(2 * sy)), max(1, int(3 * sx)), max(1, int(4 * sy)))
    # Crown
    crown = colors.YELLOW
    crown_y = head_y - max(2, int(4 * sy))
    _rect(s, crown, head_x + 1, crown_y, head_w - 2, max(2, int(4 * sy)))
    # Crown spikes
    for dx in [head_x + 2, head_x + head_w // 2, head_x + head_w - 3]:
        _rect(s, crown, dx, crown_y - max(1, int(2 * sy)), max(1, int(2 * sx)), max(1, int(2 * sy)))
    # Red eyes
    eye_y = head_y + max(1, int(3 * sy))
    for dx in [head_x + max(1, int(3 * sx)), head_x + head_w - max(1, int(3 * sx)) - 1]:
        _px(s, dx, eye_y, (255, 0, 0))
        _px(s, dx, eye_y + 1, (255, 0, 0))
    # Body (armored)
    body_w = max(3, int(14 * sx))
    body_h = max(3, int(14 * sy))
    body_x = (w - body_w) // 2
    body_y = head_y + head_h
    _rect(s, dark_g, body_x, body_y, body_w, body_h)
    _rect(s, colors.SILVER, body_x + 1, body_y + 1, body_w - 2, body_h - 2)  # armor
    _rect(s, dark_g, body_x + 2, body_y + 2, body_w - 4, body_h - 4)
    # Legs
    leg_y = body_y + body_h
    _rect(s, g, body_x + 2, leg_y, max(1, int(3 * sx)), max(2, int(8 * sy)))
    _rect(s, g, body_x + body_w - max(1, int(3 * sx)) - 2, leg_y, max(1, int(3 * sx)), max(2, int(8 * sy)))
    # Axe (right side)
    axe_x = body_x + body_w + max(1, int(1 * sx))
    axe_y = head_y + offset
    _rect(s, colors.BROWN, axe_x, axe_y, max(1, int(2 * sx)), max(5, int(18 * sy)))
    # Axe head
    _rect(s, colors.SILVER, axe_x - max(1, int(2 * sx)), axe_y, max(3, int(6 * sx)), max(2, int(5 * sy)))


def _draw_generic_enemy(s, w, h, frame):
    """Fallback red-tinted humanoid."""
    sx, sy = w / 24, h / 32
    skin = (180, 80, 80)
    dark = (140, 50, 50)
    offset = 1 if frame == 1 else 0

    head_w, head_h = max(2, int(8 * sx)), max(2, int(8 * sy))
    head_x = (w - head_w) // 2
    head_y = int(2 * sy) + offset
    _rect(s, skin, head_x, head_y, head_w, head_h)
    eye_y = head_y + max(1, int(3 * sy))
    _px(s, head_x + max(1, int(2 * sx)), eye_y, (255, 0, 0))
    _px(s, head_x + head_w - max(1, int(2 * sx)) - 1, eye_y, (255, 0, 0))
    body_w = max(2, int(10 * sx))
    body_h = max(2, int(12 * sy))
    body_x = (w - body_w) // 2
    body_y = head_y + head_h
    _rect(s, dark, body_x, body_y, body_w, body_h)
    leg_y = body_y + body_h
    _rect(s, skin, body_x + 1, leg_y, max(1, int(3 * sx)), max(2, int(8 * sy)))
    _rect(s, skin, body_x + body_w - max(1, int(3 * sx)) - 1, leg_y, max(1, int(3 * sx)), max(2, int(8 * sy)))


# ------------------------------------------------------------------
# Player token (16x16)
# ------------------------------------------------------------------

def _make_player_token(class_name: str) -> pygame.Surface:
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    class_color = colors.CLASS_COLORS.get(class_name.upper(), colors.PLAYER_COLOR)
    # Simple outlined character silhouette
    _rect(s, class_color, 5, 1, 6, 5)  # head
    _rect(s, class_color, 3, 6, 10, 6)  # body
    _rect(s, class_color, 4, 12, 3, 4)  # left leg
    _rect(s, class_color, 9, 12, 3, 4)  # right leg
    # Outline
    pygame.draw.rect(s, (255, 255, 255), (3, 1, 10, 15), 1)
    return s


# ------------------------------------------------------------------
# Scene illustrations
# ------------------------------------------------------------------

def _make_title_illustration() -> pygame.Surface:
    """300x200 dungeon archway illustration."""
    s = pygame.Surface((300, 200), pygame.SRCALPHA)

    # Dark stone background
    s.fill((15, 12, 20))

    # Stone wall
    wall = (60, 55, 65)
    _rect(s, wall, 0, 0, 300, 200)

    # Archway opening (dark)
    dark = (5, 3, 10)
    # Arch pillars
    pillar = (80, 70, 90)
    pillar_w = 40
    _rect(s, pillar, 60, 40, pillar_w, 160)
    _rect(s, pillar, 200, 40, pillar_w, 160)
    # Arch top
    pygame.draw.arc(s, pillar, (60, 10, 180, 80), 0, math.pi, 6)
    # Dark interior
    _rect(s, dark, 100, 50, 100, 150)
    pygame.draw.ellipse(s, dark, (70, 10, 160, 80))

    # Stone texture on walls
    mortar = (50, 45, 55)
    for y in range(0, 200, 20):
        pygame.draw.line(s, mortar, (0, y), (60, y))
        pygame.draw.line(s, mortar, (240, y), (300, y))
    for x in range(0, 60, 30):
        for y in range(0, 200, 20):
            pygame.draw.line(s, mortar, (x, y), (x, y + 20))
    for x in range(240, 300, 30):
        for y in range(0, 200, 20):
            pygame.draw.line(s, mortar, (x, y), (x, y + 20))

    # Torches
    for tx in [75, 225]:
        # Bracket
        _rect(s, (100, 80, 60), tx - 2, 60, 4, 12)
        # Flame
        pygame.draw.circle(s, colors.TORCH_ORANGE, (tx, 55), 6)
        pygame.draw.circle(s, colors.TORCH_YELLOW, (tx, 53), 3)

    # Steps leading in
    step_color = (70, 65, 75)
    for i in range(4):
        y = 180 - i * 8
        w = 120 - i * 10
        x = (300 - w) // 2
        _rect(s, step_color, x, y, w, 8)
        _rect(s, mortar, x, y + 7, w, 1)

    return s


def _make_area_vignette(area_id: str, area_name: str = "") -> pygame.Surface:
    """400x100 area-themed vignette illustration."""
    s = pygame.Surface((400, 100), pygame.SRCALPHA)
    combined = (area_id + " " + area_name).lower()

    if "village" in combined or "town" in combined or "hamlet" in combined:
        _draw_village_vignette(s)
    elif "forest" in combined or "wood" in combined:
        _draw_forest_vignette(s)
    elif "cave" in combined or "dungeon" in combined or "lair" in combined:
        _draw_cave_vignette(s)
    elif "temple" in combined or "shrine" in combined or "church" in combined:
        _draw_temple_vignette(s)
    else:
        _draw_default_vignette(s)

    return s


def _draw_village_vignette(s):
    """Houses with roofs."""
    s.fill((20, 25, 40))
    # Sky gradient
    for y in range(40):
        c = 20 + y
        pygame.draw.line(s, (c // 2, c // 2, c), (0, y), (400, y))
    # Ground
    _rect(s, (40, 60, 30), 0, 70, 400, 30)
    # Houses
    for hx, hw, hh in [(60, 50, 35), (160, 60, 40), (270, 45, 30), (340, 55, 38)]:
        hy = 70 - hh
        # Wall
        _rect(s, (140, 120, 90), hx, hy, hw, hh)
        # Roof
        pts = [(hx - 5, hy), (hx + hw + 5, hy), (hx + hw // 2, hy - 20)]
        pygame.draw.polygon(s, (160, 60, 40), pts)
        # Door
        _rect(s, (80, 50, 30), hx + hw // 2 - 5, hy + hh - 15, 10, 15)
        # Window
        _rect(s, (200, 200, 100), hx + 8, hy + 8, 8, 8)
    # Path
    _rect(s, (100, 85, 60), 120, 80, 160, 20)


def _draw_forest_vignette(s):
    """Trees and foliage."""
    s.fill((10, 20, 15))
    # Ground
    _rect(s, (30, 50, 25), 0, 75, 400, 25)
    # Trees
    trunk = (80, 50, 30)
    for tx, th in [(40, 55), (100, 65), (170, 50), (230, 60), (290, 55), (350, 45)]:
        ty = 75 - th
        # Trunk
        _rect(s, trunk, tx - 3, ty + th - 20, 6, 20)
        # Canopy (layered triangles)
        for i in range(3):
            w = 30 - i * 6
            y_off = ty + i * 12
            pts = [(tx, y_off), (tx - w // 2, y_off + 18), (tx + w // 2, y_off + 18)]
            green = (20 + i * 15, 80 + i * 20, 20 + i * 10)
            pygame.draw.polygon(s, green, pts)


def _draw_cave_vignette(s):
    """Dark cave archway."""
    s.fill((15, 12, 18))
    # Cave walls
    wall = (50, 45, 55)
    _rect(s, wall, 0, 0, 400, 100)
    # Cave opening
    dark = (5, 3, 8)
    pygame.draw.ellipse(s, dark, (100, 10, 200, 90))
    # Stalactites
    for sx_pos in range(120, 300, 25):
        h = 10 + (sx_pos * 7) % 20
        pygame.draw.polygon(s, wall, [(sx_pos, 10), (sx_pos - 4, 10 + h), (sx_pos + 4, 10 + h)])
    # Torch
    _rect(s, (100, 80, 60), 88, 30, 4, 12)
    pygame.draw.circle(s, colors.TORCH_ORANGE, (90, 26), 6)
    pygame.draw.circle(s, colors.TORCH_YELLOW, (90, 24), 3)


def _draw_temple_vignette(s):
    """Temple/shrine pillars."""
    s.fill((20, 18, 30))
    # Floor
    _rect(s, (60, 55, 70), 0, 80, 400, 20)
    # Pillars
    pillar = (150, 140, 160)
    for px in [80, 160, 240, 320]:
        _rect(s, pillar, px - 8, 15, 16, 65)
        _rect(s, (170, 160, 180), px - 10, 10, 20, 8)
        _rect(s, (170, 160, 180), px - 10, 75, 20, 8)
    # Roof
    _rect(s, (100, 90, 110), 60, 5, 280, 10)
    # Altar
    _rect(s, (120, 100, 80), 180, 55, 40, 25)
    # Golden cross
    pygame.draw.line(s, colors.YELLOW, (200, 40), (200, 55), 2)
    pygame.draw.line(s, colors.YELLOW, (193, 47), (207, 47), 2)


def _draw_default_vignette(s):
    """Generic landscape."""
    s.fill((15, 20, 35))
    # Hills
    for hx, hw, hh in [(0, 200, 30), (150, 250, 25), (300, 200, 35)]:
        pygame.draw.ellipse(s, (30, 50, 30), (hx, 70 - hh, hw, hh * 2))
    # Ground
    _rect(s, (35, 55, 30), 0, 75, 400, 25)
    # Path
    _rect(s, (80, 70, 50), 170, 78, 60, 22)
