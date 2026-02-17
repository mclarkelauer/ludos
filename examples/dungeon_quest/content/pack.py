"""QuestPack — top-level container for a complete adventure."""

from __future__ import annotations

from dataclasses import dataclass, field

from .types import (
    CharacterDef,
    ClassDef,
    DialogueTree,
    DungeonLevel,
    EncounterDef,
    EnemyDef,
    ItemDef,
    OverworldArea,
    QuestDef,
)


@dataclass(frozen=True)
class QuestPack:
    name: str
    description: str
    starting_area_id: str
    party: tuple[CharacterDef, ...]
    classes: tuple[ClassDef, ...]
    areas: tuple[OverworldArea, ...]
    enemies: tuple[EnemyDef, ...]
    encounters: tuple[EncounterDef, ...]
    dialogues: tuple[DialogueTree, ...]
    items: tuple[ItemDef, ...]
    quests: tuple[QuestDef, ...]
    dungeon_levels: tuple[DungeonLevel, ...] = ()
    starting_items: tuple[str, ...] = ()  # item_ids
    starting_gold: int = 0
    intro_text: str = ""
    victory_flag: str = "game_victory"
    victory_text: str = "Congratulations! You have completed the quest!"
