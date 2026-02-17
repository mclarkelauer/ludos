"""Character creation, effective stats, level-up, and XP."""

from __future__ import annotations

from ..context import GameContext
from ..state import ActiveBuff, Character
from ...content.types import (
    AbilityEffect,
    CharacterDef,
    ClassDef,
    EquipmentSlot,
    ItemDef,
)


def create_character(char_def: CharacterDef, class_def: ClassDef) -> Character:
    """Create a runtime Character from content definitions."""
    level = char_def.level
    max_hp = class_def.base_hp + class_def.hp_per_level * (level - 1) + char_def.bonus_hp
    max_mp = class_def.base_mp + class_def.mp_per_level * (level - 1) + char_def.bonus_mp
    base_atk = class_def.base_attack + class_def.attack_per_level * (level - 1) + char_def.bonus_attack
    base_def = class_def.base_defense + class_def.defense_per_level * (level - 1) + char_def.bonus_defense
    base_spd = class_def.base_speed + class_def.speed_per_level * (level - 1) + char_def.bonus_speed

    abilities = [a for a in class_def.abilities if a.level_required <= level]

    return Character(
        name=char_def.name,
        char_class=char_def.char_class,
        level=level,
        xp=0,
        current_hp=max_hp,
        max_hp=max_hp,
        current_mp=max_mp,
        max_mp=max_mp,
        base_attack=base_atk,
        base_defense=base_def,
        base_speed=base_spd,
        abilities=abilities,
    )


def effective_attack(char: Character, ctx: GameContext) -> int:
    """Total attack including equipment and buffs."""
    total = char.base_attack
    for slot, item_id in char.equipment.items():
        if item_id and item_id in ctx.items:
            total += ctx.items[item_id].attack_bonus
    for buff in char.buffs:
        if buff.effect == AbilityEffect.BUFF_ATTACK:
            total += buff.power
        elif buff.effect == AbilityEffect.DEBUFF_ATTACK:
            total -= buff.power
    return max(0, total)


def effective_defense(char: Character, ctx: GameContext) -> int:
    """Total defense including equipment and buffs."""
    total = char.base_defense
    for slot, item_id in char.equipment.items():
        if item_id and item_id in ctx.items:
            total += ctx.items[item_id].defense_bonus
    for buff in char.buffs:
        if buff.effect == AbilityEffect.BUFF_DEFENSE:
            total += buff.power
        elif buff.effect == AbilityEffect.DEBUFF_DEFENSE:
            total -= buff.power
    return max(0, total)


def effective_speed(char: Character, ctx: GameContext) -> int:
    """Total speed including equipment."""
    total = char.base_speed
    for slot, item_id in char.equipment.items():
        if item_id and item_id in ctx.items:
            total += ctx.items[item_id].speed_bonus
    return max(0, total)


def xp_for_level(level: int) -> int:
    """XP needed to reach a given level."""
    return level * 100


def check_level_up(char: Character, class_def: ClassDef) -> bool:
    """Check and apply level-up if XP threshold is met. Returns True if leveled up."""
    needed = xp_for_level(char.level + 1)
    if char.xp < needed:
        return False

    char.xp -= needed
    char.level += 1
    char.max_hp += class_def.hp_per_level
    char.max_mp += class_def.mp_per_level
    char.base_attack += class_def.attack_per_level
    char.base_defense += class_def.defense_per_level
    char.base_speed += class_def.speed_per_level
    char.current_hp = char.max_hp
    char.current_mp = char.max_mp

    # Learn new abilities
    for ability in class_def.abilities:
        if ability.level_required == char.level and ability not in char.abilities:
            char.abilities.append(ability)

    return True


def tick_buffs(char: Character) -> list[str]:
    """Decrement buff durations. Returns messages for expired buffs."""
    expired: list[str] = []
    remaining: list[ActiveBuff] = []
    for buff in char.buffs:
        buff.remaining_turns -= 1
        if buff.remaining_turns <= 0:
            expired.append(f"{buff.source_name} wore off on {char.name}.")
        else:
            remaining.append(buff)
    char.buffs = remaining
    return expired
