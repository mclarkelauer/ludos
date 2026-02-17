"""Window wrapper around pygame display."""

import warnings

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
            self._focus_window()
        except pygame.error as e:
            raise InitializationError(f"Failed to create window: {e}") from e

    @staticmethod
    def _focus_window() -> None:
        """Raise the window and grab input focus."""
        try:
            from pygame._sdl2.video import Window as SDLWindow

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*surface-rendering.*",
                    category=DeprecationWarning,
                )
                sdl_window = SDLWindow.from_display_module()
            sdl_window.focus()
        except Exception:
            pass  # Best-effort; not all platforms support this

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
