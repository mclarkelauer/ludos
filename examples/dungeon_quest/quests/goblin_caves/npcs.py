"""NPC dialogue trees for the Goblin Caves quest."""

from examples.dungeon_quest.content.types import (
    DialogueChoice,
    DialogueNode,
    DialogueTree,
)

# ── Village Elder ──

ELDER_DIALOGUE = DialogueTree(
    dialogue_id="elder_talk",
    nodes=(
        DialogueNode(
            node_id="elder_1",
            speaker="Elder Maren",
            text="Thank the gods you've come! Goblins have overrun the caves to the east. They've been raiding our village for weeks.",
            choices=(
                DialogueChoice(text="We'll take care of it.", next_node_id="elder_accept"),
                DialogueChoice(text="Tell me more about these goblins.", next_node_id="elder_info"),
            ),
        ),
        DialogueNode(
            node_id="elder_info",
            speaker="Elder Maren",
            text="Their chief, Grukk, is cunning and strong. He has a shaman advisor too. Be careful in those caves — they're full of traps and creatures.",
            next_node_id="elder_accept",
        ),
        DialogueNode(
            node_id="elder_accept",
            speaker="Elder Maren",
            text="Take these supplies. May fortune favor you, adventurers!",
            gives_item="health_potion",
            sets_flag="talked_to_elder",
        ),
    ),
    repeatable=False,
)

# ── Village Merchant ──

MERCHANT_DIALOGUE = DialogueTree(
    dialogue_id="merchant_talk",
    nodes=(
        DialogueNode(
            node_id="merchant_1",
            speaker="Merchant Bram",
            text="I don't have much left after the goblin raids, but take this. You'll need it more than me.",
            choices=(
                DialogueChoice(text="Thank you.", next_node_id="merchant_give"),
                DialogueChoice(text="Keep it, you need it more.", next_node_id="merchant_decline"),
            ),
        ),
        DialogueNode(
            node_id="merchant_give",
            speaker="Merchant Bram",
            text="Good luck in those caves!",
            gives_item="mana_potion",
        ),
        DialogueNode(
            node_id="merchant_decline",
            speaker="Merchant Bram",
            text="Brave and kind! Here, at least take this old cloak I found.",
            gives_item="cloak_shadows",
        ),
    ),
    repeatable=False,
)

# ── Captured Villager (in dungeon) ──

CAPTIVE_DIALOGUE = DialogueTree(
    dialogue_id="captive_talk",
    nodes=(
        DialogueNode(
            node_id="captive_1",
            speaker="Captive Villager",
            text="Please, help me! The goblins locked me in here. The chief's chambers are deeper in the caves. He keeps a key on his person.",
            choices=(
                DialogueChoice(text="We'll free you. Stay safe.", next_node_id="captive_free"),
                DialogueChoice(text="What can you tell me about what's ahead?", next_node_id="captive_info"),
            ),
        ),
        DialogueNode(
            node_id="captive_info",
            speaker="Captive Villager",
            text="There's a shaman guarding the way down. Beyond that, it's the chief's throne room. He's tough, but he heals when wounded — interrupt him if you can!",
            next_node_id="captive_free",
        ),
        DialogueNode(
            node_id="captive_free",
            speaker="Captive Villager",
            text="Thank you! I'll make my way out. Be careful down there!",
            sets_flag="freed_captive",
            heals_party=True,
        ),
    ),
    repeatable=False,
)

# ── Post-victory Elder ──

ELDER_VICTORY_DIALOGUE = DialogueTree(
    dialogue_id="elder_victory",
    nodes=(
        DialogueNode(
            node_id="ev_1",
            speaker="Elder Maren",
            text="You've done it! The goblins are routed! The village is safe once more. You are true heroes!",
            sets_flag="game_victory",
        ),
    ),
    required_flag="defeated_chief",
    repeatable=False,
)

ALL_DIALOGUES = (ELDER_DIALOGUE, MERCHANT_DIALOGUE, CAPTIVE_DIALOGUE, ELDER_VICTORY_DIALOGUE)
