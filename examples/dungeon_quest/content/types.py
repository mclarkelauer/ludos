"""All content dataclasses and enums for quest authoring.

Quest authors import from here — no pygame, no engine logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CharacterClass(Enum):
    WARRIOR = auto()
    ROGUE = auto()
    CLERIC = auto()
    MAGE = auto()


class DamageType(Enum):
    PHYSICAL = auto()
    FIRE = auto()
    ICE = auto()
    HOLY = auto()


class TargetType(Enum):
    SINGLE_ENEMY = auto()
    ALL_ENEMIES = auto()
    SINGLE_ALLY = auto()
    ALL_ALLIES = auto()
    SELF = auto()


class AbilityEffect(Enum):
    DAMAGE = auto()
    HEAL = auto()
    BUFF_ATTACK = auto()
    BUFF_DEFENSE = auto()
    DEBUFF_ATTACK = auto()
    DEBUFF_DEFENSE = auto()


class EquipmentSlot(Enum):
    WEAPON = auto()
    ARMOR = auto()
    ACCESSORY = auto()


class ItemType(Enum):
    EQUIPMENT = auto()
    CONSUMABLE = auto()
    KEY_ITEM = auto()


class TileType(Enum):
    FLOOR = auto()
    WALL = auto()
    DOOR = auto()
    STAIRS_DOWN = auto()
    STAIRS_UP = auto()
    CHEST = auto()
    TRAP = auto()
    NPC = auto()
    ENTRANCE = auto()


class ObjectiveType(Enum):
    DEFEAT_ENCOUNTER = auto()
    REACH_AREA = auto()
    OBTAIN_ITEM = auto()
    SET_FLAG = auto()
    TALK_TO_NPC = auto()


# ---------------------------------------------------------------------------
# Content dataclasses (all frozen — quest authors only define data)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AbilityDef:
    name: str
    description: str
    effect: AbilityEffect
    target: TargetType
    power: int
    cost: int = 0
    damage_type: DamageType = DamageType.PHYSICAL
    level_required: int = 1
    accuracy_bonus: int = 0
    duration: int = 0  # 0 = instant


@dataclass(frozen=True)
class ClassDef:
    char_class: CharacterClass
    base_hp: int
    base_mp: int
    base_attack: int
    base_defense: int
    base_speed: int
    hp_per_level: int
    mp_per_level: int
    attack_per_level: int
    defense_per_level: int
    speed_per_level: int
    abilities: tuple[AbilityDef, ...] = ()


@dataclass(frozen=True)
class CharacterDef:
    name: str
    char_class: CharacterClass
    level: int = 1
    bonus_hp: int = 0
    bonus_mp: int = 0
    bonus_attack: int = 0
    bonus_defense: int = 0
    bonus_speed: int = 0
    starting_equipment: tuple[str, ...] = ()  # item_ids


@dataclass(frozen=True)
class ItemDef:
    item_id: str
    name: str
    description: str
    item_type: ItemType
    slot: EquipmentSlot | None = None
    attack_bonus: int = 0
    defense_bonus: int = 0
    speed_bonus: int = 0
    hp_bonus: int = 0
    mp_bonus: int = 0
    heal_amount: int = 0
    mp_restore: int = 0
    class_restriction: CharacterClass | None = None


@dataclass(frozen=True)
class EnemyDef:
    enemy_id: str
    name: str
    hp: int
    mp: int
    attack: int
    defense: int
    speed: int
    xp_reward: int
    gold_reward: int
    abilities: tuple[AbilityDef, ...] = ()
    loot_table: tuple[tuple[str, float], ...] = ()  # (item_id, drop_chance)


@dataclass(frozen=True)
class EncounterDef:
    encounter_id: str
    enemies: tuple[str, ...]  # enemy_ids
    is_boss: bool = False
    intro_text: str = ""
    victory_text: str = ""
    defeat_text: str = ""
    on_victory_set_flag: str | None = None


@dataclass(frozen=True)
class DialogueChoice:
    text: str
    next_node_id: str
    required_flag: str | None = None
    sets_flag: str | None = None


@dataclass(frozen=True)
class DialogueNode:
    node_id: str
    speaker: str
    text: str
    choices: tuple[DialogueChoice, ...] = ()
    next_node_id: str | None = None  # auto-advance if no choices
    sets_flag: str | None = None
    gives_item: str | None = None  # item_id
    starts_encounter: str | None = None  # encounter_id
    heals_party: bool = False


@dataclass(frozen=True)
class DialogueTree:
    dialogue_id: str
    nodes: tuple[DialogueNode, ...]  # first node is entry point
    required_flag: str | None = None
    repeatable: bool = True


@dataclass(frozen=True)
class TileTrigger:
    x: int
    y: int
    encounter_id: str | None = None
    dialogue_id: str | None = None
    item_id: str | None = None
    sets_flag: str | None = None
    once: bool = True
    text: str = ""


@dataclass(frozen=True)
class DungeonLevel:
    level_id: str
    name: str
    width: int
    height: int
    tiles: tuple[tuple[TileType, ...], ...]  # rows of tile types
    player_start: tuple[int, int] = (1, 1)
    triggers: tuple[TileTrigger, ...] = ()
    random_encounter_ids: tuple[str, ...] = ()
    random_encounter_chance: float = 0.1


@dataclass(frozen=True)
class AreaConnection:
    target_area_id: str
    label: str
    required_flag: str | None = None
    locked_text: str = "The way is blocked."


@dataclass(frozen=True)
class OverworldArea:
    area_id: str
    name: str
    description: str
    connections: tuple[AreaConnection, ...] = ()
    dungeon_levels: tuple[str, ...] = ()  # level_ids in order
    npcs: tuple[str, ...] = ()  # dialogue_ids
    rest_available: bool = False


@dataclass(frozen=True)
class ObjectiveDef:
    objective_id: str
    description: str
    objective_type: ObjectiveType
    target: str  # encounter_id, area_id, item_id, flag, or dialogue_id
    required_flag: str | None = None


@dataclass(frozen=True)
class QuestDef:
    quest_id: str
    name: str
    description: str
    objectives: tuple[ObjectiveDef, ...]
    completion_flag: str
    rewards_xp: int = 0
    rewards_gold: int = 0
    rewards_items: tuple[str, ...] = ()  # item_ids
