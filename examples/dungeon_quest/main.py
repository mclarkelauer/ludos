"""Bootstrap: load quest, build state, run engine."""

from __future__ import annotations

import pygame

from ludos import EngineConfig, GameEngine, KeyBindings

from .engine.characters.stats import create_character
from .engine.characters.inventory import equip_item
from .engine.context import GameContext
from .engine.quests.tracker import update_quests
from .engine.state import DungeonQuestState
from .engine.scenes.title import TitleScene
from .quests.goblin_caves import QUEST_PACK


def build_bindings() -> KeyBindings:
    """Build key bindings extending defaults with WASD and shortcuts."""
    bindings = KeyBindings.defaults()
    # WASD movement
    bindings.bind_key(pygame.K_w, "w")
    bindings.bind_key(pygame.K_a, "a")
    bindings.bind_key(pygame.K_s, "s")
    bindings.bind_key(pygame.K_d, "d")
    # Shortcuts
    bindings.bind_key(pygame.K_i, "inventory")
    bindings.bind_key(pygame.K_p, "party")
    bindings.bind_key(pygame.K_q, "quest_log")
    bindings.bind_key(pygame.K_TAB, "next_tab")
    # Combat quick actions
    bindings.bind_key(pygame.K_1, "quick_1")
    bindings.bind_key(pygame.K_2, "quick_2")
    bindings.bind_key(pygame.K_3, "quick_3")
    bindings.bind_key(pygame.K_4, "quick_4")
    return bindings


def build_state(ctx: GameContext) -> DungeonQuestState:
    """Build initial game state from a QuestPack."""
    pack = ctx.quest_pack

    # Create party characters
    party = []
    for char_def in pack.party:
        cls_def = ctx.classes[char_def.char_class]
        char = create_character(char_def, cls_def)
        party.append(char)

    state = DungeonQuestState(
        party=party,
        gold=pack.starting_gold,
        inventory=list(pack.starting_items),
    )

    # Set starting area
    state.exploration.current_area_id = pack.starting_area_id

    # Intro text
    if pack.intro_text:
        state.show_intro = True
        state.intro_text = pack.intro_text

    # Equip starting equipment
    for i, char_def in enumerate(pack.party):
        for item_id in char_def.starting_equipment:
            if item_id not in state.inventory:
                state.inventory.append(item_id)
            equip_item(party[i], item_id, state, ctx)

    return state


def main() -> None:
    """Entry point for Dungeon Quest."""
    ctx = GameContext.from_quest_pack(QUEST_PACK)
    state = build_state(ctx)

    def state_factory():
        return build_state(ctx)

    engine = GameEngine(
        config=EngineConfig(
            width=960,
            height=720,
            title=f"Dungeon Quest — {QUEST_PACK.name}",
            fps=60,
            bg_color=(10, 10, 15),
        ),
        initial_state=state,
        bindings=build_bindings(),
    )

    title = TitleScene(engine=engine, ctx=ctx, state_factory=state_factory)
    engine._initial_scene = title  # noqa: SLF001

    engine.run()


if __name__ == "__main__":
    main()
