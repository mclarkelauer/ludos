"""Tests for input events."""

from ludos.input.events import InputEvent, InputType


class TestInputType:
    def test_all_types_exist(self):
        assert InputType.KEY_DOWN
        assert InputType.KEY_UP
        assert InputType.MOUSE_DOWN
        assert InputType.MOUSE_UP
        assert InputType.MOUSE_MOTION
        assert InputType.QUIT


class TestInputEvent:
    def test_frozen(self):
        event = InputEvent(type=InputType.KEY_DOWN, key=42)
        try:
            event.key = 99  # type: ignore
            assert False, "Should be frozen"
        except AttributeError:
            pass

    def test_defaults(self):
        event = InputEvent(type=InputType.QUIT)
        assert event.key is None
        assert event.button is None
        assert event.pos is None
        assert event.action is None

    def test_with_action(self):
        event = InputEvent(type=InputType.KEY_DOWN, key=273, action="move_up")
        assert event.action == "move_up"

    def test_equality(self):
        a = InputEvent(type=InputType.KEY_DOWN, key=42)
        b = InputEvent(type=InputType.KEY_DOWN, key=42)
        assert a == b
