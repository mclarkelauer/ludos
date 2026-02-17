"""Goblin Caves quest — exports QUEST_PACK."""

from examples.dungeon_quest.content.pack import QuestPack

from .areas import ALL_AREAS, ALL_DUNGEON_LEVELS
from .encounters import ALL_ENCOUNTERS, ALL_ENEMIES
from .items import ALL_ITEMS
from .npcs import ALL_DIALOGUES
from .objectives import ALL_QUESTS
from .party import ALL_CLASSES, STARTING_PARTY

QUEST_PACK = QuestPack(
    name="The Goblin Caves",
    description="Clear the goblin caves and save Millbrook Village from the goblin menace!",
    starting_area_id="village",
    party=STARTING_PARTY,
    classes=ALL_CLASSES,
    areas=ALL_AREAS,
    enemies=ALL_ENEMIES,
    encounters=ALL_ENCOUNTERS,
    dialogues=ALL_DIALOGUES,
    items=ALL_ITEMS,
    quests=ALL_QUESTS,
    dungeon_levels=ALL_DUNGEON_LEVELS,
    starting_items=("health_potion", "health_potion", "mana_potion"),
    starting_gold=50,
    intro_text=(
        "The village of Millbrook has lived in peace for generations. But now, "
        "goblins have taken over the caves to the east, raiding farms and "
        "kidnapping villagers. A band of adventurers has answered the call "
        "for help. Your quest begins in Millbrook Village..."
    ),
    victory_flag="game_victory",
    victory_text=(
        "With Chief Grukk defeated and the goblins scattered, peace returns "
        "to Millbrook Village. The grateful villagers celebrate their heroes. "
        "Your adventure in the Goblin Caves is complete!"
    ),
)
