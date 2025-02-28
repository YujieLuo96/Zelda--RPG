import pygame
import random
import math
import copy
from enum import Enum
from pygame.locals import *
from collections import defaultdict
from perlin_noise import PerlinNoise  # pip install perlin-noise

# Initialize Pygame
pygame.init()

# Game Configuration
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
TILE_SIZE = 32
PLAYER_SPEED = 4
CHUNK_SIZE = 16  # Each chunk contains 16x16 tiles

# Color Definitions
COLORS = {
    # Terrain colors
    "grass": (75, 160, 75),
    "tall_grass": (65, 140, 65),
    "forest": (35, 110, 35),
    "deep_forest": (25, 90, 25),
    "water": (65, 105, 225),
    "deep_water": (40, 75, 180),
    "sand": (235, 210, 155),
    "mountain": (130, 120, 115),
    "snow": (235, 235, 250),
    "desert": (245, 215, 145),
    "lava": (230, 80, 0),
    "stone": (140, 140, 140),
    "road": (180, 170, 160),
    "path": (200, 190, 170),
    "house": (160, 120, 90),
    "roof": (130, 60, 40),
    "village_center": (180, 140, 100),

    # UI colors
    "ui_background": (40, 40, 60, 220),
    "ui_border": (80, 80, 120),
    "ui_title": (220, 220, 255),
    "ui_text": (230, 230, 230),
    "ui_highlight": (255, 215, 0),
    "ui_button": (60, 60, 100),
    "ui_button_hover": (80, 80, 140),
    "ui_health": (220, 50, 50),
    "ui_mana": (50, 80, 220),
    "ui_exp": (240, 220, 30),
    "ui_panel": (25, 25, 40, 230),

    # Entity colors
    "player": (30, 120, 220),
    "enemy": (220, 60, 40),
    "npc": (120, 220, 120),
    "item": (220, 220, 60),

    # Currency colors
    "gold": (255, 215, 0),
    "silver": (192, 192, 192),
    "copper": (184, 115, 51),

    # Status effects
    "poison": (80, 220, 80),
    "burn": (250, 100, 20),
    "freeze": (100, 200, 255),
    "buff": (220, 180, 40)
}


# Enums
class Biome(Enum):
    PLAINS = 1
    FOREST = 2
    MOUNTAINS = 3
    DESERT = 4
    SWAMP = 5
    TUNDRA = 6
    VOLCANIC = 7
    OCEAN = 8


class TerrainType(Enum):
    GRASS = 1
    TALL_GRASS = 2
    FOREST = 3
    DEEP_FOREST = 4
    WATER = 5
    DEEP_WATER = 6
    SAND = 7
    MOUNTAIN = 8
    SNOW = 9
    DESERT = 10
    STONE = 11
    LAVA = 12
    ROAD = 13
    PATH = 14
    HOUSE = 15
    ROOF = 16
    VILLAGE_CENTER = 17


class WeaponType(Enum):
    SWORD = 1
    GREATSWORD = 2
    DAGGER = 3
    SPEAR = 4
    BOW = 5
    STAFF = 6


class ArmorType(Enum):
    LIGHT = 1
    MEDIUM = 2
    HEAVY = 3
    ROBE = 4


class SkillType(Enum):
    SLASH = 1
    FIREBALL = 2
    HEAL = 3
    CHARGE = 4
    POISON_STRIKE = 5
    FROST_NOVA = 6
    THUNDERBOLT = 7
    WHIRLWIND = 8


class MonsterType(Enum):
    SLIME = 1
    WOLF = 2
    GOBLIN = 3
    SKELETON = 4
    TROLL = 5
    GHOST = 6
    DRAGON = 7
    BANDIT = 8


class ItemType(Enum):
    WEAPON = 1
    ARMOR = 2
    POTION = 3
    MATERIAL = 4
    SCROLL = 5


class PotionType(Enum):
    HEALTH = 1
    MANA = 2
    STRENGTH = 3
    SPEED = 4
    DEFENSE = 5


# Terrain Passability
TERRAIN_PASSABLE = {
    TerrainType.GRASS: True,
    TerrainType.TALL_GRASS: True,
    TerrainType.FOREST: True,
    TerrainType.DEEP_FOREST: False,
    TerrainType.WATER: False,
    TerrainType.DEEP_WATER: False,
    TerrainType.SAND: True,
    TerrainType.MOUNTAIN: False,
    TerrainType.SNOW: True,
    TerrainType.DESERT: True,
    TerrainType.STONE: True,
    TerrainType.LAVA: False,
    TerrainType.ROAD: True,
    TerrainType.PATH: True,
    TerrainType.HOUSE: False,
    TerrainType.ROOF: False,
    TerrainType.VILLAGE_CENTER: True
}

# Biome Terrain Weights
BIOME_TERRAIN_WEIGHTS = {
    Biome.PLAINS: [
        (TerrainType.GRASS, 70),
        (TerrainType.TALL_GRASS, 20),
        (TerrainType.FOREST, 10)
    ],
    Biome.FOREST: [
        (TerrainType.FOREST, 60),
        (TerrainType.DEEP_FOREST, 20),
        (TerrainType.GRASS, 15),
        (TerrainType.WATER, 5)
    ],
    Biome.MOUNTAINS: [
        (TerrainType.STONE, 40),
        (TerrainType.MOUNTAIN, 35),
        (TerrainType.SNOW, 15),
        (TerrainType.GRASS, 10)
    ],
    Biome.DESERT: [
        (TerrainType.SAND, 70),
        (TerrainType.DESERT, 20),
        (TerrainType.STONE, 10)
    ],
    Biome.SWAMP: [
        (TerrainType.GRASS, 40),
        (TerrainType.WATER, 35),
        (TerrainType.TALL_GRASS, 25)
    ],
    Biome.TUNDRA: [
        (TerrainType.SNOW, 70),
        (TerrainType.STONE, 15),
        (TerrainType.WATER, 15)
    ],
    Biome.VOLCANIC: [
        (TerrainType.STONE, 50),
        (TerrainType.LAVA, 30),
        (TerrainType.MOUNTAIN, 20)
    ],
    Biome.OCEAN: [
        (TerrainType.DEEP_WATER, 70),
        (TerrainType.WATER, 25),
        (TerrainType.SAND, 5)
    ]
}

# Biome Monster Spawns
BIOME_MONSTER_WEIGHTS = {
    Biome.PLAINS: [
        (MonsterType.SLIME, 40),
        (MonsterType.WOLF, 30),
        (MonsterType.GOBLIN, 20),
        (MonsterType.BANDIT, 10)
    ],
    Biome.FOREST: [
        (MonsterType.WOLF, 40),
        (MonsterType.GOBLIN, 30),
        (MonsterType.BANDIT, 20),
        (MonsterType.TROLL, 10)
    ],
    Biome.MOUNTAINS: [
        (MonsterType.GOBLIN, 35),
        (MonsterType.TROLL, 30),
        (MonsterType.DRAGON, 5),
        (MonsterType.SKELETON, 30)
    ],
    Biome.DESERT: [
        (MonsterType.SKELETON, 40),
        (MonsterType.GOBLIN, 30),
        (MonsterType.BANDIT, 30)
    ],
    Biome.SWAMP: [
        (MonsterType.SLIME, 35),
        (MonsterType.GHOST, 35),
        (MonsterType.GOBLIN, 30)
    ],
    Biome.TUNDRA: [
        (MonsterType.WOLF, 40),
        (MonsterType.SKELETON, 30),
        (MonsterType.GHOST, 30)
    ],
    Biome.VOLCANIC: [
        (MonsterType.DRAGON, 30),
        (MonsterType.TROLL, 40),
        (MonsterType.GOBLIN, 30)
    ],
    Biome.OCEAN: [
        (MonsterType.SLIME, 80),
        (MonsterType.GHOST, 20)
    ]
}

# Biome Shop Configuration
BIOME_SHOPS = {
    Biome.PLAINS: {
        "items": [
            (ItemType.WEAPON, {WeaponType.SWORD: 0.5, WeaponType.BOW: 0.5}),
            (ItemType.ARMOR, {ArmorType.LIGHT: 0.7, ArmorType.MEDIUM: 0.3}),
            (ItemType.POTION, {PotionType.HEALTH: 0.7, PotionType.MANA: 0.3})
        ],
        "color": COLORS["npc"]
    },
    Biome.FOREST: {
        "items": [
            (ItemType.WEAPON, {WeaponType.BOW: 0.7, WeaponType.DAGGER: 0.3}),
            (ItemType.ARMOR, {ArmorType.LIGHT: 0.8, ArmorType.MEDIUM: 0.2}),
            (ItemType.POTION, {PotionType.HEALTH: 0.5, PotionType.MANA: 0.3, PotionType.SPEED: 0.2})
        ],
        "color": COLORS["npc"]
    },
    Biome.MOUNTAINS: {
        "items": [
            (ItemType.WEAPON, {WeaponType.GREATSWORD: 0.6, WeaponType.SPEAR: 0.4}),
            (ItemType.ARMOR, {ArmorType.MEDIUM: 0.6, ArmorType.HEAVY: 0.4}),
            (ItemType.POTION, {PotionType.HEALTH: 0.5, PotionType.STRENGTH: 0.5})
        ],
        "color": COLORS["npc"]
    },
    Biome.DESERT: {
        "items": [
            (ItemType.WEAPON, {WeaponType.SPEAR: 0.5, WeaponType.DAGGER: 0.5}),
            (ItemType.ARMOR, {ArmorType.LIGHT: 0.6, ArmorType.MEDIUM: 0.4}),
            (ItemType.POTION, {PotionType.HEALTH: 0.7, PotionType.SPEED: 0.3})
        ],
        "color": COLORS["npc"]
    },
    Biome.SWAMP: {
        "items": [
            (ItemType.WEAPON, {WeaponType.STAFF: 0.7, WeaponType.DAGGER: 0.3}),
            (ItemType.ARMOR, {ArmorType.ROBE: 0.7, ArmorType.LIGHT: 0.3}),
            (ItemType.POTION, {PotionType.MANA: 0.6, PotionType.HEALTH: 0.4})
        ],
        "color": COLORS["npc"]
    },
    Biome.TUNDRA: {
        "items": [
            (ItemType.WEAPON, {WeaponType.STAFF: 0.5, WeaponType.GREATSWORD: 0.5}),
            (ItemType.ARMOR, {ArmorType.HEAVY: 0.6, ArmorType.ROBE: 0.4}),
            (ItemType.POTION, {PotionType.HEALTH: 0.4, PotionType.MANA: 0.4, PotionType.DEFENSE: 0.2})
        ],
        "color": COLORS["npc"]
    },
    Biome.VOLCANIC: {
        "items": [
            (ItemType.WEAPON, {WeaponType.GREATSWORD: 0.8, WeaponType.STAFF: 0.2}),
            (ItemType.ARMOR, {ArmorType.HEAVY: 0.8, ArmorType.ROBE: 0.2}),
            (ItemType.POTION, {PotionType.STRENGTH: 0.5, PotionType.DEFENSE: 0.5})
        ],
        "color": COLORS["npc"]
    }
}


# Skill System
class Skill:
    def __init__(self, name, skill_type, mp_cost, effect, cooldown=0, range=1, target_type="single", description=""):
        self.name = name
        self.type = skill_type
        self.mp_cost = mp_cost
        self.effect = effect
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.range = range
        self.target_type = target_type
        self.description = description
        self.icon_color = (200, 200, 200)  # Default color

        # Set skill icon color based on type
        if skill_type == SkillType.FIREBALL:
            self.icon_color = (255, 80, 0)
        elif skill_type == SkillType.HEAL:
            self.icon_color = (80, 255, 80)
        elif skill_type == SkillType.FROST_NOVA:
            self.icon_color = (80, 180, 255)
        elif skill_type == SkillType.THUNDERBOLT:
            self.icon_color = (200, 200, 30)
        elif skill_type == SkillType.POISON_STRIKE:
            self.icon_color = (100, 220, 100)

    def can_use(self, caster):
        return caster.stats["mp"] >= self.mp_cost and self.current_cooldown <= 0

    def use(self, caster, target):
        if not self.can_use(caster):
            return f"Cannot use {self.name}: insufficient MP or on cooldown"

        # Consume MP
        caster.stats["mp"] -= self.mp_cost

        # Execute effect
        result = self.effect(caster, target)

        # Set cooldown
        self.current_cooldown = self.cooldown

        return result

    def update_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def get_info(self):
        info = f"{self.name} ({self.mp_cost} MP)\n"
        info += f"Type: {self.target_type.capitalize()}\n"
        info += f"Range: {self.range} tiles\n"
        info += f"Cooldown: {self.cooldown} turns\n"
        info += f"Description: {self.description}"
        return info


# Skill effect functions
def slash_effect(caster, target):
    """Basic slash attack with bonus damage"""
    base_dmg = caster.stats["attack"] * 1.5 - target.stats["defense"] // 2
    dmg = max(int(base_dmg), 1)
    target.stats["hp"] -= dmg
    return f"{caster.name} used Slash! Dealt {dmg} damage to {target.name}!"


def fireball_effect(caster, target):
    """Fire damage with chance to burn"""
    base_dmg = caster.stats["attack"] * 2 - target.stats["defense"] // 2
    dmg = max(int(base_dmg), 1)
    target.stats["hp"] -= dmg

    # Chance to apply burn
    if random.random() < 0.3:
        target.add_status_effect("burn", 3, 2)
        return f"{caster.name} used Fireball! Dealt {dmg} damage and burned {target.name}!"

    return f"{caster.name} used Fireball! Dealt {dmg} damage to {target.name}!"


def heal_effect(caster, target=None):
    """Restore target's HP"""
    target = caster if target is None else target
    heal_amt = caster.stats["max_hp"] // 3
    target.stats["hp"] = min(target.stats["max_hp"], target.stats["hp"] + heal_amt)
    return f"{caster.name} used Heal! Restored {heal_amt} HP!"


def charge_effect(caster, target):
    """Rush attack with knockback"""
    base_dmg = caster.stats["attack"] * 1.8 - target.stats["defense"] // 2
    dmg = max(int(base_dmg), 1)
    target.stats["hp"] -= dmg

    # Knockback logic (if target has position)
    if hasattr(target, "rect") and hasattr(caster, "rect"):
        direction_x = 1 if caster.rect.x < target.rect.x else -1
        direction_y = 1 if caster.rect.y < target.rect.y else -1
        target.rect.x += direction_x * 40
        target.rect.y += direction_y * 40

    return f"{caster.name} used Charge! Dealt {dmg} damage and knocked back {target.name}!"


def poison_strike_effect(caster, target):
    """Poison damage over time"""
    base_dmg = caster.stats["attack"] * 1.2 - target.stats["defense"] // 2
    dmg = max(int(base_dmg), 1)
    target.stats["hp"] -= dmg

    # Apply poison effect
    poison_dmg = max(caster.stats["attack"] // 4, 1)
    target.add_status_effect("poison", 4, poison_dmg)

    return f"{caster.name} used Poison Strike! Dealt {dmg} damage and poisoned {target.name}!"


def frost_nova_effect(caster, targets):
    """AoE frost damage with freeze chance"""
    total_dmg = 0
    affected = 0

    for target in targets:
        if target == caster:
            continue

        dist = ((target.rect.centerx - caster.rect.centerx) ** 2 +
                (target.rect.centery - caster.rect.centery) ** 2) ** 0.5

        if dist <= caster.stats["attack_range"] * TILE_SIZE * 2:
            base_dmg = caster.stats["attack"] * 1.3 - target.stats["defense"] // 2
            dmg = max(int(base_dmg), 1)
            target.stats["hp"] -= dmg
            total_dmg += dmg
            affected += 1

            # Chance to freeze
            if random.random() < 0.2:
                target.add_status_effect("freeze", 2)

    if affected > 0:
        return f"{caster.name} used Frost Nova! Dealt {total_dmg} damage to {affected} enemies!"
    else:
        return f"{caster.name} used Frost Nova but hit nothing!"


def thunderbolt_effect(caster, target):
    """Lightning damage with stun chance"""
    # Check for critical hit with double chance
    crit_chance = caster.stats["crit"] * 2
    is_crit = random.random() * 100 < crit_chance

    base_dmg = caster.stats["attack"] * 1.7 - target.stats["defense"] // 2
    if is_crit:
        base_dmg *= 2

    dmg = max(int(base_dmg), 1)
    target.stats["hp"] -= dmg

    # Chance to stun
    stun_msg = ""
    if random.random() < 0.25:
        target.add_status_effect("stun", 1)
        stun_msg = f" and stunned {target.name}"

    if is_crit:
        return f"{caster.name} used Thunderbolt! CRITICAL! Dealt {dmg} damage{stun_msg}!"
    else:
        return f"{caster.name} used Thunderbolt! Dealt {dmg} damage{stun_msg}!"


def whirlwind_effect(caster, targets):
    """AoE damage around caster"""
    total_dmg = 0
    affected = 0

    for target in targets:
        if target == caster:
            continue

        dist = ((target.rect.centerx - caster.rect.centerx) ** 2 +
                (target.rect.centery - caster.rect.centery) ** 2) ** 0.5

        if dist <= caster.stats["attack_range"] * TILE_SIZE * 1.5:
            base_dmg = caster.stats["attack"] * 1.1 - target.stats["defense"] // 2
            dmg = max(int(base_dmg), 1)
            target.stats["hp"] -= dmg
            total_dmg += dmg
            affected += 1

    if affected > 0:
        return f"{caster.name} used Whirlwind! Dealt {total_dmg} damage to {affected} enemies!"
    else:
        return f"{caster.name} used Whirlwind but hit nothing!"


# Define predefined skills
SKILLS = {
    SkillType.SLASH: Skill(
        name="Slash",
        skill_type=SkillType.SLASH,
        mp_cost=5,
        effect=slash_effect,
        cooldown=1,
        range=1,
        description="A powerful slash dealing 150% weapon damage."
    ),
    SkillType.FIREBALL: Skill(
        name="Fireball",
        skill_type=SkillType.FIREBALL,
        mp_cost=15,
        effect=fireball_effect,
        cooldown=3,
        range=4,
        description="Launch a fireball dealing heavy damage with a chance to burn."
    ),
    SkillType.HEAL: Skill(
        name="Heal",
        skill_type=SkillType.HEAL,
        mp_cost=20,
        effect=heal_effect,
        cooldown=4,
        range=0,
        description="Restore a significant amount of HP."
    ),
    SkillType.CHARGE: Skill(
        name="Charge",
        skill_type=SkillType.CHARGE,
        mp_cost=12,
        effect=charge_effect,
        cooldown=5,
        range=3,
        description="Charge at an enemy, dealing damage and knocking them back."
    ),
    SkillType.POISON_STRIKE: Skill(
        name="Poison Strike",
        skill_type=SkillType.POISON_STRIKE,
        mp_cost=10,
        effect=poison_strike_effect,
        cooldown=3,
        range=1,
        description="A venomous attack that poisons the target."
    ),
    SkillType.FROST_NOVA: Skill(
        name="Frost Nova",
        skill_type=SkillType.FROST_NOVA,
        mp_cost=18,
        effect=frost_nova_effect,
        cooldown=4,
        range=2,
        target_type="aoe",
        description="Release a wave of frost that damages all nearby enemies with a chance to freeze."
    ),
    SkillType.THUNDERBOLT: Skill(
        name="Thunderbolt",
        skill_type=SkillType.THUNDERBOLT,
        mp_cost=15,
        effect=thunderbolt_effect,
        cooldown=3,
        range=3,
        description="Call down lightning on a target with double critical hit chance and a chance to stun."
    ),
    SkillType.WHIRLWIND: Skill(
        name="Whirlwind",
        skill_type=SkillType.WHIRLWIND,
        mp_cost=14,
        effect=whirlwind_effect,
        cooldown=5,
        range=1,
        target_type="aoe",
        description="Spin your weapon around, hitting all nearby enemies."
    )
}

# Weapon-Skill Associations
WEAPON_SKILLS = {
    WeaponType.SWORD: [SkillType.SLASH, SkillType.CHARGE],
    WeaponType.GREATSWORD: [SkillType.SLASH, SkillType.WHIRLWIND],
    WeaponType.DAGGER: [SkillType.SLASH, SkillType.POISON_STRIKE],
    WeaponType.SPEAR: [SkillType.SLASH, SkillType.CHARGE],
    WeaponType.BOW: [SkillType.SLASH],
    WeaponType.STAFF: [SkillType.FIREBALL, SkillType.FROST_NOVA, SkillType.THUNDERBOLT]
}


# Equipment class
class Equipment:
    def __init__(self, name, item_type, stats, weapon_type=None, armor_type=None, value=0, description=""):
        self.name = name
        self.type = item_type
        self.weapon_type = weapon_type
        self.armor_type = armor_type
        self.stats = stats
        self.value = value
        self.description = description
        self.equipped = False
        self.count = 1
        self.potion_type = None
        self.skill = None

        # Set equipment range for weapons
        self.range = 1
        if weapon_type == WeaponType.SPEAR:
            self.range = 2
        elif weapon_type == WeaponType.BOW:
            self.range = 5
        elif weapon_type == WeaponType.STAFF:
            self.range = 4

        # Assign skill based on weapon type
        if weapon_type and weapon_type in WEAPON_SKILLS:
            skill_type = WEAPON_SKILLS[weapon_type][0]  # Take first skill as default
            self.skill = copy.deepcopy(SKILLS[skill_type])

    def __str__(self):
        if self.type == ItemType.WEAPON:
            return f"{self.name} ({self.weapon_type.name})"
        elif self.type == ItemType.ARMOR:
            return f"{self.name} ({self.armor_type.name})"
        else:
            return self.name

    def get_stats_text(self):
        text = f"{self.name}\n"

        if self.type == ItemType.WEAPON:
            text += f"Type: {self.weapon_type.name}\n"
            text += f"Attack: +{self.stats.get('attack', 0)}\n"
            if 'crit' in self.stats:
                text += f"Critical: +{self.stats['crit']}%\n"
            if 'agility' in self.stats:
                text += f"Agility: +{self.stats['agility']}\n"
            text += f"Range: {self.range}\n"
            if self.skill:
                text += f"Skill: {self.skill.name}\n"

        elif self.type == ItemType.ARMOR:
            text += f"Type: {self.armor_type.name}\n"
            text += f"Defense: +{self.stats.get('defense', 0)}\n"
            if 'hp' in self.stats:
                text += f"HP: +{self.stats['hp']}\n"
            if 'mp' in self.stats:
                text += f"MP: +{self.stats['mp']}\n"

        elif self.type == ItemType.POTION:
            if 'hp' in self.stats:
                text += f"Restores {self.stats['hp']} HP\n"
            if 'mp' in self.stats:
                text += f"Restores {self.stats['mp']} MP\n"
            if 'strength' in self.stats:
                text += f"Strength: +{self.stats['strength']} for {self.stats.get('duration', 60)} seconds\n"
            if 'defense' in self.stats:
                text += f"Defense: +{self.stats['defense']} for {self.stats.get('duration', 60)} seconds\n"
            if 'speed' in self.stats:
                text += f"Speed: +{self.stats['speed']} for {self.stats.get('duration', 60)} seconds\n"

        text += f"Value: {self.value} gold\n"

        if self.description:
            text += f"\n{self.description}"

        return text


# Define weapons
WEAPONS = {
    WeaponType.SWORD: Equipment(
        name="Steel Sword",
        item_type=ItemType.WEAPON,
        weapon_type=WeaponType.SWORD,
        stats={"attack": 10, "crit": 5, "agility": 3},
        value=50,
        description="A standard steel sword, reliable and sturdy."
    ),
    WeaponType.GREATSWORD: Equipment(
        name="Iron Greatsword",
        item_type=ItemType.WEAPON,
        weapon_type=WeaponType.GREATSWORD,
        stats={"attack": 18, "crit": 3, "agility": -2},
        value=120,
        description="A heavy two-handed sword with high damage but slower attack speed."
    ),
    WeaponType.DAGGER: Equipment(
        name="Assassin's Dagger",
        item_type=ItemType.WEAPON,
        weapon_type=WeaponType.DAGGER,
        stats={"attack": 6, "crit": 15, "agility": 8},
        value=80,
        description="A lightweight blade designed for quick strikes and critical hits."
    ),
    WeaponType.SPEAR: Equipment(
        name="Hunter's Spear",
        item_type=ItemType.WEAPON,
        weapon_type=WeaponType.SPEAR,
        stats={"attack": 12, "crit": 5, "agility": 0},
        value=100,
        description="A long spear with extended reach, good for keeping enemies at bay."
    ),
    WeaponType.BOW: Equipment(
        name="Recurve Bow",
        item_type=ItemType.WEAPON,
        weapon_type=WeaponType.BOW,
        stats={"attack": 9, "crit": 10, "agility": 5},
        value=90,
        description="A curved bow allowing attacks from a safe distance."
    ),
    WeaponType.STAFF: Equipment(
        name="Wizard's Staff",
        item_type=ItemType.WEAPON,
        weapon_type=WeaponType.STAFF,
        stats={"attack": 8, "crit": 5, "agility": 0, "mp": 20},
        value=110,
        description="A magical staff that enhances spellcasting abilities."
    )
}

# Define armors
ARMORS = {
    ArmorType.LIGHT: Equipment(
        name="Leather Armor",
        item_type=ItemType.ARMOR,
        armor_type=ArmorType.LIGHT,
        stats={"defense": 5, "hp": 15, "agility": 3},
        value=40,
        description="Lightweight armor made from treated hides, offering basic protection."
    ),
    ArmorType.MEDIUM: Equipment(
        name="Chainmail",
        item_type=ItemType.ARMOR,
        armor_type=ArmorType.MEDIUM,
        stats={"defense": 10, "hp": 25, "agility": 0},
        value=75,
        description="Flexible metal rings linked together providing good balance of protection and mobility."
    ),
    ArmorType.HEAVY: Equipment(
        name="Plate Armor",
        item_type=ItemType.ARMOR,
        armor_type=ArmorType.HEAVY,
        stats={"defense": 18, "hp": 40, "agility": -3},
        value=130,
        description="Heavy metal plates offering excellent protection at the cost of agility."
    ),
    ArmorType.ROBE: Equipment(
        name="Wizard Robe",
        item_type=ItemType.ARMOR,
        armor_type=ArmorType.ROBE,
        stats={"defense": 3, "hp": 10, "mp": 30},
        value=60,
        description="Enchanted robes that enhance magical abilities."
    )
}

# Define potions
POTIONS = {
    PotionType.HEALTH: Equipment(
        name="Health Potion",
        item_type=ItemType.POTION,
        stats={"hp": 50},
        value=20,
        description="A red potion that restores health."
    ),
    PotionType.MANA: Equipment(
        name="Mana Potion",
        item_type=ItemType.POTION,
        stats={"mp": 40},
        value=25,
        description="A blue potion that restores mana."
    ),
    PotionType.STRENGTH: Equipment(
        name="Strength Potion",
        item_type=ItemType.POTION,
        stats={"strength": 10, "duration": 300},
        value=40,
        description="Temporarily increases attack power."
    ),
    PotionType.SPEED: Equipment(
        name="Agility Potion",
        item_type=ItemType.POTION,
        stats={"agility": 10, "duration": 300},
        value=40,
        description="Temporarily increases agility and movement speed."
    ),
    PotionType.DEFENSE: Equipment(
        name="Defense Potion",
        item_type=ItemType.POTION,
        stats={"defense": 10, "duration": 300},
        value=40,
        description="Temporarily increases defense."
    )
}


# Create upgraded versions of basic equipment
def create_upgraded_equipment():
    upgraded_weapons = {}
    upgraded_armors = {}

    # Create upgraded weapons
    for weapon_type, base_weapon in WEAPONS.items():
        # Uncommon upgrade
        uncommon = copy.deepcopy(base_weapon)
        uncommon.name = "Fine " + base_weapon.name
        for stat in uncommon.stats:
            uncommon.stats[stat] = int(uncommon.stats[stat] * 1.3)
        uncommon.value = int(base_weapon.value * 1.5)
        uncommon.description = "A well-crafted " + base_weapon.description

        # Rare upgrade
        rare = copy.deepcopy(base_weapon)
        rare.name = "Superior " + base_weapon.name
        for stat in rare.stats:
            rare.stats[stat] = int(rare.stats[stat] * 1.7)
        rare.value = int(base_weapon.value * 3)
        rare.description = "A masterfully crafted " + base_weapon.description

        # Epic upgrade
        epic = copy.deepcopy(base_weapon)
        epic.name = "Legendary " + base_weapon.name
        for stat in epic.stats:
            epic.stats[stat] = int(epic.stats[stat] * 2.5)
        epic.value = int(base_weapon.value * 7)
        epic.description = "A legendary " + base_weapon.description

        # Add second skill to epic weapons
        if weapon_type in WEAPON_SKILLS and len(WEAPON_SKILLS[weapon_type]) > 1:
            skill_type = WEAPON_SKILLS[weapon_type][1]
            epic.skill = copy.deepcopy(SKILLS[skill_type])

        upgraded_weapons[weapon_type] = {
            "base": base_weapon,
            "uncommon": uncommon,
            "rare": rare,
            "epic": epic
        }

    # Create upgraded armors
    for armor_type, base_armor in ARMORS.items():
        # Uncommon upgrade
        uncommon = copy.deepcopy(base_armor)
        uncommon.name = "Fine " + base_armor.name
        for stat in uncommon.stats:
            uncommon.stats[stat] = int(uncommon.stats[stat] * 1.3)
        uncommon.value = int(base_armor.value * 1.5)
        uncommon.description = "A well-crafted " + base_armor.description

        # Rare upgrade
        rare = copy.deepcopy(base_armor)
        rare.name = "Superior " + base_armor.name
        for stat in rare.stats:
            rare.stats[stat] = int(rare.stats[stat] * 1.7)
        rare.value = int(base_armor.value * 3)
        rare.description = "A masterfully crafted " + base_armor.description

        # Epic upgrade
        epic = copy.deepcopy(base_armor)
        epic.name = "Legendary " + base_armor.name
        for stat in epic.stats:
            epic.stats[stat] = int(epic.stats[stat] * 2.5)
        epic.value = int(base_armor.value * 7)
        epic.description = "A legendary " + base_armor.description

        upgraded_armors[armor_type] = {
            "base": base_armor,
            "uncommon": uncommon,
            "rare": rare,
            "epic": epic
        }

    return upgraded_weapons, upgraded_armors


UPGRADED_WEAPONS, UPGRADED_ARMORS = create_upgraded_equipment()


# Camera class
class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.rect.topleft)

    def apply_rect(self, rect):
        return rect.move(self.rect.topleft)

    def update(self, target):
        x = -target.rect.centerx + self.width // 2
        y = -target.rect.centery + self.height // 2

        # Apply smooth movement
        # self.rect.x += (x - self.rect.x) * 0.1
        # self.rect.y += (y - self.rect.y) * 0.1

        # For now, using direct positioning for simplicity
        self.rect.x = x
        self.rect.y = y

        # Limit scrolling to map size
        # This would require knowing the map boundaries
        # We'll implement this later when we have the map generation


