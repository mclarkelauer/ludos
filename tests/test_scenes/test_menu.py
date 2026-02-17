"""Tests for MenuScene."""

from unittest.mock import MagicMock, patch

from ludos.input.events import InputEvent, InputType
from ludos.scenes.menu import MenuConfig, MenuItem, MenuScene
from ludos.state.base import BaseGameState


def _action_event(action: str) -> InputEvent:
    return InputEvent(type=InputType.KEY_DOWN, action=action)


class TestMenuItem:
    def test_fields(self):
        cb = lambda: None
        item = MenuItem(label="Start", action=cb)
        assert item.label == "Start"
        assert item.action is cb


class TestMenuConfig:
    def test_defaults(self):
        cfg = MenuConfig()
        assert cfg.font_size == 36
        assert cfg.text_color == (255, 255, 255)
        assert cfg.highlight_color == (255, 255, 0)
        assert cfg.bg_color == (0, 0, 0)
        assert cfg.title == ""

    def test_custom(self):
        cfg = MenuConfig(title="Main Menu", font_size=24)
        assert cfg.title == "Main Menu"
        assert cfg.font_size == 24


class TestMenuScene:
    def setup_method(self):
        self.called = []
        self.items = [
            MenuItem("Start", lambda: self.called.append("start")),
            MenuItem("Options", lambda: self.called.append("options")),
            MenuItem("Quit", lambda: self.called.append("quit")),
        ]
        self.menu = MenuScene(self.items)
        self.state = BaseGameState()

    def test_initial_selection(self):
        assert self.menu.selected == 0

    def test_move_down(self):
        self.menu.handle_input(_action_event("move_down"), self.state)
        assert self.menu.selected == 1

    def test_move_up_wraps(self):
        self.menu.handle_input(_action_event("move_up"), self.state)
        assert self.menu.selected == 2  # wraps to last

    def test_move_down_wraps(self):
        self.menu.selected = 2
        self.menu.handle_input(_action_event("move_down"), self.state)
        assert self.menu.selected == 0  # wraps to first

    def test_confirm_calls_action(self):
        self.menu.selected = 1
        self.menu.handle_input(_action_event("confirm"), self.state)
        assert self.called == ["options"]

    def test_confirm_first_item(self):
        self.menu.handle_input(_action_event("confirm"), self.state)
        assert self.called == ["start"]

    def test_items_property(self):
        assert self.menu.items is self.items

    @patch("ludos.scenes.menu.pygame.font.Font")
    def test_render_calls_fill(self, mock_font_cls):
        mock_font = MagicMock()
        mock_font.render.return_value = MagicMock()
        mock_font.render.return_value.get_rect.return_value = MagicMock()
        mock_font_cls.return_value = mock_font

        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600

        self.menu.render(surface, self.state)
        surface.fill.assert_called_once_with((0, 0, 0))

    @patch("ludos.scenes.menu.pygame.font.Font")
    def test_render_with_title(self, mock_font_cls):
        mock_font = MagicMock()
        mock_font.render.return_value = MagicMock()
        mock_font.render.return_value.get_rect.return_value = MagicMock()
        mock_font_cls.return_value = mock_font

        surface = MagicMock()
        surface.get_width.return_value = 800
        surface.get_height.return_value = 600

        menu = MenuScene(self.items, MenuConfig(title="Test Menu"))
        menu.render(surface, self.state)
        # Title + 3 items = 4 render calls
        assert mock_font.render.call_count == 4

    def test_update_is_noop(self):
        self.menu.update(0.016, self.state)  # no error

    def test_input_repeat_delay_default(self):
        assert self.menu.input_repeat_delay == 0.15

    def test_empty_menu_confirm_no_crash(self):
        menu = MenuScene([])
        menu.handle_input(_action_event("confirm"), self.state)  # no crash
