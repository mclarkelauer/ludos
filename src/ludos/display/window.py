"""Window wrapper around pygame display."""

import pygame

from ludos.errors import InitializationError, RenderError


class Window:
    """Manages the pygame display surface.

    Example:
        window = Window(800, 600, "My Game")
        surface = window.surface
        window.flip()
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Ludos",
        flags: int = 0,
    ) -> None:
        self._width = width
        self._height = height
        self._title = title
        try:
            self._surface = pygame.display.set_mode((width, height), flags)
            pygame.display.set_caption(title)
        except pygame.error as e:
            raise InitializationError(f"Failed to create window: {e}") from e

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def title(self) -> str:
        return self._title

    def clear(self, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """Fill the surface with a solid color."""
        self._surface.fill(color)

    def flip(self) -> None:
        """Swap display buffers."""
        try:
            pygame.display.flip()
        except pygame.error as e:
            raise RenderError(f"Display flip failed: {e}") from e
