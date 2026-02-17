"""Shared engine enums for runtime state."""

from enum import Enum, auto


class CombatPhase(Enum):
    INTRO = auto()
    ROLLING_INITIATIVE = auto()
    CHOOSE_ACTION = auto()
    CHOOSE_TARGET = auto()
    CHOOSE_ABILITY = auto()
    CHOOSE_ITEM = auto()
    RESOLVING = auto()
    ENEMY_TURN = auto()
    VICTORY = auto()
    DEFEAT = auto()
    FLEE_CHECK = auto()


class GamePhase(Enum):
    TITLE = auto()
    OVERWORLD = auto()
    DUNGEON = auto()
    COMBAT = auto()
    DIALOGUE = auto()
    INVENTORY = auto()
    PARTY = auto()
    REST = auto()
    GAME_OVER = auto()
