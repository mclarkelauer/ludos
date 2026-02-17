"""Dialogue scene — NPC conversation with typewriter + choices."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..dialogue.runner import (
    advance_dialogue,
    get_available_choices,
    get_current_node,
    start_dialogue,
)
from ..rendering import colors, fonts
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.text import draw_text, draw_typewriter
from ..rendering.menu_renderer import draw_menu
from ..state import DungeonQuestState

if TYPE_CHECKING:
    from ludos import GameEngine
    from ..context import GameContext

TYPEWRITER_SPEED = 30.0  # chars per second


class DialogueScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx: GameContext, dialogue_id: str) -> None:
        self._engine = engine
        self._ctx = ctx
        self._dialogue_id = dialogue_id
        self._layout: Layout | None = None
        self._pending_encounter: str | None = None
        self._notification = ""

    def on_enter(self, state: BaseGameState) -> None:
        s = self._cast(state)
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)
        start_dialogue(self._dialogue_id, s, self._ctx)

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)
        node = get_current_node(s, self._ctx)
        if not node:
            self._close(s)
            return

        if not s.dialogue.typewriter_done:
            if event.action == "confirm":
                # Skip typewriter
                s.dialogue.typewriter_done = True
                s.dialogue.typewriter_progress = float(len(node.text) + 1)
            return

        choices = get_available_choices(node, s)
        if choices:
            if event.action == "move_up":
                s.dialogue.choice_cursor = (s.dialogue.choice_cursor - 1) % len(choices)
            elif event.action == "move_down":
                s.dialogue.choice_cursor = (s.dialogue.choice_cursor + 1) % len(choices)
            elif event.action == "confirm":
                ended, enc_id, msg = advance_dialogue(s.dialogue.choice_cursor, s, self._ctx)
                if msg:
                    self._notification = msg
                if enc_id:
                    self._pending_encounter = enc_id
                if ended:
                    self._close(s)
        else:
            if event.action == "confirm":
                ended, enc_id, msg = advance_dialogue(None, s, self._ctx)
                if msg:
                    self._notification = msg
                if enc_id:
                    self._pending_encounter = enc_id
                if ended:
                    self._close(s)

    def update(self, dt: float, state: BaseGameState) -> None:
        s = self._cast(state)
        node = get_current_node(s, self._ctx)
        if not node:
            return

        if not s.dialogue.typewriter_done:
            s.dialogue.typewriter_progress += TYPEWRITER_SPEED * dt
            if s.dialogue.typewriter_progress >= len(node.text):
                s.dialogue.typewriter_done = True

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        s = self._cast(state)
        if not self._layout:
            return

        node = get_current_node(s, self._ctx)
        if not node:
            return

        # Dark backdrop
        overlay = pygame.Surface((self._layout.width, self._layout.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Speaker name
        speaker_rect = self._layout.dialogue_speaker()
        font_large = fonts.large()
        speaker_surf = font_large.render(node.speaker, True, colors.YELLOW)
        surface.blit(speaker_surf, (speaker_rect.x + 10, speaker_rect.y))

        # Dialogue text with typewriter
        text_rect = self._layout.dialogue_text()
        inner = draw_panel(surface, text_rect)
        if s.dialogue.typewriter_done:
            draw_text(surface, node.text, inner, colors.WHITE, fonts.normal())
        else:
            draw_typewriter(
                surface, node.text, inner, s.dialogue.typewriter_progress / max(1, len(node.text)),
                colors.WHITE, fonts.normal(),
            )

        # Choices
        if s.dialogue.typewriter_done:
            choices = get_available_choices(node, s)
            if choices:
                choice_rect = self._layout.dialogue_choices()
                inner = draw_panel(surface, choice_rect)
                items = [text for _, text in choices]
                draw_menu(surface, inner, items, s.dialogue.choice_cursor)
            else:
                prompt = fonts.small().render("[Enter] to continue", True, colors.LIGHT_GRAY)
                surface.blit(prompt, (self._layout.width // 2 - prompt.get_width() // 2, self._layout.height - 30))

        # Notification
        if self._notification:
            notif = fonts.normal().render(self._notification, True, colors.HEAL_COLOR)
            surface.blit(notif, (self._layout.width // 2 - notif.get_width() // 2, self._layout.height // 3))

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state

    def _close(self, s: DungeonQuestState) -> None:
        if self._pending_encounter:
            from .combat import CombatScene
            enc_id = self._pending_encounter
            self._pending_encounter = None
            self._engine.scene_manager.pop(s)
            scene = CombatScene(self._engine, self._ctx, enc_id)
            self._engine.scene_manager.push(scene, s)
        else:
            self._engine.scene_manager.pop(s)
