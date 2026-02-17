"""Tile grid movement, collision, and trigger detection."""

from __future__ import annotations

import random

from ..context import GameContext
from ..state import DungeonQuestState
from ...content.types import DungeonLevel, TileType


def can_move(level: DungeonLevel, x: int, y: int) -> bool:
    """Check if a tile is walkable."""
    if x < 0 or y < 0 or y >= level.height or x >= level.width:
        return False
    tile = level.tiles[y][x]
    return tile != TileType.WALL


def move_player(
    dx: int,
    dy: int,
    state: DungeonQuestState,
    ctx: GameContext,
) -> tuple[str | None, str | None, str | None]:
    """Move player by delta. Returns (trigger_encounter_id, trigger_dialogue_id, message)."""
    level_id = state.exploration.dungeon_level_id
    if not level_id or level_id not in ctx.dungeon_levels:
        return None, None, None

    level = ctx.dungeon_levels[level_id]
    nx = state.exploration.player_x + dx
    ny = state.exploration.player_y + dy

    if not can_move(level, nx, ny):
        return None, None, None

    state.exploration.player_x = nx
    state.exploration.player_y = ny

    tile = level.tiles[ny][nx]
    encounter_id = None
    dialogue_id = None
    message = None

    # Check triggers
    for trigger in level.triggers:
        if trigger.x == nx and trigger.y == ny:
            trigger_key = f"{nx},{ny},{level_id}"

            if trigger.once and trigger_key in state.exploration.triggered_once:
                continue

            if trigger.once:
                state.exploration.triggered_once.add(trigger_key)

            if trigger.text:
                message = trigger.text

            if trigger.encounter_id:
                encounter_id = trigger.encounter_id
            if trigger.dialogue_id:
                dialogue_id = trigger.dialogue_id
            if trigger.item_id:
                state.inventory.append(trigger.item_id)
                if trigger.item_id in ctx.items:
                    message = f"Found: {ctx.items[trigger.item_id].name}!"
            if trigger.sets_flag:
                state.quest.flags.add(trigger.sets_flag)
            break

    # Random encounters on floor tiles
    if (
        not encounter_id
        and tile == TileType.FLOOR
        and level.random_encounter_ids
        and random.random() < level.random_encounter_chance
    ):
        encounter_id = random.choice(level.random_encounter_ids)

    return encounter_id, dialogue_id, message


def get_current_tile(state: DungeonQuestState, ctx: GameContext) -> TileType | None:
    """Get the tile type at the player's current position."""
    level_id = state.exploration.dungeon_level_id
    if not level_id or level_id not in ctx.dungeon_levels:
        return None
    level = ctx.dungeon_levels[level_id]
    x, y = state.exploration.player_x, state.exploration.player_y
    if 0 <= y < level.height and 0 <= x < level.width:
        return level.tiles[y][x]
    return None


def enter_dungeon(
    area_id: str,
    state: DungeonQuestState,
    ctx: GameContext,
) -> str | None:
    """Enter the first dungeon level of an area. Returns error or None."""
    area = ctx.areas.get(area_id)
    if not area or not area.dungeon_levels:
        return "No dungeon here."

    level_id = area.dungeon_levels[0]
    if level_id not in ctx.dungeon_levels:
        return "Dungeon level not found."

    level = ctx.dungeon_levels[level_id]
    state.exploration.dungeon_level_id = level_id
    state.exploration.in_dungeon = True
    state.exploration.player_x = level.player_start[0]
    state.exploration.player_y = level.player_start[1]
    state.exploration.dungeon_level_index = 0

    return None


def go_deeper(
    state: DungeonQuestState,
    ctx: GameContext,
) -> str | None:
    """Go to next dungeon level (stairs down). Returns error or None."""
    area = ctx.areas.get(state.exploration.current_area_id)
    if not area:
        return "No area."

    next_idx = state.exploration.dungeon_level_index + 1
    if next_idx >= len(area.dungeon_levels):
        return "No deeper levels."

    level_id = area.dungeon_levels[next_idx]
    if level_id not in ctx.dungeon_levels:
        return "Level not found."

    level = ctx.dungeon_levels[level_id]
    state.exploration.dungeon_level_id = level_id
    state.exploration.dungeon_level_index = next_idx
    state.exploration.player_x = level.player_start[0]
    state.exploration.player_y = level.player_start[1]

    return None


def exit_dungeon(state: DungeonQuestState) -> None:
    """Return to the overworld."""
    state.exploration.in_dungeon = False
    state.exploration.dungeon_level_id = None
