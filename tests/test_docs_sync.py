"""Tests that documentation stays in sync with the framework.

If any of these tests fail, the docs at docs/guide.md need updating.
"""

import ast
import importlib
import inspect
import re
from dataclasses import fields
from pathlib import Path

import pytest

import ludos
from ludos import (
    BaseGameState,
    BaseScene,
    EngineConfig,
    GameEngine,
    InputType,
    KeyBindings,
    MenuConfig,
    MenuItem,
    StateManager,
)
from ludos.errors import (
    LudosError,
    InitializationError,
    InputError,
    PersistenceError,
    RenderError,
    SceneError,
    StateError,
)
from ludos.scenes.manager import SceneManager

DOCS_DIR = Path(__file__).parent.parent / "docs"
GUIDE = DOCS_DIR / "guide.md"


@pytest.fixture
def guide_text():
    return GUIDE.read_text()


# ---------------------------------------------------------------------------
# 1. Every public export in __all__ is mentioned in the guide
# ---------------------------------------------------------------------------
class TestPublicAPIDocumented:
    def test_all_exports_mentioned_in_guide(self, guide_text):
        missing = []
        for name in ludos.__all__:
            if name not in guide_text:
                missing.append(name)
        assert missing == [], f"Undocumented public exports: {missing}"


# ---------------------------------------------------------------------------
# 2. Documented class signatures match actual source
# ---------------------------------------------------------------------------
class TestClassSignatures:
    def test_base_game_state_fields_documented(self, guide_text):
        """Every BaseGameState field should appear in the docs."""
        for f in fields(BaseGameState):
            assert f.name in guide_text, (
                f"BaseGameState.{f.name} not documented in guide"
            )

    def test_engine_config_fields_documented(self, guide_text):
        """Every EngineConfig field should appear in the docs."""
        for f in fields(EngineConfig):
            assert f.name in guide_text, (
                f"EngineConfig.{f.name} not documented in guide"
            )

    def test_menu_config_fields_documented(self, guide_text):
        """Every MenuConfig field should appear in the docs."""
        for f in fields(MenuConfig):
            assert f.name in guide_text, (
                f"MenuConfig.{f.name} not documented in guide"
            )

    def test_input_type_values_documented(self, guide_text):
        """Every InputType enum member should appear in the docs."""
        for member in InputType:
            assert member.name in guide_text, (
                f"InputType.{member.name} not documented in guide"
            )

    def test_base_scene_abstract_methods_documented(self, guide_text):
        """Every abstract method on BaseScene should appear in the docs."""
        for name in ("handle_input", "update", "render"):
            assert name in guide_text, (
                f"BaseScene.{name} not documented in guide"
            )

    def test_base_scene_lifecycle_hooks_documented(self, guide_text):
        """Lifecycle hooks should appear in the docs."""
        for name in ("on_enter", "on_exit"):
            assert name in guide_text, (
                f"BaseScene.{name} not documented in guide"
            )

    def test_scene_manager_methods_documented(self, guide_text):
        """SceneManager public methods should appear in the docs."""
        for name in ("push", "pop", "replace", "clear", "active", "depth"):
            assert name in guide_text, (
                f"SceneManager.{name} not documented in guide"
            )

    def test_state_manager_api_documented(self, guide_text):
        """StateManager public API should appear in the docs."""
        for name in ("state", "dirty", "update", "mark_clean"):
            assert name in guide_text, (
                f"StateManager.{name} not documented in guide"
            )

    def test_key_bindings_methods_documented(self, guide_text):
        """KeyBindings public methods should appear in the docs."""
        for name in ("defaults", "bind_key", "unbind_key", "bind_mouse",
                      "get_key_action", "get_mouse_action"):
            assert name in guide_text, (
                f"KeyBindings.{name} not documented in guide"
            )

    def test_input_handler_methods_documented(self, guide_text):
        """InputHandler public methods should appear in the docs."""
        for name in ("on", "off", "poll"):
            # "on" is too short and common, check "handler.on" pattern
            if name == "on":
                assert "handler.on(" in guide_text or ".on(" in guide_text, (
                    "InputHandler.on not documented in guide"
                )
            else:
                assert name in guide_text, (
                    f"InputHandler.{name} not documented in guide"
                )

    def test_engine_methods_documented(self, guide_text):
        """GameEngine public methods should appear in the docs."""
        for name in ("run", "stop", "state_manager", "scene_manager",
                      "input_handler", "window"):
            assert name in guide_text, (
                f"GameEngine.{name} not documented in guide"
            )


