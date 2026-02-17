"""Turn-based combat scene (phase-driven)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ludos import BaseGameState, BaseScene, InputEvent

from ..combat.ai import choose_enemy_action
from ..combat.resolver import (
    apply_ability,
    award_victory,
    check_combat_end,
    init_combat,
    resolve_attack,
    roll_turn_order,
)
from ..characters.stats import (
    check_level_up,
    effective_attack,
    effective_defense,
    effective_speed,
    tick_buffs,
)
from ..dice import d20
from ..rendering import colors, fonts
from ..rendering.combat_renderer import draw_combat_screen
from ..rendering.effects import (
    BuffEffect,
    DamageNumberEffect,
    EffectManager,
    HealGlowEffect,
    HitFlashEffect,
    SlashEffect,
    SpellEffect,
)
from ..rendering.layout import Layout
from ..rendering.panels import draw_panel
from ..rendering.text import draw_text
from ..state import DungeonQuestState, Enemy
from ..types import CombatPhase
from ...content.types import AbilityEffect, DamageType, ItemType, TargetType

if TYPE_CHECKING:
    from ludos import GameEngine


ACTIONS = ["Attack", "Abilities", "Items", "Defend", "Flee"]


class CombatScene(BaseScene):
    input_repeat_delay = 0.15

    def __init__(self, engine: GameEngine, ctx, encounter_id: str) -> None:
        self._engine = engine
        self._ctx = ctx
        self._encounter_id = encounter_id
        self._layout: Layout | None = None
        self._effects = EffectManager()
        self._resolve_delay = 0.0
        self._victory_delay = 0.0

    def on_enter(self, state: BaseGameState) -> None:
        s = self._cast(state)
        init_combat(self._encounter_id, s, self._ctx)
        s.combat.phase = CombatPhase.ROLLING_INITIATIVE
        window = self._engine.window
        if window:
            self._layout = Layout(window.width, window.height)

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        s = self._cast(state)
        combat = s.combat
        phase = combat.phase

        if phase == CombatPhase.INTRO:
            if event.action == "confirm":
                combat.phase = CombatPhase.ROLLING_INITIATIVE
            return

        if phase == CombatPhase.CHOOSE_ACTION:
            if event.action == "move_up":
                combat.action_cursor = (combat.action_cursor - 1) % len(ACTIONS)
            elif event.action == "move_down":
                combat.action_cursor = (combat.action_cursor + 1) % len(ACTIONS)
            elif event.action == "confirm":
                self._select_action(s)
            return

        if phase == CombatPhase.CHOOSE_TARGET:
            alive_enemies = [e for e in combat.enemies if not e.is_dead]
            if event.action == "move_up":
                combat.target_cursor = (combat.target_cursor - 1) % len(alive_enemies)
            elif event.action == "move_down":
                combat.target_cursor = (combat.target_cursor + 1) % len(alive_enemies)
            elif event.action == "confirm":
                self._attack_target(s)
            elif event.action == "cancel":
                combat.phase = CombatPhase.CHOOSE_ACTION
            return

        if phase == CombatPhase.CHOOSE_ABILITY:
            char = self._current_char(s)
            usable = self._usable_abilities(s)
            if not usable:
                combat.phase = CombatPhase.CHOOSE_ACTION
                return
            if event.action == "move_up":
                combat.ability_cursor = (combat.ability_cursor - 1) % len(usable)
            elif event.action == "move_down":
                combat.ability_cursor = (combat.ability_cursor + 1) % len(usable)
            elif event.action == "confirm":
                self._use_ability(s)
            elif event.action == "cancel":
                combat.phase = CombatPhase.CHOOSE_ACTION
            return

        if phase == CombatPhase.CHOOSE_ITEM:
            usable = self._usable_items(s)
            if not usable:
                combat.phase = CombatPhase.CHOOSE_ACTION
                return
            if event.action == "move_up":
                combat.item_cursor = (combat.item_cursor - 1) % len(usable)
            elif event.action == "move_down":
                combat.item_cursor = (combat.item_cursor + 1) % len(usable)
            elif event.action == "confirm":
                self._use_combat_item(s)
            elif event.action == "cancel":
                combat.phase = CombatPhase.CHOOSE_ACTION
            return

        if phase in (CombatPhase.VICTORY, CombatPhase.DEFEAT):
            if event.action == "confirm":
                self._end_combat(s)
            return

    def update(self, dt: float, state: BaseGameState) -> None:
        s = self._cast(state)
        combat = s.combat
        self._effects.update(dt)

        if combat.phase == CombatPhase.ROLLING_INITIATIVE:
            combat.turn_order = roll_turn_order(s.party, combat.enemies, self._ctx)
            combat.current_turn_index = 0
            combat.combat_log.append("Battle begins!")
            self._advance_turn(s)

        elif combat.phase == CombatPhase.RESOLVING:
            self._resolve_delay += dt
            if self._resolve_delay > 0.8:
                self._resolve_delay = 0.0
                self._after_resolve(s)

        elif combat.phase == CombatPhase.ENEMY_TURN:
            self._resolve_delay += dt
            if self._resolve_delay > 0.6:
                self._resolve_delay = 0.0
                self._do_enemy_turn(s)

        elif combat.phase == CombatPhase.FLEE_CHECK:
            self._resolve_delay += dt
            if self._resolve_delay > 0.5:
                self._resolve_delay = 0.0
                combat.phase = CombatPhase.CHOOSE_ACTION

        elif combat.phase in (CombatPhase.VICTORY, CombatPhase.DEFEAT):
            self._victory_delay += dt

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        s = self._cast(state)
        if not self._layout:
            return

        combat = s.combat
        phase = combat.phase

        # Build action/sub menus based on phase
        action_items = None
        action_cursor = 0
        sub_items = None
        sub_cursor = 0
        show_targets = False

        if phase == CombatPhase.CHOOSE_ACTION:
            action_items = ACTIONS
            action_cursor = combat.action_cursor

        elif phase == CombatPhase.CHOOSE_TARGET:
            action_items = ACTIONS
            action_cursor = combat.action_cursor
            alive = [e for e in combat.enemies if not e.is_dead]
            sub_items = [e.name for e in alive]
            sub_cursor = combat.target_cursor
            show_targets = True

        elif phase == CombatPhase.CHOOSE_ABILITY:
            usable = self._usable_abilities(s)
            sub_items = [f"{a.name} ({a.cost}MP)" for a in usable]
            sub_cursor = combat.ability_cursor

        elif phase == CombatPhase.CHOOSE_ITEM:
            usable = self._usable_items(s)
            sub_items = [self._ctx.items[iid].name for iid in usable]
            sub_cursor = combat.item_cursor

        draw_combat_screen(
            surface,
            self._layout,
            combat,
            s.party,
            action_items=action_items,
            action_cursor=action_cursor,
            sub_items=sub_items,
            sub_cursor=sub_cursor,
            show_targets=show_targets,
            effects=self._effects,
        )

        # Phase-specific overlays
        if phase in (CombatPhase.VICTORY, CombatPhase.DEFEAT):
            overlay = pygame.Surface((self._layout.width, self._layout.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            font = fonts.large()
            if phase == CombatPhase.VICTORY:
                txt = "VICTORY!"
                color = colors.YELLOW
            else:
                txt = "DEFEAT..."
                color = colors.HP_RED
            txt_surf = font.render(txt, True, color)
            rect = txt_surf.get_rect(center=(self._layout.width // 2, self._layout.height // 3))
            surface.blit(txt_surf, rect)

            # Show rewards for victory
            if phase == CombatPhase.VICTORY and self._victory_delay > 0.5:
                info_font = fonts.normal()
                y = self._layout.height // 2
                for line in combat.combat_log[-5:]:
                    info_surf = info_font.render(line, True, colors.WHITE)
                    info_rect = info_surf.get_rect(center=(self._layout.width // 2, y))
                    surface.blit(info_surf, info_rect)
                    y += 28

            prompt = fonts.small().render("[Enter] to continue", True, colors.LIGHT_GRAY)
            surface.blit(prompt, prompt.get_rect(center=(self._layout.width // 2, self._layout.height * 3 // 4)))

    # -- Internal helpers --

    def _cast(self, state: BaseGameState) -> DungeonQuestState:
        assert isinstance(state, DungeonQuestState)
        return state

    def _target_screen_pos(self, index: int, is_enemy: bool) -> tuple[int, int]:
        """Compute screen position for effects based on arena layout."""
        if not self._layout:
            return (400, 200)
        layout = self._layout
        arena_y = layout.height // 3 + layout.height // 6  # center of arena
        if is_enemy:
            x = layout.width - 80 - index * 60
        else:
            x = 60 + index * 60
        return (x, arena_y)

    def _spawn_attack_effects(self, target_idx: int, is_enemy_target: bool, damage: int | None = None) -> None:
        """Spawn slash + hit flash + damage number on target."""
        x, y = self._target_screen_pos(target_idx, is_enemy_target)
        self._effects.add(SlashEffect(x, y))
        self._effects.add(HitFlashEffect(x, y))
        if damage is not None:
            text = str(damage)
            color = colors.DAMAGE_COLOR
            if damage == 0:
                text = "MISS"
                color = colors.LIGHT_GRAY
            self._effects.add(DamageNumberEffect(x, y - 20, text, color))

    def _spawn_spell_effects(self, target_idx: int, is_enemy_target: bool, damage_type: str = "FIRE", value: int = 0) -> None:
        """Spawn spell particles + damage number."""
        x, y = self._target_screen_pos(target_idx, is_enemy_target)
        self._effects.add(SpellEffect(x, y, damage_type))
        self._effects.add(HitFlashEffect(x, y))
        if value:
            self._effects.add(DamageNumberEffect(x, y - 20, str(value), colors.DAMAGE_COLOR))

    def _spawn_heal_effects(self, target_idx: int, is_enemy_target: bool, amount: int = 0) -> None:
        """Spawn heal glow + green number."""
        x, y = self._target_screen_pos(target_idx, is_enemy_target)
        self._effects.add(HealGlowEffect(x, y))
        if amount:
            self._effects.add(DamageNumberEffect(x, y - 20, f"+{amount}", colors.HEAL_COLOR))

    def _spawn_buff_effects(self, target_idx: int, is_enemy_target: bool, is_debuff: bool = False) -> None:
        """Spawn buff/debuff sparkle."""
        x, y = self._target_screen_pos(target_idx, is_enemy_target)
        color = colors.DEBUFF_COLOR if is_debuff else colors.BUFF_COLOR
        self._effects.add(BuffEffect(x, y, color))

    def _current_char(self, s: DungeonQuestState) -> str | None:
        """Get current actor name from turn order."""
        combat = s.combat
        if combat.current_turn_index < len(combat.turn_order):
            return combat.turn_order[combat.current_turn_index]
        return None

    def _find_char(self, s: DungeonQuestState, name: str):
        for c in s.party:
            if c.name == name:
                return c
        return None

    def _find_enemy(self, s: DungeonQuestState, name: str):
        for e in s.combat.enemies:
            if e.name == name:
                return e
        return None

    def _advance_turn(self, s: DungeonQuestState) -> None:
        """Advance to the next living combatant's turn."""
        combat = s.combat

        while combat.current_turn_index < len(combat.turn_order):
            name = combat.turn_order[combat.current_turn_index]
            combat.current_actor = name

            # Check if combatant is alive
            char = self._find_char(s, name)
            if char and not char.is_dead:
                # Tick buffs
                msgs = tick_buffs(char)
                combat.combat_log.extend(msgs)
                combat.phase = CombatPhase.CHOOSE_ACTION
                combat.action_cursor = 0
                combat.combat_log.append(f"--- {name}'s turn ---")
                return

            enemy = self._find_enemy(s, name)
            if enemy and not enemy.is_dead:
                combat.phase = CombatPhase.ENEMY_TURN
                combat.combat_log.append(f"--- {name}'s turn ---")
                return

            combat.current_turn_index += 1

        # All turns done — new round
        combat.phase = CombatPhase.ROLLING_INITIATIVE

    def _select_action(self, s: DungeonQuestState) -> None:
        combat = s.combat
        action = ACTIONS[combat.action_cursor]

        if action == "Attack":
            combat.target_cursor = 0
            combat.phase = CombatPhase.CHOOSE_TARGET

        elif action == "Abilities":
            usable = self._usable_abilities(s)
            if usable:
                combat.ability_cursor = 0
                combat.phase = CombatPhase.CHOOSE_ABILITY
            else:
                combat.combat_log.append("No abilities available!")

        elif action == "Items":
            usable = self._usable_items(s)
            if usable:
                combat.item_cursor = 0
                combat.phase = CombatPhase.CHOOSE_ITEM
            else:
                combat.combat_log.append("No usable items!")

        elif action == "Defend":
            name = combat.current_actor
            combat.defending.add(name)
            combat.combat_log.append(f"{name} takes a defensive stance.")
            self._next_turn(s)

        elif action == "Flee":
            enc = self._ctx.encounters[combat.encounter_id]
            if enc.is_boss:
                combat.combat_log.append("Cannot flee from a boss battle!")
            else:
                roll = d20()
                if roll > 10:
                    combat.combat_log.append(f"Fled successfully! (rolled {roll})")
                    self._engine.scene_manager.pop(s)
                else:
                    combat.combat_log.append(f"Failed to flee! (rolled {roll})")
                    combat.phase = CombatPhase.FLEE_CHECK
                    self._resolve_delay = 0.0

    def _attack_target(self, s: DungeonQuestState) -> None:
        combat = s.combat
        char = self._find_char(s, combat.current_actor)
        if not char:
            return

        alive = [e for e in combat.enemies if not e.is_dead]
        if not alive:
            return
        target_idx = combat.target_cursor % len(alive)
        target = alive[target_idx]

        old_hp = target.current_hp
        atk = effective_attack(char, self._ctx)
        msgs = resolve_attack(
            char.name,
            atk,
            target.name,
            target.defense,
            lambda dmg: self._apply_damage_enemy(target, dmg),
            target.name in combat.defending,
            power=atk,
        )
        damage_dealt = old_hp - target.current_hp
        self._spawn_attack_effects(target_idx, True, damage_dealt)
        combat.combat_log.extend(msgs)
        combat.phase = CombatPhase.RESOLVING
        self._resolve_delay = 0.0

    def _apply_damage_enemy(self, enemy: Enemy, dmg: int) -> None:
        enemy.current_hp = max(0, enemy.current_hp - dmg)
        if enemy.current_hp <= 0:
            enemy.is_dead = True

    def _usable_abilities(self, s: DungeonQuestState):
        char = self._find_char(s, s.combat.current_actor)
        if not char:
            return []
        return [a for a in char.abilities if a.cost <= char.current_mp]

    def _usable_items(self, s: DungeonQuestState) -> list[str]:
        seen: set[str] = set()
        usable: list[str] = []
        for item_id in s.inventory:
            if item_id in seen:
                continue
            seen.add(item_id)
            if item_id in self._ctx.items:
                item = self._ctx.items[item_id]
                if item.item_type == ItemType.CONSUMABLE:
                    usable.append(item_id)
        return usable

    def _use_ability(self, s: DungeonQuestState) -> None:
        combat = s.combat
        char = self._find_char(s, combat.current_actor)
        if not char:
            return
        usable = self._usable_abilities(s)
        if not usable:
            return
        ability = usable[combat.ability_cursor % len(usable)]
        char.current_mp -= ability.cost

        # Determine damage type string for effects
        dmg_type = getattr(ability, "damage_type", DamageType.PHYSICAL)
        dmg_type_str = dmg_type.name if dmg_type else "PHYSICAL"

        # Determine targets
        if ability.target == TargetType.SINGLE_ENEMY:
            alive = [e for e in combat.enemies if not e.is_dead]
            targets = [alive[0]] if alive else []
            msgs = apply_ability(char.name, ability, targets, False, s, self._ctx)
            if alive:
                self._spawn_spell_effects(0, True, dmg_type_str)
        elif ability.target == TargetType.ALL_ENEMIES:
            targets = [e for e in combat.enemies if not e.is_dead]
            msgs = apply_ability(char.name, ability, targets, False, s, self._ctx)
            for i in range(len(targets)):
                self._spawn_spell_effects(i, True, dmg_type_str)
        elif ability.target == TargetType.SINGLE_ALLY:
            alive = [c for c in s.party if not c.is_dead]
            target = min(alive, key=lambda c: c.current_hp / max(1, c.max_hp)) if alive else None
            msgs = apply_ability(char.name, ability, [target] if target else [], True, s, self._ctx)
            if target and ability.effect == AbilityEffect.HEAL:
                idx = next((i for i, c in enumerate(s.party) if c.name == target.name and not c.is_dead), 0)
                self._spawn_heal_effects(idx, False)
            elif target:
                idx = next((i for i, c in enumerate(s.party) if c.name == target.name and not c.is_dead), 0)
                self._spawn_buff_effects(idx, False)
        elif ability.target == TargetType.ALL_ALLIES:
            targets = [c for c in s.party if not c.is_dead]
            msgs = apply_ability(char.name, ability, targets, True, s, self._ctx)
            for i in range(len(targets)):
                if ability.effect == AbilityEffect.HEAL:
                    self._spawn_heal_effects(i, False)
                else:
                    self._spawn_buff_effects(i, False)
        elif ability.target == TargetType.SELF:
            msgs = apply_ability(char.name, ability, [char], True, s, self._ctx)
            idx = next((i for i, c in enumerate(s.party) if c.name == char.name), 0)
            if ability.effect == AbilityEffect.HEAL:
                self._spawn_heal_effects(idx, False)
            else:
                self._spawn_buff_effects(idx, False)
        else:
            msgs = []

        combat.combat_log.extend(msgs)
        combat.phase = CombatPhase.RESOLVING
        self._resolve_delay = 0.0

    def _use_combat_item(self, s: DungeonQuestState) -> None:
        combat = s.combat
        usable = self._usable_items(s)
        if not usable:
            return
        item_id = usable[combat.item_cursor % len(usable)]
        item = self._ctx.items[item_id]

        # Use on current actor
        char = self._find_char(s, combat.current_actor)
        if not char:
            return

        s.inventory.remove(item_id)
        msgs = []
        char_idx = next((i for i, c in enumerate(s.party) if c.name == char.name), 0)
        if item.heal_amount:
            old_hp = char.current_hp
            char.current_hp = min(char.max_hp, char.current_hp + item.heal_amount)
            healed = char.current_hp - old_hp
            msgs.append(f"{char.name} uses {item.name}! Recovered {healed} HP.")
            self._spawn_heal_effects(char_idx, False, healed)
        if item.mp_restore:
            old_mp = char.current_mp
            char.current_mp = min(char.max_mp, char.current_mp + item.mp_restore)
            msgs.append(f"{char.name} recovers {char.current_mp - old_mp} MP.")
            self._spawn_buff_effects(char_idx, False)
        if not msgs:
            msgs.append(f"{char.name} uses {item.name}.")

        combat.combat_log.extend(msgs)
        combat.phase = CombatPhase.RESOLVING
        self._resolve_delay = 0.0

    def _do_enemy_turn(self, s: DungeonQuestState) -> None:
        combat = s.combat
        enemy = self._find_enemy(s, combat.current_actor)
        if not enemy or enemy.is_dead:
            self._next_turn(s)
            return

        action_type, target = choose_enemy_action(enemy, s.party, s)

        if action_type == "ability" and target:
            ability, targets = target
            enemy.mp -= ability.cost
            msgs = apply_ability(enemy.name, ability, targets, isinstance(targets[0], Enemy), s, self._ctx)
            combat.combat_log.extend(msgs)
            # Spawn spell effects on targets
            dmg_type = getattr(ability, "damage_type", DamageType.PHYSICAL)
            dmg_type_str = dmg_type.name if dmg_type else "PHYSICAL"
            is_ally_target = isinstance(targets[0], Enemy)
            for i in range(len(targets)):
                if ability.effect == AbilityEffect.HEAL:
                    self._spawn_heal_effects(i, is_ally_target)
                else:
                    self._spawn_spell_effects(i, not is_ally_target, dmg_type_str)
        elif action_type == "attack" and target:
            char = target
            old_hp = char.current_hp
            char_def = effective_defense(char, self._ctx)
            msgs = resolve_attack(
                enemy.name,
                enemy.attack,
                char.name,
                char_def,
                lambda dmg, c=char: self._apply_damage_char(c, dmg),
                char.name in combat.defending,
                power=enemy.attack,
            )
            combat.combat_log.extend(msgs)
            damage_dealt = old_hp - char.current_hp
            char_idx = next((i for i, c in enumerate(s.party) if c.name == char.name), 0)
            self._spawn_attack_effects(char_idx, False, damage_dealt)

        combat.phase = CombatPhase.RESOLVING
        self._resolve_delay = 0.0

    def _apply_damage_char(self, char, dmg: int) -> None:
        char.current_hp = max(0, char.current_hp - dmg)
        if char.current_hp <= 0:
            char.is_dead = True

    def _after_resolve(self, s: DungeonQuestState) -> None:
        result = check_combat_end(s)
        if result == "victory":
            msgs = award_victory(s, self._ctx)
            s.combat.combat_log.extend(msgs)
            # Check level ups
            for char in s.party:
                if not char.is_dead:
                    cls_def = self._ctx.classes.get(char.char_class)
                    if cls_def and check_level_up(char, cls_def):
                        s.combat.combat_log.append(f"{char.name} leveled up to {char.level}!")
            s.combat.phase = CombatPhase.VICTORY
            self._victory_delay = 0.0
        elif result == "defeat":
            enc = self._ctx.encounters[s.combat.encounter_id]
            if enc.defeat_text:
                s.combat.combat_log.append(enc.defeat_text)
            s.combat.phase = CombatPhase.DEFEAT
            self._victory_delay = 0.0
        else:
            self._next_turn(s)

    def _next_turn(self, s: DungeonQuestState) -> None:
        s.combat.current_turn_index += 1
        self._advance_turn(s)

    def _end_combat(self, s: DungeonQuestState) -> None:
        if s.combat.phase == CombatPhase.VICTORY:
            # Clear defending
            s.combat.defending.clear()
            # Clear buffs
            for char in s.party:
                char.buffs.clear()
            self._engine.scene_manager.pop(s)
        elif s.combat.phase == CombatPhase.DEFEAT:
            from .game_over import GameOverScene
            scene = GameOverScene(self._engine, self._ctx, victory=False)
            self._engine.scene_manager.clear(s)
            self._engine.scene_manager.push(scene, s)
