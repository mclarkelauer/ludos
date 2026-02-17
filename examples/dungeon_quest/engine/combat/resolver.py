"""Turn order, damage calculation, and action resolution."""

from __future__ import annotations

import random

from ...content.types import AbilityDef, AbilityEffect, TargetType
from ..context import GameContext
from ..dice import d20, roll_attack, roll_damage, roll_initiative
from ..state import ActiveBuff, Character, CombatState, DungeonQuestState, Enemy
from ..characters.stats import effective_attack, effective_defense, effective_speed


def init_combat(
    encounter_id: str,
    state: DungeonQuestState,
    ctx: GameContext,
) -> None:
    """Set up combat state from an encounter definition."""
    enc = ctx.encounters[encounter_id]
    enemies: list[Enemy] = []
    for eid in enc.enemies:
        edef = ctx.enemies[eid]
        enemies.append(
            Enemy(
                name=edef.name,
                enemy_id=edef.enemy_id,
                current_hp=edef.hp,
                max_hp=edef.hp,
                mp=edef.mp,
                attack=edef.attack,
                defense=edef.defense,
                speed=edef.speed,
                abilities=list(edef.abilities),
            )
        )

    state.combat = CombatState(
        encounter_id=encounter_id,
        enemies=enemies,
        combat_log=[],
    )
    if enc.intro_text:
        state.combat.combat_log.append(enc.intro_text)


def roll_turn_order(
    party: list[Character],
    enemies: list[Enemy],
    ctx: GameContext,
) -> list[str]:
    """Roll initiative for all combatants. Returns ordered list of names."""
    rolls: list[tuple[str, int]] = []
    for c in party:
        if not c.is_dead:
            rolls.append((c.name, roll_initiative(effective_speed(c, ctx))))
    for e in enemies:
        if not e.is_dead:
            rolls.append((e.name, roll_initiative(e.speed)))
    rolls.sort(key=lambda x: x[1], reverse=True)
    return [name for name, _ in rolls]


def resolve_attack(
    attacker_name: str,
    attacker_atk: int,
    target_name: str,
    target_def: int,
    target_hp_setter,
    defending: bool,
    accuracy_bonus: int = 0,
    power: int = 0,
) -> list[str]:
    """Resolve a basic attack. Returns log messages."""
    total, hit, crit = roll_attack(attacker_atk, accuracy_bonus, target_def)
    messages: list[str] = []

    if not hit:
        messages.append(f"{attacker_name} attacks {target_name}... Miss!")
        return messages

    dmg = roll_damage(power or attacker_atk, attacker_atk, target_def, crit)
    if defending:
        dmg = max(1, dmg // 2)

    if crit:
        messages.append(f"CRITICAL HIT! {attacker_name} strikes {target_name} for {dmg} damage!")
    else:
        messages.append(f"{attacker_name} attacks {target_name} for {dmg} damage.")

    target_hp_setter(dmg)
    return messages


def apply_ability(
    user_name: str,
    ability: AbilityDef,
    targets: list[Character] | list[Enemy],
    is_ally_target: bool,
    state: DungeonQuestState,
    ctx: GameContext,
) -> list[str]:
    """Apply an ability's effect to targets. Returns log messages."""
    messages: list[str] = []
    messages.append(f"{user_name} uses {ability.name}!")

    for target in targets:
        if ability.effect == AbilityEffect.DAMAGE:
            # Damage ability
            if isinstance(target, Character):
                target_def = effective_defense(target, ctx)
            else:
                target_def = target.defense
            dmg = max(1, ability.power + d20() // 4 - target_def // 2)
            is_defending = (
                isinstance(target, Character)
                and target.name in state.combat.defending
            )
            if is_defending:
                dmg = max(1, dmg // 2)
            target.current_hp = max(0, target.current_hp - dmg)
            messages.append(f"  {target.name} takes {dmg} {ability.damage_type.name} damage.")
            if target.current_hp <= 0:
                target.is_dead = True
                messages.append(f"  {target.name} is defeated!")

        elif ability.effect == AbilityEffect.HEAL:
            heal = ability.power + d20() // 4
            if isinstance(target, Character):
                old_hp = target.current_hp
                target.current_hp = min(target.max_hp, target.current_hp + heal)
                actual = target.current_hp - old_hp
            else:
                old_hp = target.current_hp
                target.current_hp = min(target.max_hp, target.current_hp + heal)
                actual = target.current_hp - old_hp
            messages.append(f"  {target.name} is healed for {actual} HP.")

        elif ability.effect in (
            AbilityEffect.BUFF_ATTACK,
            AbilityEffect.BUFF_DEFENSE,
            AbilityEffect.DEBUFF_ATTACK,
            AbilityEffect.DEBUFF_DEFENSE,
        ):
            buff = ActiveBuff(
                effect=ability.effect,
                power=ability.power,
                remaining_turns=max(1, ability.duration),
                source_name=ability.name,
            )
            target.buffs.append(buff)
            effect_name = ability.effect.name.replace("_", " ").title()
            messages.append(f"  {target.name} gains {effect_name} ({ability.power}) for {buff.remaining_turns} turns.")

    return messages


def check_combat_end(state: DungeonQuestState) -> str | None:
    """Check if combat should end. Returns 'victory', 'defeat', or None."""
    all_enemies_dead = all(e.is_dead for e in state.combat.enemies)
    all_party_dead = all(c.is_dead for c in state.party)

    if all_enemies_dead:
        return "victory"
    if all_party_dead:
        return "defeat"
    return None


def award_victory(state: DungeonQuestState, ctx: GameContext) -> list[str]:
    """Calculate and apply victory rewards. Returns messages."""
    enc = ctx.encounters[state.combat.encounter_id]
    messages: list[str] = []

    total_xp = 0
    total_gold = 0
    loot: list[str] = []

    for enemy in state.combat.enemies:
        edef = ctx.enemies[enemy.enemy_id]
        total_xp += edef.xp_reward
        total_gold += edef.gold_reward
        for item_id, chance in edef.loot_table:
            if random.random() < chance:
                loot.append(item_id)

    state.combat.pending_xp = total_xp
    state.combat.pending_gold = total_gold
    state.combat.pending_loot = loot
    state.gold += total_gold

    for item_id in loot:
        state.inventory.append(item_id)

    messages.append(f"Victory! Earned {total_xp} XP and {total_gold} gold.")

    for item_id in loot:
        if item_id in ctx.items:
            messages.append(f"  Found: {ctx.items[item_id].name}")

    # Distribute XP to living party members
    alive = [c for c in state.party if not c.is_dead]
    if alive:
        xp_each = total_xp // len(alive)
        for char in alive:
            char.xp += xp_each

    # Set encounter flag
    if enc.on_victory_set_flag:
        state.quest.flags.add(enc.on_victory_set_flag)

    if enc.victory_text:
        messages.append(enc.victory_text)

    return messages
