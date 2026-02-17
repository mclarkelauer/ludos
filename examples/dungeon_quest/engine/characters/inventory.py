"""Equipment and inventory management."""

from __future__ import annotations

from ..context import GameContext
from ..state import Character, DungeonQuestState
from ...content.types import ItemType


def equip_item(
    char: Character, item_id: str, state: DungeonQuestState, ctx: GameContext
) -> str | None:
    """Equip an item from inventory. Returns message or None on failure."""
    if item_id not in ctx.items:
        return None
    item = ctx.items[item_id]
    if item.item_type != ItemType.EQUIPMENT or item.slot is None:
        return None
    if item.class_restriction and item.class_restriction != char.char_class:
        return f"{char.name} cannot equip {item.name}."
    if item_id not in state.inventory:
        return None

    # Unequip current item in that slot
    current = char.equipment.get(item.slot)
    if current:
        state.inventory.append(current)

    state.inventory.remove(item_id)
    char.equipment[item.slot] = item_id

    # Apply HP/MP bonuses
    if item.hp_bonus:
        char.max_hp += item.hp_bonus
        char.current_hp = min(char.current_hp + item.hp_bonus, char.max_hp)
    if item.mp_bonus:
        char.max_mp += item.mp_bonus
        char.current_mp = min(char.current_mp + item.mp_bonus, char.max_mp)

    return f"{char.name} equipped {item.name}."


def unequip_item(
    char: Character, slot, state: DungeonQuestState, ctx: GameContext
) -> str | None:
    """Unequip from a slot. Returns message or None."""
    item_id = char.equipment.get(slot)
    if not item_id:
        return None
    item = ctx.items[item_id]
    char.equipment[slot] = None
    state.inventory.append(item_id)

    # Remove HP/MP bonuses
    if item.hp_bonus:
        char.max_hp -= item.hp_bonus
        char.current_hp = min(char.current_hp, char.max_hp)
    if item.mp_bonus:
        char.max_mp -= item.mp_bonus
        char.current_mp = min(char.current_mp, char.max_mp)

    return f"{char.name} unequipped {item.name}."


def use_consumable(
    char: Character, item_id: str, state: DungeonQuestState, ctx: GameContext
) -> str | None:
    """Use a consumable item. Returns message or None."""
    if item_id not in ctx.items:
        return None
    item = ctx.items[item_id]
    if item.item_type != ItemType.CONSUMABLE:
        return None
    if item_id not in state.inventory:
        return None

    state.inventory.remove(item_id)
    messages = []

    if item.heal_amount:
        old_hp = char.current_hp
        char.current_hp = min(char.current_hp + item.heal_amount, char.max_hp)
        healed = char.current_hp - old_hp
        messages.append(f"{char.name} recovered {healed} HP")

    if item.mp_restore:
        old_mp = char.current_mp
        char.current_mp = min(char.current_mp + item.mp_restore, char.max_mp)
        restored = char.current_mp - old_mp
        messages.append(f"{char.name} recovered {restored} MP")

    if not messages:
        messages.append(f"{char.name} used {item.name}")

    return f"{char.name} used {item.name}! " + ", ".join(messages) + "."
