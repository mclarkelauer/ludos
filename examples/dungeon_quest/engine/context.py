"""GameContext — typed lookup dicts built from QuestPack at startup."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..content.pack import QuestPack
from ..content.types import (
    CharacterClass,
    ClassDef,
    DialogueTree,
    DungeonLevel,
    EncounterDef,
    EnemyDef,
    ItemDef,
    OverworldArea,
    QuestDef,
)


@dataclass
class GameContext:
    quest_pack: QuestPack
    items: dict[str, ItemDef] = field(default_factory=dict)
    enemies: dict[str, EnemyDef] = field(default_factory=dict)
    encounters: dict[str, EncounterDef] = field(default_factory=dict)
    dialogues: dict[str, DialogueTree] = field(default_factory=dict)
    areas: dict[str, OverworldArea] = field(default_factory=dict)
    dungeon_levels: dict[str, DungeonLevel] = field(default_factory=dict)
    classes: dict[CharacterClass, ClassDef] = field(default_factory=dict)
    quests: dict[str, QuestDef] = field(default_factory=dict)

    @classmethod
    def from_quest_pack(cls, pack: QuestPack) -> GameContext:
        ctx = cls(quest_pack=pack)
        for item in pack.items:
            ctx.items[item.item_id] = item
        for enemy in pack.enemies:
            ctx.enemies[enemy.enemy_id] = enemy
        for enc in pack.encounters:
            ctx.encounters[enc.encounter_id] = enc
        for dlg in pack.dialogues:
            ctx.dialogues[dlg.dialogue_id] = dlg
        for area in pack.areas:
            ctx.areas[area.area_id] = area
        for level in pack.dungeon_levels:
            ctx.dungeon_levels[level.level_id] = level
        for cls_def in pack.classes:
            ctx.classes[cls_def.char_class] = cls_def
        for quest in pack.quests:
            ctx.quests[quest.quest_id] = quest
        return ctx
