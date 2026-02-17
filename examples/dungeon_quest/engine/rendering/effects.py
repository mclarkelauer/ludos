"""Combat visual effects — particles, flashes, floating numbers.

All effects are self-contained: they update over time and render onto a
surface, returning False from update() when they expire.
"""

from __future__ import annotations

import math
import random

import pygame

from . import colors, fonts


# ======================================================================
# Base
# ======================================================================

class Effect:
    """Base class for timed visual effects."""

    def update(self, dt: float) -> bool:
        """Advance the effect. Return True while alive, False when done."""
        return False

    def render(self, surface: pygame.Surface) -> None:
        """Draw the effect onto *surface*."""


class EffectManager:
    """Manages a list of active effects, ticking and rendering them."""

    def __init__(self) -> None:
        self._effects: list[Effect] = []

    def add(self, effect: Effect) -> None:
        self._effects.append(effect)

    def update(self, dt: float) -> None:
        self._effects = [e for e in self._effects if e.update(dt)]

    def render(self, surface: pygame.Surface) -> None:
        for e in self._effects:
            e.render(surface)

    @property
    def active(self) -> bool:
        return len(self._effects) > 0


# ======================================================================
# Damage numbers
# ======================================================================

class DamageNumberEffect(Effect):
    """Floating damage/heal number that rises and fades out."""

    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        color: tuple[int, int, int] = colors.DAMAGE_COLOR,
        duration: float = 1.0,
    ) -> None:
        self._x = float(x)
        self._y = float(y)
        self._text = text
        self._color = color
        self._duration = duration
        self._elapsed = 0.0
        self._font = fonts.normal()

    def update(self, dt: float) -> bool:
        self._elapsed += dt
        self._y -= 40 * dt  # float upward
        return self._elapsed < self._duration

    def render(self, surface: pygame.Surface) -> None:
        progress = self._elapsed / self._duration
        alpha = max(0, int(255 * (1.0 - progress)))
        txt_surf = self._font.render(self._text, True, self._color)
        alpha_surf = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(txt_surf, (0, 0))
        alpha_surf.set_alpha(alpha)
        surface.blit(alpha_surf, (int(self._x) - txt_surf.get_width() // 2, int(self._y)))


# ======================================================================
# Slash (physical attack)
# ======================================================================

class SlashEffect(Effect):
    """White arc lines sweeping across target area."""

    def __init__(self, x: int, y: int, width: int = 60, height: int = 60) -> None:
        self._x = x
        self._y = y
        self._w = width
        self._h = height
        self._duration = 0.3
        self._elapsed = 0.0

    def update(self, dt: float) -> bool:
        self._elapsed += dt
        return self._elapsed < self._duration

    def render(self, surface: pygame.Surface) -> None:
        progress = min(1.0, self._elapsed / self._duration)
        alpha = max(0, int(255 * (1.0 - progress * 0.7)))

        slash_surf = pygame.Surface((self._w, self._h), pygame.SRCALPHA)

        # Draw 2-3 arc lines at different sweep positions
        for i in range(3):
            sweep = progress * 1.2 - i * 0.15
            if sweep < 0 or sweep > 1:
                continue
            cx = int(self._w * 0.3)
            cy = int(self._h * 0.5)
            radius = int(self._w * 0.4)
            start_angle = math.pi * 0.2 + sweep * math.pi * 0.6
            end_angle = start_angle + 0.5
            arc_rect = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
            color = (255, 255, 255, alpha)
            pygame.draw.arc(slash_surf, color, arc_rect, start_angle, end_angle, 2)

        surface.blit(slash_surf, (self._x - self._w // 2, self._y - self._h // 2))


# ======================================================================
# Spell effects (per DamageType)
# ======================================================================

class SpellEffect(Effect):
    """Spell particles based on damage type."""

    def __init__(self, x: int, y: int, damage_type: str = "FIRE") -> None:
        self._x = x
        self._y = y
        self._type = damage_type.upper()
        self._duration = 0.5
        self._elapsed = 0.0
        # Generate particles
        self._particles: list[dict] = []
        for _ in range(12):
            self._particles.append({
                "ox": random.randint(-20, 20),
                "oy": random.randint(-20, 20),
                "vx": random.uniform(-30, 30),
                "vy": random.uniform(-60, -10),
                "size": random.randint(2, 5),
                "life": random.uniform(0.3, 0.5),
            })

    def update(self, dt: float) -> bool:
        self._elapsed += dt
        for p in self._particles:
            p["ox"] += p["vx"] * dt
            p["oy"] += p["vy"] * dt
        return self._elapsed < self._duration

    def render(self, surface: pygame.Surface) -> None:
        progress = self._elapsed / self._duration

        for p in self._particles:
            if self._elapsed > p["life"]:
                continue
            alpha = max(0, int(255 * (1.0 - self._elapsed / p["life"])))
            px = int(self._x + p["ox"])
            py = int(self._y + p["oy"])
            size = p["size"]

            if self._type == "FIRE":
                color = (240, 120 + random.randint(0, 40), 20, alpha)
                pygame.draw.circle(surface, color[:3], (px, py), size)
            elif self._type == "ICE":
                color = (100, 180, 255)
                # Diamond shape
                pts = [(px, py - size), (px + size, py), (px, py + size), (px - size, py)]
                s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
                offset_pts = [(size, 0), (size * 2, size), (size, size * 2), (0, size)]
                pygame.draw.polygon(s, (*color, alpha), offset_pts)
                surface.blit(s, (px - size, py - size))
            elif self._type == "HOLY":
                color = (255, 220, 50)
                # Golden ring expanding
                radius = int(size * (1 + progress * 2))
                s = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s, (*color, alpha), (radius + 2, radius + 2), radius, 2)
                surface.blit(s, (px - radius - 2, py - radius - 2))
                # Small cross
                if p == self._particles[0]:
                    cross_size = max(2, int(6 * (1 - progress)))
                    s2 = pygame.Surface((cross_size * 2, cross_size * 2), pygame.SRCALPHA)
                    cx, cy = cross_size, cross_size
                    pygame.draw.line(s2, (*color, alpha), (cx, cy - cross_size), (cx, cy + cross_size), 2)
                    pygame.draw.line(s2, (*color, alpha), (cx - cross_size, cy), (cx + cross_size, cy), 2)
                    surface.blit(s2, (self._x - cross_size, self._y - cross_size))
            else:
                # PHYSICAL — fallback slash-like
                color = (200, 200, 200, alpha)
                pygame.draw.circle(surface, color[:3], (px, py), size)


# ======================================================================
# Heal glow
# ======================================================================

class HealGlowEffect(Effect):
    """Green particles rising + green tint overlay."""

    def __init__(self, x: int, y: int, width: int = 50, height: int = 70) -> None:
        self._x = x
        self._y = y
        self._w = width
        self._h = height
        self._duration = 0.6
        self._elapsed = 0.0
        self._particles: list[dict] = []
        for _ in range(8):
            self._particles.append({
                "ox": random.randint(-width // 2, width // 2),
                "oy": random.randint(0, height // 2),
                "vy": random.uniform(-50, -20),
                "size": random.randint(2, 4),
            })

    def update(self, dt: float) -> bool:
        self._elapsed += dt
        for p in self._particles:
            p["oy"] += p["vy"] * dt
        return self._elapsed < self._duration

    def render(self, surface: pygame.Surface) -> None:
        progress = self._elapsed / self._duration
        alpha = max(0, int(180 * (1.0 - progress)))

        # Green tint overlay
        overlay = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        overlay.fill((40, 200, 40, alpha // 3))
        surface.blit(overlay, (self._x - self._w // 2, self._y - self._h // 2))

        # Green particles
        for p in self._particles:
            pa = max(0, int(255 * (1.0 - progress)))
            px = int(self._x + p["ox"])
            py = int(self._y + p["oy"])
            pygame.draw.circle(surface, (80, 255, 80), (px, py), p["size"])


# ======================================================================
# Hit flash
# ======================================================================

class HitFlashEffect(Effect):
    """White alpha rect flash on target."""

    def __init__(self, x: int, y: int, width: int = 50, height: int = 70) -> None:
        self._x = x
        self._y = y
        self._w = width
        self._h = height
        self._duration = 0.15
        self._elapsed = 0.0

    def update(self, dt: float) -> bool:
        self._elapsed += dt
        return self._elapsed < self._duration

    def render(self, surface: pygame.Surface) -> None:
        progress = self._elapsed / self._duration
        alpha = max(0, int(200 * (1.0 - progress)))
        flash = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        flash.fill((255, 255, 255, alpha))
        surface.blit(flash, (self._x - self._w // 2, self._y - self._h // 2))


# ======================================================================
# Buff sparkle
# ======================================================================

class BuffEffect(Effect):
    """Blue/purple sparkle dots."""

    def __init__(self, x: int, y: int, color: tuple[int, int, int] = colors.BUFF_COLOR) -> None:
        self._x = x
        self._y = y
        self._color = color
        self._duration = 0.4
        self._elapsed = 0.0
        self._sparkles: list[dict] = []
        for _ in range(6):
            self._sparkles.append({
                "ox": random.randint(-20, 20),
                "oy": random.randint(-30, 10),
                "vy": random.uniform(-40, -15),
                "phase": random.uniform(0, math.pi * 2),
            })

    def update(self, dt: float) -> bool:
        self._elapsed += dt
        for sp in self._sparkles:
            sp["oy"] += sp["vy"] * dt
        return self._elapsed < self._duration

    def render(self, surface: pygame.Surface) -> None:
        progress = self._elapsed / self._duration
        for sp in self._sparkles:
            alpha = max(0, int(255 * (1.0 - progress)))
            # Twinkle
            twinkle = 0.5 + 0.5 * math.sin(sp["phase"] + self._elapsed * 12)
            size = max(1, int(3 * twinkle))
            px = int(self._x + sp["ox"])
            py = int(self._y + sp["oy"])
            c = tuple(min(255, int(v * twinkle + 100 * (1 - twinkle))) for v in self._color)
            pygame.draw.circle(surface, c, (px, py), size)
