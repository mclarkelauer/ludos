"""Starting party and class definitions for the Goblin Caves quest."""

from examples.dungeon_quest.content.types import (
    AbilityDef,
    AbilityEffect,
    CharacterClass,
    CharacterDef,
    ClassDef,
    DamageType,
    TargetType,
)

# ── Abilities ──

# Warrior
POWER_STRIKE = AbilityDef(
    name="Power Strike",
    description="A mighty blow dealing extra damage.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.SINGLE_ENEMY,
    power=12,
    cost=4,
    damage_type=DamageType.PHYSICAL,
    accuracy_bonus=2,
)

WAR_CRY = AbilityDef(
    name="War Cry",
    description="Boosts the party's attack.",
    effect=AbilityEffect.BUFF_ATTACK,
    target=TargetType.ALL_ALLIES,
    power=3,
    cost=6,
    duration=3,
)

# Rogue
BACKSTAB = AbilityDef(
    name="Backstab",
    description="Strike a vital point for massive damage.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.SINGLE_ENEMY,
    power=15,
    cost=5,
    damage_type=DamageType.PHYSICAL,
    accuracy_bonus=4,
)

POISON_BLADE = AbilityDef(
    name="Poison Blade",
    description="Weaken an enemy's defense.",
    effect=AbilityEffect.DEBUFF_DEFENSE,
    target=TargetType.SINGLE_ENEMY,
    power=4,
    cost=4,
    duration=3,
    level_required=2,
)

# Cleric
HEAL = AbilityDef(
    name="Heal",
    description="Restore HP to one ally.",
    effect=AbilityEffect.HEAL,
    target=TargetType.SINGLE_ALLY,
    power=20,
    cost=5,
    damage_type=DamageType.HOLY,
)

HOLY_LIGHT = AbilityDef(
    name="Holy Light",
    description="Smite enemies with divine radiance.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.ALL_ENEMIES,
    power=8,
    cost=8,
    damage_type=DamageType.HOLY,
    level_required=2,
)

BLESS = AbilityDef(
    name="Bless",
    description="Raise an ally's defense.",
    effect=AbilityEffect.BUFF_DEFENSE,
    target=TargetType.SINGLE_ALLY,
    power=3,
    cost=4,
    duration=3,
)

# Mage
FIREBALL = AbilityDef(
    name="Fireball",
    description="Hurl a ball of flame at all enemies.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.ALL_ENEMIES,
    power=10,
    cost=8,
    damage_type=DamageType.FIRE,
)

ICE_SHARD = AbilityDef(
    name="Ice Shard",
    description="Pierce one enemy with a shard of ice.",
    effect=AbilityEffect.DAMAGE,
    target=TargetType.SINGLE_ENEMY,
    power=12,
    cost=5,
    damage_type=DamageType.ICE,
    accuracy_bonus=2,
)

ARCANE_SHIELD = AbilityDef(
    name="Arcane Shield",
    description="Protect yourself with magical energy.",
    effect=AbilityEffect.BUFF_DEFENSE,
    target=TargetType.SELF,
    power=5,
    cost=4,
    duration=3,
    level_required=2,
)

# ── Class Definitions ──

WARRIOR_CLASS = ClassDef(
    char_class=CharacterClass.WARRIOR,
    base_hp=50,
    base_mp=10,
    base_attack=8,
    base_defense=6,
    base_speed=4,
    hp_per_level=12,
    mp_per_level=2,
    attack_per_level=3,
    defense_per_level=2,
    speed_per_level=1,
    abilities=(POWER_STRIKE, WAR_CRY),
)

ROGUE_CLASS = ClassDef(
    char_class=CharacterClass.ROGUE,
    base_hp=35,
    base_mp=15,
    base_attack=6,
    base_defense=4,
    base_speed=8,
    hp_per_level=8,
    mp_per_level=3,
    attack_per_level=2,
    defense_per_level=1,
    speed_per_level=3,
    abilities=(BACKSTAB, POISON_BLADE),
)

CLERIC_CLASS = ClassDef(
    char_class=CharacterClass.CLERIC,
    base_hp=40,
    base_mp=30,
    base_attack=5,
    base_defense=5,
    base_speed=4,
    hp_per_level=10,
    mp_per_level=6,
    attack_per_level=1,
    defense_per_level=2,
    speed_per_level=1,
    abilities=(HEAL, HOLY_LIGHT, BLESS),
)

MAGE_CLASS = ClassDef(
    char_class=CharacterClass.MAGE,
    base_hp=30,
    base_mp=40,
    base_attack=3,
    base_defense=3,
    base_speed=5,
    hp_per_level=6,
    mp_per_level=8,
    attack_per_level=1,
    defense_per_level=1,
    speed_per_level=2,
    abilities=(FIREBALL, ICE_SHARD, ARCANE_SHIELD),
)

ALL_CLASSES = (WARRIOR_CLASS, ROGUE_CLASS, CLERIC_CLASS, MAGE_CLASS)

# ── Starting Party ──

ALDRIC = CharacterDef(
    name="Aldric",
    char_class=CharacterClass.WARRIOR,
    level=1,
    starting_equipment=("iron_sword", "chain_mail"),
)

SHADOW = CharacterDef(
    name="Shadow",
    char_class=CharacterClass.ROGUE,
    level=1,
    starting_equipment=("dagger", "leather_armor"),
)

ELENA = CharacterDef(
    name="Elena",
    char_class=CharacterClass.CLERIC,
    level=1,
    starting_equipment=("holy_mace", "leather_armor"),
)

IGNIS = CharacterDef(
    name="Ignis",
    char_class=CharacterClass.MAGE,
    level=1,
    starting_equipment=("magic_staff",),
)

STARTING_PARTY = (ALDRIC, SHADOW, ELENA, IGNIS)
