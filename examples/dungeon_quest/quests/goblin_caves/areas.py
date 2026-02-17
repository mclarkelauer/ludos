"""Overworld areas and dungeon maps for the Goblin Caves quest."""

from examples.dungeon_quest.content.types import (
    AreaConnection,
    DungeonLevel,
    OverworldArea,
    TileTrigger,
    TileType,
)

T = TileType

# Shorthand aliases
F = T.FLOOR
W = T.WALL
D = T.DOOR
SD = T.STAIRS_DOWN
SU = T.STAIRS_UP
CH = T.CHEST
TR = T.TRAP
NP = T.NPC
EN = T.ENTRANCE

# ── Dungeon Level 1: Cave Entrance ──

CAVE_L1_TILES = (
    (W, W, W, W, W, W, W, W, W, W, W, W, W, W, W),
    (W, EN,F, F, F, W, F, F, F, F, F, W, F, F, W),
    (W, F, F, W, F, W, F, W, W, W, F, W, F, F, W),
    (W, F, W, W, F, F, F, F, F, W, F, F, F, W, W),
    (W, F, F, F, F, W, W, W, F, W, F, W, F, F, W),
    (W, W, W, D, W, W, F, F, F, F, F, W, W, F, W),
    (W, F, F, F, F, F, F, W, W, W, F, F, F, F, W),
    (W, F, W, W, W, W, F, W, CH,W, F, W, W, F, W),
    (W, F, F, F, F, F, F, F, F, F, F, F, F, F, W),
    (W, W, W, W, W, W, W, W, W, W, W, SD,W, W, W),
    (W, W, W, W, W, W, W, W, W, W, W, W, W, W, W),
)

CAVE_L1_TRIGGERS = (
    TileTrigger(x=8, y=7, item_id="health_potion", once=True, text="You find a health potion in the chest!"),
    TileTrigger(x=7, y=4, encounter_id="cave_bats", once=True, text="Bats!"),
    TileTrigger(x=3, y=5, encounter_id="goblin_patrol", once=True),
)

CAVE_LEVEL_1 = DungeonLevel(
    level_id="cave_l1",
    name="Goblin Caves — Entrance",
    width=15,
    height=11,
    tiles=CAVE_L1_TILES,
    player_start=(1, 1),
    triggers=CAVE_L1_TRIGGERS,
    random_encounter_ids=("cave_bats",),
    random_encounter_chance=0.08,
)

# ── Dungeon Level 2: Deep Caves ──

CAVE_L2_TILES = (
    (W, W, W, W, W, W, W, W, W, W, W, W, W, W, W),
    (W, SU,F, F, F, F, F, W, F, F, F, F, F, F, W),
    (W, F, W, W, W, W, F, W, F, W, W, W, W, F, W),
    (W, F, F, F, TR,W, F, F, F, F, F, NP,W, F, W),
    (W, W, W, W, F, W, F, W, W, W, W, W, W, F, W),
    (W, F, F, F, F, F, F, F, F, F, F, F, F, F, W),
    (W, F, W, W, W, W, W, D, W, W, W, W, W, F, W),
    (W, F, F, F, F, F, F, F, F, F, F, F, F, F, W),
    (W, W, W, W, W, W, F, W, F, W, W, W, W, F, W),
    (W, F, F, CH,F, F, F, W, F, F, F, F, SD,F, W),
    (W, W, W, W, W, W, W, W, W, W, W, W, W, W, W),
)

CAVE_L2_TRIGGERS = (
    TileTrigger(x=4, y=3, encounter_id="cave_spiders", once=True, text="Spiders ambush you!"),
    TileTrigger(x=11, y=3, dialogue_id="captive_talk", once=True),
    TileTrigger(x=7, y=6, encounter_id="shaman_guard", once=True, text="The shaman blocks your path!"),
    TileTrigger(x=3, y=9, item_id="elixir", once=True, text="You find an elixir hidden in the chest!"),
)

CAVE_LEVEL_2 = DungeonLevel(
    level_id="cave_l2",
    name="Goblin Caves — Deep Tunnels",
    width=15,
    height=11,
    tiles=CAVE_L2_TILES,
    player_start=(1, 1),
    triggers=CAVE_L2_TRIGGERS,
    random_encounter_ids=("cave_spiders", "cave_bats"),
    random_encounter_chance=0.10,
)

# ── Dungeon Level 3: Chief's Lair ──

CAVE_L3_TILES = (
    (W, W, W, W, W, W, W, W, W, W, W),
    (W, SU,F, F, F, F, F, F, F, F, W),
    (W, F, F, W, F, W, F, W, F, F, W),
    (W, F, W, F, F, F, F, F, W, F, W),
    (W, F, F, F, F, TR,F, F, F, F, W),
    (W, F, W, F, F, F, F, F, W, F, W),
    (W, F, F, W, F, CH,F, W, F, F, W),
    (W, F, F, F, F, F, F, F, F, F, W),
    (W, W, W, W, W, W, W, W, W, W, W),
)

CAVE_L3_TRIGGERS = (
    TileTrigger(x=5, y=4, encounter_id="goblin_chief_battle", once=True,
                text="Chief Grukk awaits you!"),
    TileTrigger(x=5, y=6, item_id="cave_key", once=True,
                text="You find a key behind the throne!",
                sets_flag="has_cave_key"),
)

CAVE_LEVEL_3 = DungeonLevel(
    level_id="cave_l3",
    name="Goblin Caves — Chief's Lair",
    width=11,
    height=9,
    tiles=CAVE_L3_TILES,
    player_start=(1, 1),
    triggers=CAVE_L3_TRIGGERS,
)

ALL_DUNGEON_LEVELS = (CAVE_LEVEL_1, CAVE_LEVEL_2, CAVE_LEVEL_3)

# ── Overworld Areas ──

VILLAGE = OverworldArea(
    area_id="village",
    name="Millbrook Village",
    description=(
        "A small farming village nestled in a green valley. Smoke rises from "
        "cottage chimneys, but the streets are quiet — the villagers live in fear "
        "of goblin raids from the caves to the east. The village elder stands "
        "near the well, looking worried."
    ),
    connections=(
        AreaConnection(target_area_id="forest_path", label="Forest Path (East)"),
    ),
    npcs=("elder_talk", "merchant_talk", "elder_victory"),
    rest_available=True,
)

FOREST_PATH = OverworldArea(
    area_id="forest_path",
    name="Forest Path",
    description=(
        "A narrow dirt path winds through dense forest. Broken carts and scattered "
        "supplies line the road — evidence of goblin ambushes. The trees thin out "
        "ahead, revealing a rocky hillside with a dark cave entrance."
    ),
    connections=(
        AreaConnection(target_area_id="village", label="Millbrook Village (West)"),
        AreaConnection(target_area_id="cave_entrance", label="Cave Entrance (East)"),
    ),
)

CAVE_ENTRANCE_AREA = OverworldArea(
    area_id="cave_entrance",
    name="Cave Entrance",
    description=(
        "A gaping maw of rock opens in the hillside. Crude goblin totems flank "
        "the entrance, and the smell of smoke and rotting food drifts out. "
        "Faint torchlight flickers from within. This is the Goblin Caves."
    ),
    connections=(
        AreaConnection(target_area_id="forest_path", label="Forest Path (West)"),
    ),
    dungeon_levels=("cave_l1", "cave_l2", "cave_l3"),
)

ALL_AREAS = (VILLAGE, FOREST_PATH, CAVE_ENTRANCE_AREA)