# ---------------------------------------------------------------------------
# 3. Error hierarchy documented correctly
# ---------------------------------------------------------------------------
class TestErrorDocsSync:
    def test_all_error_classes_documented(self, guide_text):
        error_classes = [
            "LudosError", "InitializationError", "StateError",
            "SceneError", "InputError", "RenderError", "PersistenceError",
        ]
        for name in error_classes:
            assert name in guide_text, f"{name} not documented in guide"

    def test_error_hierarchy_accurate(self):
        """All custom errors must inherit from LudosError."""
        for cls in (InitializationError, StateError, SceneError,
                     InputError, RenderError, PersistenceError):
            assert issubclass(cls, LudosError)


# ---------------------------------------------------------------------------
# 4. Default key bindings table matches actual defaults
# ---------------------------------------------------------------------------
class TestDefaultBindingsDocumented:
    def test_default_key_bindings_match(self, guide_text):
        """The documented default bindings must match KeyBindings.defaults()."""
        import pygame
        bindings = KeyBindings.defaults()

        expected = {
            pygame.K_UP: "move_up",
            pygame.K_DOWN: "move_down",
            pygame.K_LEFT: "move_left",
            pygame.K_RIGHT: "move_right",
            pygame.K_RETURN: "confirm",
            pygame.K_ESCAPE: "cancel",
            pygame.K_SPACE: "action",
        }
        for key, action in expected.items():
            actual = bindings.get_key_action(key)
            assert actual == action, (
                f"Default binding for {key} is {actual!r}, expected {action!r}"
            )
            assert action in guide_text, (
                f"Default action {action!r} not in guide"
            )

    def test_default_mouse_bindings_match(self, guide_text):
        bindings = KeyBindings.defaults()
        expected = {1: "click", 3: "right_click"}
        for button, action in expected.items():
            actual = bindings.get_mouse_action(button)
            assert actual == action, (
                f"Default mouse binding for button {button} is {actual!r}, expected {action!r}"
            )
            assert action in guide_text, (
                f"Default mouse action {action!r} not in guide"
            )


# ---------------------------------------------------------------------------
# 5. Code examples in docs are valid Python (syntax check)
# ---------------------------------------------------------------------------
class TestCodeExamples:
    def _extract_python_blocks(self, text: str) -> list[str]:
        """Extract all ```python ... ``` fenced code blocks."""
        pattern = r"```python\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

    def test_all_code_blocks_parse(self, guide_text):
        """Every Python code block in the guide must be valid syntax."""
        blocks = self._extract_python_blocks(guide_text)
        assert len(blocks) > 0, "No Python code blocks found in guide"
        for i, block in enumerate(blocks):
            try:
                ast.parse(block)
            except SyntaxError as e:
                pytest.fail(
                    f"Code block {i + 1} has syntax error at line {e.lineno}: {e.msg}\n"
                    f"---\n{block}---"
                )


# ---------------------------------------------------------------------------
# 6. MenuConfig defaults documented correctly
# ---------------------------------------------------------------------------
class TestMenuConfigDefaults:
    def test_documented_defaults_match_code(self, guide_text):
        """MenuConfig defaults in the docs must match the actual defaults."""
        cfg = MenuConfig()
        checks = {
            "font_size": (cfg.font_size, "36"),
            "title_font_size": (cfg.title_font_size, "48"),
            "item_spacing": (cfg.item_spacing, "10"),
            "text_color": (cfg.text_color, "(255, 255, 255)"),
            "highlight_color": (cfg.highlight_color, "(255, 255, 0)"),
            "bg_color": (cfg.bg_color, "(0, 0, 0)"),
        }
        for field_name, (actual, doc_str) in checks.items():
            assert doc_str in guide_text, (
                f"MenuConfig.{field_name} default {actual!r} "
                f"(expected {doc_str!r} in docs)"
            )


# ---------------------------------------------------------------------------
# 7. EngineConfig defaults documented correctly
# ---------------------------------------------------------------------------
class TestEngineConfigDefaults:
    def test_documented_defaults_match_code(self, guide_text):
        cfg = EngineConfig()
        checks = {
            "width": (cfg.width, "800"),
            "height": (cfg.height, "600"),
            "fps": (cfg.fps, "60"),
        }
        for field_name, (actual, doc_str) in checks.items():
            assert doc_str in guide_text, (
                f"EngineConfig.{field_name} default {actual!r} not documented"
            )


# ---------------------------------------------------------------------------
# 8. Persistence functions documented
# ---------------------------------------------------------------------------
class TestPersistenceDocsSync:
    def test_save_state_documented(self, guide_text):
        assert "save_state" in guide_text, "save_state not documented in guide"

    def test_load_state_documented(self, guide_text):
        assert "load_state" in guide_text, "load_state not documented in guide"
