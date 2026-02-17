"""Dice rolling utilities for D&D-style mechanics."""

from __future__ import annotations

import random


def d20() -> int:
    return random.randint(1, 20)


def d6() -> int:
    return random.randint(1, 6)


def roll_initiative(speed: int) -> int:
    return d20() + speed


def roll_attack(attack: int, accuracy_bonus: int, defense: int) -> tuple[int, bool, bool]:
    """Roll an attack.

    Returns (total_roll, is_hit, is_crit).
    Nat 1 always misses, nat 20 always crits.
    """
    roll = d20()
    if roll == 1:
        return roll, False, False
    if roll == 20:
        return roll, True, True
    total = roll + attack + accuracy_bonus
    target = 10 + defense
    return total, total >= target, False


def roll_damage(power: int, attack: int, defense: int, is_crit: bool = False) -> int:
    """Calculate damage dealt.

    damage = max(1, power + attack - defense // 2 + d6)
    Crits double the result.
    """
    base = max(1, power + attack - defense // 2 + d6())
    return base * 2 if is_crit else base
