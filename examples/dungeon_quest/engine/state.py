"""Mutable runtime state for the dungeon quest engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from ludos import BaseGameState

from ..content.types import AbilityDef, AbilityEffect, CharacterClass, EquipmentSlot
from .types import CombatPhase


@dataclass
class ActiveBuff:
    effect: AbilityEffect
    power: int
    remaining_turns: int
    source_name: str


@dataclass
class Character:
    name: str
    char_class: CharacterClass
    level: int
    xp: int
    current_hp: int
    max_hp: int
    current_mp: int
    max_mp: int
    base_attack: int
    base_defense: int
    base_speed: int
    equipment: dict[EquipmentSlot, str | None] = field(
        default_factory=lambda: {
            EquipmentSlot.WEAPON: None,
            EquipmentSlot.ARMOR: None,
            EquipmentSlot.ACCESSORY: None,
        }
    )
    abilities: list[AbilityDef] = field(default_factory=list)
    buffs: list[ActiveBuff] = field(default_factory=list)
    is_dead: bool = False


@dataclass
class Enemy:
    name: str
    enemy_id: str
    current_hp: int
    max_hp: int
    mp: int
    attack: int
    defense: int
    speed: int
    abilities: list[AbilityDef] = field(default_factory=list)
    buffs: list[ActiveBuff] = field(default_factory=list)
    is_dead: bool = False


@dataclass
class CombatState:
    encounter_id: str = ""
    enemies: list[Enemy] = field(default_factory=list)
    turn_order: list[str] = field(default_factory=list)  # names
    current_turn_index: int = 0
    phase: CombatPhase = CombatPhase.INTRO
    action_cursor: int = 0
    target_cursor: int = 0
    ability_cursor: int = 0
    item_cursor: int = 0
    combat_log: list[str] = field(default_factory=list)
    pending_xp: int = 0
    pending_gold: int = 0
    pending_loot: list[str] = field(default_factory=list)
    defending: set[str] = field(default_factory=set)  # character names
    intro_timer: float = 0.0
    resolve_timer: float = 0.0
    current_actor: str = ""


@dataclass
class ExplorationState:
    current_area_id: str = ""
    dungeon_level_id: str | None = None
    player_x: int = 0
    player_y: int = 0
    in_dungeon: bool = False
    triggered_once: set[str] = field(default_factory=set)  # "x,y,level_id"
    overworld_cursor: int = 0
    dungeon_level_index: int = 0


@dataclass
class DialogueState:
    active_dialogue_id: str | None = None
    current_node_id: str | None = None
    choice_cursor: int = 0
    typewriter_progress: float = 0.0
    typewriter_done: bool = False
    waiting_for_input: bool = False


@dataclass
class QuestState:
    flags: set[str] = field(default_factory=set)
    completed_objectives: set[str] = field(default_factory=set)
    active_quests: list[str] = field(default_factory=list)  # quest_ids
    completed_quests: list[str] = field(default_factory=list)


@dataclass
class DungeonQuestState(BaseGameState):
    party: list[Character] = field(default_factory=list)
    gold: int = 0
    inventory: list[str] = field(default_factory=list)  # item_ids
    combat: CombatState = field(default_factory=CombatState)
    exploration: ExplorationState = field(default_factory=ExplorationState)
    dialogue: DialogueState = field(default_factory=DialogueState)
    quest: QuestState = field(default_factory=QuestState)
    message_log: list[str] = field(default_factory=list)
    notification: str = ""
    notification_timer: float = 0.0
    show_intro: bool = False
    intro_text: str = ""
    game_won: bool = False
    victory_text: str = ""
