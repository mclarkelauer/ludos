"""Quest and objective definitions for the Goblin Caves quest."""

from examples.dungeon_quest.content.types import (
    ObjectiveDef,
    ObjectiveType,
    QuestDef,
)

# ── Main Quest ──

MAIN_QUEST = QuestDef(
    quest_id="main_quest",
    name="The Goblin Caves",
    description="Clear the goblin caves and defeat Chief Grukk to save Millbrook Village.",
    objectives=(
        ObjectiveDef(
            objective_id="obj_talk_elder",
            description="Speak with Elder Maren in Millbrook Village",
            objective_type=ObjectiveType.TALK_TO_NPC,
            target="elder_talk",
        ),
        ObjectiveDef(
            objective_id="obj_reach_caves",
            description="Reach the Cave Entrance",
            objective_type=ObjectiveType.REACH_AREA,
            target="cave_entrance",
        ),
        ObjectiveDef(
            objective_id="obj_defeat_chief",
            description="Defeat Goblin Chief Grukk",
            objective_type=ObjectiveType.DEFEAT_ENCOUNTER,
            target="goblin_chief_battle",
        ),
        ObjectiveDef(
            objective_id="obj_return_village",
            description="Return to Elder Maren with the news",
            objective_type=ObjectiveType.SET_FLAG,
            target="game_victory",
            required_flag="defeated_chief",
        ),
    ),
    completion_flag="main_quest_complete",
    rewards_xp=200,
    rewards_gold=100,
)

# ── Side Quest ──

RESCUE_QUEST = QuestDef(
    quest_id="rescue_quest",
    name="Lost Villager",
    description="Find and free the captured villager in the goblin caves.",
    objectives=(
        ObjectiveDef(
            objective_id="obj_find_captive",
            description="Find the captive villager",
            objective_type=ObjectiveType.TALK_TO_NPC,
            target="captive_talk",
        ),
    ),
    completion_flag="rescue_complete",
    rewards_xp=50,
    rewards_gold=25,
)

ALL_QUESTS = (MAIN_QUEST, RESCUE_QUEST)
