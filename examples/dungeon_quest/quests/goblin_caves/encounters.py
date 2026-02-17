"""Enemy and encounter definitions for the Goblin Caves quest."""

from examples.dungeon_quest.content.types import (
    AbilityDef,
    AbilityEffect,
    DamageType,
    EncounterDef,
    EnemyDef,
    TargetType,
)

# ── Enemy Abilities ──

GOBLIN_SLASH = AbilityDef(
    name="Goblin Slash",
    description="A wild slash.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.SINGLE_ENEMY,
    power=6,
    cost=0,
    damage_type=DamageType.PHYSICAL,
)

POISON_SPIT = AbilityDef(
    name="Poison Spit",
    description="Spit venom to weaken defense.",
    effect=AbilityEffect.DEBUFF_DEFENSE,
    target=TargetType.SINGLE_ENEMY,
    power=2,
    cost=3,
    duration=2,
)

FIRE_BREATH = AbilityDef(
    name="Fire Breath",
    description="Breathe fire on all foes.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.ALL_ENEMIES,
    power=8,
    cost=5,
    damage_type=DamageType.FIRE,
)

RALLY = AbilityDef(
    name="Rally",
    description="Boost allies' attack.",
    effect=AbilityEffect.BUFF_ATTACK,
    target=TargetType.ALL_ALLIES,
    power=3,
    cost=4,
    duration=2,
)

BOSS_HEAL = AbilityDef(
    name="Dark Mending",
    description="Heal with dark energy.",
    effect=AbilityEffect.HEAL,
    target=TargetType.SELF,
    power=25,
    cost=8,
)

BOSS_SMASH = AbilityDef(
    name="Crushing Blow",
    description="A devastating overhead strike.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.SINGLE_ENEMY,
    power=18,
    cost=6,
    damage_type=DamageType.PHYSICAL,
    accuracy_bonus=2,
)

# ── Enemy Definitions ──

GOBLIN = EnemyDef(
    enemy_id="goblin",
    name="Goblin",
    hp=20,
    mp=0,
    attack=5,
    defense=3,
    speed=5,
    xp_reward=15,
    gold_reward=5,
    loot_table=(("health_potion", 0.2),),
)

GOBLIN_ARCHER = EnemyDef(
    enemy_id="goblin_archer",
    name="Goblin Archer",
    hp=15,
    mp=0,
    attack=7,
    defense=2,
    speed=6,
    xp_reward=18,
    gold_reward=7,
    loot_table=(("health_potion", 0.15),),
)

GOBLIN_SHAMAN = EnemyDef(
    enemy_id="goblin_shaman",
    name="Goblin Shaman",
    hp=22,
    mp=15,
    attack=4,
    defense=3,
    speed=4,
    xp_reward=25,
    gold_reward=10,
    abilities=(POISON_SPIT, RALLY),
    loot_table=(("mana_potion", 0.3),),
)

CAVE_BAT = EnemyDef(
    enemy_id="cave_bat",
    name="Cave Bat",
    hp=12,
    mp=0,
    attack=4,
    defense=1,
    speed=9,
    xp_reward=10,
    gold_reward=2,
)

CAVE_SPIDER = EnemyDef(
    enemy_id="cave_spider",
    name="Cave Spider",
    hp=18,
    mp=5,
    attack=6,
    defense=2,
    speed=7,
    xp_reward=20,
    gold_reward=4,
    abilities=(POISON_SPIT,),
    loot_table=(("health_potion", 0.15),),
)

GOBLIN_CHIEF = EnemyDef(
    enemy_id="goblin_chief",
    name="Goblin Chief Grukk",
    hp=80,
    mp=20,
    attack=10,
    defense=7,
    speed=5,
    xp_reward=100,
    gold_reward=50,
    abilities=(BOSS_SMASH, BOSS_HEAL, RALLY),
    loot_table=(("steel_sword", 0.5), ("amulet_vigor", 0.3), ("elixir", 1.0)),
)

ALL_ENEMIES = (GOBLIN, GOBLIN_ARCHER, GOBLIN_SHAMAN, CAVE_BAT, CAVE_SPIDER, GOBLIN_CHIEF)

# ── Encounters ──

PATROL_ENCOUNTER = EncounterDef(
    encounter_id="goblin_patrol",
    enemies=("goblin", "goblin", "goblin_archer"),
    intro_text="A goblin patrol spots you!",
    victory_text="The goblins are defeated.",
    on_victory_set_flag="defeated_patrol",
)

BAT_ENCOUNTER = EncounterDef(
    encounter_id="cave_bats",
    enemies=("cave_bat", "cave_bat", "cave_bat"),
    intro_text="Bats swarm from the darkness!",
)

SPIDER_ENCOUNTER = EncounterDef(
    encounter_id="cave_spiders",
    enemies=("cave_spider", "cave_spider"),
    intro_text="Giant spiders drop from the ceiling!",
)

SHAMAN_ENCOUNTER = EncounterDef(
    encounter_id="shaman_guard",
    enemies=("goblin_shaman", "goblin", "goblin_archer"),
    intro_text="A shaman and his guards block your path!",
    on_victory_set_flag="defeated_shaman",
)

BOSS_ENCOUNTER = EncounterDef(
    encounter_id="goblin_chief_battle",
    enemies=("goblin_chief", "goblin_shaman", "goblin"),
    is_boss=True,
    intro_text="Chief Grukk rises from his throne! 'You dare enter MY caves?!'",
    victory_text="Chief Grukk falls! The goblin threat is ended!",
    defeat_text="The goblins drag your unconscious bodies out of the cave...",
    on_victory_set_flag="defeated_chief",
)

ALL_ENCOUNTERS = (PATROL_ENCOUNTER, BAT_ENCOUNTER, SPIDER_ENCOUNTER, SHAMAN_ENCOUNTER, BOSS_ENCOUNTER)
