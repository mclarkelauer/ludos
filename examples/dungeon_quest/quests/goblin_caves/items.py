"""Equipment and consumable definitions for the Goblin Caves quest."""

from examples.dungeon_quest.content.types import (
    CharacterClass,
    EquipmentSlot,
    ItemDef,
    ItemType,
)

# ── Equipment ──

IRON_SWORD = ItemDef(
    item_id="iron_sword",
    name="Iron Sword",
    description="A sturdy iron blade.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.WEAPON,
    attack_bonus=3,
)

STEEL_SWORD = ItemDef(
    item_id="steel_sword",
    name="Steel Sword",
    description="A well-forged steel blade. Warriors only.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.WEAPON,
    attack_bonus=5,
    class_restriction=CharacterClass.WARRIOR,
)

DAGGER = ItemDef(
    item_id="dagger",
    name="Sharp Dagger",
    description="A swift dagger favored by rogues.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.WEAPON,
    attack_bonus=2,
    speed_bonus=2,
)

MAGIC_STAFF = ItemDef(
    item_id="magic_staff",
    name="Oak Staff",
    description="A staff humming with arcane energy.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.WEAPON,
    attack_bonus=1,
    mp_bonus=10,
    class_restriction=CharacterClass.MAGE,
)

HOLY_MACE = ItemDef(
    item_id="holy_mace",
    name="Holy Mace",
    description="A blessed mace for the devout.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.WEAPON,
    attack_bonus=3,
    class_restriction=CharacterClass.CLERIC,
)

LEATHER_ARMOR = ItemDef(
    item_id="leather_armor",
    name="Leather Armor",
    description="Light but protective leather armor.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.ARMOR,
    defense_bonus=2,
)

CHAIN_MAIL = ItemDef(
    item_id="chain_mail",
    name="Chain Mail",
    description="Interlocking metal rings for solid protection.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.ARMOR,
    defense_bonus=4,
    speed_bonus=-1,
)

CLOAK_OF_SHADOWS = ItemDef(
    item_id="cloak_shadows",
    name="Cloak of Shadows",
    description="A dark cloak that enhances stealth.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.ARMOR,
    defense_bonus=1,
    speed_bonus=3,
    class_restriction=CharacterClass.ROGUE,
)

AMULET_OF_VIGOR = ItemDef(
    item_id="amulet_vigor",
    name="Amulet of Vigor",
    description="Grants the wearer extra vitality.",
    item_type=ItemType.EQUIPMENT,
    slot=EquipmentSlot.ACCESSORY,
    hp_bonus=15,
)

# ── Consumables ──

HEALTH_POTION = ItemDef(
    item_id="health_potion",
    name="Health Potion",
    description="Restores 30 HP.",
    item_type=ItemType.CONSUMABLE,
    heal_amount=30,
)

MANA_POTION = ItemDef(
    item_id="mana_potion",
    name="Mana Potion",
    description="Restores 20 MP.",
    item_type=ItemType.CONSUMABLE,
    mp_restore=20,
)

ELIXIR = ItemDef(
    item_id="elixir",
    name="Elixir",
    description="Restores 50 HP and 30 MP.",
    item_type=ItemType.CONSUMABLE,
    heal_amount=50,
    mp_restore=30,
)

# ── Key Items ──

CAVE_KEY = ItemDef(
    item_id="cave_key",
    name="Cave Key",
    description="A rusty key found on a goblin chief.",
    item_type=ItemType.KEY_ITEM,
)

ALL_ITEMS = (
    IRON_SWORD, STEEL_SWORD, DAGGER, MAGIC_STAFF, HOLY_MACE,
    LEATHER_ARMOR, CHAIN_MAIL, CLOAK_OF_SHADOWS, AMULET_OF_VIGOR,
    HEALTH_POTION, MANA_POTION, ELIXIR, CAVE_KEY,
)
