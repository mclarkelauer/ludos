"""Tests for error hierarchy."""

import pytest

from ludos.errors import (
    LudosError,
    InitializationError,
    InputError,
    RenderError,
    SceneError,
    StateError,
)


class TestErrorHierarchy:
    def test_all_errors_inherit_from_ludos_error(self):
        for cls in (InitializationError, StateError, SceneError, InputError, RenderError):
            assert issubclass(cls, LudosError)

    def test_ludos_error_inherits_from_exception(self):
        assert issubclass(LudosError, Exception)

    def test_errors_carry_message(self):
        err = StateError("bad state")
        assert str(err) == "bad state"

    def test_errors_catchable_as_ludos_error(self):
        with pytest.raises(LudosError):
            raise InputError("bad input")
