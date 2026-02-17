"""Panel layout calculator for screen regions."""

from __future__ import annotations

import pygame

MARGIN = 8


class Layout:
    """Computes panel Rects from screen dimensions."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def full_screen(self) -> pygame.Rect:
        return pygame.Rect(MARGIN, MARGIN, self.width - MARGIN * 2, self.height - MARGIN * 2)

    def top_bar(self, h: int = 40) -> pygame.Rect:
        return pygame.Rect(MARGIN, MARGIN, self.width - MARGIN * 2, h)

    def bottom_bar(self, h: int = 40) -> pygame.Rect:
        return pygame.Rect(MARGIN, self.height - h - MARGIN, self.width - MARGIN * 2, h)

    # -- Combat layout --

    def combat_enemies(self) -> pygame.Rect:
        """Top-right area for enemy list."""
        w = self.width // 2 - MARGIN * 2
        return pygame.Rect(self.width // 2 + MARGIN, MARGIN, w, self.height // 3)

    def combat_party(self) -> pygame.Rect:
        """Top-left area for party HUD."""
        w = self.width // 2 - MARGIN * 2
        return pygame.Rect(MARGIN, MARGIN, w, self.height // 3)

    def combat_log(self) -> pygame.Rect:
        """Middle area for combat log."""
        top = self.height // 3 + MARGIN
        h = self.height // 3 - MARGIN * 2
        return pygame.Rect(MARGIN, top, self.width - MARGIN * 2, h)

    def combat_actions(self) -> pygame.Rect:
        """Bottom area for action menu."""
        top = self.height * 2 // 3 + MARGIN
        h = self.height // 3 - MARGIN * 2
        return pygame.Rect(MARGIN, top, self.width // 2 - MARGIN * 2, h)

    def combat_info(self) -> pygame.Rect:
        """Bottom-right area for sub-menus/info."""
        top = self.height * 2 // 3 + MARGIN
        h = self.height // 3 - MARGIN * 2
        w = self.width // 2 - MARGIN * 2
        return pygame.Rect(self.width // 2 + MARGIN, top, w, h)

    # -- Overworld layout --

    def overworld_description(self) -> pygame.Rect:
        """Top area for area description."""
        return pygame.Rect(MARGIN, MARGIN, self.width - MARGIN * 2, self.height // 2 - MARGIN)

    def overworld_actions(self) -> pygame.Rect:
        """Bottom area for action menu."""
        top = self.height // 2 + MARGIN
        return pygame.Rect(MARGIN, top, self.width - MARGIN * 2, self.height // 2 - MARGIN * 2)

    # -- Dungeon layout --

    def dungeon_map(self) -> pygame.Rect:
        """Main area for tile grid."""
        return pygame.Rect(MARGIN, MARGIN, self.width - 220, self.height - MARGIN * 2)

    def dungeon_hud(self) -> pygame.Rect:
        """Right sidebar for party HUD."""
        return pygame.Rect(self.width - 210, MARGIN, 200, self.height - MARGIN * 2)

    # -- Dialogue layout --

    def dialogue_speaker(self) -> pygame.Rect:
        return pygame.Rect(MARGIN, self.height // 2 - 30, self.width - MARGIN * 2, 30)

    def dialogue_text(self) -> pygame.Rect:
        top = self.height // 2
        return pygame.Rect(MARGIN, top, self.width - MARGIN * 2, self.height // 3)

    def dialogue_choices(self) -> pygame.Rect:
        top = self.height * 5 // 6
        return pygame.Rect(MARGIN, top, self.width - MARGIN * 2, self.height // 6 - MARGIN)

    # -- Generic centered panel --

    def centered(self, w: int, h: int) -> pygame.Rect:
        x = (self.width - w) // 2
        y = (self.height - h) // 2
        return pygame.Rect(x, y, w, h)
