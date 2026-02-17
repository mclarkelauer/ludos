"""Dialogue tree traversal, condition evaluation, and effects."""

from __future__ import annotations

from ..context import GameContext
from ..state import DialogueState, DungeonQuestState
from ...content.types import DialogueNode, DialogueTree


def start_dialogue(
    dialogue_id: str,
    state: DungeonQuestState,
    ctx: GameContext,
) -> bool:
    """Start a dialogue tree. Returns False if not available."""
    tree = ctx.dialogues.get(dialogue_id)
    if not tree or not tree.nodes:
        return False

    if tree.required_flag and tree.required_flag not in state.quest.flags:
        return False

    state.dialogue.active_dialogue_id = dialogue_id
    state.dialogue.current_node_id = tree.nodes[0].node_id
    state.dialogue.choice_cursor = 0
    state.dialogue.typewriter_progress = 0.0
    state.dialogue.typewriter_done = False
    state.dialogue.waiting_for_input = False
    return True


def get_current_node(
    state: DungeonQuestState,
    ctx: GameContext,
) -> DialogueNode | None:
    """Get the current dialogue node."""
    dlg_id = state.dialogue.active_dialogue_id
    node_id = state.dialogue.current_node_id
    if not dlg_id or not node_id:
        return None

    tree = ctx.dialogues.get(dlg_id)
    if not tree:
        return None

    for node in tree.nodes:
        if node.node_id == node_id:
            return node
    return None


def get_available_choices(
    node: DialogueNode,
    state: DungeonQuestState,
) -> list[tuple[int, str]]:
    """Get (index, text) for choices available given current flags."""
    available = []
    for i, choice in enumerate(node.choices):
        if choice.required_flag and choice.required_flag not in state.quest.flags:
            continue
        available.append((i, choice.text))
    return available


def apply_node_effects(
    node: DialogueNode,
    state: DungeonQuestState,
    ctx: GameContext,
) -> tuple[str | None, str | None]:
    """Apply side effects of a node. Returns (encounter_id, message)."""
    message = None

    if node.sets_flag:
        state.quest.flags.add(node.sets_flag)

    if node.gives_item:
        state.inventory.append(node.gives_item)
        if node.gives_item in ctx.items:
            message = f"Received: {ctx.items[node.gives_item].name}"

    if node.heals_party:
        for char in state.party:
            if not char.is_dead:
                char.current_hp = char.max_hp
                char.current_mp = char.max_mp
        message = "Party fully healed!"

    encounter_id = node.starts_encounter
    return encounter_id, message


def advance_dialogue(
    choice_index: int | None,
    state: DungeonQuestState,
    ctx: GameContext,
) -> tuple[bool, str | None, str | None]:
    """Advance to the next node. Returns (dialogue_ended, encounter_id, message)."""
    node = get_current_node(state, ctx)
    if not node:
        return True, None, None

    # Apply effects of current node
    encounter_id, message = apply_node_effects(node, state, ctx)

    # Determine next node
    next_node_id = None
    if node.choices and choice_index is not None:
        available = get_available_choices(node, state)
        if choice_index < len(available):
            orig_idx = available[choice_index][0]
            choice = node.choices[orig_idx]
            if choice.sets_flag:
                state.quest.flags.add(choice.sets_flag)
            next_node_id = choice.next_node_id
    elif node.next_node_id:
        next_node_id = node.next_node_id

    if next_node_id:
        state.dialogue.current_node_id = next_node_id
        state.dialogue.choice_cursor = 0
        state.dialogue.typewriter_progress = 0.0
        state.dialogue.typewriter_done = False
        state.dialogue.waiting_for_input = False
        return False, encounter_id, message

    # Dialogue ended
    # Mark dialogue as used
    dlg_id = state.dialogue.active_dialogue_id
    if dlg_id:
        state.quest.flags.add(f"talked_{dlg_id}")

    state.dialogue.active_dialogue_id = None
    state.dialogue.current_node_id = None
    return True, encounter_id, message
