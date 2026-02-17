"""Quest objective checking, flag management, and completion."""

from __future__ import annotations

from ..context import GameContext
from ..state import DungeonQuestState
from ...content.types import ObjectiveType


def check_objective(
    objective_id: str,
    state: DungeonQuestState,
    ctx: GameContext,
) -> bool:
    """Check if a specific objective is met."""
    # Find the objective
    for quest in ctx.quests.values():
        for obj in quest.objectives:
            if obj.objective_id != objective_id:
                continue

            if obj.required_flag and obj.required_flag not in state.quest.flags:
                return False

            if obj.objective_type == ObjectiveType.DEFEAT_ENCOUNTER:
                enc = ctx.encounters.get(obj.target)
                if enc and enc.on_victory_set_flag:
                    return enc.on_victory_set_flag in state.quest.flags
                return False

            elif obj.objective_type == ObjectiveType.REACH_AREA:
                return f"reached_{obj.target}" in state.quest.flags

            elif obj.objective_type == ObjectiveType.OBTAIN_ITEM:
                return obj.target in state.inventory

            elif obj.objective_type == ObjectiveType.SET_FLAG:
                return obj.target in state.quest.flags

            elif obj.objective_type == ObjectiveType.TALK_TO_NPC:
                return f"talked_{obj.target}" in state.quest.flags

    return False


def update_quests(state: DungeonQuestState, ctx: GameContext) -> list[str]:
    """Check all active quests for completion. Returns messages."""
    messages: list[str] = []

    # Auto-activate quests that don't have prerequisites
    for quest_id, quest in ctx.quests.items():
        if quest_id in state.quest.active_quests or quest_id in state.quest.completed_quests:
            continue
        # Activate if the first objective has no prerequisite flag
        first_obj = quest.objectives[0] if quest.objectives else None
        can_start = first_obj is None or not first_obj.required_flag or first_obj.required_flag in state.quest.flags
        if can_start:
            state.quest.active_quests.append(quest_id)
            messages.append(f"New quest: {quest.name}")

    # Check objectives for active quests
    for quest_id in list(state.quest.active_quests):
        quest = ctx.quests.get(quest_id)
        if not quest:
            continue

        all_complete = True
        for obj in quest.objectives:
            if obj.objective_id in state.quest.completed_objectives:
                continue
            if check_objective(obj.objective_id, state, ctx):
                state.quest.completed_objectives.add(obj.objective_id)
                messages.append(f"Objective complete: {obj.description}")
            else:
                all_complete = False

        if all_complete:
            state.quest.active_quests.remove(quest_id)
            state.quest.completed_quests.append(quest_id)
            state.quest.flags.add(quest.completion_flag)

            # Award rewards
            if quest.rewards_xp:
                alive = [c for c in state.party if not c.is_dead]
                if alive:
                    xp_each = quest.rewards_xp // len(alive)
                    for char in alive:
                        char.xp += xp_each
                messages.append(f"Earned {quest.rewards_xp} XP!")

            if quest.rewards_gold:
                state.gold += quest.rewards_gold
                messages.append(f"Earned {quest.rewards_gold} gold!")

            for item_id in quest.rewards_items:
                state.inventory.append(item_id)
                if item_id in ctx.items:
                    messages.append(f"Received: {ctx.items[item_id].name}")

            messages.append(f"Quest complete: {quest.name}!")

    return messages
