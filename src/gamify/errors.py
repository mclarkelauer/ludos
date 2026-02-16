"""Gamify error hierarchy."""


class GamifyError(Exception):
    """Base exception for all gamify errors."""


class InitializationError(GamifyError):
    """Raised when engine or subsystem initialization fails."""


class StateError(GamifyError):
    """Raised when state operations fail."""


class SceneError(GamifyError):
    """Raised when scene operations fail."""


class InputError(GamifyError):
    """Raised when input operations fail."""


class RenderError(GamifyError):
    """Raised when rendering operations fail."""
