"""Enemy action selection heuristics."""

from __future__ import annotations

import random

from ...content.types import AbilityEffect, TargetType
from ..state import Character, DungeonQuestState, Enemy


def choose_enemy_action(
    enemy: Enemy,
    party: list[Character],
    state: DungeonQuestState,
) -> tuple[str, object | None]:
    """Choose an action for an enemy.

    Returns (action_type, target_or_ability) where action_type is:
    - "attack": target is a Character
    - "ability": target is (AbilityDef, targets_list)
    """
    alive_party = [c for c in party if not c.is_dead]
    if not alive_party:
        return "attack", alive_party[0] if alive_party else None

    # Check if should heal (HP < 30%)
    if enemy.current_hp < enemy.max_hp * 0.3:
        heal_abilities = [
            a for a in enemy.abilities
            if a.effect == AbilityEffect.HEAL
            and a.cost <= enemy.mp
            and a.target in (TargetType.SELF, TargetType.SINGLE_ALLY)
        ]
        if heal_abilities:
            ability = heal_abilities[0]
            return "ability", (ability, [enemy])

    # Check for AoE if >2 alive targets (40% chance)
    if len(alive_party) > 2 and random.random() < 0.4:
        aoe_abilities = [
            a for a in enemy.abilities
            if a.effect == AbilityEffect.DAMAGE
            and a.target == TargetType.ALL_ENEMIES
            and a.cost <= enemy.mp
        ]
        if aoe_abilities:
            ability = aoe_abilities[0]
            return "ability", (ability, alive_party)

    # Check for single-target abilities (30% chance)
    if random.random() < 0.3:
        single_abilities = [
            a for a in enemy.abilities
            if a.effect == AbilityEffect.DAMAGE
            and a.target == TargetType.SINGLE_ENEMY
            and a.cost <= enemy.mp
        ]
        if single_abilities:
            ability = random.choice(single_abilities)
            target = min(alive_party, key=lambda c: c.current_hp)
            return "ability", (ability, [target])

    # Default: attack lowest HP
    target = min(alive_party, key=lambda c: c.current_hp)
    return "attack", target
