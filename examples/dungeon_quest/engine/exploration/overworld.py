"""Overworld node-graph traversal and area logic."""

from __future__ import annotations

from ..context import GameContext
from ..state import DungeonQuestState
from ...content.types import OverworldArea


def get_available_connections(
    area: OverworldArea,
    state: DungeonQuestState,
) -> list[tuple[str, str, bool]]:
    """Get (target_area_id, label, is_locked) for each connection."""
    result = []
    for conn in area.connections:
        locked = conn.required_flag is not None and conn.required_flag not in state.quest.flags
        result.append((conn.target_area_id, conn.label, locked))
    return result


def get_locked_text(area: OverworldArea, target_area_id: str) -> str:
    for conn in area.connections:
        if conn.target_area_id == target_area_id:
            return conn.locked_text
    return "The way is blocked."


def travel_to_area(
    target_area_id: str,
    state: DungeonQuestState,
    ctx: GameContext,
) -> str | None:
    """Move to a new area. Returns error message or None on success."""
    if target_area_id not in ctx.areas:
        return "Unknown area."

    current = ctx.areas.get(state.exploration.current_area_id)
    if current:
        # Verify connection exists and is unlocked
        for conn in current.connections:
            if conn.target_area_id == target_area_id:
                if conn.required_flag and conn.required_flag not in state.quest.flags:
                    return conn.locked_text
                break
        else:
            return "No path to that area."

    state.exploration.current_area_id = target_area_id
    state.exploration.in_dungeon = False
    state.exploration.dungeon_level_id = None
    state.exploration.overworld_cursor = 0

    # Set reach_area flag for quest tracking
    state.quest.flags.add(f"reached_{target_area_id}")

    return None


def get_area_actions(
    area: OverworldArea,
    state: DungeonQuestState,
    ctx: GameContext,
) -> list[str]:
    """Get list of available actions in current area."""
    actions = []

    # Travel options
    for conn in area.connections:
        locked = conn.required_flag and conn.required_flag not in state.quest.flags
        prefix = "[Locked] " if locked else ""
        actions.append(f"Travel: {prefix}{conn.label}")

    # Dungeon entry
    if area.dungeon_levels:
        actions.append("Enter Dungeon")

    # NPCs
    for dlg_id in area.npcs:
        if dlg_id in ctx.dialogues:
            dlg = ctx.dialogues[dlg_id]
            if dlg.required_flag and dlg.required_flag not in state.quest.flags:
                continue
            if not dlg.repeatable and dlg_id in state.quest.flags:
                continue
            speaker = dlg.nodes[0].speaker if dlg.nodes else "NPC"
            actions.append(f"Talk: {speaker}")

    # Rest
    if area.rest_available:
        actions.append("Rest")

    # Always available
    actions.append("Party")
    actions.append("Inventory")

    return actions
