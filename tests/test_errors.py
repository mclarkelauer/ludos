"""Tests for error hierarchy."""

import pytest

from gamify.errors import (
    GamifyError,
    InitializationError,
    InputError,
    RenderError,
    SceneError,
    StateError,
)


class TestErrorHierarchy:
    def test_all_errors_inherit_from_gamify_error(self):
        for cls in (InitializationError, StateError, SceneError, InputError, RenderError):
            assert issubclass(cls, GamifyError)

    def test_gamify_error_inherits_from_exception(self):
        assert issubclass(GamifyError, Exception)

    def test_errors_carry_message(self):
        err = StateError("bad state")
        assert str(err) == "bad state"

    def test_errors_catchable_as_gamify_error(self):
        with pytest.raises(GamifyError):
            raise InputError("bad input")
