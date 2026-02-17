"""Ludos error hierarchy."""


class LudosError(Exception):
    """Base exception for all ludos errors."""


class InitializationError(LudosError):
    """Raised when engine or subsystem initialization fails."""


class StateError(LudosError):
    """Raised when state operations fail."""


class SceneError(LudosError):
    """Raised when scene operations fail."""


class InputError(LudosError):
    """Raised when input operations fail."""


class RenderError(LudosError):
    """Raised when rendering operations fail."""


class PersistenceError(LudosError):
    """Raised when save/load operations fail."""