# Map class
class GameMap:
    def __init__(self):
        self.terrain_map = {}  # Store terrain data
        self.chunk_size = CHUNK_SIZE  # Chunk size
        self.generated_chunks = set()  # Keep track of generated chunks

        # Initialize random seeds
        self.seed = random.randint(0, 999999)
        detail_seed = 7 * self.seed % 117
        biome_seed = 13 * self.seed % 91
        feature_seed = 19 * self.seed % 67

        # Terrain generators
        self.height_noise = PerlinNoise(octaves=3, seed=self.seed)
        self.detail_noise = PerlinNoise(octaves=6, seed=detail_seed)
        self.biome_noise = PerlinNoise(octaves=4, seed=biome_seed)
        self.feature_noise = PerlinNoise(octaves=5, seed=feature_seed)

        # Noise parameters
        self.height_scale = 150.0
        self.detail_scale = 50.0
        self.biome_scale = 250.0
        self.feature_scale = 100.0

        # Village parameters
        self.village_density = 0.03
        self.village_locations = {}

    def get_height(self, x, y):
        """Get terrain height value (0-1)"""
        # Base low-frequency noise
        base = self.height_noise([x / self.height_scale, y / self.height_scale])

        # High-frequency detail noise
        detail = self.detail_noise([x / self.detail_scale, y / self.detail_scale])

        # Blend noises
        height = base * 0.7 + detail * 0.3

        # Normalize to 0-1
        height = (height + 1) / 2

        return height

    def get_biome_value(self, x, y):
        """Get biome noise value"""
        return self.biome_noise([x / self.biome_scale, y / self.biome_scale])

    def get_feature_value(self, x, y):
        """Get feature noise value (for rivers, lakes, etc.)"""
        return self.feature_noise([x / self.feature_scale, y / self.feature_scale])

    def determine_biome(self, x, y):
        """Determine biome based on noise value and height"""
        height = self.get_height(x, y)
        biome_value = self.get_biome_value(x, y)

        # Ocean and water bodies
        if height < 0.3:
            return Biome.OCEAN

        # Normalize biome value to -1 to 1
        biome_value = (biome_value + 1) / 2

        # Mountain regions (based on height)
        if height > 0.75:
            if biome_value < 0.3:
                return Biome.TUNDRA
            elif biome_value < 0.7:
                return Biome.MOUNTAINS
            else:
                return Biome.VOLCANIC

        # Other biomes (based on biome noise)
        if height < 0.4:
            return Biome.SWAMP
        elif biome_value < 0.2:
            return Biome.TUNDRA
        elif biome_value < 0.4:
            return Biome.FOREST
        elif biome_value < 0.6:
            return Biome.PLAINS
        elif biome_value < 0.8:
            return Biome.DESERT
        else:
            return Biome.FOREST

    def get_terrain(self, x, y):
        """Get terrain type at global coordinates"""
        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        if (chunk_x, chunk_y) not in self.terrain_map:
            self.generate_chunk(chunk_x, chunk_y)
        local_x = x % self.chunk_size
        local_y = y % self.chunk_size
        return self.terrain_map[(chunk_x, chunk_y)][local_y][local_x]

    def is_passable(self, x, y):
        """Check if terrain is passable at global coordinates"""
        terrain = self.get_terrain(x, y)
        return TERRAIN_PASSABLE.get(terrain, True)

    def generate_chunk(self, chunk_x, chunk_y):
        """Generate a new chunk of terrain"""
        chunk = []

        # Check if we should place a village
        should_place_village = random.random() < self.village_density
        village_center = None

        if should_place_village:
            # Place village somewhere in the chunk
            local_x = random.randint(3, self.chunk_size - 4)
            local_y = random.randint(3, self.chunk_size - 4)
            village_center = (chunk_x * self.chunk_size + local_x, chunk_y * self.chunk_size + local_y)
            self.village_locations[(chunk_x, chunk_y)] = village_center

        # Generate terrain for each tile in the chunk
        for local_y in range(self.chunk_size):
            row = []
            for local_x in range(self.chunk_size):
                # Calculate global coordinates
                global_x = chunk_x * self.chunk_size + local_x
                global_y = chunk_y * self.chunk_size + local_y

                # Check if this is the village center
                if village_center and village_center == (global_x, global_y):
                    row.append(TerrainType.VILLAGE_CENTER)
                    continue

                # Check if this is near the village center
                if village_center:
                    dist_to_village_sq = (global_x - village_center[0]) ** 2 + (global_y - village_center[1]) ** 2

                    # Houses around village center
                    if dist_to_village_sq <= 9:  # Within 3 tiles
                        row.append(TerrainType.HOUSE)
                        continue

                    # Roads/paths around houses
                    if dist_to_village_sq <= 25:  # Within 5 tiles
                        if random.random() < 0.7:  # 70% chance for path
                            row.append(TerrainType.PATH)
                            continue

                # Get height and biome
                height = self.get_height(global_x, global_y)
                biome = self.determine_biome(global_x, global_y)
                feature_value = self.get_feature_value(global_x, global_y)

                # Generate terrain based on biome
                if biome == Biome.OCEAN:
                    if height < 0.2:
                        row.append(TerrainType.DEEP_WATER)
                    else:
                        row.append(TerrainType.WATER)
                elif abs(feature_value) > 0.8:  # Special features like rivers or lakes
                    if height < 0.4:
                        row.append(TerrainType.WATER)
                    else:
                        # Random feature based on biome
                        terrain_weights = BIOME_TERRAIN_WEIGHTS[biome]
                        terrain = random.choices(
                            [terrain for terrain, _ in terrain_weights],
                            weights=[weight for _, weight in terrain_weights],
                            k=1
                        )[0]
                        row.append(terrain)
                else:
                    # Standard biome terrain
                    terrain_weights = BIOME_TERRAIN_WEIGHTS[biome]
                    terrain = random.choices(
                        [terrain for terrain, _ in terrain_weights],
                        weights=[weight for _, weight in terrain_weights],
                        k=1
                    )[0]
                    row.append(terrain)

            chunk.append(row)

        # Store the generated chunk
        self.terrain_map[(chunk_x, chunk_y)] = chunk
        self.generated_chunks.add((chunk_x, chunk_y))

    def draw(self, surface, camera):
        """Draw visible portion of the map"""
        # Determine the chunks that should be visible based on camera position
        cam_chunk_x = (-camera.rect.x) // (self.chunk_size * TILE_SIZE)
        cam_chunk_y = (-camera.rect.y) // (self.chunk_size * TILE_SIZE)

        # Draw a 3x3 grid of chunks around the camera
        for cy in range(cam_chunk_y - 1, cam_chunk_y + 2):
            for cx in range(cam_chunk_x - 1, cam_chunk_x + 2):
                # Ensure the chunk is generated
                if (cx, cy) not in self.terrain_map:
                    self.generate_chunk(cx, cy)

                # Draw the chunk
                for local_y in range(self.chunk_size):
                    for local_x in range(self.chunk_size):
                        # Calculate global position
                        global_x = cx * self.chunk_size + local_x
                        global_y = cy * self.chunk_size + local_y

                        # Calculate screen position
                        screen_x = global_x * TILE_SIZE + camera.rect.x
                        screen_y = global_y * TILE_SIZE + camera.rect.y

                        # Skip if off-screen
                        if (screen_x < -TILE_SIZE or screen_x > SCREEN_WIDTH or
                                screen_y < -TILE_SIZE or screen_y > SCREEN_HEIGHT):
                            continue

                        # Get terrain type and color
                        terrain = self.terrain_map[(cx, cy)][local_y][local_x]
                        color = COLORS["grass"]  # Default color

                        # Map terrain to color
                        if terrain == TerrainType.GRASS:
                            color = COLORS["grass"]
                        elif terrain == TerrainType.TALL_GRASS:
                            color = COLORS["tall_grass"]
                        elif terrain == TerrainType.FOREST:
                            color = COLORS["forest"]
                        elif terrain == TerrainType.DEEP_FOREST:
                            color = COLORS["deep_forest"]
                        elif terrain == TerrainType.WATER:
                            color = COLORS["water"]
                        elif terrain == TerrainType.DEEP_WATER:
                            color = COLORS["deep_water"]
                        elif terrain == TerrainType.SAND:
                            color = COLORS["sand"]
                        elif terrain == TerrainType.MOUNTAIN:
                            color = COLORS["mountain"]
                        elif terrain == TerrainType.SNOW:
                            color = COLORS["snow"]
                        elif terrain == TerrainType.DESERT:
                            color = COLORS["desert"]
                        elif terrain == TerrainType.STONE:
                            color = COLORS["stone"]
                        elif terrain == TerrainType.LAVA:
                            color = COLORS["lava"]
                        elif terrain == TerrainType.ROAD:
                            color = COLORS["road"]
                        elif terrain == TerrainType.PATH:
                            color = COLORS["path"]
                        elif terrain == TerrainType.HOUSE:
                            color = COLORS["house"]
                        elif terrain == TerrainType.ROOF:
                            color = COLORS["roof"]
                        elif terrain == TerrainType.VILLAGE_CENTER:
                            color = COLORS["village_center"]

                        # Draw the tile
                        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(surface, color, rect)

                        # Add details for some terrain types
                        if terrain == TerrainType.FOREST:
                            # Draw simple tree trunk
                            trunk_rect = pygame.Rect(screen_x + TILE_SIZE // 3, screen_y + TILE_SIZE // 2,
                                                     TILE_SIZE // 3, TILE_SIZE // 2)
                            pygame.draw.rect(surface, (100, 70, 40), trunk_rect)

                            # Draw simple tree top (circle)
                            pygame.draw.circle(surface, (45, 120, 45),
                                               (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 3),
                                               TILE_SIZE // 2)

                        elif terrain == TerrainType.HOUSE:
                            # Draw house walls
                            pygame.draw.rect(surface, COLORS["house"], rect)

                            # Draw house roof
                            roof_points = [
                                (screen_x, screen_y),
                                (screen_x + TILE_SIZE, screen_y),
                                (screen_x + TILE_SIZE // 2, screen_y - TILE_SIZE // 2)
                            ]
                            pygame.draw.polygon(surface, COLORS["roof"], roof_points)

                            # Draw door
                            door_rect = pygame.Rect(screen_x + TILE_SIZE // 3, screen_y + TILE_SIZE // 2,
                                                    TILE_SIZE // 3, TILE_SIZE // 2)
                            pygame.draw.rect(surface, (60, 30, 15), door_rect)

                        elif terrain == TerrainType.VILLAGE_CENTER:
                            # Draw well or fountain
                            pygame.draw.circle(surface, COLORS["stone"],
                                               (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2),
                                               TILE_SIZE // 2)
                            pygame.draw.circle(surface, COLORS["water"],
                                               (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2),
                                               TILE_SIZE // 3)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game=None):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.name = "Hero"
        self.game = game  # 添加对游戏对象的引用

        # Animation state
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.direction = "down"  # down, up, left, right
        self.moving = False
        self.attacking = False
        self.attack_frame = 0

        # Core stats
        self.base_stats = {
            "level": 1,
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "attack": 100,
            "defense": 50,
            "crit": 50,
            "agility": 50,
            "exp": 0,
            "next_level_exp": 100,
            "attack_range": 1,
            "attack_speed": 1.0
        }

        self.stats = self.base_stats.copy()

        # Equipment
        self.equipped = {
            "weapon": None,
            "armor": None
        }

        # Inventory
        self.inventory = []
        self.max_inventory = 20

        # Skills
        self.skills = [copy.deepcopy(SKILLS[SkillType.SLASH])]
        self.active_skill = None

        # Currency
        self.gold = 0
        self.silver = 0
        self.copper = 0

        # Status effects
        self.status_effects = []

        # Cooldowns
        self.attack_cooldown = 0
        self.skill_cooldown = 0

        # Floating text
        self.floating_texts = []

        # Draw the player
        self.update_appearance()

        # Add starting equipment
        self.add_starting_equipment()

        self.player_stats = {
            "monsters_killed": 0,
            "total_gold": 0,
            "items_found": 0,
            "deaths": 0,
            "levels_gained": 0,
            "potions_used": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "play_time": 0
        }

    def add_starting_equipment(self):
        """Add starting equipment"""
        # Add starting weapon (sword)
        sword = copy.deepcopy(WEAPONS[WeaponType.SWORD])
        self.equip(sword)

        # Add starting armor (leather)
        armor = copy.deepcopy(ARMORS[ArmorType.LIGHT])
        self.equip(armor)

        # Add some healing potions
        for _ in range(3):
            health_potion = copy.deepcopy(POTIONS[PotionType.HEALTH])
            self.add_to_inventory(health_potion)

        # Add a mana potion
        mana_potion = copy.deepcopy(POTIONS[PotionType.MANA])
        self.add_to_inventory(mana_potion)

        # Add starting gold
        self.add_currency(gold=2, silver=5, copper=0)

    def draw(self, surface, camera_pos):
        """Draw player on surface"""
        # Get screen position
        screen_x = self.rect.x - camera_pos[0]
        screen_y = self.rect.y - camera_pos[1]

        # Draw player
        surface.blit(self.image, (screen_x, screen_y))

    def update_appearance(self):
        """Update player sprite based on current state"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        # Body color
        body_color = COLORS["player"]

        # Draw body based on direction
        if self.direction == "down":
            # Draw body
            pygame.draw.rect(self.image, body_color,
                             pygame.Rect(TILE_SIZE // 4, TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))

            # Draw head
            pygame.draw.circle(self.image, body_color,
                               (TILE_SIZE // 2, TILE_SIZE // 4), TILE_SIZE // 4)

            # Draw eyes
            eye_y = TILE_SIZE // 5
            pygame.draw.circle(self.image, (255, 255, 255),
                               (TILE_SIZE // 3, eye_y), TILE_SIZE // 12)
            pygame.draw.circle(self.image, (255, 255, 255),
                               (TILE_SIZE * 2 // 3, eye_y), TILE_SIZE // 12)

            # Draw pupils
            pygame.draw.circle(self.image, (0, 0, 0),
                               (TILE_SIZE // 3, eye_y), TILE_SIZE // 24)
            pygame.draw.circle(self.image, (0, 0, 0),
                               (TILE_SIZE * 2 // 3, eye_y), TILE_SIZE // 24)

        elif self.direction == "up":
            # Draw body
            pygame.draw.rect(self.image, body_color,
                             pygame.Rect(TILE_SIZE // 4, TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))

            # Draw head
            pygame.draw.circle(self.image, body_color,
                               (TILE_SIZE // 2, TILE_SIZE // 4), TILE_SIZE // 4)

            # Just draw hair or hat when facing up
            hair_color = (170, 85, 0)  # Brown hair
            pygame.draw.rect(self.image, hair_color,
                             pygame.Rect(TILE_SIZE // 4, 0, TILE_SIZE // 2, TILE_SIZE // 4))

        elif self.direction == "left":
            # Draw body
            pygame.draw.rect(self.image, body_color,
                             pygame.Rect(TILE_SIZE // 4, TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))

            # Draw head
            pygame.draw.circle(self.image, body_color,
                               (TILE_SIZE // 4, TILE_SIZE // 4), TILE_SIZE // 4)

            # Draw eyes
            eye_x = TILE_SIZE // 5
            pygame.draw.circle(self.image, (255, 255, 255),
                               (eye_x, TILE_SIZE // 4), TILE_SIZE // 12)

            # Draw pupils
            pygame.draw.circle(self.image, (0, 0, 0),
                               (eye_x - TILE_SIZE // 24, TILE_SIZE // 4), TILE_SIZE // 24)

        elif self.direction == "right":
            # Draw body
            pygame.draw.rect(self.image, body_color,
                             pygame.Rect(TILE_SIZE // 4, TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))

            # Draw head
            pygame.draw.circle(self.image, body_color,
                               (TILE_SIZE * 3 // 4, TILE_SIZE // 4), TILE_SIZE // 4)

            # Draw eyes
            eye_x = TILE_SIZE * 4 // 5
            pygame.draw.circle(self.image, (255, 255, 255),
                               (eye_x, TILE_SIZE // 4), TILE_SIZE // 12)

            # Draw pupils
            pygame.draw.circle(self.image, (0, 0, 0),
                               (eye_x + TILE_SIZE // 24, TILE_SIZE // 4), TILE_SIZE // 24)

        # Draw arms and legs with animation
        self.draw_limbs()

        # Draw equipped weapon if any
        self.draw_weapon()

        # Draw status effects
        self.draw_status_effects()

    def draw_limbs(self):
        """Draw arms and legs with animation"""
        body_color = COLORS["player"]

        # Animation offset for walking
        offset = math.sin(self.animation_frame * 5) * 3 if self.moving else 0

        if self.direction == "down" or self.direction == "up":
            # Draw arms
            arm_y = TILE_SIZE // 2
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE // 4, arm_y),
                             (TILE_SIZE // 8, arm_y + offset), 2)
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE * 3 // 4, arm_y),
                             (TILE_SIZE * 7 // 8, arm_y - offset), 2)

            # Draw legs
            leg_y = TILE_SIZE * 3 // 4
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE * 3 // 8, leg_y),
                             (TILE_SIZE * 3 // 8, leg_y + 5 + offset), 2)
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE * 5 // 8, leg_y),
                             (TILE_SIZE * 5 // 8, leg_y + 5 - offset), 2)

        elif self.direction == "left":
            # Draw arms
            arm_x = TILE_SIZE // 4
            pygame.draw.line(self.image, body_color,
                             (arm_x, TILE_SIZE // 2),
                             (arm_x - 5, TILE_SIZE // 2 + offset), 2)

            # Draw legs
            leg_y = TILE_SIZE * 3 // 4
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE * 3 // 8, leg_y),
                             (TILE_SIZE * 3 // 8 - 3, leg_y + 5 + offset), 2)
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE * 5 // 8, leg_y),
                             (TILE_SIZE * 5 // 8 - 3, leg_y + 5 - offset), 2)

        elif self.direction == "right":
            # Draw arms
            arm_x = TILE_SIZE * 3 // 4
            pygame.draw.line(self.image, body_color,
                             (arm_x, TILE_SIZE // 2),
                             (arm_x + 5, TILE_SIZE // 2 + offset), 2)

            # Draw legs
            leg_y = TILE_SIZE * 3 // 4
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE * 3 // 8, leg_y),
                             (TILE_SIZE * 3 // 8 + 3, leg_y + 5 + offset), 2)
            pygame.draw.line(self.image, body_color,
                             (TILE_SIZE * 5 // 8, leg_y),
                             (TILE_SIZE * 5 // 8 + 3, leg_y + 5 - offset), 2)

    def draw_weapon(self):
        """Draw equipped weapon"""
        if not self.equipped["weapon"]:
            return

        weapon_type = self.equipped["weapon"].weapon_type

        # Attack animation
        if self.attacking:
            attack_progress = self.attack_frame / 10.0  # 0 to 1
            self.draw_attack_animation(weapon_type, attack_progress)
        else:
            # Draw idle weapon
            if weapon_type == WeaponType.SWORD:
                self.draw_sword()
            elif weapon_type == WeaponType.GREATSWORD:
                self.draw_greatsword()
            elif weapon_type == WeaponType.DAGGER:
                self.draw_dagger()
            elif weapon_type == WeaponType.SPEAR:
                self.draw_spear()
            elif weapon_type == WeaponType.BOW:
                self.draw_bow()
            elif weapon_type == WeaponType.STAFF:
                self.draw_staff()

    def draw_sword(self):
        """Draw sword"""
        weapon_color = (200, 200, 200)  # Silver
        hilt_color = (150, 100, 50)  # Brown

        if self.direction == "down":
            # Draw sword along right side
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 3 // 4), 3)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 2 // 3, TILE_SIZE // 2),
                             (TILE_SIZE * 5 // 6, TILE_SIZE // 2), 2)

        elif self.direction == "up":
            # Draw sword along right side
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 4), 3)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 2 // 3, TILE_SIZE // 2),
                             (TILE_SIZE * 5 // 6, TILE_SIZE // 2), 2)

        elif self.direction == "left":
            # Draw sword pointing left
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE // 4, TILE_SIZE // 2),
                             (0, TILE_SIZE // 2), 3)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE // 4, TILE_SIZE * 2 // 5),
                             (TILE_SIZE // 4, TILE_SIZE * 3 // 5), 2)

        elif self.direction == "right":
            # Draw sword pointing right
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE, TILE_SIZE // 2), 3)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 2 // 5),
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 3 // 5), 2)

    def draw_greatsword(self):
        """Draw greatsword"""
        weapon_color = (200, 200, 200)  # Silver
        hilt_color = (150, 100, 50)  # Brown

        if self.direction == "down":
            # Draw sword behind player
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE // 2, TILE_SIZE // 8),
                             (TILE_SIZE // 2, TILE_SIZE * 7 // 8), 4)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 3 // 8, TILE_SIZE // 4),
                             (TILE_SIZE * 5 // 8, TILE_SIZE // 4), 3)

        elif self.direction == "up":
            # Draw sword behind player
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE // 2, TILE_SIZE // 8),
                             (TILE_SIZE // 2, TILE_SIZE * 7 // 8), 4)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 3 // 8, TILE_SIZE * 3 // 4),
                             (TILE_SIZE * 5 // 8, TILE_SIZE * 3 // 4), 3)

        elif self.direction == "left":
            # Draw sword sideways
            pygame.draw.line(self.image, weapon_color,
                             (0, TILE_SIZE // 2),
                             (TILE_SIZE, TILE_SIZE // 2), 4)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE // 4, TILE_SIZE * 3 // 8),
                             (TILE_SIZE // 4, TILE_SIZE * 5 // 8), 3)

        elif self.direction == "right":
            # Draw sword sideways
            pygame.draw.line(self.image, weapon_color,
                             (0, TILE_SIZE // 2),
                             (TILE_SIZE, TILE_SIZE // 2), 4)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 3 // 8),
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 5 // 8), 3)

    def draw_dagger(self):
        """Draw dagger"""
        weapon_color = (180, 180, 180)  # Light silver
        hilt_color = (50, 50, 50)  # Dark gray

        if self.direction == "down":
            # Draw dagger on right side
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 2 // 3), 2)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 2 // 3, TILE_SIZE // 2),
                             (TILE_SIZE * 5 // 6, TILE_SIZE // 2), 1)

        elif self.direction == "up":
            # Draw dagger on right side
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 3), 2)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 2 // 3, TILE_SIZE // 2),
                             (TILE_SIZE * 5 // 6, TILE_SIZE // 2), 1)

        elif self.direction == "left":
            # Draw dagger pointing left
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE // 4, TILE_SIZE // 2),
                             (TILE_SIZE // 8, TILE_SIZE // 2), 2)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE // 4, TILE_SIZE // 3),
                             (TILE_SIZE // 4, TILE_SIZE * 2 // 3), 1)

        elif self.direction == "right":
            # Draw dagger pointing right
            pygame.draw.line(self.image, weapon_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE * 7 // 8, TILE_SIZE // 2), 2)
            # Draw hilt
            pygame.draw.line(self.image, hilt_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 3),
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 2 // 3), 1)

    def draw_spear(self):
        """Draw spear"""
        weapon_color = (150, 150, 150)  # Metal color
        shaft_color = (120, 80, 40)  # Wood color

        if self.direction == "down":
            # Draw spear shaft
            pygame.draw.line(self.image, shaft_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE * 3 // 4, TILE_SIZE), 3)
            # Draw spear tip
            pygame.draw.polygon(self.image, weapon_color, [
                (TILE_SIZE * 3 // 4, TILE_SIZE),
                (TILE_SIZE * 2 // 3, TILE_SIZE * 5 // 6),
                (TILE_SIZE * 5 // 6, TILE_SIZE * 5 // 6)
            ])

        elif self.direction == "up":
            # Draw spear shaft
            pygame.draw.line(self.image, shaft_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE * 3 // 4, 0), 3)
            # Draw spear tip
            pygame.draw.polygon(self.image, weapon_color, [
                (TILE_SIZE * 3 // 4, 0),
                (TILE_SIZE * 2 // 3, TILE_SIZE // 6),
                (TILE_SIZE * 5 // 6, TILE_SIZE // 6)
            ])

        elif self.direction == "left":
            # Draw spear shaft
            pygame.draw.line(self.image, shaft_color,
                             (TILE_SIZE // 4, TILE_SIZE // 2),
                             (0, TILE_SIZE // 2), 3)
            # Draw spear tip
            pygame.draw.polygon(self.image, weapon_color, [
                (0, TILE_SIZE // 2),
                (TILE_SIZE // 6, TILE_SIZE // 3),
                (TILE_SIZE // 6, TILE_SIZE * 2 // 3)
            ])

        elif self.direction == "right":
            # Draw spear shaft
            pygame.draw.line(self.image, shaft_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 2),
                             (TILE_SIZE, TILE_SIZE // 2), 3)
            # Draw spear tip
            pygame.draw.polygon(self.image, weapon_color, [
                (TILE_SIZE, TILE_SIZE // 2),
                (TILE_SIZE * 5 // 6, TILE_SIZE // 3),
                (TILE_SIZE * 5 // 6, TILE_SIZE * 2 // 3)
            ])

    def draw_bow(self):
        """Draw bow"""
        bow_color = (120, 80, 40)  # Wood color
        string_color = (250, 250, 250)  # White

        if self.direction == "down":
            # Draw bow
            pygame.draw.arc(self.image, bow_color,
                            pygame.Rect(TILE_SIZE * 2 // 3, TILE_SIZE // 3, TILE_SIZE // 3, TILE_SIZE // 2),
                            math.pi / 2, 3 * math.pi / 2, 2)
            # Draw string
            pygame.draw.line(self.image, string_color,
                             (TILE_SIZE * 2 // 3, TILE_SIZE // 3 + TILE_SIZE // 4),
                             (TILE_SIZE, TILE_SIZE // 3 + TILE_SIZE // 4), 1)

        elif self.direction == "up":
            # Draw bow
            pygame.draw.arc(self.image, bow_color,
                            pygame.Rect(TILE_SIZE * 2 // 3, TILE_SIZE // 6, TILE_SIZE // 3, TILE_SIZE // 2),
                            math.pi / 2, 3 * math.pi / 2, 2)
            # Draw string
            pygame.draw.line(self.image, string_color,
                             (TILE_SIZE * 2 // 3, TILE_SIZE // 6 + TILE_SIZE // 4),
                             (TILE_SIZE, TILE_SIZE // 6 + TILE_SIZE // 4), 1)

        elif self.direction == "left":
            # Draw bow
            pygame.draw.arc(self.image, bow_color,
                            pygame.Rect(TILE_SIZE // 6, TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE // 3),
                            0, math.pi, 2)
            # Draw string
            pygame.draw.line(self.image, string_color,
                             (TILE_SIZE // 6 + TILE_SIZE // 4, TILE_SIZE // 3),
                             (TILE_SIZE // 6 + TILE_SIZE // 4, TILE_SIZE * 2 // 3), 1)

        elif self.direction == "right":
            # Draw bow
            pygame.draw.arc(self.image, bow_color,
                            pygame.Rect(TILE_SIZE // 3, TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE // 3),
                            0, math.pi, 2)
            # Draw string
            pygame.draw.line(self.image, string_color,
                             (TILE_SIZE // 3 + TILE_SIZE // 4, TILE_SIZE // 3),
                             (TILE_SIZE // 3 + TILE_SIZE // 4, TILE_SIZE * 2 // 3), 1)

    def draw_staff(self):
        """Draw staff"""
        staff_color = (100, 50, 0)  # Dark wood
        gem_color = (50, 100, 200)  # Blue gem

        if self.direction == "down":
            # Draw staff
            pygame.draw.line(self.image, staff_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE // 3),
                             (TILE_SIZE * 3 // 4, TILE_SIZE), 3)
            # Draw gemstone
            pygame.draw.circle(self.image, gem_color,
                               (TILE_SIZE * 3 // 4, TILE_SIZE // 3),
                               TILE_SIZE // 10)

        elif self.direction == "up":
            # Draw staff
            pygame.draw.line(self.image, staff_color,
                             (TILE_SIZE * 3 // 4, TILE_SIZE * 2 // 3),
                             (TILE_SIZE * 3 // 4, 0), 3)
            # Draw gemstone
            pygame.draw.circle(self.image, gem_color,
                               (TILE_SIZE * 3 // 4, TILE_SIZE * 2 // 3),
                               TILE_SIZE // 10)

        elif self.direction == "left":
            # Draw staff
            pygame.draw.line(self.image, staff_color,
                             (TILE_SIZE * 2 // 3, TILE_SIZE // 2),
                             (0, TILE_SIZE // 2), 3)
            # Draw gemstone
            pygame.draw.circle(self.image, gem_color,
                               (TILE_SIZE * 2 // 3, TILE_SIZE // 2),
                               TILE_SIZE // 10)

        elif self.direction == "right":
            # Draw staff
            pygame.draw.line(self.image, staff_color,
                             (TILE_SIZE // 3, TILE_SIZE // 2),
                             (TILE_SIZE, TILE_SIZE // 2), 3)
            # Draw gemstone
            pygame.draw.circle(self.image, gem_color,
                               (TILE_SIZE // 3, TILE_SIZE // 2),
                               TILE_SIZE // 10)

    def draw_attack_animation(self, weapon_type, progress):
        """Draw attack animation based on weapon type and progress (0-1)"""
        # Adjust weapon position based on attack progress
        if weapon_type == WeaponType.SWORD or weapon_type == WeaponType.DAGGER:
            self.draw_sword_attack(progress)
        elif weapon_type == WeaponType.GREATSWORD:
            self.draw_greatsword_attack(progress)
        elif weapon_type == WeaponType.SPEAR:
            self.draw_spear_attack(progress)
        elif weapon_type == WeaponType.BOW:
            self.draw_bow_attack(progress)
        elif weapon_type == WeaponType.STAFF:
            self.draw_staff_attack(progress)

    def draw_sword_attack(self, progress):
        """Draw sword attack animation"""
        weapon_color = (200, 200, 200)  # Silver
        hilt_color = (150, 100, 50)  # Brown

        # Create a swing arc
        if progress < 0.5:
            attack_progress = progress * 2  # 0 to 1 in first half
        else:
            attack_progress = 2 - progress * 2  # 1 to 0 in second half

        # Get angle based on direction and progress
        if self.direction == "down":
            angle_start = math.pi * 0.75
            angle_end = angle_start + math.pi * 0.5 * attack_progress
            center = (TILE_SIZE // 2, TILE_SIZE // 2)
            radius = TILE_SIZE // 2

            # Draw sword
            start_angle = min(angle_start, angle_end)
            end_angle = max(angle_start, angle_end)
            pygame.draw.arc(self.image, weapon_color,
                            pygame.Rect(center[0] - radius, center[1] - radius,
                                        radius * 2, radius * 2),
                            start_angle, end_angle, 3)

            # Draw sword tip
            tip_x = center[0] + radius * math.cos(angle_end)
            tip_y = center[1] + radius * math.sin(angle_end)
            pygame.draw.circle(self.image, weapon_color, (int(tip_x), int(tip_y)), 2)

        elif self.direction == "up":
            angle_start = math.pi * 1.75
            angle_end = angle_start - math.pi * 0.5 * attack_progress
            center = (TILE_SIZE // 2, TILE_SIZE // 2)
            radius = TILE_SIZE // 2

            # Draw sword
            start_angle = min(angle_start, angle_end)
            end_angle = max(angle_start, angle_end)
            pygame.draw.arc(self.image, weapon_color,
                            pygame.Rect(center[0] - radius, center[1] - radius,
                                        radius * 2, radius * 2),
                            start_angle, end_angle, 3)

            # Draw sword tip
            tip_x = center[0] + radius * math.cos(angle_end)
            tip_y = center[1] + radius * math.sin(angle_end)
            pygame.draw.circle(self.image, weapon_color, (int(tip_x), int(tip_y)), 2)

        elif self.direction == "left":
            angle_start = math.pi * 1.25
            angle_end = angle_start + math.pi * 0.5 * attack_progress
            center = (TILE_SIZE // 2, TILE_SIZE // 2)
            radius = TILE_SIZE // 2

            # Draw sword
            start_angle = min(angle_start, angle_end)
            end_angle = max(angle_start, angle_end)
            pygame.draw.arc(self.image, weapon_color,
                            pygame.Rect(center[0] - radius, center[1] - radius,
                                        radius * 2, radius * 2),
                            start_angle, end_angle, 3)

            # Draw sword tip
            tip_x = center[0] + radius * math.cos(angle_end)
            tip_y = center[1] + radius * math.sin(angle_end)
            pygame.draw.circle(self.image, weapon_color, (int(tip_x), int(tip_y)), 2)

        elif self.direction == "right":
            angle_start = math.pi * 0.25
            angle_end = angle_start - math.pi * 0.5 * attack_progress
            center = (TILE_SIZE // 2, TILE_SIZE // 2)
            radius = TILE_SIZE // 2

            # Draw sword
            start_angle = min(angle_start, angle_end)
            end_angle = max(angle_start, angle_end)
            pygame.draw.arc(self.image, weapon_color,
                            pygame.Rect(center[0] - radius, center[1] - radius,
                                        radius * 2, radius * 2),
                            start_angle, end_angle, 3)

            # Draw sword tip
            tip_x = center[0] + radius * math.cos(angle_end)
            tip_y = center[1] + radius * math.sin(angle_end)
            pygame.draw.circle(self.image, weapon_color, (int(tip_x), int(tip_y)), 2)

    def draw_greatsword_attack(self, progress):
        """Draw greatsword attack animation"""
        weapon_color = (200, 200, 200)  # Silver
        hilt_color = (150, 100, 50)  # Brown

        # Greatsword has a bigger swing arc
        if progress < 0.5:
            attack_progress = progress * 2  # 0 to 1 in first half
        else:
            attack_progress = 2 - progress * 2  # 1 to 0 in second half

        # Get angle based on direction and progress
        if self.direction == "down" or self.direction == "up":
            angle_start = math.pi * (1.75 if self.direction == "up" else 0.75)
            angle_span = math.pi * 0.75  # Wider arc
            angle_end = angle_start + angle_span * attack_progress * (1 if self.direction == "down" else -1)
            center = (TILE_SIZE // 2, TILE_SIZE // 2)
            radius = TILE_SIZE * 3 // 4  # Longer

            # Draw greatsword
            start_angle = min(angle_start, angle_end)
            end_angle = max(angle_start, angle_end)
            pygame.draw.arc(self.image, weapon_color,
                            pygame.Rect(center[0] - radius, center[1] - radius,
                                        radius * 2, radius * 2),
                            start_angle, end_angle, 4)

            # Draw sword tip
            tip_x = center[0] + radius * math.cos(angle_end)
            tip_y = center[1] + radius * math.sin(angle_end)
            pygame.draw.circle(self.image, weapon_color, (int(tip_x), int(tip_y)), 3)

        elif self.direction == "left" or self.direction == "right":
            angle_start = math.pi * (1.25 if self.direction == "left" else 0.25)
            angle_span = math.pi * 0.75  # Wider arc
            angle_end = angle_start + angle_span * attack_progress * (1 if self.direction == "left" else -1)
            center = (TILE_SIZE // 2, TILE_SIZE // 2)
            radius = TILE_SIZE * 3 // 4  # Longer

            # Draw greatsword
            start_angle = min(angle_start, angle_end)
            end_angle = max(angle_start, angle_end)
            pygame.draw.arc(self.image, weapon_color,
                            pygame.Rect(center[0] - radius, center[1] - radius,
                                        radius * 2, radius * 2),
                            start_angle, end_angle, 4)

            # Draw sword tip
            tip_x = center[0] + radius * math.cos(angle_end)
            tip_y = center[1] + radius * math.sin(angle_end)
            pygame.draw.circle(self.image, weapon_color, (int(tip_x), int(tip_y)), 3)

    def draw_spear_attack(self, progress):
        """Draw spear attack animation"""
        weapon_color = (150, 150, 150)  # Metal
        shaft_color = (120, 80, 40)  # Wood

        # Spear has a thrust animation
        if progress < 0.5:
            # Thrust outward
            thrust_progress = progress * 2
        else:
            # Pull back
            thrust_progress = (1 - (progress - 0.5) * 2)

        center = (TILE_SIZE // 2, TILE_SIZE // 2)

        if self.direction == "down":
            # Thrust downward
            shaft_start = (center[0], center[1])
            shaft_end = (center[0], center[1] + TILE_SIZE // 2 + thrust_progress * TILE_SIZE)

            # Draw shaft
            pygame.draw.line(self.image, shaft_color, shaft_start, shaft_end, 3)

            # Draw tip
            tip_length = TILE_SIZE // 6
            pygame.draw.polygon(self.image, weapon_color, [
                shaft_end,
                (shaft_end[0] - tip_length // 2, shaft_end[1] - tip_length),
                (shaft_end[0] + tip_length // 2, shaft_end[1] - tip_length)
            ])

        elif self.direction == "up":
            # Thrust upward
            shaft_start = (center[0], center[1])
            shaft_end = (center[0], center[1] - TILE_SIZE // 2 - thrust_progress * TILE_SIZE)

            # Draw shaft
            pygame.draw.line(self.image, shaft_color, shaft_start, shaft_end, 3)

            # Draw tip
            tip_length = TILE_SIZE // 6
            pygame.draw.polygon(self.image, weapon_color, [
                shaft_end,
                (shaft_end[0] - tip_length // 2, shaft_end[1] + tip_length),
                (shaft_end[0] + tip_length // 2, shaft_end[1] + tip_length)
            ])

        elif self.direction == "left":
            # Thrust leftward
            shaft_start = (center[0], center[1])
            shaft_end = (center[0] - TILE_SIZE // 2 - thrust_progress * TILE_SIZE, center[1])

            # Draw shaft
            pygame.draw.line(self.image, shaft_color, shaft_start, shaft_end, 3)

            # Draw tip
            tip_length = TILE_SIZE // 6
            pygame.draw.polygon(self.image, weapon_color, [
                shaft_end,
                (shaft_end[0] + tip_length, shaft_end[1] - tip_length // 2),
                (shaft_end[0] + tip_length, shaft_end[1] + tip_length // 2)
            ])

        elif self.direction == "right":
            # Thrust rightward
            shaft_start = (center[0], center[1])
            shaft_end = (center[0] + TILE_SIZE // 2 + thrust_progress * TILE_SIZE, center[1])

            # Draw shaft
            pygame.draw.line(self.image, shaft_color, shaft_start, shaft_end, 3)

            # Draw tip
            tip_length = TILE_SIZE // 6
            pygame.draw.polygon(self.image, weapon_color, [
                shaft_end,
                (shaft_end[0] - tip_length, shaft_end[1] - tip_length // 2),
                (shaft_end[0] - tip_length, shaft_end[1] + tip_length // 2)
            ])

    def draw_bow_attack(self, progress):
        """Draw bow attack animation"""
        bow_color = (120, 80, 40)  # Wood
        string_color = (250, 250, 250)  # White
        arrow_color = (180, 160, 100)  # Light wood
        arrowhead_color = (150, 150, 150)  # Metal
        # Bow has a draw and release animation
        if progress < 0.5:
            # Drawing the bow
            draw_progress = progress * 2
        else:
            # Release and return to normal
            draw_progress = (1 - (progress - 0.5) * 2)
        center = (TILE_SIZE // 2, TILE_SIZE // 2)
        if self.direction == "down":
            # Draw bow
            bow_rect = pygame.Rect(center[0] - TILE_SIZE // 4, center[1] - TILE_SIZE // 4,
                                   TILE_SIZE // 2, TILE_SIZE // 2)
            pygame.draw.arc(self.image, bow_color, bow_rect, math.pi / 2, 3 * math.pi / 2, 2)
            # Draw string (pulled back based on progress)
            string_pull = TILE_SIZE // 6 * draw_progress
            pygame.draw.line(self.image, string_color,
                             (center[0] - TILE_SIZE // 4, center[1]),
                             (center[0] + TILE_SIZE // 4 - string_pull, center[1]), 1)
            # Draw arrow if drawing
            if draw_progress > 0.1:
                # Arrow shaft
                pygame.draw.line(self.image, arrow_color,
                                 (center[0] + TILE_SIZE // 4 - string_pull, center[1]),
                                 (center[0] + TILE_SIZE // 2, center[1]), 1)
                # Arrowhead
                pygame.draw.polygon(self.image, arrowhead_color, [
                    (center[0] + TILE_SIZE // 2, center[1]),
                    (center[0] + TILE_SIZE // 2 - 3, center[1] - 2),
                    (center[0] + TILE_SIZE // 2 - 3, center[1] + 2)
                ])
                # Fletching
                pygame.draw.line(self.image, string_color,
                                 (center[0] + TILE_SIZE // 4 - string_pull, center[1] - 2),
                                 (center[0] + TILE_SIZE // 4 - string_pull, center[1] + 2), 1)
        elif self.direction == "up":
            # Draw bow
            bow_rect = pygame.Rect(center[0] - TILE_SIZE // 4, center[1] - TILE_SIZE // 4,
                                   TILE_SIZE // 2, TILE_SIZE // 2)
            pygame.draw.arc(self.image, bow_color, bow_rect, math.pi / 2, 3 * math.pi / 2, 2)
            # Draw string (pulled back based on progress)
            string_pull = TILE_SIZE // 6 * draw_progress
            pygame.draw.line(self.image, string_color,
                             (center[0] - TILE_SIZE // 4, center[1]),
                             (center[0] + TILE_SIZE // 4 - string_pull, center[1]), 1)
            # Draw arrow if drawing
            if draw_progress > 0.1:
                # Arrow shaft
                pygame.draw.line(self.image, arrow_color,
                                 (center[0] + TILE_SIZE // 4 - string_pull, center[1]),
                                 (center[0] + TILE_SIZE // 2, center[1]), 1)
                # Arrowhead
                pygame.draw.polygon(self.image, arrowhead_color, [
                    (center[0] + TILE_SIZE // 2, center[1]),
                    (center[0] + TILE_SIZE // 2 - 3, center[1] - 2),
                    (center[0] + TILE_SIZE // 2 - 3, center[1] + 2)
                ])
                # Fletching
                pygame.draw.line(self.image, string_color,
                                 (center[0] + TILE_SIZE // 4 - string_pull, center[1] - 2),
                                 (center[0] + TILE_SIZE // 4 - string_pull, center[1] + 2), 1)
        elif self.direction == "left":
            # Draw bow
            bow_rect = pygame.Rect(center[0] - TILE_SIZE // 4, center[1] - TILE_SIZE // 4,
                                   TILE_SIZE // 2, TILE_SIZE // 2)
            pygame.draw.arc(self.image, bow_color, bow_rect, 0, math.pi, 2)
            # Draw string (pulled back based on progress)
            string_pull = TILE_SIZE // 6 * draw_progress
            pygame.draw.line(self.image, string_color,
                             (center[0], center[1] - TILE_SIZE // 4),
                             (center[0], center[1] + TILE_SIZE // 4 - string_pull), 1)
            # Draw arrow if drawing
            if draw_progress > 0.1:
                # Arrow shaft
                pygame.draw.line(self.image, arrow_color,
                                 (center[0], center[1] + TILE_SIZE // 4 - string_pull),
                                 (center[0], center[1] + TILE_SIZE // 2), 1)
                # Arrowhead
                pygame.draw.polygon(self.image, arrowhead_color, [
                    (center[0], center[1] + TILE_SIZE // 2),
                    (center[0] - 2, center[1] + TILE_SIZE // 2 - 3),
                    (center[0] + 2, center[1] + TILE_SIZE // 2 - 3)
                ])
                # Fletching
                pygame.draw.line(self.image, string_color,
                                 (center[0] - 2, center[1] + TILE_SIZE // 4 - string_pull),
                                 (center[0] + 2, center[1] + TILE_SIZE // 4 - string_pull), 1)
        elif self.direction == "right":
            # Draw bow
            bow_rect = pygame.Rect(center[0] - TILE_SIZE // 4, center[1] - TILE_SIZE // 4,
                                   TILE_SIZE // 2, TILE_SIZE // 2)
            pygame.draw.arc(self.image, bow_color, bow_rect, 0, math.pi, 2)
            # Draw string (pulled back based on progress)
            string_pull = TILE_SIZE // 6 * draw_progress
            pygame.draw.line(self.image, string_color,
                             (center[0], center[1] - TILE_SIZE // 4),
                             (center[0], center[1] + TILE_SIZE // 4 - string_pull), 1)
            # Draw arrow if drawing
            if draw_progress > 0.1:
                # Arrow shaft
                pygame.draw.line(self.image, arrow_color,
                                 (center[0], center[1] + TILE_SIZE // 4 - string_pull),
                                 (center[0], center[1] + TILE_SIZE // 2), 1)
                # Arrowhead
                pygame.draw.polygon(self.image, arrowhead_color, [
                    (center[0], center[1] + TILE_SIZE // 2),
                    (center[0] - 2, center[1] + TILE_SIZE // 2 - 3),
                    (center[0] + 2, center[1] + TILE_SIZE // 2 - 3)
                ])
                # Fletching
                pygame.draw.line(self.image, string_color,
                                 (center[0] - 2, center[1] + TILE_SIZE // 4 - string_pull),
                                 (center[0] + 2, center[1] + TILE_SIZE // 4 - string_pull), 1)

    def draw_staff_attack(self, progress):

        """Draw staff attack animation"""

        staff_color = (100, 50, 0)  # Dark wood

        gem_color = (50, 100, 200)  # Blue gem

        magic_color = (100, 150, 255, 150)  # Magic aura

        center = (TILE_SIZE // 2, TILE_SIZE // 2)

        # Staff has a charge and release animation

        charge_color = gem_color

        if progress < 0.5:

            # Charging magic

            charge_progress = progress * 2

            charge_radius = TILE_SIZE // 10 + charge_progress * TILE_SIZE // 10

            # Magic charge is more transparent at first

            alpha = int(charge_progress * 200)

            charge_color = (*gem_color[:3], alpha)

        else:

            # Release magic

            charge_progress = 1

            charge_radius = TILE_SIZE // 5

            # Magic is fully visible

            charge_color = (*gem_color[:3], 200)

        if self.direction == "down":

            # Draw staff

            pygame.draw.line(self.image, staff_color,

                             (center[0], center[1]),

                             (center[0], center[1] + TILE_SIZE // 2), 3)

            # Draw gemstone with glow

            staff_top = (center[0], center[1])

            pygame.draw.circle(self.image, gem_color, staff_top, TILE_SIZE // 10)

            if charge_progress > 0.1:
                # Create glow surface

                glow_surf = pygame.Surface((charge_radius * 2, charge_radius * 2), pygame.SRCALPHA)

                pygame.draw.circle(glow_surf, charge_color, (charge_radius, charge_radius), charge_radius)

                # Position and draw glow

                glow_pos = (staff_top[0] - charge_radius, staff_top[1] - charge_radius)

                self.image.blit(glow_surf, glow_pos)



        elif self.direction == "up":

            # Draw staff

            pygame.draw.line(self.image, staff_color,

                             (center[0], center[1]),

                             (center[0], center[1] - TILE_SIZE // 2), 3)

            # Draw gemstone with glow

            staff_top = (center[0], center[1] - TILE_SIZE // 2)

            pygame.draw.circle(self.image, gem_color, staff_top, TILE_SIZE // 10)

            if charge_progress > 0.1:
                # Create glow surface

                glow_surf = pygame.Surface((charge_radius * 2, charge_radius * 2), pygame.SRCALPHA)

                pygame.draw.circle(glow_surf, charge_color, (charge_radius, charge_radius), charge_radius)

                # Position and draw glow

                glow_pos = (staff_top[0] - charge_radius, staff_top[1] - charge_radius)

                self.image.blit(glow_surf, glow_pos)



        elif self.direction == "left":

            # Draw staff

            pygame.draw.line(self.image, staff_color,

                             (center[0], center[1]),

                             (center[0] - TILE_SIZE // 2, center[1]), 3)

            # Draw gemstone with glow

            staff_top = (center[0] - TILE_SIZE // 2, center[1])

            pygame.draw.circle(self.image, gem_color, staff_top, TILE_SIZE // 10)

            if charge_progress > 0.1:
                # Create glow surface

                glow_surf = pygame.Surface((charge_radius * 2, charge_radius * 2), pygame.SRCALPHA)

                pygame.draw.circle(glow_surf, charge_color, (charge_radius, charge_radius), charge_radius)

                # Position and draw glow

                glow_pos = (staff_top[0] - charge_radius, staff_top[1] - charge_radius)

                self.image.blit(glow_surf, glow_pos)



        elif self.direction == "right":

            # Draw staff

            pygame.draw.line(self.image, staff_color,

                             (center[0], center[1]),

                             (center[0] + TILE_SIZE // 2, center[1]), 3)

            # Draw gemstone with glow

            staff_top = (center[0] + TILE_SIZE // 2, center[1])

            pygame.draw.circle(self.image, gem_color, staff_top, TILE_SIZE // 10)

            if charge_progress > 0.1:
                # Create glow surface

                glow_surf = pygame.Surface((charge_radius * 2, charge_radius * 2), pygame.SRCALPHA)

                pygame.draw.circle(glow_surf, charge_color, (charge_radius, charge_radius), charge_radius)

                # Position and draw glow

                glow_pos = (staff_top[0] - charge_radius, staff_top[1] - charge_radius)

                self.image.blit(glow_surf, glow_pos)

    def draw_status_effects(self):

        """Draw active status effects around player"""

        if not self.status_effects:
            return

        # Draw effects as particles around player

        for effect in self.status_effects:

            effect_type = effect.get("type", "")

            if effect_type == "poison":

                color = COLORS["poison"]

            elif effect_type == "burn":

                color = COLORS["burn"]

            elif effect_type == "freeze":

                color = COLORS["freeze"]

            elif effect_type == "buff":

                color = COLORS["buff"]

            else:

                continue

            # Add some particle effects

            for _ in range(2):
                angle = self.animation_frame * 0.2 + random.random() * math.pi * 2

                distance = TILE_SIZE // 3 * (0.8 + random.random() * 0.4)

                x = TILE_SIZE // 2 + math.cos(angle) * distance

                y = TILE_SIZE // 2 + math.sin(angle) * distance

                size = 2 + random.randint(0, 2)

                # Draw particle

                pygame.draw.circle(self.image, color, (int(x), int(y)), size)

    def update(self, dt, game_map):

        """Update player state"""

        # Update animation frame

        self.animation_frame += dt * 10

        # Update cooldowns

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.skill_cooldown > 0:
            self.skill_cooldown -= dt

        # Update status effects

        self.update_status_effects(dt)

        # Update floating texts

        self.update_floating_texts(dt)

        # Update attacking animation

        if self.attacking:

            self.attack_frame += dt * 20

            if self.attack_frame >= 10:  # Attack animation finished

                self.attacking = False

                self.attack_frame = 0

        # Update appearance

        self.update_appearance()

    def update_status_effects(self, dt):

        """Update active status effects"""

        i = 0

        while i < len(self.status_effects):

            effect = self.status_effects[i]

            # Decrease duration

            effect["duration"] -= dt

            # Apply effect based on type

            if effect["type"] == "poison" and effect.get("tick_timer", 0) <= 0:

                damage = effect.get("value", 1)

                self.take_damage(damage)

                effect["tick_timer"] = 1.0  # Reset timer to 1 second

            elif effect["type"] == "burn" and effect.get("tick_timer", 0) <= 0:

                damage = effect.get("value", 1)

                self.take_damage(damage)

                effect["tick_timer"] = 0.5  # Reset timer to 0.5 seconds

            elif effect["type"] == "strength":

                # Modify attack stat (already applied when effect was added)

                pass

            elif effect["type"] == "defense":

                # Modify defense stat (already applied when effect was added)

                pass

            elif effect["type"] == "speed":

                # Modify speed stat (already applied when effect was added)

                pass

            # Update tick timer

            if "tick_timer" in effect:
                effect["tick_timer"] -= dt

            # Remove expired effects

            if effect["duration"] <= 0:

                # If it was a stat buff, remove the bonus

                if effect["type"] in ["strength", "defense", "speed"]:
                    stat_name = "attack" if effect["type"] == "strength" else effect["type"]

                    self.stats[stat_name] -= effect.get("value", 0)

                # Remove the effect

                self.status_effects.pop(i)

                self.add_floating_text(f"{effect['type']} faded", (180, 180, 180))

            else:

                i += 1

    def update_floating_texts(self, dt):

        """Update floating text positions and timers"""

        i = 0

        while i < len(self.floating_texts):

            text = self.floating_texts[i]

            text["duration"] -= dt

            text["y"] -= dt * 20  # Move upward

            # Remove expired texts

            if text["duration"] <= 0:

                self.floating_texts.pop(i)

            else:

                i += 1

    def move(self, dx, dy, game_map):

        """Move player with collision detection"""

        if dx == 0 and dy == 0:
            self.moving = False

            return

        self.moving = True

        # Set direction

        if dx > 0 and abs(dx) >= abs(dy):

            self.direction = "right"

        elif dx < 0 and abs(dx) >= abs(dy):

            self.direction = "left"

        elif dy > 0:

            self.direction = "down"

        elif dy < 0:

            self.direction = "up"

        # Calculate new position

        speed = PLAYER_SPEED

        # Apply speed buffs from effects

        for effect in self.status_effects:

            if effect["type"] == "speed":
                speed += effect.get("value", 0) / 10

        # Normalize diagonal movement

        if dx != 0 and dy != 0:
            norm = (dx ** 2 + dy ** 2) ** 0.5

            dx = dx / norm

            dy = dy / norm

        new_x = self.rect.x + dx * speed

        new_y = self.rect.y + dy * speed

        # Check collision in X direction

        tile_x = int(new_x / TILE_SIZE)

        tile_y = int(self.rect.y / TILE_SIZE)

        if game_map.is_passable(tile_x, tile_y):
            self.rect.x = new_x

        # Check collision in Y direction

        tile_x = int(self.rect.x / TILE_SIZE)

        tile_y = int(new_y / TILE_SIZE)

        if game_map.is_passable(tile_x, tile_y):
            self.rect.y = new_y

    def attack(self, targets=None):

        """Execute basic attack"""

        if self.attack_cooldown > 0 or self.attacking:
            return False

        self.attacking = True

        self.attack_frame = 0

        # Set attack cooldown based on weapon and agility

        base_cooldown = 1.0

        if self.equipped["weapon"]:

            if self.equipped["weapon"].weapon_type == WeaponType.DAGGER:

                base_cooldown = 0.7

            elif self.equipped["weapon"].weapon_type == WeaponType.GREATSWORD:

                base_cooldown = 1.5

        # Agility reduces cooldown

        cooldown_reduction = self.stats["agility"] / 100

        self.attack_cooldown = base_cooldown * (1 - cooldown_reduction)

        # Find targets in attack range if not provided

        if targets is None and hasattr(self, 'game'):
            targets = self.get_targets_in_range(self.stats["attack_range"])

        # Process attack on targets

        if targets:

            for target in targets:
                self.process_attack_on_target(target)

        return True

    def process_attack_on_target(self, target):
        """处理对单个目标的攻击伤害和效果"""
        # 计算伤害
        base_damage = self.stats["attack"] - target.stats.get("defense", 0) // 2
        damage = max(1, base_damage)

        # 检查暴击
        is_crit = random.random() * 100 < self.stats["crit"]
        if is_crit:
            damage = int(damage * 1.5)

        # 应用伤害
        target.take_damage(damage, is_crit)

        # 更新统计数据（如果有game引用）
        if hasattr(self, 'game') and self.game is not None:
            self.game.update_player_statistics("damage_dealt", damage)

        # 应用武器特定效果
        if self.equipped["weapon"]:
            weapon_type = self.equipped["weapon"].weapon_type

            # 匕首有几率施加中毒
            if weapon_type == WeaponType.DAGGER and random.random() < 0.2:
                poison_damage = max(1, self.stats["attack"] // 10)
                target.add_status_effect("poison", 3, poison_damage)

            # 法杖有几率施加灼烧
            elif weapon_type == WeaponType.STAFF and random.random() < 0.15:
                burn_damage = max(1, self.stats["attack"] // 8)
                target.add_status_effect("burn", 2, burn_damage)

            # 弓有几率造成额外伤害
            elif weapon_type == WeaponType.BOW and random.random() < 0.25:
                bonus_damage = max(1, self.stats["attack"] // 4)
                target.take_damage(bonus_damage)

                # 更新额外伤害统计
                if hasattr(self, 'game') and self.game is not None:
                    self.game.update_player_statistics("damage_dealt", bonus_damage)

        return damage

    def use_skill(self, skill_index, targets=None):

        """Use a skill by index"""

        if skill_index < 0 or skill_index >= len(self.skills):
            return False

        skill = self.skills[skill_index]

        # Check if skill can be used

        if self.skill_cooldown > 0 or not skill.can_use(self):
            return False

        # Set attack animation

        self.attacking = True

        self.attack_frame = 0

        # Find targets if needed

        if targets is None and skill.target_type == "single":

            targets = self.get_nearest_target(skill.range)

        elif targets is None and skill.target_type == "aoe":

            targets = self.get_targets_in_range(skill.range)

        # If no valid targets, don't use the skill

        if not targets and skill.target_type != "self":
            return False

        # For self-targeted skills like healing

        if skill.target_type == "self":
            targets = self

        # Use the skill

        result = skill.use(self, targets)

        # Set skill cooldown

        self.skill_cooldown = 0.5  # Global cooldown

        return result

    def get_nearest_target(self, range_tiles):

        """Get nearest valid target within range"""

        if not hasattr(self, 'game') or not self.game.enemies:
            return None

        nearest = None

        min_dist = range_tiles * TILE_SIZE

        for enemy in self.game.enemies:

            dist = ((enemy.rect.centerx - self.rect.centerx) ** 2 +

                    (enemy.rect.centery - self.rect.centery) ** 2) ** 0.5

            if dist < min_dist:
                min_dist = dist

                nearest = enemy

        return [nearest] if nearest else None

    def get_targets_in_range(self, range_tiles):

        """Get all valid targets within range"""

        if not hasattr(self, 'game') or not self.game.enemies:
            return []

        targets = []

        max_dist = range_tiles * TILE_SIZE

        for enemy in self.game.enemies:

            dist = ((enemy.rect.centerx - self.rect.centerx) ** 2 +

                    (enemy.rect.centery - self.rect.centery) ** 2) ** 0.5

            if dist <= max_dist:
                targets.append(enemy)

        return targets

    def take_damage(self, amount, is_crit=False):
        """接受伤害并显示浮动文字"""
        # 应用防御
        damage = max(1, amount)

        # 减少HP
        self.stats["hp"] = max(0, self.stats["hp"] - damage)

        # 显示浮动文字
        color = (255, 165, 0) if is_crit else (255, 70, 70)
        self.add_floating_text(str(damage), color)

        # 更新统计数据（如果有game引用）
        if hasattr(self, 'game') and self.game is not None:
            self.game.update_player_statistics("damage_taken", damage)

        return self.stats["hp"] > 0

    def heal(self, amount):

        """Heal HP and show floating text"""

        if amount <= 0:
            return

        old_hp = self.stats["hp"]

        self.stats["hp"] = min(self.stats["max_hp"], self.stats["hp"] + amount)

        healed = self.stats["hp"] - old_hp

        if healed > 0:
            self.add_floating_text("+" + str(healed), (100, 255, 100))

    def restore_mana(self, amount):

        """Restore MP and show floating text"""

        if amount <= 0:
            return

        old_mp = self.stats["mp"]

        self.stats["mp"] = min(self.stats["max_mp"], self.stats["mp"] + amount)

        restored = self.stats["mp"] - old_mp

        if restored > 0:
            self.add_floating_text("+" + str(restored) + " MP", (100, 100, 255))

    def add_status_effect(self, effect_type, duration, value=0):

        """Add a status effect"""

        # Check if effect already exists

        for effect in self.status_effects:

            if effect["type"] == effect_type:

                # Refresh duration

                effect["duration"] = max(effect["duration"], duration)

                # Update value if higher

                if value > effect.get("value", 0):
                    effect["value"] = value

                return

        # Create new effect

        effect = {

            "type": effect_type,

            "duration": duration,

            "value": value

        }

        # Add tick timer for DOT effects

        if effect_type in ["poison", "burn"]:
            effect["tick_timer"] = 1.0

        # For stat modifying effects, apply immediately

        if effect_type == "strength":

            self.stats["attack"] += value

        elif effect_type == "defense":

            self.stats["defense"] += value

        elif effect_type == "speed":

            self.stats["agility"] += value

        # Add to active effects

        self.status_effects.append(effect)

        # Show floating text

        self.add_floating_text(effect_type.upper(), COLORS.get(effect_type, (255, 255, 255)))

    def add_floating_text(self, text, color=(255, 255, 255), duration=1.0):

        """Add floating text above player"""

        self.floating_texts.append({

            "text": text,

            "color": color,

            "duration": duration,

            "y": -10  # Start above player head

        })

    def draw_floating_texts(self, surface, camera_pos):

        """Draw floating texts above player"""

        if not self.floating_texts:
            return

        # Calculate screen position

        screen_x = self.rect.centerx - camera_pos[0]

        screen_y = self.rect.top - camera_pos[1]

        font = pygame.font.Font(None, 18)

        for text in self.floating_texts:
            text_surface = font.render(text["text"], True, text["color"])

            text_rect = text_surface.get_rect(center=(screen_x, screen_y + text["y"]))

            surface.blit(text_surface, text_rect)

    def gain_exp(self, amount):

        """Gain experience and check for level up"""

        self.stats["exp"] += amount

        self.add_floating_text("+" + str(amount) + " EXP", (255, 255, 150))

        # Check for level up

        if self.stats["exp"] >= self.stats["next_level_exp"]:
            self.level_up()

            return True

        return False

    def level_up(self):

        """Process level up"""

        self.stats["level"] += 1

        self.stats["exp"] -= self.stats["next_level_exp"]

        self.stats["next_level_exp"] = int(self.stats["next_level_exp"] * 1.5)

        # Increase base stats

        self.stats["max_hp"] += 10 + self.stats["level"]

        self.stats["hp"] = self.stats["max_hp"]  # Fully heal on level up

        self.stats["max_mp"] += 5 + self.stats["level"] // 2

        self.stats["mp"] = self.stats["max_mp"]  # Fully restore mana

        self.stats["attack"] += 2

        self.stats["defense"] += 1

        self.stats["crit"] += 0.5

        self.stats["agility"] += 1

        # Update base stats

        self.base_stats = self.stats.copy()

        # Show level up text

        self.add_floating_text("LEVEL UP!", (255, 215, 0), 2.0)

        # Possibly learn new skills at certain levels

        if self.stats["level"] == 3 and len(self.skills) < 2:

            self.skills.append(copy.deepcopy(SKILLS[SkillType.HEAL]))

            self.add_floating_text("Learned: Heal", (100, 255, 100), 2.0)

        elif self.stats["level"] == 5 and len(self.skills) < 3:

            self.skills.append(copy.deepcopy(SKILLS[SkillType.FIREBALL]))

            self.add_floating_text("Learned: Fireball", (255, 100, 50), 2.0)

    def equip(self, item):

        """Equip an item"""

        if not item:
            return False

        # Remove current equipped item if any

        if item.type == ItemType.WEAPON and self.equipped["weapon"]:

            self.unequip("weapon")

        elif item.type == ItemType.ARMOR and self.equipped["armor"]:

            self.unequip("armor")

        # Equip new item

        if item.type == ItemType.WEAPON:

            self.equipped["weapon"] = item

            # Update attack range

            self.stats["attack_range"] = item.range

            # Add weapon skill if available

            if item.skill and not any(s.type == item.skill.type for s in self.skills):
                self.skills.append(item.skill)



        elif item.type == ItemType.ARMOR:

            self.equipped["armor"] = item

        else:

            # Not an equippable item

            return False

        # Apply stat bonuses

        for stat, value in item.stats.items():

            if stat in self.stats:
                self.stats[stat] += value

        item.equipped = True

        return True

    def unequip(self, slot):

        """Unequip item from specified slot"""

        if slot not in self.equipped or not self.equipped[slot]:
            return False

        item = self.equipped[slot]

        # Remove stat bonuses

        for stat, value in item.stats.items():

            if stat in self.stats:
                self.stats[stat] -= value

        # Reset attack range if unequipping a weapon

        if slot == "weapon":

            self.stats["attack_range"] = 1

            # Remove weapon skill if it was from this weapon

            if item.skill:

                skill_to_remove = None

                for skill in self.skills:

                    if skill.type == item.skill.type:
                        skill_to_remove = skill

                        break

                if skill_to_remove:
                    self.skills.remove(skill_to_remove)

        # Add item back to inventory

        self.add_to_inventory(item)

        # Clear slot

        self.equipped[slot] = None

        item.equipped = False

        return True

    def add_to_inventory(self, item):

        """Add item to inventory"""

        # Check for stackable items

        if item.type == ItemType.POTION:

            for inv_item in self.inventory:

                if inv_item.name == item.name and inv_item.type == item.type:
                    inv_item.count += item.count

                    return True

        # Check inventory limit

        if len(self.inventory) >= self.max_inventory:
            return False

        # Add to inventory

        self.inventory.append(item)

        return True

    def remove_from_inventory(self, index):

        """Remove item from inventory by index"""

        if 0 <= index < len(self.inventory):
            item = self.inventory.pop(index)

            return item

        return None

    def use_item(self, index):
        """使用背包中的物品"""
        if 0 <= index < len(self.inventory):
            item = self.inventory[index]

            # 处理药水
            if item.type == ItemType.POTION:
                # 更新统计数据（如果有game引用）
                if hasattr(self, 'game') and self.game is not None:
                    self.game.update_player_statistics("potions_used")

                # 生命药水
                if "hp" in item.stats:
                    self.heal(item.stats["hp"])

                # 法力药水
                if "mp" in item.stats:
                    self.restore_mana(item.stats["mp"])

                # 力量增益
                if "strength" in item.stats:
                    self.add_status_effect("strength", item.stats.get("duration", 60), item.stats["strength"])

                # 防御增益
                if "defense" in item.stats:
                    self.add_status_effect("defense", item.stats.get("duration", 60), item.stats["defense"])

                # 速度增益
                if "speed" in item.stats:
                    self.add_status_effect("speed", item.stats.get("duration", 60), item.stats["speed"])

                # 减少数量或移除
                item.count -= 1
                if item.count <= 0:
                    self.inventory.pop(index)

                return True

            # 处理装备
            elif item.type in [ItemType.WEAPON, ItemType.ARMOR]:
                self.equip(item)
                self.inventory.pop(index)
                return True

        return False

    def add_currency(self, gold=0, silver=0, copper=0):

        """Add currency with automatic conversion"""

        # Add copper

        self.copper += copper

        # Convert copper to silver

        if self.copper >= 10:
            self.silver += self.copper // 10

            self.copper %= 10

        # Add silver

        self.silver += silver

        # Convert silver to gold

        if self.silver >= 10:
            self.gold += self.silver // 10

            self.silver %= 10

        # Add gold

        self.gold += gold

    def get_total_copper(self):

        """Get total currency in copper value"""

        return self.gold * 100 + self.silver * 10 + self.copper

    def spend_currency(self, amount):

        """Spend currency, return True if successful"""

        total = self.get_total_copper()

        if total < amount:
            return False

        # Convert back to g/s/c

        remaining = total - amount

        self.gold = remaining // 100

        remaining %= 100

        self.silver = remaining // 10

        remaining %= 10

        self.copper = remaining

        return True


# Monster class

class Monster(pygame.sprite.Sprite):

    def __init__(self, x, y, monster_type, level=1, game=None):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.monster_type = monster_type
        self.level = level
        self.game = game  # 新增对游戏对象的引用

        # Animation state
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.direction = random.choice(["down", "up", "left", "right"])
        self.moving = False
        self.attacking = False
        self.attack_frame = 0

        # Set name based on type

        self.name = self.get_monster_name()

        # Initialize stats based on monster type and level

        self.initialize_stats()

        # Skills based on monster type

        self.skills = self.get_monster_skills()

        # Status effects

        self.status_effects = []

        # Floating text

        self.floating_texts = []

        # AI behavior

        self.aggro_range = 5 * TILE_SIZE

        self.attack_range = 1.5 * TILE_SIZE

        self.attack_cooldown = 0

        self.skill_cooldown = 0

        self.wander_cooldown = 0

        self.patrol_point = (x, y)

        self.patrol_radius = 3 * TILE_SIZE

        self.target = None

        self.path = []

        self.state = "idle"  # idle, patrol, chase, attack

        # Update appearance

        self.update_appearance()

    def get_monster_name(self):

        """Get name based on monster type"""

        if self.monster_type == MonsterType.SLIME:

            return "Slime"

        elif self.monster_type == MonsterType.WOLF:

            return "Wolf"

        elif self.monster_type == MonsterType.GOBLIN:

            return "Goblin"

        elif self.monster_type == MonsterType.SKELETON:

            return "Skeleton"

        elif self.monster_type == MonsterType.TROLL:

            return "Troll"

        elif self.monster_type == MonsterType.GHOST:

            return "Ghost"

        elif self.monster_type == MonsterType.DRAGON:

            return "Dragon"

        elif self.monster_type == MonsterType.BANDIT:

            return "Bandit"

        else:

            return "Unknown Monster"

    def initialize_stats(self):

        """Initialize monster stats based on type and level"""

        # Base stats for all monsters

        self.base_stats = {

            "level": self.level,

            "hp": 20 + self.level * 5,

            "max_hp": 20 + self.level * 5,

            "mp": 10 + self.level * 2,

            "max_mp": 10 + self.level * 2,

            "attack": 5 + self.level,

            "defense": 2 + self.level // 2,

            "crit": 3,

            "agility": 3,

            "exp_value": 10 + self.level * 5,

            "attack_range": 1,

            "attack_speed": 1.0

        }

        # Adjust stats based on monster type

        if self.monster_type == MonsterType.SLIME:

            self.base_stats.update({

                "hp": 15 + self.level * 4,

                "max_hp": 15 + self.level * 4,

                "attack": 3 + self.level,

                "defense": 1 + self.level // 3,

                "exp_value": 5 + self.level * 3

            })

        elif self.monster_type == MonsterType.WOLF:

            self.base_stats.update({

                "hp": 18 + self.level * 4,

                "max_hp": 18 + self.level * 4,

                "attack": 6 + self.level * 1.2,

                "agility": 7 + self.level // 2,

                "crit": 5,

                "attack_speed": 1.2

            })

        elif self.monster_type == MonsterType.GOBLIN:

            self.base_stats.update({

                "hp": 15 + self.level * 3,

                "max_hp": 15 + self.level * 3,

                "attack": 4 + self.level,

                "defense": 2 + self.level // 3,

                "agility": 5 + self.level // 2,

                "attack_speed": 1.1

            })

        elif self.monster_type == MonsterType.SKELETON:

            self.base_stats.update({

                "hp": 25 + self.level * 4,

                "max_hp": 25 + self.level * 4,

                "mp": 5 + self.level,

                "max_mp": 5 + self.level,

                "attack": 5 + self.level,

                "defense": 3 + self.level // 2,

                "agility": 2 + self.level // 3

            })

        elif self.monster_type == MonsterType.TROLL:

            self.base_stats.update({

                "hp": 40 + self.level * 8,

                "max_hp": 40 + self.level * 8,

                "mp": 5 + self.level,

                "max_mp": 5 + self.level,

                "attack": 8 + self.level * 1.5,

                "defense": 5 + self.level,

                "agility": 1 + self.level // 4,

                "attack_speed": 0.7,

                "exp_value": 15 + self.level * 8

            })

        elif self.monster_type == MonsterType.GHOST:

            self.base_stats.update({

                "hp": 20 + self.level * 3,

                "max_hp": 20 + self.level * 3,

                "mp": 20 + self.level * 3,

                "max_mp": 20 + self.level * 3,

                "attack": 3 + self.level * 0.8,

                "defense": 1 + self.level // 3,

                "agility": 4 + self.level // 2,

                "attack_range": 2

            })

        elif self.monster_type == MonsterType.DRAGON:

            self.base_stats.update({

                "hp": 60 + self.level * 10,

                "max_hp": 60 + self.level * 10,

                "mp": 30 + self.level * 5,

                "max_mp": 30 + self.level * 5,

                "attack": 12 + self.level * 2,

                "defense": 8 + self.level,

                "crit": 7,

                "agility": 3 + self.level // 3,

                "attack_range": 3,

                "exp_value": 50 + self.level * 15

            })

        elif self.monster_type == MonsterType.BANDIT:

            self.base_stats.update({

                "hp": 22 + self.level * 4,

                "max_hp": 22 + self.level * 4,

                "mp": 10 + self.level * 2,

                "max_mp": 10 + self.level * 2,

                "attack": 5 + self.level * 1.1,

                "defense": 3 + self.level // 2,

                "crit": 6,

                "agility": 6 + self.level // 2

            })

        # Copy to current stats

        self.stats = self.base_stats.copy()

    def get_monster_skills(self):

        """Get skills based on monster type"""

        skills = []

        # Assign skills based on monster type

        if self.monster_type == MonsterType.SLIME:

            # No special skills for slimes

            pass

        elif self.monster_type == MonsterType.WOLF:

            if self.level >= 3:
                skills.append(copy.deepcopy(SKILLS[SkillType.CHARGE]))

        elif self.monster_type == MonsterType.GOBLIN:

            if self.level >= 3:
                skills.append(copy.deepcopy(SKILLS[SkillType.POISON_STRIKE]))

        elif self.monster_type == MonsterType.SKELETON:

            if self.level >= 2:
                skills.append(copy.deepcopy(SKILLS[SkillType.SLASH]))

        elif self.monster_type == MonsterType.TROLL:

            if self.level >= 2:
                skills.append(copy.deepcopy(SKILLS[SkillType.SLASH]))

            if self.level >= 5:
                skills.append(copy.deepcopy(SKILLS[SkillType.WHIRLWIND]))

        elif self.monster_type == MonsterType.GHOST:

            if self.level >= 2:
                skills.append(copy.deepcopy(SKILLS[SkillType.FROST_NOVA]))

        elif self.monster_type == MonsterType.DRAGON:

            if self.level >= 1:
                skills.append(copy.deepcopy(SKILLS[SkillType.FIREBALL]))

            if self.level >= 5:
                skills.append(copy.deepcopy(SKILLS[SkillType.WHIRLWIND]))

        elif self.monster_type == MonsterType.BANDIT:

            if self.level >= 3:
                skills.append(copy.deepcopy(SKILLS[SkillType.SLASH]))

        return skills

    def draw(self, surface, camera_pos):
        """Draw monster on surface"""
        # Get screen position
        screen_x = self.rect.x - camera_pos[0]
        screen_y = self.rect.y - camera_pos[1]

        # Draw monster sprite
        surface.blit(self.image, (screen_x, screen_y))

    def update_appearance(self):

        """Update sprite appearance based on monster type and state"""

        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        # Draw based on monster type

        if self.monster_type == MonsterType.SLIME:

            self.draw_slime()

        elif self.monster_type == MonsterType.WOLF:

            self.draw_wolf()

        elif self.monster_type == MonsterType.GOBLIN:

            self.draw_goblin()

        elif self.monster_type == MonsterType.SKELETON:

            self.draw_skeleton()

        elif self.monster_type == MonsterType.TROLL:

            self.draw_troll()

        elif self.monster_type == MonsterType.GHOST:

            self.draw_ghost()

        elif self.monster_type == MonsterType.DRAGON:

            self.draw_dragon()

        elif self.monster_type == MonsterType.BANDIT:

            self.draw_bandit()

        # Draw status effects

        self.draw_status_effects()

    def draw_slime(self):

        """Draw slime monster"""

        # Animation bounce

        bounce = math.sin(self.animation_frame * 5) * 2

        # Base slime body - semi-circle

        slime_color = (100, 200, 100)  # Green

        radius = TILE_SIZE // 2

        # Draw main body

        pygame.draw.ellipse(self.image, slime_color,

                            pygame.Rect(0, TILE_SIZE // 4 - bounce // 2,

                                        TILE_SIZE, TILE_SIZE * 3 // 4 + bounce))

        # Draw eyes

        eye_y = TILE_SIZE // 2

        eye_spacing = TILE_SIZE // 4

        # Left eye

        pygame.draw.circle(self.image, (255, 255, 255),

                           (TILE_SIZE // 2 - eye_spacing, eye_y), 3)

        pygame.draw.circle(self.image, (0, 0, 0),

                           (TILE_SIZE // 2 - eye_spacing, eye_y), 1)

        # Right eye

        pygame.draw.circle(self.image, (255, 255, 255),

                           (TILE_SIZE // 2 + eye_spacing, eye_y), 3)

        pygame.draw.circle(self.image, (0, 0, 0),

                           (TILE_SIZE // 2 + eye_spacing, eye_y), 1)

        # Simple mouth

        mouth_y = TILE_SIZE * 2 // 3

        pygame.draw.arc(self.image, (0, 0, 0),

                        pygame.Rect(TILE_SIZE // 3, mouth_y - 3, TILE_SIZE // 3, 6),

                        0, math.pi, 1)

    def draw_wolf(self):

        """Draw wolf monster"""

        # Base wolf color

        wolf_body_color = (100, 100, 100)  # Gray

        wolf_outline_color = (50, 50, 50)  # Dark gray

        # Animation walk cycle

        walk_offset = math.sin(self.animation_frame * 5) * 2 if self.moving else 0

        # Wolf facing direction

        wolf_direction = self.direction

        # Draw body

        body_rect = pygame.Rect(TILE_SIZE // 4, TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE // 3)

        pygame.draw.ellipse(self.image, wolf_body_color, body_rect)

        pygame.draw.ellipse(self.image, wolf_outline_color, body_rect, 1)

        # Draw head

        if wolf_direction == "right":

            head_x = TILE_SIZE * 2 // 3

        elif wolf_direction == "left":

            head_x = TILE_SIZE // 3

        else:

            head_x = TILE_SIZE // 2

        head_y = TILE_SIZE // 3

        head_radius = TILE_SIZE // 6

        pygame.draw.circle(self.image, wolf_body_color, (head_x, head_y), head_radius)

        pygame.draw.circle(self.image, wolf_outline_color, (head_x, head_y), head_radius, 1)

        # Draw ears

        ear_offset = TILE_SIZE // 12

        pygame.draw.polygon(self.image, wolf_body_color, [

            (head_x - ear_offset, head_y - ear_offset),

            (head_x - ear_offset * 2, head_y - ear_offset * 3),

            (head_x, head_y - ear_offset * 2)

        ])

        pygame.draw.polygon(self.image, wolf_body_color, [

            (head_x + ear_offset, head_y - ear_offset),

            (head_x + ear_offset * 2, head_y - ear_offset * 3),

            (head_x, head_y - ear_offset * 2)

        ])

        # Draw eyes based on direction

        eye_spacing = 2

        if wolf_direction == "right":

            eye_x = head_x + 2

        elif wolf_direction == "left":

            eye_x = head_x - 2

        else:

            eye_x = head_x

        pygame.draw.circle(self.image, (255, 0, 0), (eye_x, head_y - 1), 2)

        # Draw legs

        leg_y = TILE_SIZE * 2 // 3

        # Front legs

        pygame.draw.line(self.image, wolf_outline_color,

                         (TILE_SIZE // 3, leg_y),

                         (TILE_SIZE // 3, leg_y + TILE_SIZE // 6 + walk_offset), 2)

        pygame.draw.line(self.image, wolf_outline_color,

                         (TILE_SIZE * 2 // 3, leg_y),

                         (TILE_SIZE * 2 // 3, leg_y + TILE_SIZE // 6 - walk_offset), 2)

        # Tail

        tail_start_x = TILE_SIZE // 3 if wolf_direction == "right" else TILE_SIZE * 2 // 3

        tail_start_y = TILE_SIZE // 2

        tail_end_x = tail_start_x - TILE_SIZE // 4 if wolf_direction == "right" else tail_start_x + TILE_SIZE // 4

        tail_end_y = tail_start_y - TILE_SIZE // 6

        pygame.draw.line(self.image, wolf_body_color,

                         (tail_start_x, tail_start_y),

                         (tail_end_x, tail_end_y), 2)

    def draw_goblin(self):

        """Draw goblin monster"""

        # Goblin colors

        goblin_body_color = (0, 150, 50)  # Green

        goblin_outline_color = (0, 100, 30)  # Dark green

        # Animation bouncing

        bounce = math.sin(self.animation_frame * 5) * 2 if self.moving else 0

        # Draw body

        body_rect = pygame.Rect(TILE_SIZE // 4, TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE // 3)

        pygame.draw.rect(self.image, goblin_body_color, body_rect)

        pygame.draw.rect(self.image, goblin_outline_color, body_rect, 1)

        # Draw head

        head_rect = pygame.Rect(TILE_SIZE // 3, TILE_SIZE // 6, TILE_SIZE // 3, TILE_SIZE // 4)

        pygame.draw.ellipse(self.image, goblin_body_color, head_rect)

        pygame.draw.ellipse(self.image, goblin_outline_color, head_rect, 1)

        # Draw pointed ears

        ear_length = TILE_SIZE // 6

        ear_width = TILE_SIZE // 12

        # Left ear

        pygame.draw.polygon(self.image, goblin_body_color, [

            (TILE_SIZE // 3, TILE_SIZE // 5),

            (TILE_SIZE // 6, TILE_SIZE // 10),

            (TILE_SIZE // 3 + ear_width, TILE_SIZE // 5)

        ])

        # Right ear

        pygame.draw.polygon(self.image, goblin_body_color, [

            (TILE_SIZE * 2 // 3, TILE_SIZE // 5),

            (TILE_SIZE * 5 // 6, TILE_SIZE // 10),

            (TILE_SIZE * 2 // 3 - ear_width, TILE_SIZE // 5)

        ])

        # Draw eyes based on direction

        eye_y = TILE_SIZE // 4

        if self.direction == "right":

            eye_x = TILE_SIZE * 7 // 12

        elif self.direction == "left":

            eye_x = TILE_SIZE * 5 // 12

        else:

            eye_x = TILE_SIZE // 2

        # Draw eye

        pygame.draw.circle(self.image, (255, 255, 0), (eye_x, eye_y), 2)

        # Draw arms

        arm_y = TILE_SIZE // 2

        # If attacking

        if self.attacking:

            # Based on attack progress

            attack_progress = self.attack_frame / 10.0

            if self.direction == "right":

                # Right arm attacking

                arm_angle = math.pi / 4 - attack_progress * math.pi / 2

                arm_length = TILE_SIZE // 3

                arm_end_x = TILE_SIZE * 2 // 3 + math.cos(arm_angle) * arm_length

                arm_end_y = arm_y + math.sin(arm_angle) * arm_length

                pygame.draw.line(self.image, goblin_body_color,

                                 (TILE_SIZE * 2 // 3, arm_y),

                                 (arm_end_x, arm_end_y), 2)

                # Draw weapon

                weapon_length = TILE_SIZE // 4

                weapon_end_x = arm_end_x + math.cos(arm_angle) * weapon_length

                weapon_end_y = arm_end_y + math.sin(arm_angle) * weapon_length

                pygame.draw.line(self.image, (200, 200, 100),

                                 (arm_end_x, arm_end_y),

                                 (weapon_end_x, weapon_end_y), 2)

            else:

                # Left arm attacking

                arm_angle = math.pi * 3 / 4 + attack_progress * math.pi / 2

                arm_length = TILE_SIZE // 3

                arm_end_x = TILE_SIZE // 3 + math.cos(arm_angle) * arm_length

                arm_end_y = arm_y + math.sin(arm_angle) * arm_length

                pygame.draw.line(self.image, goblin_body_color,

                                 (TILE_SIZE // 3, arm_y),

                                 (arm_end_x, arm_end_y), 2)

                # Draw weapon

                weapon_length = TILE_SIZE // 4

                weapon_end_x = arm_end_x + math.cos(arm_angle) * weapon_length

                weapon_end_y = arm_end_y + math.sin(arm_angle) * weapon_length

                pygame.draw.line(self.image, (200, 200, 100),

                                 (arm_end_x, arm_end_y),

                                 (weapon_end_x, weapon_end_y), 2)

        else:

            # Normal arms

            pygame.draw.line(self.image, goblin_body_color,

                             (TILE_SIZE // 3, arm_y),

                             (TILE_SIZE // 5, arm_y + TILE_SIZE // 6), 2)

            pygame.draw.line(self.image, goblin_body_color,

                             (TILE_SIZE * 2 // 3, arm_y),

                             (TILE_SIZE * 4 // 5, arm_y + TILE_SIZE // 6), 2)

        # Draw legs

        leg_y = TILE_SIZE * 2 // 3

        pygame.draw.line(self.image, goblin_body_color,

                         (TILE_SIZE * 3 // 8, leg_y),

                         (TILE_SIZE * 3 // 8, leg_y + TILE_SIZE // 3 + bounce), 2)

        pygame.draw.line(self.image, goblin_body_color,

                         (TILE_SIZE * 5 // 8, leg_y),

                         (TILE_SIZE * 5 // 8, leg_y + TILE_SIZE // 3 - bounce), 2)

    def draw_skeleton(self):

        """Draw skeleton monster"""

        # Skeleton colors

        bone_color = (230, 230, 220)  # Off-white

        shadow_color = (200, 200, 190)  # Slightly darker

        # Animation rattle

        rattle = (math.sin(self.animation_frame * 10) * 1) if self.moving else 0

        # Draw skull

        skull_x = TILE_SIZE // 2

        skull_y = TILE_SIZE // 4

        skull_radius = TILE_SIZE // 6

        pygame.draw.circle(self.image, bone_color, (skull_x, skull_y), skull_radius)

        # Draw eye sockets

        eye_spacing = TILE_SIZE // 10

        socket_radius = TILE_SIZE // 12

        pygame.draw.circle(self.image, (0, 0, 0),

                           (skull_x - eye_spacing, skull_y), socket_radius)

        pygame.draw.circle(self.image, (0, 0, 0),

                           (skull_x + eye_spacing, skull_y), socket_radius)

        # Draw jaw

        jaw_width = TILE_SIZE // 4

        jaw_height = TILE_SIZE // 10

        pygame.draw.rect(self.image, bone_color,

                         pygame.Rect(skull_x - jaw_width // 2,

                                     skull_y + skull_radius - jaw_height // 2,

                                     jaw_width, jaw_height))

        # Draw teeth lines

        teeth_spacing = jaw_width / 4

        for i in range(3):
            tooth_x = skull_x - jaw_width // 2 + teeth_spacing * (i + 1)

            pygame.draw.line(self.image, shadow_color,

                             (tooth_x, skull_y + skull_radius - jaw_height // 2),

                             (tooth_x, skull_y + skull_radius + jaw_height // 2), 1)

        # Draw spine and ribcage

        spine_x = skull_x

        spine_top = skull_y + skull_radius + jaw_height // 2

        spine_bottom = TILE_SIZE * 3 // 4

        # Spine

        pygame.draw.line(self.image, bone_color,

                         (spine_x, spine_top),

                         (spine_x, spine_bottom), 2)

        # Ribs

        rib_count = 3

        rib_spacing = (spine_bottom - spine_top) / (rib_count + 1)

        rib_width = TILE_SIZE // 3

        for i in range(rib_count):
            rib_y = spine_top + rib_spacing * (i + 1)

            # Left rib

            pygame.draw.arc(self.image, bone_color,

                            pygame.Rect(spine_x - rib_width, rib_y - rib_width // 2,

                                        rib_width, rib_width),

                            math.pi / 2, math.pi, 2)

            # Right rib

            pygame.draw.arc(self.image, bone_color,

                            pygame.Rect(spine_x, rib_y - rib_width // 2,

                                        rib_width, rib_width),

                            0, math.pi / 2, 2)

        # Draw arms

        if self.attacking:

            # Attack animation

            attack_progress = self.attack_frame / 10.0

            if self.direction == "right":

                # Right arm attacking

                arm_angle = -math.pi / 4 - attack_progress * math.pi / 2

                arm_length = TILE_SIZE // 3

                arm_end_x = spine_x + math.cos(arm_angle) * arm_length

                arm_end_y = spine_top + rib_spacing + math.sin(arm_angle) * arm_length

                pygame.draw.line(self.image, bone_color,

                                 (spine_x, spine_top + rib_spacing),

                                 (arm_end_x, arm_end_y), 2)

                # Draw weapon

                weapon_length = TILE_SIZE // 3

                weapon_end_x = arm_end_x + math.cos(arm_angle) * weapon_length

                weapon_end_y = arm_end_y + math.sin(arm_angle) * weapon_length

                pygame.draw.line(self.image, (150, 150, 150),

                                 (arm_end_x, arm_end_y),

                                 (weapon_end_x, weapon_end_y), 2)

            else:

                # Left arm attacking

                arm_angle = math.pi + math.pi / 4 + attack_progress * math.pi / 2

                arm_length = TILE_SIZE // 3

                arm_end_x = spine_x + math.cos(arm_angle) * arm_length

                arm_end_y = spine_top + rib_spacing + math.sin(arm_angle) * arm_length

                pygame.draw.line(self.image, bone_color,

                                 (spine_x, spine_top + rib_spacing),

                                 (arm_end_x, arm_end_y), 2)

                # Draw weapon

                weapon_length = TILE_SIZE // 3

                weapon_end_x = arm_end_x + math.cos(arm_angle) * weapon_length

                weapon_end_y = arm_end_y + math.sin(arm_angle) * weapon_length

                pygame.draw.line(self.image, (150, 150, 150),

                                 (arm_end_x, arm_end_y),

                                 (weapon_end_x, weapon_end_y), 2)

        else:

            # Normal arms

            arm_angle_left = math.pi - math.pi / 6 + rattle

            arm_angle_right = math.pi / 6 - rattle

            arm_length = TILE_SIZE // 3

            # Left arm

            arm_end_x = spine_x + math.cos(arm_angle_left) * arm_length

            arm_end_y = spine_top + rib_spacing + math.sin(arm_angle_left) * arm_length

            pygame.draw.line(self.image, bone_color,

                             (spine_x, spine_top + rib_spacing),

                             (arm_end_x, arm_end_y), 2)

            # Right arm

            arm_end_x = spine_x + math.cos(arm_angle_right) * arm_length

            arm_end_y = spine_top + rib_spacing + math.sin(arm_angle_right) * arm_length

            pygame.draw.line(self.image, bone_color,

                             (spine_x, spine_top + rib_spacing),

                             (arm_end_x, arm_end_y), 2)

        # Draw legs

        leg_angle_left = math.pi - math.pi / 8 + (rattle * 0.5)

        leg_angle_right = math.pi / 8 - (rattle * 0.5)

        leg_length = TILE_SIZE // 3

        # Left leg

        leg_end_x = spine_x + math.cos(leg_angle_left) * leg_length

        leg_end_y = spine_bottom + math.sin(leg_angle_left) * leg_length

        pygame.draw.line(self.image, bone_color,

                         (spine_x, spine_bottom),

                         (leg_end_x, leg_end_y), 2)

        # Right leg

        leg_end_x = spine_x + math.cos(leg_angle_right) * leg_length

        leg_end_y = spine_bottom + math.sin(leg_angle_right) * leg_length

        pygame.draw.line(self.image, bone_color,

                         (spine_x, spine_bottom),

                         (leg_end_x, leg_end_y), 2)

    def draw_troll(self):

        """Draw troll monster"""

        # Troll colors

        troll_body_color = (110, 139, 61)  # Olive green

        troll_dark_color = (90, 110, 50)  # Darker green

        # Animation stomp

        stomp = math.sin(self.animation_frame * 3) * 2 if self.moving else 0

        # Draw body - large and hunched

        body_width = TILE_SIZE * 2 // 3

        body_height = TILE_SIZE // 2

        body_x = (TILE_SIZE - body_width) // 2

        body_y = TILE_SIZE // 3

        pygame.draw.rect(self.image, troll_body_color,

                         pygame.Rect(body_x, body_y, body_width, body_height))

        pygame.draw.rect(self.image, troll_dark_color,

                         pygame.Rect(body_x, body_y, body_width, body_height), 1)

        # Draw head - slightly smaller than body

        head_width = body_width * 3 // 4

        head_height = TILE_SIZE // 3

        head_x = (TILE_SIZE - head_width) // 2

        head_y = body_y - head_height + TILE_SIZE // 12  # Hunched

        pygame.draw.rect(self.image, troll_body_color,

                         pygame.Rect(head_x, head_y, head_width, head_height))

        pygame.draw.rect(self.image, troll_dark_color,

                         pygame.Rect(head_x, head_y, head_width, head_height), 1)

        # Draw jaw/tusks

        jaw_width = head_width * 2 // 3

        jaw_height = TILE_SIZE // 8

        jaw_x = (TILE_SIZE - jaw_width) // 2

        jaw_y = head_y + head_height - TILE_SIZE // 16

        pygame.draw.rect(self.image, troll_body_color,

                         pygame.Rect(jaw_x, jaw_y, jaw_width, jaw_height))

        # Tusks

        tusk_length = TILE_SIZE // 8

        tusk_width = TILE_SIZE // 16

        # Left tusk

        pygame.draw.rect(self.image, (220, 220, 200),

                         pygame.Rect(jaw_x, jaw_y - tusk_length + TILE_SIZE // 16, tusk_width, tusk_length))

        # Right tusk

        pygame.draw.rect(self.image, (220, 220, 200),

                         pygame.Rect(jaw_x + jaw_width - tusk_width, jaw_y - tusk_length + TILE_SIZE // 16,

                                     tusk_width, tusk_length))

        # Draw eyes

        eye_y = head_y + head_height // 3

        eye_spacing = head_width // 3

        eye_size = TILE_SIZE // 16

        # Left eye

        pygame.draw.circle(self.image, (255, 0, 0),

                           (head_x + head_width // 3, eye_y), eye_size)

        # Right eye

        pygame.draw.circle(self.image, (255, 0, 0),

                           (head_x + head_width * 2 // 3, eye_y), eye_size)

        # Draw arms

        arm_width = TILE_SIZE // 8

        arm_height = TILE_SIZE // 2

        # Left arm

        pygame.draw.rect(self.image, troll_body_color,

                         pygame.Rect(body_x - arm_width // 2, body_y, arm_width, arm_height))

        # Right arm

        pygame.draw.rect(self.image, troll_body_color,

                         pygame.Rect(body_x + body_width - arm_width // 2, body_y, arm_width, arm_height))

        # If attacking, draw weapon

        if self.attacking:

            # Attack animation

            attack_progress = self.attack_frame / 10.0

            if self.direction in ["right", "down"]:

                # Weapon in right hand

                weapon_angle = math.pi / 4 - attack_progress * math.pi / 2

                weapon_length = TILE_SIZE // 2

                weapon_start_x = body_x + body_width

                weapon_start_y = body_y + TILE_SIZE // 4

                weapon_end_x = weapon_start_x + math.cos(weapon_angle) * weapon_length

                weapon_end_y = weapon_start_y + math.sin(weapon_angle) * weapon_length

                # Draw club/weapon

                pygame.draw.line(self.image, (150, 100, 50),

                                 (weapon_start_x, weapon_start_y),

                                 (weapon_end_x, weapon_end_y), 4)

                # Draw club end

                pygame.draw.circle(self.image, (170, 120, 70),

                                   (int(weapon_end_x), int(weapon_end_y)), 5)

            else:

                # Weapon in left hand

                weapon_angle = math.pi - math.pi / 4 + attack_progress * math.pi / 2

                weapon_length = TILE_SIZE // 2

                weapon_start_x = body_x

                weapon_start_y = body_y + TILE_SIZE // 4

                weapon_end_x = weapon_start_x + math.cos(weapon_angle) * weapon_length

                weapon_end_y = weapon_start_y + math.sin(weapon_angle) * weapon_length

                # Draw club/weapon

                pygame.draw.line(self.image, (150, 100, 50),

                                 (weapon_start_x, weapon_start_y),

                                 (weapon_end_x, weapon_end_y), 4)

                # Draw club end

                pygame.draw.circle(self.image, (170, 120, 70),

                                   (int(weapon_end_x), int(weapon_end_y)), 5)

        # Draw legs

        leg_width = TILE_SIZE // 6

        leg_height = TILE_SIZE // 4

        # Left leg with stomp animation

        pygame.draw.rect(self.image, troll_body_color,

                         pygame.Rect(body_x + body_width // 4 - leg_width // 2,

                                     body_y + body_height,

                                     leg_width, leg_height + stomp))

        # Right leg with opposite stomp animation

        pygame.draw.rect(self.image, troll_body_color,

                         pygame.Rect(body_x + body_width * 3 // 4 - leg_width // 2,

                                     body_y + body_height,

                                     leg_width, leg_height - stomp))

    def draw_ghost(self):

        """Draw ghost monster"""

        # Ghost colors - semi-transparent

        ghost_color = (220, 220, 255, 150)  # Pale blue with alpha

        ghost_outline = (180, 180, 220, 200)  # Slightly darker

        # Animation float

        float_offset = math.sin(self.animation_frame * 2) * 3

        # Create a temporary surface with alpha

        ghost_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

        # Draw ghost body - rounded rectangle

        body_rect = pygame.Rect(TILE_SIZE // 6, TILE_SIZE // 6 + float_offset,

                                TILE_SIZE * 2 // 3, TILE_SIZE * 2 // 3)

        # Draw filled body

        pygame.draw.rect(ghost_surface, ghost_color, body_rect, border_radius=8)

        # Draw outline

        pygame.draw.rect(ghost_surface, ghost_outline, body_rect, 1, border_radius=8)

        # Draw wavy bottom

        wave_points = []

        segments = 4

        wave_height = TILE_SIZE // 8

        for i in range(segments + 1):
            x = TILE_SIZE // 6 + i * (TILE_SIZE * 2 // 3) / segments

            y = body_rect.bottom + wave_height * math.sin(i * math.pi / 2 + self.animation_frame)

            wave_points.append((x, y))

        # Close shape by connecting back to body

        wave_points.append((body_rect.right, body_rect.bottom))

        wave_points.append((body_rect.left, body_rect.bottom))

        pygame.draw.polygon(ghost_surface, ghost_color, wave_points)

        # Draw eyes based on direction

        eye_y = TILE_SIZE // 3 + float_offset

        eye_spacing = TILE_SIZE // 6

        eye_radius = TILE_SIZE // 12

        # Direction-based eye positions

        if self.direction == "right":

            eye_offset = TILE_SIZE // 24

            left_eye_x = TILE_SIZE // 2

            right_eye_x = TILE_SIZE // 2 + eye_spacing

        elif self.direction == "left":

            eye_offset = -TILE_SIZE // 24

            left_eye_x = TILE_SIZE // 2 - eye_spacing

            right_eye_x = TILE_SIZE // 2

        else:

            eye_offset = 0

            left_eye_x = TILE_SIZE // 2 - eye_spacing // 2

            right_eye_x = TILE_SIZE // 2 + eye_spacing // 2

        # Draw eyes

        pygame.draw.circle(ghost_surface, (0, 0, 0),

                           (left_eye_x, eye_y), eye_radius)

        pygame.draw.circle(ghost_surface, (0, 0, 0),

                           (right_eye_x, eye_y), eye_radius)

        # Draw pupils

        pygame.draw.circle(ghost_surface, (255, 0, 0),

                           (left_eye_x + eye_offset, eye_y), eye_radius // 2)

        pygame.draw.circle(ghost_surface, (255, 0, 0),

                           (right_eye_x + eye_offset, eye_y), eye_radius // 2)

        # Draw mouth

        mouth_y = TILE_SIZE // 2 + float_offset

        mouth_width = TILE_SIZE // 4

        if self.attacking:

            # Open mouth when attacking

            pygame.draw.ellipse(ghost_surface, (0, 0, 0),

                                pygame.Rect(TILE_SIZE // 2 - mouth_width // 2, mouth_y,

                                            mouth_width, TILE_SIZE // 6))

        else:

            # Normal mouth

            pygame.draw.arc(ghost_surface, (0, 0, 0),

                            pygame.Rect(TILE_SIZE // 2 - mouth_width // 2, mouth_y,

                                        mouth_width, TILE_SIZE // 6),

                            0, math.pi, 2)

        # Ghostly particle effects

        for _ in range(3):
            particle_x = random.randint(body_rect.left, body_rect.right)

            particle_y = random.randint(body_rect.top, body_rect.bottom + wave_height)

            particle_radius = random.randint(1, 3)

            pygame.draw.circle(ghost_surface, (255, 255, 255, 100),

                               (particle_x, particle_y), particle_radius)

        # Copy to main image

        self.image.blit(ghost_surface, (0, 0))

    def draw_dragon(self):

        """Draw dragon monster"""

        # Dragon colors

        dragon_body_color = (200, 50, 50)  # Red

        dragon_dark_color = (150, 30, 30)  # Dark red

        # Animation wingbeat

        wing_offset = abs(math.sin(self.animation_frame * 3)) * 5 if self.state == "attack" else math.sin(
            self.animation_frame * 2) * 3

        # Draw body (oval)

        body_rect = pygame.Rect(TILE_SIZE // 6, TILE_SIZE // 3, TILE_SIZE * 2 // 3, TILE_SIZE // 3)

        pygame.draw.ellipse(self.image, dragon_body_color, body_rect)

        pygame.draw.ellipse(self.image, dragon_dark_color, body_rect, 1)

        # Draw neck/head

        head_direction = 1 if self.direction in ["right", "down"] else -1

        neck_top = body_rect.centery - TILE_SIZE // 6

        # Draw neck

        neck_points = [

            (body_rect.centerx, body_rect.centery),

            (body_rect.centerx + head_direction * TILE_SIZE // 6, neck_top),

            (body_rect.centerx + head_direction * TILE_SIZE // 4, neck_top),

        ]

        pygame.draw.polygon(self.image, dragon_body_color, neck_points)

        # Draw head (triangle)

        head_points = [

            (body_rect.centerx + head_direction * TILE_SIZE // 4, neck_top),

            (body_rect.centerx + head_direction * TILE_SIZE // 2, neck_top - TILE_SIZE // 8),

            (body_rect.centerx + head_direction * TILE_SIZE // 2, neck_top + TILE_SIZE // 8),

        ]

        pygame.draw.polygon(self.image, dragon_body_color, head_points)

        # Draw eye

        eye_x = body_rect.centerx + head_direction * TILE_SIZE // 3

        eye_y = neck_top - TILE_SIZE // 16

        pygame.draw.circle(self.image, (255, 255, 0), (eye_x, eye_y), 2)

        # Draw wings

        wing_top = body_rect.top - wing_offset

        # Left wing

        left_wing_points = [

            (body_rect.centerx - TILE_SIZE // 8, body_rect.top + TILE_SIZE // 12),

            (body_rect.centerx - TILE_SIZE // 3, wing_top),

            (body_rect.left, wing_top + TILE_SIZE // 6),

        ]

        pygame.draw.polygon(self.image, dragon_body_color, left_wing_points)

        pygame.draw.polygon(self.image, dragon_dark_color, left_wing_points, 1)

        # Right wing

        right_wing_points = [

            (body_rect.centerx + TILE_SIZE // 8, body_rect.top + TILE_SIZE // 12),

            (body_rect.centerx + TILE_SIZE // 3, wing_top),

            (body_rect.right, wing_top + TILE_SIZE // 6),

        ]

        pygame.draw.polygon(self.image, dragon_body_color, right_wing_points)

        pygame.draw.polygon(self.image, dragon_dark_color, right_wing_points, 1)

        # Draw tail

        tail_points = [

            (body_rect.centerx - head_direction * TILE_SIZE // 8, body_rect.centery),

            (body_rect.centerx - head_direction * TILE_SIZE // 3, body_rect.bottom + TILE_SIZE // 8),

            (body_rect.centerx - head_direction * TILE_SIZE // 2, body_rect.bottom + TILE_SIZE // 6),

        ]

        pygame.draw.polygon(self.image, dragon_body_color, tail_points)

        pygame.draw.polygon(self.image, dragon_dark_color, tail_points, 1)

        # Draw legs

        leg_length = TILE_SIZE // 6

        # Front legs

        front_leg_x = body_rect.centerx + head_direction * TILE_SIZE // 6

        pygame.draw.line(self.image, dragon_body_color,

                         (front_leg_x, body_rect.bottom),

                         (front_leg_x, body_rect.bottom + leg_length), 2)

        # Back legs

        back_leg_x = body_rect.centerx - head_direction * TILE_SIZE // 6

        pygame.draw.line(self.image, dragon_body_color,

                         (back_leg_x, body_rect.bottom),

                         (back_leg_x, body_rect.bottom + leg_length), 2)

        # Fire breath when attacking

        if self.attacking and self.attack_frame > 5:

            fire_start_x = body_rect.centerx + head_direction * TILE_SIZE // 2

            fire_start_y = neck_top

            fire_length = TILE_SIZE // 2

            # Draw multiple fire particles

            for _ in range(8):
                angle_offset = random.uniform(-0.3, 0.3)

                length_offset = random.uniform(0.5, 1.0)

                width = random.randint(2, 4)

                angle = 0 if head_direction > 0 else math.pi

                angle += angle_offset

                fire_end_x = fire_start_x + head_direction * fire_length * length_offset * math.cos(angle)

                fire_end_y = fire_start_y + fire_length * length_offset * math.sin(angle)

                # Create gradient colors for fire

                colors = [(255, 50, 0), (255, 150, 0), (255, 200, 50)]

                color = random.choice(colors)

                pygame.draw.line(self.image, color,

                                 (fire_start_x, fire_start_y),

                                 (fire_end_x, fire_end_y), width)

    def draw_bandit(self):

        """Draw bandit monster"""

        # Bandit colors

        bandit_body_color = (120, 100, 80)  # Brown

        bandit_dark_color = (80, 60, 40)  # Dark brown

        cloth_color = (160, 30, 30)  # Red cloth

        # Animation walking

        walk_offset = math.sin(self.animation_frame * 5) * 2 if self.moving else 0

        # Draw body

        body_rect = pygame.Rect(TILE_SIZE // 3, TILE_SIZE // 3, TILE_SIZE // 3, TILE_SIZE // 3)

        pygame.draw.rect(self.image, bandit_body_color, body_rect)

        # Draw head with face covering

        head_x = TILE_SIZE // 2

        head_y = TILE_SIZE // 4

        head_radius = TILE_SIZE // 6

        pygame.draw.circle(self.image, bandit_body_color, (head_x, head_y), head_radius)

        # Face covering

        face_rect = pygame.Rect(head_x - head_radius, head_y - TILE_SIZE // 24,

                                head_radius * 2, TILE_SIZE // 8)

        pygame.draw.rect(self.image, cloth_color, face_rect)

        # Eyes

        eye_y = head_y - TILE_SIZE // 16

        eye_spacing = TILE_SIZE // 10

        # Adjust eye position based on direction

        if self.direction == "right":

            eye_offset = TILE_SIZE // 32

        elif self.direction == "left":

            eye_offset = -TILE_SIZE // 32

        else:

            eye_offset = 0

        # Draw eyes

        pygame.draw.circle(self.image, (50, 50, 50),

                           (head_x - eye_spacing // 2 + eye_offset, eye_y), 2)

        pygame.draw.circle(self.image, (50, 50, 50),

                           (head_x + eye_spacing // 2 + eye_offset, eye_y), 2)

        # Draw arms

        arm_y = body_rect.centery

        arm_length = TILE_SIZE // 4

        # Determine attack state for arms

        if self.attacking:

            attack_progress = self.attack_frame / 10.0

            if self.direction == "right":

                # Right arm attack

                arm_angle = math.pi / 6 - attack_progress * math.pi / 2

                arm_end_x = TILE_SIZE // 2 + math.cos(arm_angle) * arm_length

                arm_end_y = arm_y + math.sin(arm_angle) * arm_length

                pygame.draw.line(self.image, bandit_body_color,

                                 (body_rect.right, arm_y),

                                 (arm_end_x, arm_end_y), 2)

                # Draw dagger

                dagger_length = TILE_SIZE // 5

                dagger_end_x = arm_end_x + math.cos(arm_angle) * dagger_length

                dagger_end_y = arm_end_y + math.sin(arm_angle) * dagger_length

                pygame.draw.line(self.image, (200, 200, 200),

                                 (arm_end_x, arm_end_y),

                                 (dagger_end_x, dagger_end_y), 2)

            else:

                # Left arm attack

                arm_angle = math.pi - math.pi / 6 + attack_progress * math.pi / 2

                arm_end_x = TILE_SIZE // 2 + math.cos(arm_angle) * arm_length

                arm_end_y = arm_y + math.sin(arm_angle) * arm_length

                pygame.draw.line(self.image, bandit_body_color,

                                 (body_rect.left, arm_y),

                                 (arm_end_x, arm_end_y), 2)

                # Draw dagger

                dagger_length = TILE_SIZE // 5

                dagger_end_x = arm_end_x + math.cos(arm_angle) * dagger_length

                dagger_end_y = arm_end_y + math.sin(arm_angle) * dagger_length

                pygame.draw.line(self.image, (200, 200, 200),

                                 (arm_end_x, arm_end_y),

                                 (dagger_end_x, dagger_end_y), 2)

        else:

            # Regular arms

            pygame.draw.line(self.image, bandit_body_color,

                             (body_rect.left, arm_y),

                             (body_rect.left - TILE_SIZE // 8, arm_y + walk_offset), 2)

            pygame.draw.line(self.image, bandit_body_color,

                             (body_rect.right, arm_y),

                             (body_rect.right + TILE_SIZE // 8, arm_y - walk_offset), 2)

        # Draw legs

        leg_y = body_rect.bottom

        leg_length = TILE_SIZE // 4

        # Left leg

        pygame.draw.line(self.image, bandit_body_color,

                         (body_rect.left + TILE_SIZE // 12, leg_y),

                         (body_rect.left + TILE_SIZE // 12, leg_y + leg_length + walk_offset), 2)

        # Right leg

        pygame.draw.line(self.image, bandit_body_color,

                         (body_rect.right - TILE_SIZE // 12, leg_y),

                         (body_rect.right - TILE_SIZE // 12, leg_y + leg_length - walk_offset), 2)

    def draw_status_effects(self):

        """Draw status effects around monster"""

        if not self.status_effects:
            return

        # Draw effects as particles

        for effect in self.status_effects:

            effect_type = effect.get("type", "")

            if effect_type == "poison":

                color = COLORS["poison"]

            elif effect_type == "burn":

                color = COLORS["burn"]

            elif effect_type == "freeze":

                color = COLORS["freeze"]

            elif effect_type == "stun":

                color = (255, 255, 0)

            else:

                continue

            # Add particle effects

            for _ in range(2):
                angle = self.animation_frame * 0.2 + random.random() * math.pi * 2

                distance = TILE_SIZE // 3 * (0.8 + random.random() * 0.4)

                x = TILE_SIZE // 2 + math.cos(angle) * distance

                y = TILE_SIZE // 2 + math.sin(angle) * distance

                size = 2 + random.randint(0, 2)

                # Draw particle

                pygame.draw.circle(self.image, color, (int(x), int(y)), size)

    def update(self, dt, player, game_map):

        """Update monster state"""

        # Update animation frame

        self.animation_frame += dt * 10

        # Update cooldowns

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.skill_cooldown > 0:
            self.skill_cooldown -= dt

        if self.wander_cooldown > 0:
            self.wander_cooldown -= dt

        # Update status effects

        self.update_status_effects(dt)

        # Update floating texts

        self.update_floating_texts(dt)

        # Update attacking animation

        if self.attacking:

            self.attack_frame += dt * 20

            if self.attack_frame >= 10:  # Attack animation finished

                self.attacking = False

                self.attack_frame = 0

        # Update AI behavior

        if not self.is_stunned():
            self.update_ai(player, game_map)

        # Update appearance

        self.update_appearance()

    def update_status_effects(self, dt):

        """Update active status effects"""

        i = 0

        while i < len(self.status_effects):

            effect = self.status_effects[i]

            # Decrease duration

            effect["duration"] -= dt

            # Apply effect based on type

            if effect["type"] == "poison" and effect.get("tick_timer", 0) <= 0:

                damage = effect.get("value", 1)

                self.take_damage(damage)

                effect["tick_timer"] = 1.0  # Reset timer to 1 second

            elif effect["type"] == "burn" and effect.get("tick_timer", 0) <= 0:

                damage = effect.get("value", 1)

                self.take_damage(damage)

                effect["tick_timer"] = 0.5  # Reset timer to 0.5 seconds

            elif effect["type"] == "freeze" or effect["type"] == "stun":

                # Movement restriction is handled in AI update

                pass

            # Update tick timer

            if "tick_timer" in effect:
                effect["tick_timer"] -= dt

            # Remove expired effects

            if effect["duration"] <= 0:

                self.status_effects.pop(i)

                self.add_floating_text(f"{effect['type']} faded", (180, 180, 180))

            else:

                i += 1

    def update_floating_texts(self, dt):

        """Update floating text positions and timers"""

        i = 0

        while i < len(self.floating_texts):

            text = self.floating_texts[i]

            text["duration"] -= dt

            text["y"] -= dt * 20  # Move upward

            # Remove expired texts

            if text["duration"] <= 0:

                self.floating_texts.pop(i)

            else:

                i += 1

    def is_stunned(self):

        """Check if monster is stunned or frozen"""

        for effect in self.status_effects:

            if effect["type"] in ["stun", "freeze"]:
                return True

        return False

    def update_ai(self, player, game_map):

        """Update AI behavior"""

        # Calculate distance to player

        dist_to_player = ((player.rect.centerx - self.rect.centerx) ** 2 +

                          (player.rect.centery - self.rect.centery) ** 2) ** 0.5

        # Decide state based on distance

        if dist_to_player <= self.attack_range:

            self.state = "attack"

            self.target = player

            self.moving = False

        elif dist_to_player <= self.aggro_range:

            self.state = "chase"

            self.target = player

            self.moving = True

        elif self.wander_cooldown <= 0:

            self.state = "patrol"

            self.moving = True

            # Set new patrol target

            if random.random() < 0.05:
                angle = random.random() * math.pi * 2

                distance = random.random() * self.patrol_radius

                self.patrol_point = (

                    self.rect.centerx + math.cos(angle) * distance,

                    self.rect.centery + math.sin(angle) * distance

                )

                self.wander_cooldown = random.uniform(1.0, 3.0)

        else:

            self.state = "idle"

            self.moving = False

        # Update behavior based on state

        if self.state == "attack":

            # Face the player

            self.face_target(player.rect.center)

            # Attack if cooldown is ready

            if self.attack_cooldown <= 0:

                # Try to use skill if available

                if self.skills and random.random() < 0.3 and self.skill_cooldown <= 0:

                    skill = random.choice(self.skills)

                    if skill.can_use(self):
                        self.use_skill(skill, player)

                        return

                # Regular attack

                self.attack(player)



        elif self.state == "chase":

            # Move toward player

            self.move_toward(player.rect.center, game_map)



        elif self.state == "patrol":

            # Move toward patrol point

            if self.patrol_point:
                self.move_toward(self.patrol_point, game_map)

    def face_target(self, target_pos):

        """Update direction to face target"""

        dx = target_pos[0] - self.rect.centerx

        dy = target_pos[1] - self.rect.centery

        if abs(dx) > abs(dy):

            self.direction = "right" if dx > 0 else "left"

        else:

            self.direction = "down" if dy > 0 else "up"

    def move_toward(self, target_pos, game_map):

        """Move toward target position with pathfinding"""

        # Simple direct movement for now

        # A* pathfinding would be better but more complex

        # Calculate direction

        dx = target_pos[0] - self.rect.centerx

        dy = target_pos[1] - self.rect.centery

        # Normalize

        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist == 0:
            return

        dx = dx / dist

        dy = dy / dist

        # Update direction

        if abs(dx) > abs(dy):

            self.direction = "right" if dx > 0 else "left"

        else:

            self.direction = "down" if dy > 0 else "up"

        # Calculate movement speed based on monster type

        speed = 1.0  # Default speed

        if self.monster_type == MonsterType.WOLF:

            speed = 1.5

        elif self.monster_type == MonsterType.GOBLIN:

            speed = 1.2

        elif self.monster_type == MonsterType.TROLL:

            speed = 0.7

        elif self.monster_type == MonsterType.GHOST:

            speed = 1.3

        # Calculate new position

        new_x = self.rect.x + dx * speed * PLAYER_SPEED * 0.8

        new_y = self.rect.y + dy * speed * PLAYER_SPEED * 0.8

        # Check collision in X direction

        tile_x = int(new_x / TILE_SIZE)

        tile_y = int(self.rect.y / TILE_SIZE)

        if game_map.is_passable(tile_x, tile_y):
            self.rect.x = new_x

        # Check collision in Y direction

        tile_x = int(self.rect.x / TILE_SIZE)

        tile_y = int(new_y / TILE_SIZE)

        if game_map.is_passable(tile_x, tile_y):
            self.rect.y = new_y

    def attack(self, target):

        """Execute attack on target"""

        if self.attack_cooldown > 0 or self.attacking:
            return False

        self.attacking = True

        self.attack_frame = 0

        # Set attack cooldown based on monster type

        base_cooldown = 1.0

        if self.monster_type == MonsterType.WOLF:

            base_cooldown = 0.8

        elif self.monster_type == MonsterType.TROLL:

            base_cooldown = 1.5

        elif self.monster_type == MonsterType.DRAGON:

            base_cooldown = 1.2

        self.attack_cooldown = base_cooldown

        # Calculate damage

        base_damage = self.stats["attack"] - target.stats["defense"] // 2

        damage = max(1, base_damage)

        # Check for critical hit

        is_crit = random.random() * 100 < self.stats["crit"]

        if is_crit:
            damage = int(damage * 1.5)

        # Apply damage

        target.take_damage(damage, is_crit)

        # Apply special effects based on monster type

        if self.monster_type == MonsterType.WOLF and random.random() < 0.2:

            # Wolves can cause bleeding

            bleed_damage = max(1, self.stats["attack"] // 10)

            target.add_status_effect("bleed", 3, bleed_damage)



        elif self.monster_type == MonsterType.GHOST and random.random() < 0.15:

            # Ghosts can cause fear (reduces defense)

            target.add_status_effect("fear", 4, self.stats["level"])



        elif self.monster_type == MonsterType.DRAGON and random.random() < 0.3:

            # Dragons can cause burn

            burn_damage = max(1, self.stats["attack"] // 5)

            target.add_status_effect("burn", 3, burn_damage)

        return True

    def use_skill(self, skill, target):

        """Use a skill on target"""

        if not skill.can_use(self):
            return False

        self.attacking = True

        self.attack_frame = 0

        # Use the skill

        result = skill.use(self, target)

        # Set cooldowns

        self.attack_cooldown = 1.0

        self.skill_cooldown = 3.0

        return result

    def take_damage(self, amount, is_crit=False):
        """处理受到伤害并在死亡时触发相应事件"""
        # 应用防御计算伤害
        damage = max(1, amount)

        # 减少HP
        self.stats["hp"] = max(0, self.stats["hp"] - damage)

        # 显示伤害浮动文字
        color = (255, 165, 0) if is_crit else (255, 255, 255)
        self.add_floating_text(str(damage), color)

        # 检查是否死亡
        is_alive = self.stats["hp"] > 0

        # 如果怪物死亡并且有game引用，触发死亡处理
        if not is_alive and hasattr(self, 'game') and self.game is not None:
            self.game.handle_monster_death(self)

        return is_alive

    def add_status_effect(self, effect_type, duration, value=0):

        """Add a status effect"""

        # Check if effect already exists

        for effect in self.status_effects:

            if effect["type"] == effect_type:

                # Refresh duration

                effect["duration"] = max(effect["duration"], duration)

                # Update value if higher

                if value > effect.get("value", 0):
                    effect["value"] = value

                return

        # Create new effect

        effect = {

            "type": effect_type,

            "duration": duration,

            "value": value

        }

        # Add tick timer for DOT effects

        if effect_type in ["poison", "burn", "bleed"]:
            effect["tick_timer"] = 1.0

        # Add to active effects

        self.status_effects.append(effect)

        # Show floating text

        self.add_floating_text(effect_type.upper(), COLORS.get(effect_type, (255, 255, 255)))

    def add_floating_text(self, text, color=(255, 255, 255), duration=1.0):

        """Add floating text above monster"""

        self.floating_texts.append({

            "text": text,

            "color": color,

            "duration": duration,

            "y": -10  # Start above monster head

        })

    def draw_floating_texts(self, surface, camera_pos):

        """Draw floating texts above monster"""

        if not self.floating_texts:
            return

        # Calculate screen position

        screen_x = self.rect.centerx - camera_pos[0]

        screen_y = self.rect.top - camera_pos[1]

        font = pygame.font.Font(None, 18)

        for text in self.floating_texts:
            text_surface = font.render(text["text"], True, text["color"])

            text_rect = text_surface.get_rect(center=(screen_x, screen_y + text["y"]))

            surface.blit(text_surface, text_rect)


# NPC class for shopkeepers, quest givers

class NPC(pygame.sprite.Sprite):

    def __init__(self, x, y, biome, items=None):

        super().__init__()

        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

        self.rect = self.image.get_rect(center=(x, y))

        self.biome = biome

        self.items = items or []

        # Generate items if not provided

        if not self.items:
            self.generate_shop_items()

        # Animation state

        self.animation_frame = 0

        self.animation_speed = 0.1

        self.direction = random.choice(["down", "up", "left", "right"])

        self.talking = False

        # Interaction

        self.interaction_radius = TILE_SIZE * 2

        self.dialogue = self.get_random_dialogue()

        self.interact_cooldown = 0

        # Update appearance

        self.update_appearance()

    def generate_shop_items(self):

        """Generate shop items based on biome"""

        if self.biome not in BIOME_SHOPS:
            self.biome = Biome.PLAINS  # Default

        shop_config = BIOME_SHOPS[self.biome]

        # Generate 3-6 items

        num_items = random.randint(3, 6)

        for _ in range(num_items):

            # Select item type

            item_type, type_weights = random.choices(shop_config["items"], k=1)[0]

            if item_type == ItemType.WEAPON:

                # Choose weapon type

                weapon_type = random.choices(

                    list(type_weights.keys()),

                    weights=list(type_weights.values()),

                    k=1

                )[0]

                # Determine quality based on location

                # More advanced biomes = better gear chance

                if self.biome in [Biome.VOLCANIC, Biome.TUNDRA]:

                    qualities = ["base", "uncommon", "rare", "epic"]

                    weights = [40, 30, 20, 10]

                elif self.biome in [Biome.MOUNTAINS, Biome.DESERT]:

                    qualities = ["base", "uncommon", "rare", "epic"]

                    weights = [50, 30, 15, 5]

                else:

                    qualities = ["base", "uncommon", "rare", "epic"]

                    weights = [60, 30, 9, 1]

                quality = random.choices(qualities, weights=weights, k=1)[0]

                # Get the weapon

                weapon = copy.deepcopy(UPGRADED_WEAPONS[weapon_type][quality])

                # Add the item

                self.items.append(weapon)



            elif item_type == ItemType.ARMOR:

                # Choose armor type

                armor_type = random.choices(

                    list(type_weights.keys()),

                    weights=list(type_weights.values()),

                    k=1

                )[0]

                # Determine quality based on location

                if self.biome in [Biome.VOLCANIC, Biome.TUNDRA]:

                    qualities = ["base", "uncommon", "rare", "epic"]

                    weights = [40, 30, 20, 10]

                elif self.biome in [Biome.MOUNTAINS, Biome.DESERT]:

                    qualities = ["base", "uncommon", "rare", "epic"]

                    weights = [50, 30, 15, 5]

                else:

                    qualities = ["base", "uncommon", "rare", "epic"]

                    weights = [60, 30, 9, 1]

                quality = random.choices(qualities, weights=weights, k=1)[0]

                # Get the armor

                armor = copy.deepcopy(UPGRADED_ARMORS[armor_type][quality])

                # Add the item

                self.items.append(armor)



            elif item_type == ItemType.POTION:

                # Choose potion type

                potion_type = random.choices(

                    list(type_weights.keys()),

                    weights=list(type_weights.values()),

                    k=1

                )[0]

                # Get the potion

                potion = copy.deepcopy(POTIONS[potion_type])

                # Add the item

                self.items.append(potion)

    def get_random_dialogue(self):

        """Generate random shop dialogue based on biome"""

        greetings = [

            "Welcome to my shop!",

            "Hello traveler, looking to trade?",

            "Fine goods for sale!",

            "What can I get for you today?",

            "Ah, a customer! Browse my wares."

        ]

        biome_specific = {

            Biome.PLAINS: [

                "The plains are peaceful today.",

                "Watch for wolves if you travel east.",

                "Our village grows the finest crops in the land."

            ],

            Biome.FOREST: [

                "The forest hides many secrets... and dangers.",

                "Don't venture too deep into the woods after dark.",

                "Herbs from these woods make powerful potions."

            ],

            Biome.MOUNTAINS: [

                "The mountains forge the strongest weapons.",

                "Beware the trolls that dwell in the caves.",

                "The high peaks are treacherous but beautiful."

            ],

            Biome.DESERT: [

                "Water is precious here in the desert.",

                "The sands shift and change, much like fortunes.",

                "Desert monsters are fierce - be prepared."

            ],

            Biome.SWAMP: [

                "Mind your step in the swamp.",

                "The murky waters hide many treasures... and dangers.",

                "My goods are the finest you'll find in this bog."

            ],

            Biome.TUNDRA: [

                "Keep warm in these cold lands.",

                "The frozen wastes are unforgiving.",

                "My hearth is always warm for travelers."

            ],

            Biome.VOLCANIC: [

                "Heat-forged weapons are the strongest.",

                "Be wary of fire drakes in the volcanic region.",

                "This obsidian was harvested from the volcano itself."

            ]

        }

        # Select greeting

        dialogue = random.choice(greetings)

        # Add biome-specific line if available

        if self.biome in biome_specific:
            dialogue += " " + random.choice(biome_specific[self.biome])

        return dialogue

    def update_appearance(self):

        """Update sprite appearance based on biome and state"""

        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        # Base colors based on biome

        if self.biome == Biome.PLAINS:

            body_color = (180, 140, 100)  # Light brown

            clothes_color = (100, 180, 100)  # Green

        elif self.biome == Biome.FOREST:

            body_color = (180, 140, 100)

            clothes_color = (40, 120, 40)  # Dark green

        elif self.biome == Biome.MOUNTAINS:

            body_color = (200, 160, 120)

            clothes_color = (150, 150, 150)  # Gray

        elif self.biome == Biome.DESERT:

            body_color = (220, 180, 140)  # Tan

            clothes_color = (220, 180, 60)  # Yellow

        elif self.biome == Biome.SWAMP:

            body_color = (180, 140, 100)

            clothes_color = (80, 100, 60)  # Olive

        elif self.biome == Biome.TUNDRA:

            body_color = (200, 160, 120)

            clothes_color = (220, 220, 240)  # White/blue

        elif self.biome == Biome.VOLCANIC:

            body_color = (180, 140, 100)

            clothes_color = (180, 60, 40)  # Red

        else:

            body_color = (180, 140, 100)

            clothes_color = (100, 100, 180)  # Blue

        # Animation bobbing

        bob = math.sin(self.animation_frame * 3) * 2

        # Draw body

        body_rect = pygame.Rect(TILE_SIZE // 3, TILE_SIZE // 3 + bob, TILE_SIZE // 3, TILE_SIZE // 3)

        pygame.draw.rect(self.image, body_color, body_rect)

        # Draw head

        head_x = TILE_SIZE // 2

        head_y = TILE_SIZE // 4 + bob

        head_radius = TILE_SIZE // 6

        pygame.draw.circle(self.image, body_color, (head_x, head_y), head_radius)

        # Draw hat/feature based on biome

        if self.biome == Biome.PLAINS:

            # Straw hat

            pygame.draw.ellipse(self.image, (220, 200, 100),

                                pygame.Rect(head_x - head_radius - 2, head_y - head_radius // 2,

                                            head_radius * 2 + 4, head_radius))

        elif self.biome == Biome.FOREST:

            # Hood

            hood_rect = pygame.Rect(head_x - head_radius, head_y - head_radius - 2,

                                    head_radius * 2, head_radius + 2)

            pygame.draw.ellipse(self.image, clothes_color, hood_rect)

        elif self.biome == Biome.MOUNTAINS:

            # Helmet

            pygame.draw.rect(self.image, (150, 150, 150),

                             pygame.Rect(head_x - head_radius, head_y - head_radius,

                                         head_radius * 2, head_radius))

        elif self.biome == Biome.DESERT:

            # Desert wrap

            pygame.draw.rect(self.image, clothes_color,

                             pygame.Rect(head_x - head_radius, head_y - head_radius,

                                         head_radius * 2, head_radius // 2))

        elif self.biome == Biome.VOLCANIC:

            # Blacksmith mask

            pygame.draw.rect(self.image, (80, 80, 80),

                             pygame.Rect(head_x - head_radius // 2, head_y - head_radius // 4,

                                         head_radius, head_radius // 2))

        # Draw eyes

        eye_y = head_y

        eye_spacing = TILE_SIZE // 10

        # Direction-based eyes

        if self.direction == "right":

            eye_offset = 1

        elif self.direction == "left":

            eye_offset = -1

        else:

            eye_offset = 0

        # Draw eyes

        pygame.draw.circle(self.image, (255, 255, 255),

                           (head_x - eye_spacing + eye_offset, eye_y), 2)

        pygame.draw.circle(self.image, (255, 255, 255),

                           (head_x + eye_spacing + eye_offset, eye_y), 2)

        # Draw pupils

        pygame.draw.circle(self.image, (0, 0, 0),

                           (head_x - eye_spacing + eye_offset * 2, eye_y), 1)

        pygame.draw.circle(self.image, (0, 0, 0),

                           (head_x + eye_spacing + eye_offset * 2, eye_y), 1)

        # Draw mouth

        mouth_y = head_y + head_radius // 2

        if self.talking:

            # Open talking mouth

            talk_frame = (int(self.animation_frame * 10) % 3)

            mouth_height = 2 + talk_frame

            pygame.draw.ellipse(self.image, (0, 0, 0),

                                pygame.Rect(head_x - 3, mouth_y - mouth_height // 2,

                                            6, mouth_height))

        else:

            # Closed mouth - smile

            pygame.draw.arc(self.image, (0, 0, 0),

                            pygame.Rect(head_x - 5, mouth_y - 3, 10, 6),

                            0, math.pi, 1)

        # Draw clothes

        pygame.draw.rect(self.image, clothes_color,

                         pygame.Rect(body_rect.x - 2, body_rect.y - 2,

                                     body_rect.width + 4, body_rect.height + 4),

                         2)

        # Draw arms

        arm_y = body_rect.centery

        pygame.draw.line(self.image, body_color,

                         (body_rect.x, arm_y),

                         (body_rect.x - TILE_SIZE // 8, arm_y), 2)

        pygame.draw.line(self.image, body_color,

                         (body_rect.right, arm_y),

                         (body_rect.right + TILE_SIZE // 8, arm_y), 2)

        # Draw shop icon (bag/pouch)

        bag_x = body_rect.centerx

        bag_y = body_rect.bottom - TILE_SIZE // 12

        bag_size = TILE_SIZE // 5

        pygame.draw.rect(self.image, (139, 69, 19),

                         pygame.Rect(bag_x - bag_size // 2, bag_y, bag_size, bag_size))

        # Draw tie string

        pygame.draw.line(self.image, (90, 40, 10),

                         (bag_x - bag_size // 2, bag_y + bag_size // 4),

                         (bag_x + bag_size // 2, bag_y + bag_size // 4), 1)

        # Draw interaction indicator if at right time in animation

        if math.sin(self.animation_frame * 2) > 0.7:
            # Floating exclamation mark

            pygame.draw.rect(self.image, (255, 255, 255),

                             pygame.Rect(head_x - 1, head_y - head_radius * 2, 2, 6))

            pygame.draw.circle(self.image, (255, 255, 255),

                               (head_x, head_y - head_radius * 2 + 8), 1)

    def update(self, dt, player=None):

        """Update NPC state"""

        # Update animation frame

        self.animation_frame += dt

        # Update interaction cooldown

        if self.interact_cooldown > 0:
            self.interact_cooldown -= dt

        # Check for player interaction

        if player and self.can_interact(player):

            # Face player if nearby

            dx = player.rect.centerx - self.rect.centerx

            dy = player.rect.centery - self.rect.centery

            if abs(dx) > abs(dy):

                self.direction = "right" if dx > 0 else "left"

            else:

                self.direction = "down" if dy > 0 else "up"

        # Stop talking after a while

        if self.talking and random.random() < 0.01:
            self.talking = False

        # Update appearance

        self.update_appearance()

    def can_interact(self, player):

        """Check if player is within interaction range"""

        distance = ((player.rect.centerx - self.rect.centerx) ** 2 +

                    (player.rect.centery - self.rect.centery) ** 2) ** 0.5

        return distance <= self.interaction_radius

    def interact(self):

        """Interact with NPC"""

        if self.interact_cooldown <= 0:
            self.talking = True

            self.interact_cooldown = 0.5

            return True

        return False

    def draw(self, surface, camera_pos):

        """Draw NPC on surface"""

        # Get screen position

        screen_x = self.rect.x - camera_pos[0]

        screen_y = self.rect.y - camera_pos[1]

        # Draw NPC

        surface.blit(self.image, (screen_x, screen_y))

        # Draw dialogue bubble if talking

        if self.talking:
            self.draw_dialogue(surface, (screen_x, screen_y))

    def draw_dialogue(self, surface, screen_pos):

        """Draw dialogue bubble with text"""

        # Setup text

        font = pygame.font.Font(None, 18)

        max_width = TILE_SIZE * 5

        # Split text into words

        words = self.dialogue.split()

        lines = []

        current_line = ""

        # Word wrap

        for word in words:

            test_line = current_line + word + " "

            text_width, _ = font.size(test_line)

            if text_width < max_width:

                current_line = test_line

            else:

                lines.append(current_line)

                current_line = word + " "

        # Add the last line

        if current_line:
            lines.append(current_line)

        # Calculate bubble size

        line_height = font.get_linesize()

        bubble_width = max_width

        bubble_height = line_height * len(lines) + 10

        # Calculate bubble position (above NPC)

        bubble_x = screen_pos[0] + TILE_SIZE // 2 - bubble_width // 2

        bubble_y = screen_pos[1] - bubble_height - 5

        # Draw bubble

        pygame.draw.rect(surface, (255, 255, 255),

                         pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height),

                         border_radius=5)

        pygame.draw.rect(surface, (0, 0, 0),

                         pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height),

                         1, border_radius=5)

        # Draw text

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (0, 0, 0))

            text_x = bubble_x + 5

            text_y = bubble_y + i * line_height + 5

            surface.blit(text_surface, (text_x, text_y))

        # Draw pointer

        pointer_points = [

            (screen_pos[0] + TILE_SIZE // 2, bubble_y + bubble_height),

            (screen_pos[0] + TILE_SIZE // 2 - 5, bubble_y + bubble_height - 5),

            (screen_pos[0] + TILE_SIZE // 2 + 5, bubble_y + bubble_height - 5)

        ]

        pygame.draw.polygon(surface, (255, 255, 255), pointer_points)

        pygame.draw.polygon(surface, (0, 0, 0), pointer_points, 1)


# Item class for drops and collectibles

class Item(pygame.sprite.Sprite):

    def __init__(self, x, y, equipment):

        super().__init__()

        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)

        self.rect = self.image.get_rect(center=(x, y))

        self.equipment = equipment

        # Animation state

        self.animation_frame = random.uniform(0, 100)  # Random start point

        self.animation_speed = 3

        # Pickup range

        self.pickup_radius = TILE_SIZE * 0.8

        # Update appearance

        self.update_appearance()

    def update_appearance(self):

        """Update sprite appearance based on item type"""

        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        if self.equipment.type == ItemType.WEAPON:

            self.draw_weapon()

        elif self.equipment.type == ItemType.ARMOR:

            self.draw_armor()

        elif self.equipment.type == ItemType.POTION:

            self.draw_potion()

        elif self.equipment.type == ItemType.MATERIAL:

            self.draw_material()

        else:

            self.draw_generic_item()

        # Add glow effect

        self.add_glow_effect()

    def draw_weapon(self):

        """Draw weapon icon"""

        weapon_color = (200, 200, 200)  # Silver

        hilt_color = (139, 69, 19)  # Brown

        # Get weapon type

        weapon_type = self.equipment.weapon_type

        if weapon_type == WeaponType.SWORD:

            # Draw sword blade

            pygame.draw.line(self.image, weapon_color,

                             (self.image.get_width() // 2, 2),

                             (self.image.get_width() // 2, self.image.get_height() * 2 // 3), 2)

            # Draw hilt

            pygame.draw.line(self.image, hilt_color,

                             (self.image.get_width() // 3, self.image.get_height() * 2 // 3),

                             (self.image.get_width() * 2 // 3, self.image.get_height() * 2 // 3), 2)



        elif weapon_type == WeaponType.GREATSWORD:

            # Draw blade (thicker)

            pygame.draw.line(self.image, weapon_color,

                             (self.image.get_width() // 2, 0),

                             (self.image.get_width() // 2, self.image.get_height() * 3 // 4), 3)

            # Draw hilt

            pygame.draw.line(self.image, hilt_color,

                             (self.image.get_width() // 4, self.image.get_height() * 3 // 4),

                             (self.image.get_width() * 3 // 4, self.image.get_height() * 3 // 4), 2)



        elif weapon_type == WeaponType.DAGGER:

            # Draw blade (shorter)

            pygame.draw.line(self.image, weapon_color,

                             (self.image.get_width() // 2, self.image.get_height() // 3),

                             (self.image.get_width() // 2, self.image.get_height() * 2 // 3), 2)

            # Draw hilt

            pygame.draw.line(self.image, hilt_color,

                             (self.image.get_width() * 2 // 5, self.image.get_height() * 2 // 3),

                             (self.image.get_width() * 3 // 5, self.image.get_height() * 2 // 3), 2)



        elif weapon_type == WeaponType.SPEAR:

            # Draw shaft

            pygame.draw.line(self.image, hilt_color,

                             (self.image.get_width() // 2, self.image.get_height() // 4),

                             (self.image.get_width() // 2, self.image.get_height()), 2)

            # Draw spearhead

            pygame.draw.polygon(self.image, weapon_color, [

                (self.image.get_width() // 2, 0),

                (self.image.get_width() // 3, self.image.get_height() // 4),

                (self.image.get_width() * 2 // 3, self.image.get_height() // 4)

            ])



        elif weapon_type == WeaponType.BOW:

            # Draw bow curve

            pygame.draw.arc(self.image, hilt_color,

                            pygame.Rect(2, 2, self.image.get_width() - 4, self.image.get_height() - 4),

                            -math.pi / 2, math.pi / 2, 2)

            # Draw bowstring

            pygame.draw.line(self.image, (255, 255, 255),

                             (self.image.get_width() - 2, 2),

                             (self.image.get_width() - 2, self.image.get_height() - 2), 1)



        elif weapon_type == WeaponType.STAFF:

            # Draw staff

            pygame.draw.line(self.image, hilt_color,

                             (self.image.get_width() // 2, 2),

                             (self.image.get_width() // 2, self.image.get_height()), 2)

            # Draw gem

            pygame.draw.circle(self.image, (50, 100, 200),

                               (self.image.get_width() // 2, 4), 3)

    def draw_armor(self):

        """Draw armor icon"""

        armor_color = (150, 150, 150)  # Gray

        secondary_color = (100, 100, 100)  # Darker gray

        # Get armor type

        armor_type = self.equipment.armor_type

        if armor_type == ArmorType.LIGHT:

            # Draw leather armor (brown)

            armor_color = (139, 69, 19)  # Brown

            # Draw armor shape - lighter

            pygame.draw.rect(self.image, armor_color,

                             pygame.Rect(2, 2, self.image.get_width() - 4, self.image.get_height() - 4),

                             border_radius=2)

            # Draw straps

            pygame.draw.line(self.image, secondary_color,

                             (4, self.image.get_height() // 3),

                             (self.image.get_width() - 4, self.image.get_height() // 3), 1)

            pygame.draw.line(self.image, secondary_color,

                             (4, self.image.get_height() * 2 // 3),

                             (self.image.get_width() - 4, self.image.get_height() * 2 // 3), 1)



        elif armor_type == ArmorType.MEDIUM:

            # Draw chainmail (silver gray)

            armor_color = (180, 180, 180)  # Light gray

            # Draw armor shape

            pygame.draw.rect(self.image, armor_color,

                             pygame.Rect(2, 2, self.image.get_width() - 4, self.image.get_height() - 4))

            # Draw chainmail pattern

            for y in range(4, self.image.get_height() - 2, 2):

                for x in range(4, self.image.get_width() - 2, 2):
                    pygame.draw.circle(self.image, secondary_color, (x, y), 0.5)



        elif armor_type == ArmorType.HEAVY:

            # Draw plate armor (steel)

            armor_color = (150, 150, 170)  # Bluish gray

            # Draw armor shape

            pygame.draw.rect(self.image, armor_color,

                             pygame.Rect(2, 2, self.image.get_width() - 4, self.image.get_height() - 4))

            # Draw plate details

            pygame.draw.line(self.image, secondary_color,

                             (self.image.get_width() // 2, 2),

                             (self.image.get_width() // 2, self.image.get_height() - 2), 1)

            pygame.draw.rect(self.image, secondary_color,

                             pygame.Rect(4, 4, self.image.get_width() - 8, 3), 1)



        elif armor_type == ArmorType.ROBE:

            # Draw wizard robe (blue/purple)

            armor_color = (80, 60, 140)  # Purple

            # Draw robe shape

            pygame.draw.rect(self.image, armor_color,

                             pygame.Rect(2, 0, self.image.get_width() - 4, self.image.get_height()))

            # Draw hood

            pygame.draw.arc(self.image, armor_color,

                            pygame.Rect(0, -self.image.get_height() // 2,

                                        self.image.get_width(), self.image.get_height()),

                            0, math.pi, 2)

            # Draw belt

            pygame.draw.line(self.image, (139, 69, 19),

                             (2, self.image.get_height() * 2 // 3),

                             (self.image.get_width() - 2, self.image.get_height() * 2 // 3), 1)

    def draw_potion(self):

        """Draw potion icon"""

        # Determine potion color based on effects

        potion_color = (255, 0, 0)  # Default red (health)

        if "mp" in self.equipment.stats:

            potion_color = (0, 0, 255)  # Blue for mana

        elif "strength" in self.equipment.stats:

            potion_color = (255, 100, 0)  # Orange for strength

        elif "speed" in self.equipment.stats:

            potion_color = (0, 255, 0)  # Green for speed

        elif "defense" in self.equipment.stats:

            potion_color = (255, 255, 0)  # Yellow for defense

        # Draw bottle shape

        bottle_width = self.image.get_width() * 2 // 3

        bottle_height = self.image.get_height() * 3 // 4

        bottle_x = (self.image.get_width() - bottle_width) // 2

        bottle_y = (self.image.get_height() - bottle_height)

        # Neck

        pygame.draw.rect(self.image, (200, 200, 230),

                         pygame.Rect(bottle_x + bottle_width // 3, bottle_y - 3,

                                     bottle_width // 3, 3))

        # Cork

        pygame.draw.rect(self.image, (139, 69, 19),

                         pygame.Rect(bottle_x + bottle_width // 3, bottle_y - 5,

                                     bottle_width // 3, 2))

        # Bottle

        pygame.draw.rect(self.image, (200, 200, 230, 180),

                         pygame.Rect(bottle_x, bottle_y,

                                     bottle_width, bottle_height),

                         border_radius=2)

        # Liquid

        liquid_height = bottle_height * 3 // 4

        pygame.draw.rect(self.image, potion_color,

                         pygame.Rect(bottle_x + 1, bottle_y + bottle_height - liquid_height,

                                     bottle_width - 2, liquid_height),

                         border_radius=2)

        # Highlight/shine

        pygame.draw.line(self.image, (255, 255, 255, 150),

                         (bottle_x + 2, bottle_y + 2),

                         (bottle_x + bottle_width - 2, bottle_y + 2), 1)

    def draw_material(self):

        """Draw material item icon"""

        # Default to generic material

        pygame.draw.rect(self.image, (200, 150, 100),

                         pygame.Rect(2, 2, self.image.get_width() - 4, self.image.get_height() - 4))

    def draw_generic_item(self):

        """Draw generic item icon"""

        # Draw simple square

        pygame.draw.rect(self.image, COLORS["item"],

                         pygame.Rect(2, 2, self.image.get_width() - 4, self.image.get_height() - 4))

    def add_glow_effect(self):

        """Add pulsing glow effect to item"""

        # Create a glow/outline based on value/rarity

        glow_color = (255, 255, 100)  # Default yellow

        glow_radius = 1

        # Determine rarity based on value

        if hasattr(self.equipment, 'value'):

            if self.equipment.value > 100:  # Epic

                glow_color = (255, 50, 255)  # Purple

                glow_radius = 2

            elif self.equipment.value > 50:  # Rare

                glow_color = (30, 100, 255)  # Blue

                glow_radius = 2

            elif self.equipment.value > 25:  # Uncommon

                glow_color = (30, 255, 30)  # Green

                glow_radius = 1

        # Draw subtle glow

        pygame.draw.rect(self.image, glow_color,

                         pygame.Rect(0, 0, self.image.get_width(), self.image.get_height()),

                         glow_radius, border_radius=2)

    def update(self, dt):

        """Update item state"""

        # Update animation frame

        self.animation_frame += dt * self.animation_speed

        # Floating/bobbing animation

        bob_offset = math.sin(self.animation_frame) * 2

        self.rect.y += bob_offset * dt

        # Occasionally update appearance for pulsing effect

        if random.random() < 0.05:
            self.update_appearance()

    def draw(self, surface, camera_pos):

        """Draw item on surface"""

        # Get screen position

        screen_x = self.rect.x - camera_pos[0]

        screen_y = self.rect.y - camera_pos[1]

        # Draw item

        surface.blit(self.image, (screen_x, screen_y))


# UI Button class

class UIButton:

    def __init__(self, rect, text, callback=None, bg_color=COLORS["ui_button"],

                 hover_color=COLORS["ui_button_hover"], text_color=COLORS["ui_text"],

                 border_radius=5, border_width=1):

        self.rect = pygame.Rect(rect)

        self.text = text

        self.callback = callback

        self.bg_color = bg_color

        self.hover_color = hover_color

        self.text_color = text_color

        self.border_radius = border_radius

        self.border_width = border_width

        self.hovered = False

        self.clicked = False

        self.visible = True

        self.enabled = True

        # Create font

        self.font = pygame.font.Font(None, 24)

    def draw(self, surface):

        """Draw button on surface"""

        if not self.visible:
            return

        # Determine button color

        color = self.hover_color if self.hovered else self.bg_color

        if not self.enabled:
            # Darken the color if disabled

            color = tuple(max(0, c - 50) for c in color)

        # Draw button background

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        # Draw border

        pygame.draw.rect(surface, COLORS["ui_border"], self.rect,

                         self.border_width, border_radius=self.border_radius)

        # Draw text

        text_surface = self.font.render(self.text, True, self.text_color)

        text_rect = text_surface.get_rect(center=self.rect.center)

        surface.blit(text_surface, text_rect)

    def handle_event(self, event):

        """Handle mouse events"""

        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEMOTION:

            # Check hover state

            self.hovered = self.rect.collidepoint(event.pos)



        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Check for click

            if self.hovered:
                self.clicked = True

                return True



        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

            # Check for click release

            if self.clicked and self.hovered and self.callback:
                self.callback()

                self.clicked = False

                return True

        return False


# UI Panel class

class UIPanel:

    def __init__(self, rect, bg_color=COLORS["ui_panel"], border_color=COLORS["ui_border"],

                 border_width=1, border_radius=5):

        self.rect = pygame.Rect(rect)

        self.bg_color = bg_color

        self.border_color = border_color

        self.border_width = border_width

        self.border_radius = border_radius

        self.visible = True

        self.children = []  # UI elements contained in this panel

    def add_child(self, child):

        """Add a UI element to this panel"""

        self.children.append(child)

    def draw(self, surface):

        """Draw panel and all children"""

        if not self.visible:
            return

        # Draw panel background

        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)

        # Draw border

        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect,

                             self.border_width, border_radius=self.border_radius)

        # Draw all children

        for child in self.children:
            child.draw(surface)

    def handle_event(self, event):

        """Pass events to children"""

        if not self.visible:
            return False

        # Check if mouse is over this panel

        if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:

            if not self.rect.collidepoint(event.pos):
                return False

        # Pass event to children (in reverse order for proper overlap handling)

        for child in reversed(self.children):

            if child.handle_event(event):
                return True

        return False


# UI Text class

class UIText:

    def __init__(self, rect, text, font_size=20, color=COLORS["ui_text"],

                 align="left", bg_color=None):

        self.rect = pygame.Rect(rect)

        self.text = text

        self.lines = []  # Wrapped text lines

        self.font_size = font_size

        self.color = color

        self.align = align  # left, center, right

        self.bg_color = bg_color

        self.visible = True

        # Create font and wrap text

        self.font = pygame.font.Font(None, font_size)

        self.wrap_text()

    def wrap_text(self):

        """Wrap text to fit within rect width"""

        self.lines = []

        # Split text into paragraphs

        paragraphs = self.text.split('\n')

        for paragraph in paragraphs:

            words = paragraph.split(' ')

            current_line = ""

            for word in words:

                # Try adding this word

                test_line = current_line + word + " "

                width, _ = self.font.size(test_line)

                if width < self.rect.width:

                    current_line = test_line

                else:

                    self.lines.append(current_line)

                    current_line = word + " "

            # Add the last line

            if current_line:
                self.lines.append(current_line)

            # Add empty line between paragraphs

            if len(paragraphs) > 1:
                self.lines.append("")

    def set_text(self, text):

        """Set new text and rewrap"""

        if self.text != text:
            self.text = text

            self.wrap_text()

    def draw(self, surface):

        """Draw text on surface"""

        if not self.visible:
            return

        # Draw background if specified

        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect)

        # Draw each line

        y = self.rect.y

        line_height = self.font.get_linesize()

        for line in self.lines:

            if not line:  # Skip empty lines

                y += line_height

                continue

            text_surface = self.font.render(line, True, self.color)

            # Determine x position based on alignment

            if self.align == "left":

                x = self.rect.x

            elif self.align == "center":

                x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2

            else:  # right

                x = self.rect.x + self.rect.width - text_surface.get_width()

            # Draw text

            surface.blit(text_surface, (x, y))

            y += line_height

            # Stop if we go past the bottom of the rect

            if y > self.rect.bottom:
                break

    def handle_event(self, event):

        """Handle events (passive element)"""

        return False


# UI Progress Bar

class UIProgressBar:

    def __init__(self, rect, value=100, max_value=100, color=COLORS["ui_health"],

                 bg_color=(30, 30, 30), border_color=COLORS["ui_border"],

                 border_width=1, show_text=False, text_color=COLORS["ui_text"]):

        self.rect = pygame.Rect(rect)

        self.value = value

        self.max_value = max_value

        self.color = color

        self.bg_color = bg_color

        self.border_color = border_color

        self.border_width = border_width

        self.show_text = show_text

        self.text_color = text_color

        self.visible = True

        # Create font for text

        self.font = pygame.font.Font(None, 18)

    def set_value(self, value):

        """Set current value"""

        self.value = max(0, min(value, self.max_value))

    def set_max_value(self, max_value):

        """Set maximum value"""

        self.max_value = max_value

        self.value = min(self.value, self.max_value)

    def draw(self, surface):

        """Draw progress bar on surface"""

        if not self.visible:
            return

        # Draw background

        pygame.draw.rect(surface, self.bg_color, self.rect)

        # Calculate filled portion

        fill_width = int(self.rect.width * (self.value / self.max_value))

        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)

        # Draw filled portion

        pygame.draw.rect(surface, self.color, fill_rect)

        # Draw border

        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)

        # Draw text if enabled

        if self.show_text:
            text = f"{self.value}/{self.max_value}"

            text_surface = self.font.render(text, True, self.text_color)

            text_rect = text_surface.get_rect(center=self.rect.center)

            surface.blit(text_surface, text_rect)

    def handle_event(self, event):

        """Handle events (passive element)"""

        return False


# UI Image class

class UIImage:

    def __init__(self, rect, image, bg_color=None, border_color=None, border_width=0, scale=True):

        self.rect = pygame.Rect(rect)

        self.original_image = image

        self.bg_color = bg_color

        self.border_color = border_color

        self.border_width = border_width

        self.scale = scale

        self.visible = True

        # Scale image if needed

        if self.scale and self.original_image:

            self.image = pygame.transform.scale(self.original_image,

                                                (self.rect.width, self.rect.height))

        else:

            self.image = self.original_image

    def set_image(self, image):

        """Set new image"""

        self.original_image = image

        if self.scale and self.original_image:

            self.image = pygame.transform.scale(self.original_image,

                                                (self.rect.width, self.rect.height))

        else:

            self.image = self.original_image

    def draw(self, surface):

        """Draw image on surface"""

        if not self.visible or not self.image:
            return

        # Draw background if specified

        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect)

        # Draw image

        surface.blit(self.image, self.rect)

        # Draw border if specified

        if self.border_color and self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)

    def handle_event(self, event):

        """Handle events (passive element)"""

        return False


# UI Inventory Slot class

class UIInventorySlot:

    def __init__(self, rect, item=None, callback=None, bg_color=(50, 50, 70),

                 highlight_color=COLORS["ui_highlight"], text_color=COLORS["ui_text"]):

        self.rect = pygame.Rect(rect)

        self.item = item

        self.callback = callback

        self.bg_color = bg_color

        self.highlight_color = highlight_color

        self.text_color = text_color

        self.visible = True

        self.selected = False

        self.hovered = False

        # Create font for item count

        self.font = pygame.font.Font(None, 16)

    def set_item(self, item):

        """Set slot item"""

        self.item = item

    def draw(self, surface):

        """Draw inventory slot on surface"""

        if not self.visible:
            return

        # Draw background - change color if selected or hovered

        if self.selected:

            color = self.highlight_color

        elif self.hovered:

            color = tuple(min(255, c + 20) for c in self.bg_color)

        else:

            color = self.bg_color

        pygame.draw.rect(surface, color, self.rect, border_radius=3)

        pygame.draw.rect(surface, COLORS["ui_border"], self.rect, 1, border_radius=3)

        # Draw item if present

        if self.item:
            self.draw_item(surface)

    def draw_item(self, surface):

        """Draw item in slot"""

        if not self.item:
            return

        # Determine item color based on type

        if self.item.type == ItemType.WEAPON:

            color = (200, 100, 100)  # Red for weapons

        elif self.item.type == ItemType.ARMOR:

            color = (100, 100, 200)  # Blue for armor

        elif self.item.type == ItemType.POTION:

            if "hp" in self.item.stats:

                color = (255, 0, 0)  # Red for health

            elif "mp" in self.item.stats:

                color = (0, 0, 255)  # Blue for mana

            else:

                color = (255, 255, 0)  # Yellow for other potions

        else:

            color = (200, 200, 200)  # Gray for other items

        # Draw item icon

        icon_size = min(self.rect.width, self.rect.height) - 6

        icon_rect = pygame.Rect(

            self.rect.x + (self.rect.width - icon_size) // 2,

            self.rect.y + (self.rect.height - icon_size) // 2,

            icon_size, icon_size

        )

        pygame.draw.rect(surface, color, icon_rect, border_radius=2)

        # Draw item count if stackable

        if hasattr(self.item, 'count') and self.item.count > 1:
            count_text = self.font.render(str(self.item.count), True, self.text_color)

            text_rect = count_text.get_rect(bottomright=(self.rect.right - 2, self.rect.bottom - 2))

            # Draw background for text

            pygame.draw.rect(surface, (0, 0, 0, 150), text_rect.inflate(2, 2))

            # Draw text

            surface.blit(count_text, text_rect)

    def handle_event(self, event):

        """Handle mouse events for inventory slot"""

        if not self.visible:
            return False

        if event.type == pygame.MOUSEMOTION:

            # Check hover state

            self.hovered = self.rect.collidepoint(event.pos)



        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # Check for click

            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback(self)

                return True

        return False


# UI Manager class

class UIManager:

    def __init__(self, screen):

        self.screen = screen

        self.ui_elements = []

        self.tooltips = []

        self.active_tooltip = None

        self.active_panel = None

        self.modal_panel = None

    def add_element(self, element):

        """Add UI element to manager"""

        self.ui_elements.append(element)

        return element

    def remove_element(self, element):

        """Remove UI element from manager"""

        if element in self.ui_elements:
            self.ui_elements.remove(element)

    def clear(self):

        """Clear all UI elements"""

        self.ui_elements.clear()

    def draw(self):

        """Draw all UI elements"""

        # Draw normal UI elements first

        for element in self.ui_elements:

            if element != self.modal_panel:  # Skip modal panel for now

                element.draw(self.screen)

        # Draw active tooltip

        if self.active_tooltip:
            self.active_tooltip.draw(self.screen)

        # Draw modal panel on top if present

        if self.modal_panel:
            # Darken screen behind modal

            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

            overlay.fill((0, 0, 0, 150))  # Semi-transparent black

            self.screen.blit(overlay, (0, 0))

            # Draw modal panel

            self.modal_panel.draw(self.screen)

    def handle_event(self, event):

        """Handle events for all UI elements"""

        # Handle modal panel first if present

        if self.modal_panel:
            return self.modal_panel.handle_event(event)

        # Handle normal UI elements

        for element in reversed(self.ui_elements):

            if element.handle_event(event):
                return True

        return False

    def show_tooltip(self, text, position):

        """Show tooltip at position"""

        tooltip_width = 200

        tooltip_height = 100

        # Create tooltip panel

        tooltip = UIPanel(

            pygame.Rect(position[0], position[1], tooltip_width, tooltip_height),

            bg_color=(40, 40, 60, 220),

            border_color=COLORS["ui_border"],

            border_radius=5

        )

        # Add text to tooltip

        tooltip.add_child(UIText(

            pygame.Rect(5, 5, tooltip_width - 10, tooltip_height - 10),

            text,

            font_size=16,

            color=COLORS["ui_text"]

        ))

        # Position tooltip to be fully visible

        if tooltip.rect.right > self.screen.get_width():
            tooltip.rect.right = self.screen.get_width() - 5

        if tooltip.rect.bottom > self.screen.get_height():
            tooltip.rect.bottom = self.screen.get_height() - 5

        self.active_tooltip = tooltip

    def hide_tooltip(self):

        """Hide active tooltip"""

        self.active_tooltip = None

    def show_modal(self, panel):

        """Show modal panel"""

        self.modal_panel = panel

    def hide_modal(self):

        """Hide modal panel"""

        self.modal_panel = None


# Game class to manage game state

class Game:

    def __init__(self):

        # Initialize pygame

        pygame.init()

        # Create screen

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption("Mystical Realms RPG")

        # Create game map

        self.map = GameMap()

        # 创建玩家（位于中心）
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self)
        self.player.game = self  # 确保玩家有对游戏的引用

        # 初始化玩家统计数据
        self.player_stats = {
            "monsters_killed": 0,
            "total_gold": 0,
            "items_found": 0,
            "deaths": 0,
            "levels_gained": 0,
            "potions_used": 0,
            "damage_dealt": 0,
            "damage_taken": 0,
            "play_time": 0
        }

        # Create camera

        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Create sprite groups

        self.all_sprites = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()

        self.npcs = pygame.sprite.Group()

        self.items = pygame.sprite.Group()

        # Add player to sprites

        self.all_sprites.add(self.player)

        # Generate initial map area

        self.generated_chunks = set()

        self.check_and_generate_chunks()

        # Game state

        self.running = True

        self.paused = False

        self.shop_active = False

        self.current_shop = None

        self.game_over = False

        # UI manager

        self.ui_manager = UIManager(self.screen)

        self.setup_ui()

        # Clock for timing

        self.clock = pygame.time.Clock()

        self.dt = 0  # Delta time

        # Spawn some initial enemies

        self.spawn_enemies(10)

        # Spawn some NPCs

        self.spawn_npcs(3)

    def setup_ui(self):

        """Setup game UI"""

        # Clear any existing UI

        self.ui_manager.clear()

        # Status panel (top-left)

        status_panel = UIPanel(

            pygame.Rect(10, 10, 200, 120),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Player name

        status_panel.add_child(UIText(

            pygame.Rect(10, 5, 180, 20),

            f"{self.player.name} (Level {self.player.stats['level']})",

            font_size=18,

            color=COLORS["ui_title"]

        ))

        # HP bar

        self.hp_bar = UIProgressBar(

            pygame.Rect(10, 30, 180, 20),

            value=self.player.stats["hp"],

            max_value=self.player.stats["max_hp"],

            color=COLORS["ui_health"],

            show_text=True

        )

        status_panel.add_child(self.hp_bar)

        # MP bar

        self.mp_bar = UIProgressBar(

            pygame.Rect(10, 55, 180, 20),

            value=self.player.stats["mp"],

            max_value=self.player.stats["max_mp"],

            color=COLORS["ui_mana"],

            show_text=True

        )

        status_panel.add_child(self.mp_bar)

        # EXP bar

        self.exp_bar = UIProgressBar(

            pygame.Rect(10, 80, 180, 20),

            value=self.player.stats["exp"],

            max_value=self.player.stats["next_level_exp"],

            color=COLORS["ui_exp"],

            show_text=True

        )

        status_panel.add_child(self.exp_bar)

        # Add status panel to UI

        self.ui_manager.add_element(status_panel)

        # Mini-map panel (top-right)

        minimap_panel = UIPanel(

            pygame.Rect(SCREEN_WIDTH - 210, 10, 200, 200),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Add minimap panel to UI

        self.ui_manager.add_element(minimap_panel)

        # Stats button (opens stats panel)

        stats_button = UIButton(

            pygame.Rect(10, SCREEN_HEIGHT - 50, 100, 40),

            "Stats",

            callback=self.toggle_stats_panel

        )

        self.ui_manager.add_element(stats_button)

        # Inventory button (opens inventory panel)

        inventory_button = UIButton(

            pygame.Rect(120, SCREEN_HEIGHT - 50, 100, 40),

            "Inventory",

            callback=self.toggle_inventory_panel

        )

        self.ui_manager.add_element(inventory_button)

        # Skills button (opens skills panel)

        skills_button = UIButton(

            pygame.Rect(230, SCREEN_HEIGHT - 50, 100, 40),

            "Skills",

            callback=self.toggle_skills_panel

        )

        self.ui_manager.add_element(skills_button)

        # Create (initially hidden) stats panel

        self.stats_panel = self.create_stats_panel()

        self.stats_panel.visible = False

        self.ui_manager.add_element(self.stats_panel)

        # Create (initially hidden) inventory panel

        self.inventory_panel = self.create_inventory_panel()

        self.inventory_panel.visible = False

        self.ui_manager.add_element(self.inventory_panel)

        # Create (initially hidden) skills panel

        self.skills_panel = self.create_skills_panel()

        self.skills_panel.visible = False

        self.ui_manager.add_element(self.skills_panel)

    def create_stats_panel(self):

        """Create the stats panel"""

        panel = UIPanel(

            pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 200, 300, 400),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Add title

        panel.add_child(UIText(

            pygame.Rect(10, 10, 280, 30),

            "Character Stats",

            font_size=24,

            color=COLORS["ui_title"],

            align="center"

        ))

        # Add stats text

        stats_text = f"""

Level: {self.player.stats['level']}

HP: {self.player.stats['hp']}/{self.player.stats['max_hp']}

MP: {self.player.stats['mp']}/{self.player.stats['max_mp']}

EXP: {self.player.stats['exp']}/{self.player.stats['next_level_exp']}



Attack: {self.player.stats['attack']}

Defense: {self.player.stats['defense']}

Critical: {self.player.stats['crit']}%

Agility: {self.player.stats['agility']}

Attack Range: {self.player.stats['attack_range']}

Attack Speed: {self.player.stats['attack_speed']}



Currency: {self.player.gold} gold, {self.player.silver} silver, {self.player.copper} copper

        """

        self.stats_text = UIText(

            pygame.Rect(20, 50, 260, 280),

            stats_text,

            font_size=18,

            color=COLORS["ui_text"]

        )

        panel.add_child(self.stats_text)

        # Add close button

        panel.add_child(UIButton(

            pygame.Rect(100, 350, 100, 30),

            "Close",

            callback=lambda: self.toggle_stats_panel()

        ))

        return panel

    def create_inventory_panel(self):

        """Create the inventory panel"""

        panel = UIPanel(

            pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200, 400, 400),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Add title

        panel.add_child(UIText(

            pygame.Rect(10, 10, 380, 30),

            "Inventory",

            font_size=24,

            color=COLORS["ui_title"],

            align="center"

        ))

        # Create inventory slots

        self.inventory_slots = []

        slot_size = 40

        slots_per_row = 8

        margin = 10

        start_x = (panel.rect.width - (slot_size * slots_per_row + margin * (slots_per_row - 1))) // 2

        start_y = 50

        for i in range(self.player.max_inventory):

            row = i // slots_per_row

            col = i % slots_per_row

            x = start_x + col * (slot_size + margin)

            y = start_y + row * (slot_size + margin)

            # Determine if slot has an item

            item = None

            if i < len(self.player.inventory):
                item = self.player.inventory[i]

            # Create slot

            slot = UIInventorySlot(

                pygame.Rect(x, y, slot_size, slot_size),

                item=item,

                callback=self.on_inventory_slot_click

            )

            panel.add_child(slot)

            self.inventory_slots.append(slot)

        # Add equipment section

        panel.add_child(UIText(

            pygame.Rect(10, 260, 380, 30),

            "Equipment",

            font_size=20,

            color=COLORS["ui_title"],

            align="center"

        ))

        # Weapon slot

        weapon_slot = UIInventorySlot(

            pygame.Rect(start_x, 300, slot_size, slot_size),

            item=self.player.equipped["weapon"],

            callback=self.on_equipment_slot_click

        )

        panel.add_child(weapon_slot)

        panel.add_child(UIText(

            pygame.Rect(start_x, 300 + slot_size + 5, slot_size, 20),

            "Weapon",

            font_size=16,

            color=COLORS["ui_text"],

            align="center"

        ))

        self.weapon_slot = weapon_slot

        # Armor slot

        armor_slot = UIInventorySlot(

            pygame.Rect(start_x + slot_size + margin, 300, slot_size, slot_size),

            item=self.player.equipped["armor"],

            callback=self.on_equipment_slot_click

        )

        panel.add_child(armor_slot)

        panel.add_child(UIText(

            pygame.Rect(start_x + slot_size + margin, 300 + slot_size + 5, slot_size, 20),

            "Armor",

            font_size=16,

            color=COLORS["ui_text"],

            align="center"

        ))

        self.armor_slot = armor_slot

        # Add close button

        panel.add_child(UIButton(

            pygame.Rect(150, 350, 100, 30),

            "Close",

            callback=lambda: self.toggle_inventory_panel()

        ))

        return panel

    def create_skills_panel(self):

        """Create the skills panel"""

        panel = UIPanel(

            pygame.Rect(SCREEN_WIDTH // 2 - 175, SCREEN_HEIGHT // 2 - 200, 350, 400),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Add title

        panel.add_child(UIText(

            pygame.Rect(10, 10, 330, 30),

            "Skills",

            font_size=24,

            color=COLORS["ui_title"],

            align="center"

        ))

        # Add skills list

        skill_buttons = []

        y = 50

        for i, skill in enumerate(self.player.skills):
            # Create skill button

            skill_button = UIButton(

                pygame.Rect(20, y, 310, 40),

                f"{skill.name} (MP: {skill.mp_cost})",

                callback=lambda s=skill: self.assign_skill(s)

            )

            panel.add_child(skill_button)

            skill_buttons.append(skill_button)

            y += 50

        # Add skill description text

        self.skill_description = UIText(

            pygame.Rect(20, 250, 310, 100),

            "Select a skill to see its description",

            font_size=16,

            color=COLORS["ui_text"]

        )

        panel.add_child(self.skill_description)

        # Add close button

        panel.add_child(UIButton(

            pygame.Rect(125, 350, 100, 30),

            "Close",

            callback=lambda: self.toggle_skills_panel()

        ))

        return panel

    def create_shop_panel(self, npc):

        """Create shop panel for NPC"""

        panel = UIPanel(

            pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Add title

        panel.add_child(UIText(

            pygame.Rect(10, 10, 480, 30),

            "Shop",

            font_size=24,

            color=COLORS["ui_title"],

            align="center"

        ))

        # Add merchant dialogue

        panel.add_child(UIText(

            pygame.Rect(20, 40, 460, 40),

            npc.dialogue,

            font_size=16,

            color=COLORS["ui_text"]

        ))

        # Add player currency info

        panel.add_child(UIText(

            pygame.Rect(20, 80, 460, 20),

            f"Your Money: {self.player.gold} gold, {self.player.silver} silver, {self.player.copper} copper",

            font_size=16,

            color=COLORS["ui_highlight"]

        ))

        # Create shop item list

        self.shop_buttons = []

        y = 110

        for i, item in enumerate(npc.items):

            # Determine if player can afford

            total_copper = self.player.get_total_copper()

            can_afford = total_copper >= item.value * 100

            # Color based on affordability

            color = COLORS["ui_button"] if can_afford else (60, 60, 60)

            # Create item button

            item_button = UIButton(

                pygame.Rect(20, y, 460, 30),

                f"{item.name} - {item.value} gold",

                callback=lambda item=item: self.buy_item(item) if can_afford else None,

                bg_color=color

            )

            panel.add_child(item_button)

            self.shop_buttons.append(item_button)

            y += 35

            # Limit to 7 items per page

            if i >= 6:
                break

        # Add item description text

        self.shop_description = UIText(

            pygame.Rect(20, 250, 460, 100),

            "Select an item to see its description",

            font_size=16,

            color=COLORS["ui_text"]

        )

        panel.add_child(self.shop_description)

        # Add close button

        panel.add_child(UIButton(

            pygame.Rect(200, 350, 100, 30),

            "Close",

            callback=self.close_shop

        ))

        return panel

    def create_game_over_panel(self):
        """增强的游戏结束面板"""
        panel = UIPanel(
            pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200, 400, 400),
            bg_color=COLORS["ui_panel"],
            border_color=COLORS["ui_border"]
        )

        # 添加标题
        panel.add_child(UIText(
            pygame.Rect(10, 20, 380, 40),
            "游戏结束",
            font_size=36,
            color=(255, 0, 0),
            align="center"
        ))

        # 添加死亡信息
        death_text = f"你被击败了，等级：{self.player.stats['level']}\n\n"
        death_text += f"击败的怪物数量：{self.player_stats.get('monsters_killed', 0)}\n"
        death_text += f"收集的金币：{self.player_stats.get('total_gold', 0)}\n"
        death_text += f"发现的物品：{self.player_stats.get('items_found', 0)}\n\n"
        death_text += "你想要做什么？"

        panel.add_child(UIText(
            pygame.Rect(20, 70, 360, 180),
            death_text,
            font_size=18,
            color=COLORS["ui_text"],
            align="center"
        ))

        # 添加重新开始按钮
        panel.add_child(UIButton(
            pygame.Rect(50, 280, 300, 40),
            "重新开始游戏",
            callback=self.restart_game
        ))

        # 添加退出按钮
        panel.add_child(UIButton(
            pygame.Rect(50, 330, 300, 40),
            "退出至桌面",
            callback=self.quit_game
        ))

        return panel

    def quit_game(self):
        """退出游戏"""
        self.running = False

    def toggle_stats_panel(self):

        """Toggle stats panel visibility"""

        self.stats_panel.visible = not self.stats_panel.visible

        # Update stats text if showing panel

        if self.stats_panel.visible:
            stats_text = f"""

Level: {self.player.stats['level']}

HP: {self.player.stats['hp']}/{self.player.stats['max_hp']}

MP: {self.player.stats['mp']}/{self.player.stats['max_mp']}

EXP: {self.player.stats['exp']}/{self.player.stats['next_level_exp']}



Attack: {self.player.stats['attack']}

Defense: {self.player.stats['defense']}

Critical: {self.player.stats['crit']}%

Agility: {self.player.stats['agility']}

Attack Range: {self.player.stats['attack_range']}

Attack Speed: {self.player.stats['attack_speed']}



Currency: {self.player.gold} gold, {self.player.silver} silver, {self.player.copper} copper

            """

            self.stats_text.set_text(stats_text)

    def toggle_inventory_panel(self):

        """Toggle inventory panel visibility"""

        self.inventory_panel.visible = not self.inventory_panel.visible

        # Update inventory slots if showing panel

        if self.inventory_panel.visible:
            self.update_inventory_ui()

    def toggle_skills_panel(self):

        """Toggle skills panel visibility"""

        self.skills_panel.visible = not self.skills_panel.visible

    def update_inventory_ui(self):

        """Update inventory UI with current items"""

        # Update inventory slots

        for i, slot in enumerate(self.inventory_slots):

            if i < len(self.player.inventory):

                slot.set_item(self.player.inventory[i])

            else:

                slot.set_item(None)

        # Update equipment slots

        self.weapon_slot.set_item(self.player.equipped["weapon"])

        self.armor_slot.set_item(self.player.equipped["armor"])

    def on_inventory_slot_click(self, slot):

        """Handle inventory slot click"""

        if not slot.item:
            return

        # Create item action menu

        item_panel = UIPanel(

            pygame.Rect(slot.rect.x + slot.rect.width, slot.rect.y, 150, 120),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Add item name

        item_panel.add_child(UIText(

            pygame.Rect(10, 10, 130, 20),

            slot.item.name,

            font_size=16,

            color=COLORS["ui_title"]

        ))

        # Actions depend on item type

        y = 40

        if slot.item.type == ItemType.WEAPON or slot.item.type == ItemType.ARMOR:

            # Add equip button

            item_panel.add_child(UIButton(

                pygame.Rect(10, y, 130, 25),

                "Equip",

                callback=lambda: self.equip_item(slot.item)

            ))

            y += 30



        elif slot.item.type == ItemType.POTION:

            # Add use button

            item_panel.add_child(UIButton(

                pygame.Rect(10, y, 130, 25),

                "Use",

                callback=lambda: self.use_item(slot.item)

            ))

            y += 30

        # Add drop button

        item_panel.add_child(UIButton(

            pygame.Rect(10, y, 130, 25),

            "Drop",

            callback=lambda: self.drop_item(slot.item)

        ))

        # Show the panel

        self.ui_manager.show_modal(item_panel)

    def on_equipment_slot_click(self, slot):

        """Handle equipment slot click"""

        if not slot.item:
            return

        # Create action menu

        equip_panel = UIPanel(

            pygame.Rect(slot.rect.x + slot.rect.width, slot.rect.y, 150, 80),

            bg_color=COLORS["ui_panel"],

            border_color=COLORS["ui_border"]

        )

        # Add item name

        equip_panel.add_child(UIText(

            pygame.Rect(10, 10, 130, 20),

            slot.item.name,

            font_size=16,

            color=COLORS["ui_title"]

        ))

        # Add unequip button

        equip_panel.add_child(UIButton(

            pygame.Rect(10, 40, 130, 25),

            "Unequip",

            callback=lambda: self.unequip_item(slot.item)

        ))

        # Show the panel

        self.ui_manager.show_modal(equip_panel)

    def equip_item(self, item):

        """Equip item and update UI"""

        # Remove from inventory

        if item in self.player.inventory:
            self.player.inventory.remove(item)

        # Equip the item

        self.player.equip(item)

        # Update UI

        self.update_inventory_ui()

        # Hide modal panel

        self.ui_manager.hide_modal()

    def unequip_item(self, item):

        """Unequip item and update UI"""

        # Check which slot

        if self.player.equipped["weapon"] == item:

            self.player.unequip("weapon")

        elif self.player.equipped["armor"] == item:

            self.player.unequip("armor")

        # Update UI

        self.update_inventory_ui()

        # Hide modal panel

        self.ui_manager.hide_modal()

    def use_item(self, item):

        """Use item and update UI"""

        # Find item in inventory

        try:

            index = self.player.inventory.index(item)

            self.player.use_item(index)

            # Update UI

            self.update_inventory_ui()

            self.update_status_bars()



        except ValueError:

            # Item not found

            pass

        # Hide modal panel

        self.ui_manager.hide_modal()

    def drop_item(self, item):

        """Drop item to ground"""

        # Find item in inventory

        try:

            index = self.player.inventory.index(item)

            dropped_item = self.player.remove_from_inventory(index)

            if dropped_item:
                # Create item entity at player position

                item_entity = Item(self.player.rect.centerx, self.player.rect.centery, dropped_item)

                self.items.add(item_entity)

                self.all_sprites.add(item_entity)

            # Update UI

            self.update_inventory_ui()



        except ValueError:

            # Item not found

            pass

        # Hide modal panel

        self.ui_manager.hide_modal()

    def assign_skill(self, skill):

        """Display skill info and allow assigning to hotkey"""

        # Update skill description

        description = skill.get_info()

        self.skill_description.set_text(description)

    def open_shop(self, npc):

        """Open shop with NPC"""

        self.shop_active = True

        self.current_shop = npc

        # Create shop panel

        shop_panel = self.create_shop_panel(npc)

        # Show shop panel

        self.ui_manager.show_modal(shop_panel)

    def close_shop(self):

        """Close shop"""

        self.shop_active = False

        self.current_shop = None

        # Hide modal panel

        self.ui_manager.hide_modal()

    def buy_item(self, item):

        """Buy item from shop"""

        # Check if player can afford

        if self.player.get_total_copper() >= item.value * 100:

            # Create a copy of the item

            bought_item = copy.deepcopy(item)

            # Add to inventory if space available

            if len(self.player.inventory) < self.player.max_inventory:

                # Spend money

                self.player.spend_currency(item.value * 100)

                # Add to inventory

                self.player.add_to_inventory(bought_item)

                # Show message

                print(f"Bought {bought_item.name} for {item.value} gold")

                # Update shop display

                self.close_shop()

                self.open_shop(self.current_shop)

            else:

                # Inventory full message

                print("Inventory is full!")

        else:

            # Not enough money message

            print("Not enough money!")

    def update_status_bars(self):

        """Update HP, MP, and EXP bars"""

        self.hp_bar.set_value(self.player.stats["hp"])

        self.hp_bar.set_max_value(self.player.stats["max_hp"])

        self.mp_bar.set_value(self.player.stats["mp"])

        self.mp_bar.set_max_value(self.player.stats["max_mp"])

        self.exp_bar.set_value(self.player.stats["exp"])

        self.exp_bar.set_max_value(self.player.stats["next_level_exp"])

    def check_and_generate_chunks(self):

        """Check and generate map chunks around player"""

        # Get player's chunk coordinates

        player_chunk_x = self.player.rect.centerx // (CHUNK_SIZE * TILE_SIZE)

        player_chunk_y = self.player.rect.centery // (CHUNK_SIZE * TILE_SIZE)

        # Generate 3x3 grid of chunks around player

        for cy in range(player_chunk_y - 1, player_chunk_y + 2):

            for cx in range(player_chunk_x - 1, player_chunk_x + 2):

                chunk_key = (cx, cy)

                # Only generate if not already generated

                if chunk_key not in self.generated_chunks:
                    # Generate map chunk

                    self.map.generate_chunk(cx, cy)

                    # Generate entities in this chunk

                    self.generate_entities_in_chunk(cx, cy)

                    # Mark chunk as generated

                    self.generated_chunks.add(chunk_key)

    def generate_entities_in_chunk(self, chunk_x, chunk_y):

        """Generate monsters, items, and NPCs in a chunk"""

        # Get chunk coordinates

        chunk_rect = pygame.Rect(

            chunk_x * CHUNK_SIZE * TILE_SIZE,

            chunk_y * CHUNK_SIZE * TILE_SIZE,

            CHUNK_SIZE * TILE_SIZE,

            CHUNK_SIZE * TILE_SIZE

        )

        # Determine chunk's primary biome

        center_x = chunk_rect.centerx // TILE_SIZE

        center_y = chunk_rect.centery // TILE_SIZE

        biome = self.map.determine_biome(center_x, center_y)

        # Generate monsters based on biome

        self.generate_monsters_in_chunk(chunk_rect, biome)

        # Generate NPCs (rarely)

        if random.random() < 0.2:  # 20% chance

            self.generate_npc_in_chunk(chunk_rect, biome)

        # Generate items (rarely)

        if random.random() < 0.3:  # 30% chance

            self.generate_items_in_chunk(chunk_rect, biome)

    def generate_monsters_in_chunk(self, chunk_rect, biome):
        """基于生物群系在区块中生成怪物"""
        # 确定要生成的怪物数量
        num_monsters = random.randint(1, 4)

        # 生成怪物
        for _ in range(num_monsters):
            # 尝试找到有效的生成位置
            for attempt in range(10):  # 最多尝试10次
                # 区块内随机位置
                x = random.randint(chunk_rect.left, chunk_rect.right)
                y = random.randint(chunk_rect.top, chunk_rect.bottom)

                # 检查位置是否有效（可通行地形）
                tile_x = x // TILE_SIZE
                tile_y = y // TILE_SIZE

                if self.map.is_passable(tile_x, tile_y):
                    # 找到有效位置，确定怪物类型
                    monster_type = self.get_monster_type_for_biome(biome)

                    # 基于与中心距离确定怪物等级
                    distance = ((x - SCREEN_WIDTH // 2) ** 2 + (y - SCREEN_HEIGHT // 2) ** 2) ** 0.5
                    level = max(1, int(distance / (TILE_SIZE * 50)))

                    # 创建怪物（传递game引用）
                    monster = Monster(x, y, monster_type, level, self)

                    # 添加到精灵组
                    self.enemies.add(monster)
                    self.all_sprites.add(monster)

                    break  # 成功生成

    def get_monster_type_for_biome(self, biome):

        """Determine monster type based on biome"""

        # Use weights from biome configuration

        if biome in BIOME_MONSTER_WEIGHTS:

            weights = BIOME_MONSTER_WEIGHTS[biome]

            # Choose monster type based on weights

            monster_types, monster_weights = zip(*weights)

            return random.choices(monster_types, weights=monster_weights, k=1)[0]

        else:

            # Default to slime

            return MonsterType.SLIME

    def generate_npc_in_chunk(self, chunk_rect, biome):

        """Generate NPC in chunk"""

        # Try to find valid position

        for attempt in range(10):  # Try up to 10 times

            # Random position in chunk

            x = random.randint(chunk_rect.left, chunk_rect.right)

            y = random.randint(chunk_rect.top, chunk_rect.bottom)

            # Check if position is valid (passable terrain)

            tile_x = x // TILE_SIZE

            tile_y = y // TILE_SIZE

            if self.map.is_passable(tile_x, tile_y):
                # Valid position found, create NPC

                npc = NPC(x, y, biome)

                # Add to sprite groups

                self.npcs.add(npc)

                self.all_sprites.add(npc)

                break  # Successfully spawned

    def generate_items_in_chunk(self, chunk_rect, biome):

        """Generate items in chunk"""

        # Determine number of items to spawn

        num_items = random.randint(1, 2)

        # Spawn items

        for _ in range(num_items):

            # Try to find valid position

            for attempt in range(10):  # Try up to 10 times

                # Random position in chunk

                x = random.randint(chunk_rect.left, chunk_rect.right)

                y = random.randint(chunk_rect.top, chunk_rect.bottom)

                # Check if position is valid (passable terrain)

                tile_x = x // TILE_SIZE

                tile_y = y // TILE_SIZE

                if self.map.is_passable(tile_x, tile_y):
                    # Valid position found, determine item type

                    item = self.generate_random_item(biome)

                    # Create item entity

                    item_entity = Item(x, y, item)

                    # Add to sprite groups

                    self.items.add(item_entity)

                    self.all_sprites.add(item_entity)

                    break  # Successfully spawned

    def generate_random_item(self, biome):

        """Generate random item based on biome"""

        # Determine item type

        item_type_weights = [

            (ItemType.WEAPON, 25),

            (ItemType.ARMOR, 25),

            (ItemType.POTION, 50)

        ]

        item_type = random.choices(

            [t for t, _ in item_type_weights],

            weights=[w for _, w in item_type_weights],

            k=1

        )[0]

        if item_type == ItemType.WEAPON:

            # Choose random weapon

            weapon_type = random.choice(list(WeaponType))

            # Basic weapon

            return copy.deepcopy(WEAPONS[weapon_type])



        elif item_type == ItemType.ARMOR:

            # Choose random armor

            armor_type = random.choice(list(ArmorType))

            # Basic armor

            return copy.deepcopy(ARMORS[armor_type])



        elif item_type == ItemType.POTION:

            # Choose random potion

            potion_type = random.choice(list(PotionType))

            # Basic potion

            return copy.deepcopy(POTIONS[potion_type])

    def spawn_enemies(self, count):
        """生成初始怪物在玩家周围"""
        for _ in range(count):
            # 在玩家周围随机位置
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(TILE_SIZE * 10, TILE_SIZE * 20)
            x = self.player.rect.centerx + int(math.cos(angle) * distance)
            y = self.player.rect.centery + int(math.sin(angle) * distance)

            # 检查位置是否有效
            tile_x = x // TILE_SIZE
            tile_y = y // TILE_SIZE

            if self.map.is_passable(tile_x, tile_y):
                # 选择怪物类型
                monster_type = random.choice([
                    MonsterType.SLIME,
                    MonsterType.WOLF,
                    MonsterType.GOBLIN
                ])

                # 创建怪物（传递game引用）
                monster = Monster(x, y, monster_type, 1, self)

                # 添加到精灵组
                self.enemies.add(monster)
                self.all_sprites.add(monster)

    def spawn_npcs(self, count):

        """Spawn initial NPCs around player"""

        for _ in range(count):

            # Random position around player

            angle = random.uniform(0, 2 * math.pi)

            distance = random.uniform(TILE_SIZE * 10, TILE_SIZE * 15)

            x = self.player.rect.centerx + int(math.cos(angle) * distance)

            y = self.player.rect.centery + int(math.sin(angle) * distance)

            # Check if position is valid

            tile_x = x // TILE_SIZE

            tile_y = y // TILE_SIZE

            if self.map.is_passable(tile_x, tile_y):
                # Determine biome

                biome = self.map.determine_biome(tile_x, tile_y)

                # Create NPC

                npc = NPC(x, y, biome)

                # Add to sprite groups

                self.npcs.add(npc)

                self.all_sprites.add(npc)

    def check_player_item_pickups(self):
        """检查玩家是否可以拾取附近的物品"""
        for item in self.items:
            # 计算与玩家的距离
            distance = ((item.rect.centerx - self.player.rect.centerx) ** 2 +
                        (item.rect.centery - self.player.rect.centery) ** 2) ** 0.5

            if distance <= item.pickup_radius:
                # 检查这是否是金币拾取
                if hasattr(item.equipment, 'stats') and 'gold_value' in item.equipment.stats:
                    # 将金币添加给玩家
                    gold_value = item.equipment.stats['gold_value']
                    self.player.add_currency(gold=gold_value)
                    self.player.add_floating_text(f"+{gold_value} 金币", COLORS["gold"])
                    item.kill()  # 从世界中移除物品
                else:
                    # 尝试添加到背包
                    if self.player.add_to_inventory(item.equipment):
                        # 从世界中移除物品
                        item.kill()
                        # 更新统计数据
                        self.update_player_statistics("items_found")

    def check_player_npc_interaction(self):

        """Check if player can interact with NPCs"""

        # Only check if E key is pressed

        keys = pygame.key.get_pressed()

        if not keys[pygame.K_e]:
            return

        for npc in self.npcs:

            # Check if in range

            if npc.can_interact(self.player):

                # Interact with NPC

                if npc.interact():
                    # Open shop

                    self.open_shop(npc)

                    return

    def update(self):
        """更新游戏状态"""
        # 计算 delta time
        self.dt = self.clock.tick(60) / 1000.0

        # 如果游戏结束则跳过更新
        if self.game_over:
            return

        # 如果暂停则跳过更新
        if self.paused:
            return

        # 如果商店激活则跳过更新
        if self.shop_active:
            return

        # 更新游戏时间统计
        self.update_player_statistics("play_time", self.dt)

        # 更新玩家
        self.player.update(self.dt, self.map)

        # 检查玩家死亡
        if self.player.stats["hp"] <= 0:
            self.game_over = True
            self.update_player_statistics("deaths")
            self.ui_manager.show_modal(self.create_game_over_panel())
            return

        # Generate new map chunks if needed

        self.check_and_generate_chunks()

        # Update camera

        self.camera.update(self.player)

        # Update enemies

        for enemy in self.enemies:
            enemy.update(self.dt, self.player, self.map)

        # Update NPCs

        for npc in self.npcs:
            npc.update(self.dt, self.player)

        # Update items

        for item in self.items:
            item.update(self.dt)

        # Check for item pickups

        self.check_player_item_pickups()

        # Check for NPC interactions

        self.check_player_npc_interaction()

        # Update HP, MP, EXP bars

        self.update_status_bars()

    def handle_events(self):

        """Handle input events"""

        for event in pygame.event.get():

            # Quit event

            if event.type == pygame.QUIT:
                self.running = False

            # Handle UI events first

            if self.ui_manager.handle_event(event):
                continue

            # Handle keyboard events

            if event.type == pygame.KEYDOWN:

                # Pause/unpause

                if event.key == pygame.K_ESCAPE:

                    self.paused = not self.paused



                # Inventory shortcut

                elif event.key == pygame.K_i:

                    self.toggle_inventory_panel()



                # Stats shortcut

                elif event.key == pygame.K_c:

                    self.toggle_stats_panel()



                # Skills shortcut

                elif event.key == pygame.K_k:

                    self.toggle_skills_panel()



                # Use item hotkeys

                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:

                    # Use item in slot 0-4

                    slot = event.key - pygame.K_1

                    if 0 <= slot < len(self.player.inventory):
                        self.player.use_item(slot)

                        self.update_status_bars()



            # Handle mouse events

            elif event.type == pygame.MOUSEBUTTONDOWN:

                # Left click for attack

                if event.button == 1 and not self.shop_active and not self.paused:
                    self.player.attack()

    def handle_monster_death(self, monster):
        """处理怪物死亡 - 经验获取、掉落物品和移除怪物"""
        # 更新统计数据
        self.update_player_statistics("monsters_killed")

        # 移除精灵组
        monster.kill()

        # 给予玩家经验
        exp_gained = monster.stats["exp_value"]
        level_up = self.player.gain_exp(exp_gained)

        # 如果玩家升级，更新UI并记录统计
        if level_up:
            self.update_player_statistics("levels_gained")
            self.update_status_bars()

        # 生成掉落物
        self.generate_monster_loot(monster)

    def generate_monster_loot(self, monster):
        """生成怪物死亡后的掉落物"""
        # 基础掉落概率
        drop_chance = 0.75

        # 更高等级的怪物有更好的掉落概率
        drop_chance += min(0.2, monster.level * 0.02)

        # 如果不掉落则跳过
        if random.random() > drop_chance:
            return

        # 确定掉落类型
        # 金币有最高概率
        if random.random() < 0.6:
            self.drop_gold(monster)
        else:
            self.drop_item(monster)

    def drop_gold(self, monster):
        """基于怪物等级和类型掉落金币"""
        # 基础金币掉落量
        base_gold = monster.level * 2

        # 基于怪物类型的奖励金币
        if monster.monster_type == MonsterType.DRAGON:
            base_gold *= 5
        elif monster.monster_type == MonsterType.TROLL:
            base_gold *= 3
        elif monster.monster_type == MonsterType.BANDIT:
            base_gold *= 2

        # 添加随机性
        gold_amount = max(1, int(base_gold * random.uniform(0.8, 1.2)))

        # 创建特殊的"金币"物品
        gold_item = Equipment(
            name=f"{gold_amount} 金币",
            item_type=ItemType.POTION,  # 重用药水类型作为拾取物
            stats={"gold_value": gold_amount},
            value=gold_amount,
            description=f"一堆{gold_amount}金币"
        )

        # 在怪物位置创建物品实体，添加轻微随机偏移
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        item_entity = Item(monster.rect.centerx + offset_x, monster.rect.centery + offset_y, gold_item)

        # 添加到精灵组
        self.items.add(item_entity)
        self.all_sprites.add(item_entity)

        # 更新统计数据
        self.update_player_statistics("total_gold", gold_amount)

    def drop_item(self, monster):
        """基于怪物等级和类型掉落物品"""
        # 基于怪物等级确定物品稀有度
        rarity_roll = random.random() + (monster.level * 0.02)

        # 特定怪物类型增加稀有度
        if monster.monster_type == MonsterType.DRAGON:
            rarity_roll += 0.2
        elif monster.monster_type == MonsterType.BANDIT:
            rarity_roll += 0.1

        if rarity_roll > 0.98:
            quality = "epic"
        elif rarity_roll > 0.85:
            quality = "rare"
        elif rarity_roll > 0.6:
            quality = "uncommon"
        else:
            quality = "base"

        # 确定物品类型
        item_type_roll = random.random()

        if item_type_roll < 0.4:
            # 掉落药水
            potion_type = random.choice(list(PotionType))
            item = copy.deepcopy(POTIONS[potion_type])
        elif item_type_roll < 0.7:
            # 掉落武器
            weapon_type = random.choice(list(WeaponType))
            item = copy.deepcopy(UPGRADED_WEAPONS[weapon_type][quality])
        else:
            # 掉落护甲
            armor_type = random.choice(list(ArmorType))
            item = copy.deepcopy(UPGRADED_ARMORS[armor_type][quality])

        # 在怪物位置创建物品实体，添加轻微随机偏移
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        item_entity = Item(monster.rect.centerx + offset_x, monster.rect.centery + offset_y, item)

        # 添加到精灵组
        self.items.add(item_entity)
        self.all_sprites.add(item_entity)

        # 更新统计数据
        self.update_player_statistics("items_found")

    def update_player_statistics(self, stat_name, value=1):
        """更新玩家统计数据"""
        if hasattr(self, 'player_stats') and stat_name in self.player_stats:
            self.player_stats[stat_name] += value

    def handle_movement(self):

        """Handle player movement input"""

        # Skip if paused or in shop

        if self.paused or self.shop_active:
            return

        # Get keyboard state

        keys = pygame.key.get_pressed()

        # Calculate movement direction

        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1

        # Move player

        self.player.move(dx, dy, self.map)

    def draw(self):

        """Draw game state"""

        # Clear screen

        self.screen.fill((0, 0, 0))

        # Get camera position

        camera_pos = (-self.camera.rect.x, -self.camera.rect.y)

        # Draw map

        self.map.draw(self.screen, self.camera)

        # Draw sprites

        for sprite in self.all_sprites:

            if isinstance(sprite, (Player, Monster, NPC, Item)):

                sprite.draw(self.screen, camera_pos)

                # Draw floating texts for entities

                if hasattr(sprite, "draw_floating_texts"):
                    sprite.draw_floating_texts(self.screen, camera_pos)

        # Draw UI

        self.ui_manager.draw()

        # Draw paused text if paused

        if self.paused:
            font = pygame.font.Font(None, 48)

            text = font.render("PAUSED", True, (255, 255, 255))

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

            self.screen.blit(text, text_rect)

        # Update display

        pygame.display.flip()

    def restart_game(self):

        """Restart the game"""

        self.__init__()  # Reinitialize game

    def run(self):

        """Main game loop"""

        while self.running:
            self.handle_events()

            self.handle_movement()

            self.update()

            self.draw()

        pygame.quit()


# Main function

def main():
    """Main function"""

    # Initialize pygame

    pygame.init()

    # Create and run game

    game = Game()

    game.run()


# Run the game

if __name__ == "__main__":
    main()

