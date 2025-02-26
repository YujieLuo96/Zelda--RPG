import pygame
import random
import sys
import math
import os
from collections import deque
from enum import Enum
from typing import List, Dict, Tuple, Optional, Union, Set

# ---------- 初始化 ----------
pygame.init()

# ---------- 常量设置 ----------
# 屏幕尺寸和基础设置
TILE_SIZE = 35
MAP_WIDTH = 37  # 必须为奇数，方便生成迷宫
MAP_HEIGHT = 37
SIDEBAR_WIDTH = 300  # 侧边栏宽度
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE + SIDEBAR_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE
FPS = 60
MAX_ROOM = 6
MAX_ROOM_SIZE = 19

# 颜色定义
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_BROWN = (139, 69, 19)
COLOR_LIGHT_BLUE = (173, 216, 230)

# 墙壁相关颜色
COLOR_STONE = (40, 40, 40)  # 基础石墙颜色
COLOR_MOSS = (34, 139, 34)  # 青苔颜色
COLOR_CRACK = (80, 80, 80)  # 裂缝颜色
COLOR_HIGHLIGHT = (90, 90, 90)  # 石墙高光
COLOR_SHADOW = (20, 20, 20)  # 石墙阴影
COLOR_FLOOR_CRACK = (180, 180, 180, 60)  # 半透明裂缝颜色
COLOR_FLOOR_STONE = (200, 200, 200, 40)  # 石块边缘颜色
COLOR_WALL = (0, 0, 0)
COLOR_FLOOR = (150, 150, 150)
COLOR_PLAYER = (0, 255, 0)
COLOR_MONSTER = (255, 0, 0)
COLOR_CHEST = (255, 215, 0)
COLOR_EXIT = (0, 0, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_HP = (255, 0, 0)
COLOR_ATK = (255, 165, 0)
COLOR_DEF = (0, 255, 255)

# UI颜色
COLOR_BUTTON = (90, 90, 90)
COLOR_BUTTON_HOVER = (120, 120, 120)
COLOR_UI_TEXT = (200, 160, 60)
COLOR_DEATH_RED = (139, 0, 0)

# 特殊房间参数
FOUNTAIN_ROOM_PROB = 0.2  # 喷泉房生成概率
FOUNTAIN_SPAWN_INTERVAL = 2000  # 史莱姆生成间隔(毫秒)
LAVA_ROOM_PROB = 0.2  # 岩浆房生成概率
LAVA_SPAWN_INTERVAL = 2500  # 岩浆怪物生成间隔
LAVA_DAMAGE = 80  # 岩浆伤害(每秒)

# 路径效果
PATHTIME = 0.35  # 路径显示时长(秒)
ORDINARYEFFECT = True  # 普通路径效果
LIGHTNINGEFFECT_RED = False  # 红色闪电效果
LIGHTNINGEFFECT_YELLOW = False  # 黄色闪电效果
LIGHTNINGEFFECT_BLUE = False  # 蓝色闪电效果

# 怪物追踪距离
MONSTER_DISTANCE = 6

# 怪物强度参数
S_MONSTER = 2
N = 3
MONSTER_MIN = math.ceil(N)
MONSTER_MAX = math.ceil(N * 8)

# 道具数量范围
M = 4
ITEM_MIN = math.ceil(8)
ITEM_MAX = math.ceil(M * 8)

# 怪物权重（生成几率）
MONSTER_WEIGHT = [10, 10, 5, 5, 5, 12, 16, 12, 8, 6, 5, 5, 8, 2, 1, 1, 1, 1, 1, 1, 1]


# ---------- 枚举类型 ----------
class EntityType(Enum):
    PLAYER = 0
    MONSTER = 1
    NPC = 2
    ITEM = 3


class ItemType(Enum):
    WEAPON = 0
    ARMOR = 1
    POTION = 2
    MATERIAL = 3
    CURRENCY = 4
    CHEST = 5
    HP_SMALL = 6
    HP_LARGE = 7
    ATK_GEM = 8
    DEF_GEM = 9


class WeaponType(Enum):
    SWORD = 0
    DAGGER = 1
    BOW = 2
    STAFF = 3
    SPEAR = 4
    AXE = 5
    HAMMER = 6
    WAND = 7
    SHIELD = 8
    GUN = 9


class ArmorType(Enum):
    HELMET = 0
    CHESTPLATE = 1
    LEGGINGS = 2
    BOOTS = 3
    GLOVES = 4
    AMULET = 5
    RING = 6
    BELT = 7
    CLOAK = 8
    BRACELET = 9


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class TerrainType(Enum):
    FLOOR = 0
    WALL = 1
    FOUNTAIN = 2
    LAVA = 3
    STATUE = 4
    HELL_FLOOR = 5


# ---------- 游戏数据 ----------
# 怪物数据列表
monsters_data = [
    {"name": "蝙蝠", "HP": 50, "ATK": 20, "DEF": 5, "size": (1, 1), "coin": 20, "speed": 5, "level": 1},
    {"name": "白色蝙蝠", "HP": 55, "ATK": 22, "DEF": 6, "size": (1, 1), "coin": 22, "speed": 4, "level": 1},
    {"name": "腐蚀怪", "HP": 200, "ATK": 40, "DEF": 15, "size": (1, 1), "coin": 50, "speed": 15, "level": 2},
    {"name": "火焰骑士", "HP": 250, "ATK": 35, "DEF": 30, "size": (1, 1), "coin": 50, "speed": 18, "level": 3},
    {"name": "纯火焰骑士", "HP": 300, "ATK": 40, "DEF": 35, "size": (1, 1), "coin": 55, "speed": 15, "level": 4},
    {"name": "骷髅", "HP": 100, "ATK": 30, "DEF": 10, "size": (1, 2), "coin": 35, "speed": 25, "level": 1},
    {"name": "史莱姆", "HP": 80, "ATK": 25, "DEF": 8, "size": (1, 1), "coin": 25, "speed": 20, "level": 1},
    {"name": "红史莱姆", "HP": 160, "ATK": 35, "DEF": 12, "size": (1, 1), "coin": 45, "speed": 25, "level": 2},
    {"name": "黑史莱姆", "HP": 240, "ATK": 45, "DEF": 16, "size": (1, 1), "coin": 60, "speed": 30, "level": 3},
    {"name": "闪光史莱姆", "HP": 280, "ATK": 55, "DEF": 30, "size": (1, 1), "coin": 90, "speed": 20, "level": 4},
    {"name": "电击球", "HP": 200, "ATK": 40, "DEF": 15, "size": (1, 1), "coin": 50, "speed": 4, "level": 2},
    {"name": "异色电击球", "HP": 220, "ATK": 44, "DEF": 18, "size": (1, 1), "coin": 55, "speed": 4, "level": 2},
    {"name": "魔法师", "HP": 120, "ATK": 35, "DEF": 12, "size": (1, 2), "coin": 60, "speed": 35, "level": 3},
    {"name": "魔王", "HP": 1000, "ATK": 50, "DEF": 20, "size": (2, 2), "coin": 300, "speed": 50, "level": 5},
    {"name": "圣洁魔王", "HP": 1100, "ATK": 55, "DEF": 22, "size": (2, 2), "coin": 330, "speed": 45, "level": 6},
    {"name": "普通巨龙", "HP": 5000, "ATK": 110, "DEF": 50, "size": (3, 3), "coin": 1200, "speed": 60, "level": 7},
    {"name": "冰霜巨龙", "HP": 5500, "ATK": 130, "DEF": 55, "size": (3, 3), "coin": 1300, "speed": 60, "level": 8},
    {"name": "血腥闪电", "HP": 6000, "ATK": 200, "DEF": 110, "size": (3, 3), "coin": 1500, "speed": 30, "level": 7},
    {"name": "纯青闪电", "HP": 7000, "ATK": 300, "DEF": 130, "size": (3, 3), "coin": 2000, "speed": 30, "level": 8},
    {"name": "金色闪电", "HP": 8000, "ATK": 400, "DEF": 150, "size": (3, 3), "coin": 2500, "speed": 30, "level": 9},
    {"name": "火焰领主", "HP": 6500, "ATK": 130, "DEF": 60, "size": (3, 3), "coin": 1500, "speed": 60, "level": 7},
    {"name": "纯火焰领主", "HP": 7500, "ATK": 180, "DEF": 80, "size": (3, 3), "coin": 1900, "speed": 50, "level": 8}
]

# 装备类型
EQUIPMENT_TYPES = {
    # 武器列表
    "WOOD_SWORD": {"name": "木剑", "type": "weapon", "atk": 5, "multiple": 1, "durability": 20},
    "BRONZE_DAGGER": {"name": "青铜匕首", "type": "weapon", "atk": 8, "multiple": 1.1, "durability": 30},
    "STEEL_DAGGER": {"name": "钢匕首", "type": "weapon", "atk": 12, "multiple": 1.2, "durability": 40},
    "COPPER_SWORD": {"name": "铜剑", "type": "weapon", "atk": 15, "multiple": 1.1, "durability": 50},
    "IRON_SWORD": {"name": "铁剑", "type": "weapon", "atk": 20, "multiple": 1.2, "durability": 60},
    "FINE_STEEL_DAGGER": {"name": "精钢匕首", "type": "weapon", "atk": 25, "multiple": 1.3, "durability": 70},
    "FINE_IRON_SWORD": {"name": "精铁长剑", "type": "weapon", "atk": 30, "multiple": 1.3, "durability": 80},
    "GUTS_GREATSWORD": {"name": "格斯大剑", "type": "weapon", "atk": 50, "multiple": 1.5, "durability": 100},

    # 护甲列表
    "WOOD_ARMOR": {"name": "木甲", "type": "armor", "def": 5, "multiple": 1, "durability": 30},
    "COPPER_ARMOR": {"name": "铜甲", "type": "armor", "def": 10, "multiple": 1.1, "durability": 50},
    "IRON_ARMOR": {"name": "铁甲", "type": "armor", "def": 15, "multiple": 1.2, "durability": 70},
    "STEEL_ARMOR": {"name": "钢甲", "type": "armor", "def": 20, "multiple": 1.3, "durability": 90},
    "LIGHTNING_ARMOR_RED": {"name": "红闪电甲", "type": "armor", "def": 30, "multiple": 1.4, "durability": 110},
    "LIGHTNING_ARMOR_BLUE": {"name": "蓝闪电甲", "type": "armor", "def": 30, "multiple": 1.4, "durability": 110},
    "LIGHTNING_ARMOR_YELLOW": {"name": "黄闪电甲", "type": "armor", "def": 30, "multiple": 1.4, "durability": 110}
}

# 地形属性
terrain_properties = {
    TerrainType.FLOOR: {"color": COLOR_FLOOR, "walkable": True},
    TerrainType.WALL: {"color": COLOR_STONE, "walkable": False},
    TerrainType.FOUNTAIN: {"color": COLOR_LIGHT_BLUE, "walkable": True},
    TerrainType.LAVA: {"color": (255, 69, 0), "walkable": True},
    TerrainType.STATUE: {"color": (20, 20, 20), "walkable": False},
    TerrainType.HELL_FLOOR: {"color": (60, 30, 30), "walkable": True}
}


# ---------- 技能类 ----------
class Skill:
    def __init__(self, name, description, mana_cost, cooldown,
                 damage_multiplier=1.0, range_multiplier=1.0,
                 area_effect=False, area_radius=0, status_effects=None):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.damage_multiplier = damage_multiplier
        self.range_multiplier = range_multiplier
        self.area_effect = area_effect
        self.area_radius = area_radius
        self.status_effects = status_effects if status_effects else []
        self.current_cooldown = 0

    def use(self, user, target=None):
        if self.current_cooldown > 0:
            return False, f"{self.name}还在冷却中({self.current_cooldown}回合)"

        if user.mana < self.mana_cost:
            return False, "法力不足"

        user.mana -= self.mana_cost
        self.current_cooldown = self.cooldown

        # 子类实现具体效果
        return True, f"{user.name}使用了{self.name}"

    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def __str__(self):
        return f"{self.name}: {self.description} (法力: {self.mana_cost}, 冷却: {self.cooldown})"


class FireballSkill(Skill):
    def __init__(self):
        super().__init__(
            name="火球术",
            description="发射一个火球，造成火焰伤害",
            mana_cost=20,
            cooldown=3,
            damage_multiplier=1.5,
            range_multiplier=2.0,
            area_effect=True,
            area_radius=2,
            status_effects=[{"type": "burn", "duration": 3, "damage_per_turn": 5}]
        )

    def use(self, user, target=None):
        success, message = super().use(user, target)
        if not success:
            return success, message

        base_damage = user.attack * self.damage_multiplier

        if target:
            damage = max(1, int(base_damage - target.defense * 0.5))
            target.take_damage(damage)

            # 应用状态效果
            for effect in self.status_effects:
                target.add_status_effect(effect)

            return True, f"{user.name}的火球击中了{target.name}，造成{damage}点伤害!"

        return True, f"{user.name}释放了火球但没有命中!"


class HealSkill(Skill):
    def __init__(self):
        super().__init__(
            name="治疗术",
            description="恢复自己或盟友的生命值",
            mana_cost=15,
            cooldown=4,
            damage_multiplier=0,
            range_multiplier=1.5,
            area_effect=False
        )

    def use(self, user, target=None):
        success, message = super().use(user, target)
        if not success:
            return success, message

        heal_target = target if target else user
        heal_amount = int(user.max_health * 0.3)
        heal_target.health = min(heal_target.max_health, heal_target.health + heal_amount)

        return True, f"{user.name}治疗了{heal_target.name}，恢复了{heal_amount}点生命值!"


class StunSkill(Skill):
    def __init__(self):
        super().__init__(
            name="眩晕打击",
            description="眩晕目标一段时间",
            mana_cost=25,
            cooldown=5,
            damage_multiplier=0.5,
            range_multiplier=1.0,
            area_effect=False,
            status_effects=[{"type": "stun", "duration": 2}]
        )

    def use(self, user, target=None):
        success, message = super().use(user, target)
        if not success:
            return success, message

        if target:
            damage = max(1, int(user.attack * self.damage_multiplier - target.defense * 0.3))
            target.take_damage(damage)

            # 应用眩晕效果
            for effect in self.status_effects:
                target.add_status_effect(effect)

            return True, f"{user.name}眩晕了{target.name}，造成{damage}点伤害!"

        return True, f"{user.name}尝试眩晕但没有命中!"


class PoisonDartSkill(Skill):
    def __init__(self):
        super().__init__(
            name="毒镖",
            description="发射一支毒镖，造成持续伤害",
            mana_cost=15,
            cooldown=4,
            damage_multiplier=0.7,
            range_multiplier=1.8,
            area_effect=False,
            status_effects=[{"type": "poison", "duration": 4, "damage_per_turn": 8}]
        )

    def use(self, user, target=None):
        success, message = super().use(user, target)
        if not success:
            return success, message

        if target:
            damage = max(1, int(user.attack * self.damage_multiplier - target.defense * 0.2))
            target.take_damage(damage)

            # 应用毒药效果
            for effect in self.status_effects:
                target.add_status_effect(effect)

            return True, f"{user.name}的毒镖命中了{target.name}，造成{damage}点伤害外加中毒效果!"

        return True, f"{user.name}发射了毒镖但没有命中!"


class WhirlwindSkill(Skill):
    def __init__(self):
        super().__init__(
            name="旋风斩",
            description="旋转攻击，命中周围所有敌人",
            mana_cost=30,
            cooldown=6,
            damage_multiplier=1.2,
            range_multiplier=1.0,
            area_effect=True,
            area_radius=3
        )

    def use(self, user, target=None):
        success, message = super().use(user, target)
        if not success:
            return success, message

        # 简化版实现：只攻击主要目标
        if target:
            damage = max(1, int(user.attack * self.damage_multiplier - target.defense * 0.2))
            target.take_damage(damage)
            return True, f"{user.name}的旋风斩击中了{target.name}，造成{damage}点伤害!"

        return True, f"{user.name}使用了旋风斩，但没有击中任何目标!"


# 所有技能字典
ALL_SKILLS = {
    "fireball": FireballSkill(),
    "heal": HealSkill(),
    "stun": StunSkill(),
    "poison_dart": PoisonDartSkill(),
    "whirlwind": WhirlwindSkill()
}


# ---------- 状态效果 ----------
class StatusEffect:
    def __init__(self, effect_type, duration, **kwargs):
        self.type = effect_type
        self.duration = duration
        self.properties = kwargs

    def apply(self, entity):
        # 根据类型应用效果
        if self.type == "burn":
            if "damage_per_turn" in self.properties:
                entity.take_damage(self.properties["damage_per_turn"])
                return f"{entity.name}受到{self.properties['damage_per_turn']}点燃烧伤害"

        elif self.type == "poison":
            if "damage_per_turn" in self.properties:
                entity.take_damage(self.properties["damage_per_turn"])
                return f"{entity.name}受到{self.properties['damage_per_turn']}点毒素伤害"

        elif self.type == "stun":
            entity.can_act = False
            return f"{entity.name}被眩晕了"

        return ""

    def update(self, entity):
        self.duration -= 1
        result = self.apply(entity)

        if self.duration <= 0:
            # 移除效果
            if self.type == "stun":
                entity.can_act = True
                return f"{entity.name}不再被眩晕"

        return result


# ---------- 特殊效果类 ----------
class CrackEffect:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.lifetime = 2.0  # 效果持续时间(秒)
        self.cracks = []  # 裂缝列表

        # 生成裂缝
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) <= radius:
                    self.cracks.append((x + dx, y + dy))

    def update(self, dt):
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, screen):
        for (cx, cy) in self.cracks:
            rect = pygame.Rect(cx * TILE_SIZE, cy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (80, 80, 80), rect)
            # 绘制裂缝细节
            for _ in range(3):
                start_x = cx * TILE_SIZE + random.randint(2, TILE_SIZE - 2)
                start_y = cy * TILE_SIZE + random.randint(2, TILE_SIZE - 2)
                end_x = start_x + random.randint(-4, 4)
                end_y = start_y + random.randint(-4, 4)
                pygame.draw.line(screen, (50, 50, 50), (start_x, start_y), (end_x, end_y), 2)


class IceBreathEffect:
    def __init__(self, start_pos, direction):
        self.start_pos = start_pos  # 吐息起点(巨龙嘴部位置)
        self.direction = direction  # 吐息方向向量
        self.lifetime = 2.0  # 效果持续时间(秒)
        self.ice_particles = []  # 冰晶粒子
        self.area = set()  # 影响区域坐标

        # 生成扇形区域
        length = 7  # 最大长度
        angle = math.radians(45)  # 扇形角度
        base_dir = math.atan2(direction[1], direction[0])
        for r in range(1, length + 1):
            for theta in [base_dir - angle / 2 + i * angle / 8 for i in range(9)]:
                x = int(start_pos[0] / TILE_SIZE + r * math.cos(theta))
                y = int(start_pos[1] / TILE_SIZE + r * math.sin(theta))
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    self.area.add((x, y))
                    # 添加冰雾粒子
                    self.ice_particles.append({
                        'pos': (x * TILE_SIZE + random.randint(2, 22), y * TILE_SIZE + random.randint(2, 22)),
                        'size': random.randint(2, 4),
                        'alpha': random.randint(100, 200)
                    })

    def update(self, dt):
        self.lifetime -= dt
        # 粒子飘散效果
        for p in self.ice_particles:
            p['pos'] = (p['pos'][0] + random.randint(-1, 1), p['pos'][1] + random.randint(-1, 1))
            p['alpha'] = max(0, p['alpha'] - 5)
        return self.lifetime > 0

    def draw(self, screen):
        # 绘制寒冰区域
        for (x, y) in self.area:
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (135, 206, 235, 50), rect)  # 半透明冰雾

        # 绘制动态冰晶
        for p in self.ice_particles:
            alpha_surface = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (240, 255, 255, p['alpha']),
                               (p['size'], p['size']), p['size'])
            screen.blit(alpha_surface, p['pos'])


class PoisonBall:
    def __init__(self, start, target):
        self.pos = list(start)
        self.target = target
        self.speed = 8  # 像素/帧
        self.trail = []  # 拖尾轨迹
        self.exploded = False

        # 计算移动方向
        dx = target[0] - start[0]
        dy = target[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.dir = (1, 0)
        else:
            self.dir = (dx / dist * self.speed, dy / dist * self.speed)

    def update(self, dt):
        if not self.exploded:
            # 更新位置
            self.pos[0] += self.dir[0]
            self.pos[1] += self.dir[1]
            self.trail.append(tuple(self.pos))
            if len(self.trail) > 10:
                self.trail.pop(0)

            # 命中检测
            if math.hypot(self.pos[0] - self.target[0], self.pos[1] - self.target[1]) < self.speed:
                self.exploded = True
                return True  # 需要触发中毒效果
        return False

    def draw(self, screen):
        # 绘制拖尾
        for i, pos in enumerate(self.trail):
            alpha = 255 * (i + 1) / len(self.trail)
            radius = int(3 * (i + 1) / len(self.trail))
            pygame.draw.circle(screen, (50, 205, 50, alpha),
                               (int(pos[0]), int(pos[1])), radius)

        # 绘制毒球主体
        if not self.exploded:
            pygame.draw.circle(screen, (50, 205, 50),
                               (int(self.pos[0]), int(self.pos[1])), 6)
            # 毒球光晕
            glow = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow, (50, 205, 50, 80), (10, 10), 8)
            screen.blit(glow, (int(self.pos[0] - 10), int(self.pos[1] - 10)))


class ElectricEffect:
    def __init__(self, px, py):
        self.particles = []
        self.duration = 0.3  # 持续时间0.3秒

        # 生成随机闪电路径
        for _ in range(8):
            start = (px * TILE_SIZE + random.randint(5, 25), py * TILE_SIZE + random.randint(5, 25))
            end = (start[0] + random.randint(-20, 20), start[1] + random.randint(-20, 20))
            self.particles.append({
                'start': start,
                'end': end,
                'alpha': 255
            })

    def update(self, dt):
        self.duration -= dt
        for p in self.particles:
            p['alpha'] = max(0, p['alpha'] - 20)
        return self.duration > 0

    def draw(self, screen):
        for p in self.particles:
            color = (255, 255, 0, p['alpha']) if random.random() > 0.3 else (255, 165, 0, p['alpha'])
            pygame.draw.line(screen, color, p['start'], p['end'], 2)


class FireStrikeEffect:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.lifetime = 2.0
        self.flames = []

        # 生成火焰区域
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) <= radius:
                    self.flames.append({
                        'pos': (x + dx, y + dy),
                        'particles': [self.create_particle(x + dx, y + dy) for _ in range(5)]
                    })

    def create_particle(self, x, y):
        return {
            'px': x * TILE_SIZE + random.randint(5, 25),
            'py': y * TILE_SIZE + random.randint(5, 25),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-5, -2),
            'life': 1.0
        }

    def update(self, dt):
        self.lifetime -= dt
        for flame in self.flames:
            # 更新现有粒子
            for p in flame['particles']:
                p['px'] += p['vx']
                p['py'] += p['vy']
                p['vy'] += 0.3  # 重力
                p['life'] -= dt * 0.5

            # 生成新粒子
            if random.random() < 0.6:
                flame['particles'].append(self.create_particle(*flame['pos']))

            # 移除过期粒子
            flame['particles'] = [p for p in flame['particles'] if p['life'] > 0]

        return self.lifetime > 0

    def draw(self, screen):
        for flame in self.flames:
            # 绘制基底火焰
            rect = pygame.Rect(flame['pos'][0] * TILE_SIZE, flame['pos'][1] * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (200, 80, 0), rect)

            # 绘制动态粒子
            for p in flame['particles']:
                alpha = int(255 * p['life'])
                color = (255, 150 + int(105 * p['life']), 0, alpha)
                pygame.draw.circle(screen, color, (int(p['px']), int(p['py'])),
                                   int(3 * p['life']))


class BlueFireStrikeEffect:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.lifetime = 2.0
        self.flames = []

        # 生成火焰区域
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if abs(dx) + abs(dy) <= radius:
                    self.flames.append({
                        'pos': (x + dx, y + dy),
                        'particles': [self.create_particle(x + dx, y + dy) for _ in range(5)]
                    })

    def create_particle(self, x, y):
        return {
            'px': x * TILE_SIZE + random.randint(5, 25),
            'py': y * TILE_SIZE + random.randint(5, 25),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-5, -2),
            'life': 1.0
        }

    def update(self, dt):
        self.lifetime -= dt
        for flame in self.flames:
            # 更新现有粒子
            for p in flame['particles']:
                p['px'] += p['vx']
                p['py'] += p['vy']
                p['vy'] += 0.3  # 重力
                p['life'] -= dt * 0.5

            # 生成新粒子
            if random.random() < 0.6:
                flame['particles'].append(self.create_particle(*flame['pos']))

            # 移除过期粒子
            flame['particles'] = [p for p in flame['particles'] if p['life'] > 0]

        return self.lifetime > 0

    def draw(self, screen):
        for flame in self.flames:
            # 绘制基底火焰
            rect = pygame.Rect(flame['pos'][0] * TILE_SIZE, flame['pos'][1] * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (55, 175, 255), rect)

            # 绘制动态粒子
            for p in flame['particles']:
                alpha = int(255 * p['life'])
                color = (0, 105 - int(105 * p['life']), 255, alpha)
                pygame.draw.circle(screen, color, (int(p['px']), int(p['py'])),
                                   int(3 * p['life']))


class CorrosionEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.create_time = pygame.time.get_ticks()
        self.particles = []  # 腐蚀粒子效果

        # 初始化腐蚀粒子
        for _ in range(20):
            self.particles.append({
                'pos': (x * TILE_SIZE + random.randint(2, 29), y * TILE_SIZE + random.randint(2, 29)),
                'size': random.randint(2, 4),
                'alpha': 255,
                'speed': (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            })

    def update(self, current_time):
        # 更新粒子状态
        for p in self.particles:
            p['pos'] = (p['pos'][0] + p['speed'][0], p['pos'][1] + p['speed'][1])
            p['alpha'] = max(0, 255 - (current_time - self.create_time) * 85 // 1000)  # 3秒淡出

        return current_time - self.create_time < 3000  # 3秒后消失

    def draw(self, screen):
        # 绘制基底腐蚀效果
        base_alpha = max(0, 200 - (pygame.time.get_ticks() - self.create_time) // 15)
        base_rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (91, 13, 133, base_alpha), base_rect)  # 紫黑色基底

        # 绘制动态腐蚀粒子
        for p in self.particles:
            if p['alpha'] > 0:
                pygame.draw.circle(screen, (139, 0, 0, p['alpha']),  # 深红色粒子
                                   (int(p['pos'][0]), int(p['pos'][1])), p['size'])


# ---------- 基础实体类 ----------
class Entity:
    def __init__(self, name, x, y, entity_type):
        self.name = name
        self.x = x
        self.y = y
        self.entity_type = entity_type
        self.direction = Direction.DOWN
        self.sprite = None
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.visible = True

    def update(self):
        self.rect.x = self.x * TILE_SIZE
        self.rect.y = self.y * TILE_SIZE

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        if not self.visible:
            return

        if self.sprite:
            surface.blit(self.sprite, (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y))
        else:
            pygame.draw.rect(surface, COLOR_RED,
                             (self.rect.x - camera_offset_x, self.rect.y - camera_offset_y,
                              TILE_SIZE, TILE_SIZE))


# ---------- 战斗实体类 ----------
class CombatEntity(Entity):
    def __init__(self, name, x, y, entity_type,
                 max_health, attack, defense,
                 crit_rate, agility, mana):
        super().__init__(name, x, y, entity_type)

        # 基础属性
        self.max_health = max_health
        self.health = max_health
        self.max_mana = mana
        self.mana = mana
        self.base_attack = attack
        self.base_defense = defense
        self.base_crit_rate = crit_rate  # 暴击率(0-100)
        self.base_agility = agility  # 敏捷(0-100)

        # 当前属性(受装备和状态效果影响)
        self.attack = attack
        self.defense = defense
        self.crit_rate = crit_rate
        self.agility = agility

        # 战斗状态
        self.alive = True
        self.can_act = True
        self.status_effects = []
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def remove_skill(self, skill_name):
        self.skills = [skill for skill in self.skills if skill.name != skill_name]

    def use_skill(self, skill_index, target=None):
        if skill_index < 0 or skill_index >= len(self.skills):
            return False, "无效的技能索引"

        if not self.can_act:
            return False, f"{self.name}当前无法行动"

        skill = self.skills[skill_index]
        return skill.use(self, target)

    def add_status_effect(self, effect_dict):
        effect = StatusEffect(effect_dict["type"], effect_dict["duration"],
                              **{k: v for k, v in effect_dict.items() if k not in ["type", "duration"]})
        self.status_effects.append(effect)

    def update_status_effects(self):
        messages = []
        remaining_effects = []

        for effect in self.status_effects:
            message = effect.update(self)
            if message:
                messages.append(message)

            if effect.duration > 0:
                remaining_effects.append(effect)

        self.status_effects = remaining_effects
        return messages

    def attack_target(self, target):
        if not self.can_act or not self.alive or not target.alive:
            return 0, False, "无法攻击"

        # 根据敏捷计算命中率
        hit_chance = min(95, max(20, 70 + (self.agility - target.agility) / 2))
        hit = random.random() * 100 < hit_chance

        if not hit:
            return 0, False, f"{self.name}的攻击未命中!"

        # 暴击检查
        crit = random.random() * 100 < self.crit_rate

        # 计算伤害
        damage_multiplier = 2.0 if crit else 1.0
        base_damage = self.attack * damage_multiplier
        damage = max(1, int(base_damage - target.defense * 0.6))

        # 应用伤害
        target.take_damage(damage)

        return damage, crit, f"{self.name}{'暴击' if crit else '命中'}{target.name}，造成{damage}点伤害!"

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def die(self):
        self.alive = False
        self.health = 0

    def update(self):
        super().update()

        if self.alive:
            # 更新技能冷却
            for skill in self.skills:
                skill.update()

            # 更新状态效果
            self.update_status_effects()

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        super().draw(surface, camera_offset_x, camera_offset_y)

        # 绘制血条
        if self.alive:
            health_width = int((self.health / self.max_health) * TILE_SIZE)
            health_height = 5

            pygame.draw.rect(surface, COLOR_RED,
                             (self.rect.x - camera_offset_x,
                              self.rect.y - camera_offset_y - health_height - 2,
                              TILE_SIZE, health_height))

            pygame.draw.rect(surface, COLOR_GREEN,
                             (self.rect.x - camera_offset_x,
                              self.rect.y - camera_offset_y - health_height - 2,
                              health_width, health_height))


# ---------- 武器类 ----------
class Weapon:
    def __init__(self, name, weapon_type, attack, crit_rate,
                 range_value, multiple, durability=100, skills=None):
        self.name = name
        self.weapon_type = weapon_type
        self.attack = attack
        self.crit_rate = crit_rate
        self.range = range_value
        self.multiple = multiple
        self.durability = durability
        self.max_durability = durability
        self.skills = skills if skills else []
        self.sprite = None
        self.equipped = False
        self.value = int(attack * 10 + crit_rate * 5 + range_value * 3 + multiple * 50)

    def __str__(self):
        return (f"{self.name} - 类型: {self.weapon_type.name}, 攻击: {self.attack}, "
                f"暴击: {self.crit_rate}%, 范围: {self.range}, 倍率: {self.multiple}x")


# ---------- 护甲类 ----------
class Armor:
    def __init__(self, name, armor_type, defense, agility_mod, multiple, durability=100, mana_mod=0):
        self.name = name
        self.armor_type = armor_type
        self.defense = defense
        self.agility_mod = agility_mod
        self.multiple = multiple
        self.mana_mod = mana_mod
        self.durability = durability
        self.max_durability = durability
        self.sprite = None
        self.equipped = False
        self.value = int(defense * 15 + abs(agility_mod) * 10 + abs(mana_mod) * 5 + multiple * 50)

    def __str__(self):
        return (f"{self.name} - 类型: {self.armor_type.name}, 防御: {self.defense}, "
                f"敏捷: {self.agility_mod:+.1f}, 倍率: {self.multiple}x")


# ---------- 药水类 ----------
class Potion:
    def __init__(self, name, potion_type, effect_value,
                 duration=0, description=""):
        self.name = name
        self.potion_type = potion_type
        self.effect_value = effect_value
        self.duration = duration
        self.description = description
        self.sprite = None
        self.value = effect_value * (2 + duration // 3)

    def use(self, target):
        if self.potion_type == ItemType.HP_SMALL or self.potion_type == ItemType.HP_LARGE:
            target.heal(self.effect_value)
            return f"{target.name}恢复了{self.effect_value}点生命值"

        # 可以实现更多药水类型

        return "什么都没发生"

    def __str__(self):
        return f"{self.name} - {self.description}"


# ---------- 物品工厂 ----------
class ItemFactory:
    @staticmethod
    def create_weapons():
        weapons = []

        # 从EQUIPMENT_TYPES创建武器
        for key, data in EQUIPMENT_TYPES.items():
            if data["type"] == "weapon":
                weapon = Weapon(
                    name=data["name"],
                    weapon_type=WeaponType.SWORD,  # 可以根据名称判断类型
                    attack=data["atk"],
                    crit_rate=10,  # 默认暴击率
                    range_value=1,  # 默认范围
                    multiple=data["multiple"],
                    durability=data["durability"]
                )
                weapons.append(weapon)

        return weapons

    @staticmethod
    def create_armors():
        armors = []

        # 从EQUIPMENT_TYPES创建护甲
        for key, data in EQUIPMENT_TYPES.items():
            if data["type"] == "armor":
                armor = Armor(
                    name=data["name"],
                    armor_type=ArmorType.CHESTPLATE,  # 可以根据名称判断类型
                    defense=data["def"],
                    agility_mod=0,  # 默认敏捷修正
                    multiple=data["multiple"],
                    durability=data["durability"]
                )
                armors.append(armor)

        return armors

    @staticmethod
    def create_potions():
        potions = [
            Potion("小型生命药水", ItemType.HP_SMALL, 100, 0, "恢复100点生命值"),
            Potion("大型生命药水", ItemType.HP_LARGE, 300, 0, "恢复300点生命值")
        ]
        return potions


# ---------- 库存系统 ----------
class Inventory:
    def __init__(self, capacity=20):
        self.capacity = capacity
        self.items = []
        self.gold = 0

    def add_item(self, item):
        if len(self.items) >= self.capacity:
            return False, "背包已满"

        self.items.append(item)
        return True, f"获得了{item.name}"

    def remove_item(self, item_index):
        if item_index < 0 or item_index >= len(self.items):
            return False, "无效的物品索引"

        item = self.items.pop(item_index)
        return True, f"移除了{item.name}"

    def use_item(self, item_index, target):
        if item_index < 0 or item_index >= len(self.items):
            return False, "无效的物品索引"

        item = self.items[item_index]
        if hasattr(item, 'use'):
            result = item.use(target)
            self.items.pop(item_index)
            return True, result
        else:
            return False, "此物品无法直接使用"

    def can_afford(self, price):
        return self.gold >= price

    def spend(self, price):
        if not self.can_afford(price):
            return False
        self.gold -= price
        return True

    def __str__(self):
        return f"背包: {len(self.items)}/{self.capacity}件物品, 金币: {self.gold}"


# ---------- 玩家类 ----------
class Player(CombatEntity):
    def __init__(self, name, x, y):
        super().__init__(name, x, y, EntityType.PLAYER,
                         max_health=100, attack=10, defense=5,
                         crit_rate=5, agility=10, mana=50)

        self.inventory = Inventory()
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100

        # 装备槽
        self.equipped_weapon = None
        self.equipped_armor = None

        # 初始技能
        self.add_skill(ALL_SKILLS["fireball"])

        # 路径显示相关
        self.path = []
        self.path_timer = 0
        self.lightning_path_red = LIGHTNINGEFFECT_RED
        self.lightning_path_yellow = LIGHTNINGEFFECT_YELLOW
        self.lightning_path_blue = LIGHTNINGEFFECT_BLUE

        # 状态效果
        self.debuffs = {
            'frozen_area': None,  # 冰冻区域
            'poison_end': 0,  # 中毒结束时间
            'stun_end': 0,  # 眩晕结束时间
            'paralyze_end': 0,  # 麻痹结束时间
            'in_corrosion': False,  # 是否在腐蚀区域
            'red_fear': False,  # 红色恐惧状态
            'blue_fear': False,  # 蓝色恐惧状态
            'gold_fear': False  # 金色恐惧状态
        }

    def move(self, dx, dy, world_map):
        new_x = self.x + dx
        new_y = self.y + dy

        # 设置方向
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.DOWN
        elif dy < 0:
            self.direction = Direction.UP

        # 检查新位置是否可通行
        if world_map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True

        return False

    def equip_weapon(self, weapon):
        # 卸下当前武器
        if self.equipped_weapon:
            self.attack -= self.equipped_weapon.attack
            self.crit_rate -= self.equipped_weapon.crit_rate

        # 装备新武器
        self.equipped_weapon = weapon
        self.attack += weapon.attack
        self.crit_rate += weapon.crit_rate

    def equip_armor(self, armor):
        # 卸下当前护甲
        if self.equipped_armor:
            self.defense -= self.equipped_armor.defense
            self.agility -= self.equipped_armor.agility_mod

        # 装备新护甲
        self.equipped_armor = armor
        self.defense += armor.defense
        self.agility += armor.agility_mod

        # 更新路径效果
        self.lightning_path_red = False
        self.lightning_path_yellow = False
        self.lightning_path_blue = False

        if armor:
            if "红闪电甲" in armor.name:
                self.lightning_path_red = True
            elif "黄闪电甲" in armor.name:
                self.lightning_path_yellow = True
            elif "蓝闪电甲" in armor.name:
                self.lightning_path_blue = True

    def gain_exp(self, amount):
        self.exp += amount

        # 检查升级
        while self.exp >= self.exp_to_next_level:
            self.level_up()

    def level_up(self):
        self.exp -= self.exp_to_next_level
        self.level += 1

        # 提升属性
        self.max_health += 10
        self.health = self.max_health
        self.max_mana += 5
        self.mana = self.max_mana
        self.base_attack += 2
        self.attack += 2
        self.base_defense += 1
        self.defense += 1

        # 下一级所需经验
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)

    def update(self):
        super().update()

        # 法力恢复
        if self.mana < self.max_mana:
            self.mana = min(self.max_mana, self.mana + 1)

        # 更新路径计时器
        if self.path_timer > 0:
            self.path_timer -= 1

    def reduce_equipment_durability(self):
        # 减少装备耐久度
        if self.equipped_weapon:
            self.equipped_weapon.durability -= 1
            if self.equipped_weapon.durability <= 0:
                self.attack -= self.equipped_weapon.attack
                self.crit_rate -= self.equipped_weapon.crit_rate
                self.equipped_weapon = None

        if self.equipped_armor:
            self.equipped_armor.durability -= 1
            if self.equipped_armor.durability <= 0:
                self.defense -= self.equipped_armor.defense
                self.agility -= self.equipped_armor.agility_mod
                self.equipped_armor = None

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        # 基本绘制
        super().draw(surface, camera_offset_x, camera_offset_y)

        # 如果使用基础绘制，需要自定义玩家外观
        px = (self.x * TILE_SIZE) - camera_offset_x
        py = (self.y * TILE_SIZE) - camera_offset_y

        # ------ 基础造型参数 ------
        body_color = (30, 144, 255)  # 盔甲蓝色
        skin_color = (255, 218, 185)  # 肤色
        boots_color = (105, 105, 105)  # 靴子深灰
        sword_color = (192, 192, 192)  # 剑银灰色
        sword_highlights = (230, 230, 230)

        # ------ 头部绘制 ------
        head_radius = TILE_SIZE // 6
        pygame.draw.circle(surface, skin_color,
                           (px + TILE_SIZE // 2, py + head_radius + 2), head_radius)
        # 面部特征
        pygame.draw.arc(surface, (0, 0, 0),
                        (px + TILE_SIZE // 2 - head_radius, py + 2,
                         head_radius * 2, head_radius * 2),
                        math.radians(200), math.radians(340), 1)  # 微笑曲线

        # ------ 身体躯干 ------
        torso_height = TILE_SIZE // 3
        torso_rect = (px + TILE_SIZE // 4, py + head_radius * 2 + 4,
                      TILE_SIZE // 2, torso_height)
        pygame.draw.rect(surface, body_color, torso_rect)

        # ------ 腿部造型 ------
        leg_width = TILE_SIZE // 8
        # 左腿
        pygame.draw.rect(surface, boots_color,
                         (px + TILE_SIZE // 2 - leg_width * 2, py + torso_height + head_radius * 2 + 4,
                          leg_width, TILE_SIZE // 3))
        # 右腿
        pygame.draw.rect(surface, boots_color,
                         (px + TILE_SIZE // 2 + leg_width, py + torso_height + head_radius * 2 + 4,
                          leg_width, TILE_SIZE // 3))

        # ------ 手臂动态造型 ------
        arm_length = TILE_SIZE // 3
        # 左臂（握剑姿势）
        pygame.draw.line(surface, skin_color,
                         (px + TILE_SIZE // 4, py + head_radius * 2 + torso_height // 2),
                         (px + TILE_SIZE // 4 - arm_length // 2,
                          py + head_radius * 2 + torso_height // 2 + arm_length // 2),
                         3)
        # 右臂（自然下垂）
        pygame.draw.line(surface, skin_color,
                         (px + TILE_SIZE - TILE_SIZE // 4, py + head_radius * 2 + torso_height // 2),
                         (px + TILE_SIZE - TILE_SIZE // 4 + arm_length // 3,
                          py + head_radius * 2 + torso_height // 2 + arm_length // 3),
                         3)

        # ------ 精致长剑造型 ------
        sword_x = px + TILE_SIZE // 4 - arm_length // 2  # 剑柄起始位置
        sword_y = py + head_radius * 2 + torso_height // 2 + arm_length // 2

        # 剑刃（带渐细效果）
        blade_points = [
            (sword_x - 1, sword_y),
            (sword_x - TILE_SIZE // 3, sword_y - TILE_SIZE // 2),  # 剑尖
            (sword_x + 1, sword_y),
            (sword_x + TILE_SIZE // 8, sword_y + TILE_SIZE // 8)
        ]
        pygame.draw.polygon(surface, sword_color, blade_points)

        # 剑柄装饰
        hilt_rect = (sword_x - 2, sword_y - 3, 4, 6)
        pygame.draw.rect(surface, (139, 69, 19), hilt_rect)  # 木柄颜色
        pygame.draw.circle(surface, (255, 215, 0),  # 宝石装饰
                           (sword_x, sword_y - 1), 2)

        # 剑刃高光
        pygame.draw.line(surface, sword_highlights,
                         (sword_x - TILE_SIZE // 4, sword_y - TILE_SIZE // 3),
                         (sword_x - TILE_SIZE // 8, sword_y - TILE_SIZE // 6), 1)

        # ------ 盔甲细节 ------
        # 肩甲
        pygame.draw.arc(surface, (255, 255, 255),
                        (px + TILE_SIZE // 4 - 2, py + head_radius * 2 + 2,
                         TILE_SIZE // 2 + 4, torso_height // 2),
                        math.radians(180), math.radians(360), 2)
        # 腰带
        pygame.draw.rect(surface, (139, 69, 19),
                         (px + TILE_SIZE // 4, py + head_radius * 2 + torso_height - 3,
                          TILE_SIZE // 2, 3))


# ---------- 怪物类 ----------
class Monster(CombatEntity):
    def __init__(self, data, x, y, floor_level=1):
        # 从怪物数据计算属性
        name = data["name"]
        max_health = self.scale_stat(data["HP"], floor_level)
        attack = self.scale_stat(data["ATK"], floor_level)
        defense = self.scale_stat(data["DEF"], floor_level)

        super().__init__(name, x, y, EntityType.MONSTER,
                         max_health, attack, defense, 5, data["speed"], 0)

        self.size = data["size"]
        self.coin = self.scale_stat(data["coin"], floor_level)
        self.level = data["level"]
        self.speed = data["speed"]
        self.move_counter = 0
        self.exp_reward = int(max_health * 0.2)

        # 特殊技能和属性
        self.setup_special_abilities(data, floor_level)

    def scale_stat(self, base_value, floor_level):
        """根据楼层等级缩放属性值"""
        return int(base_value * (1 + 0.15 * floor_level) * (0.8 + 0.4 * random.random()))

    def setup_special_abilities(self, data, floor_level):
        """设置怪物特殊能力"""
        if "魔王" in self.name:
            self.skill_cd = 0
            self.crack_cd = 10  # 地裂冷却
            self.crack_range = 4
            self.crack_damage = self.scale_stat(data["ATK"], floor_level)
            self.stun_duration = 3

        elif "冰霜巨龙" in self.name:
            self.skill_cd = 0
            self.breath_cd = 8
            self.breath_range = 6
            self.ice_damage = 1.5 * self.scale_stat(data["ATK"], floor_level)

        elif "魔法师" in self.name:
            self.skill_cd = 0
            self.magic_cd = 5
            self.magic_range = 4

        elif "电击球" in self.name:
            self.skill_cd = 0
            self.electric_cd = 1
            self.electric_range = 4

        elif "火焰领主" in self.name:
            self.skill_cd = 0
            self.strike_cd = 1.7
            self.strike_range = 9
            self.strike_damage = self.scale_stat(data["ATK"], floor_level) * 2

    def update(self, player, world_map, dt):
        super().update()

        if not self.alive or not self.can_act:
            return "", False, 0

        # 更新移动计数器
        self.move_counter += 1
        if self.move_counter < self.speed:
            return "", False, 0

        # 重置计数器
        self.move_counter = 0

        # 计算与玩家的距离
        distance = abs(player.x - self.x) + abs(player.y - self.y)

        # 使用特殊技能
        if hasattr(self, 'skill_cd'):
            self.skill_cd -= dt

            # 电击球技能
            if "电击球" in self.name and distance <= self.electric_range and self.skill_cd <= 0:
                damage = random.randint(self.attack, self.attack * 2)
                player.take_damage(max(damage - player.defense, 0))
                player.debuffs['paralyze_end'] = pygame.time.get_ticks() + 1000
                self.skill_cd = self.electric_cd
                return f"电击球电击造成{max(damage - player.defense, 0)}伤害！", True, ElectricEffect(player.x, player.y)

            # 魔王技能
            elif "魔王" in self.name and distance <= self.crack_range and self.skill_cd <= 0:
                player.take_damage(self.crack_damage)
                player.debuffs['stun_end'] = pygame.time.get_ticks() + self.stun_duration * 1000
                self.skill_cd = self.crack_cd
                return f"魔王使用地裂技能，造成{self.crack_damage}点伤害！", True, CrackEffect(player.x, player.y, 3)

            # 冰霜巨龙技能
            elif "冰霜巨龙" in self.name and distance <= self.breath_range and self.skill_cd <= 0:
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.hypot(dx, dy)
                if dist == 0:
                    direction = (1, 0)
                else:
                    direction = (dx / dist, dy / dist)

                mouth_pos = (self.x * TILE_SIZE + TILE_SIZE * 1.5, self.y * TILE_SIZE + TILE_SIZE // 2)
                player.take_damage(self.ice_damage)
                self.skill_cd = self.breath_cd
                return f"冰霜巨龙使用冰霜吐息，造成{self.ice_damage}点伤害！", True, IceBreathEffect(mouth_pos, direction)

            # 魔法师技能
            elif "魔法师" in self.name and distance <= self.magic_range and self.skill_cd <= 0:
                start = (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2)
                target = (player.x * TILE_SIZE + TILE_SIZE // 2, player.y * TILE_SIZE + TILE_SIZE // 2)
                self.skill_cd = self.magic_cd
                return "魔法师发射了毒液法术！", True, PoisonBall(start, target)

            # 火焰领主技能
            elif "火焰领主" in self.name and distance <= self.strike_range and self.skill_cd <= 0:
                player.take_damage(self.strike_damage)
                self.skill_cd = self.strike_cd
                if "纯" in self.name:
                    return f"纯火焰领主发动纯青熔岩重击，造成{self.strike_damage}伤害！", True, BlueFireStrikeEffect(
                        player.x, player.y, 3)
                else:
                    return f"火焰领主发动熔岩重击，造成{self.strike_damage}伤害！", True, FireStrikeEffect(player.x,
                                                                                                         player.y, 3)

        # 移动逻辑
        if distance <= MONSTER_DISTANCE:
            # 确定向玩家移动的方向
            dx = 0
            dy = 0

            if self.x < player.x:
                dx = 1
            elif self.x > player.x:
                dx = -1

            if self.y < player.y:
                dy = 1
            elif self.y > player.y:
                dy = -1

            # 尝试移动，优先移动距离更远的轴
            if abs(self.x - player.x) > abs(self.y - player.y):
                if not self.move(dx, 0, world_map):
                    self.move(0, dy, world_map)
            else:
                if not self.move(0, dy, world_map):
                    self.move(dx, 0, world_map)

            # 如果与玩家相邻，进行攻击
            if distance <= 1.5:
                damage, crit, message = self.attack_target(player)
                return message, False, 0

        return "", False, 0

    def move(self, dx, dy, world_map):
        new_x = self.x + dx
        new_y = self.y + dy

        # 设置方向
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.DOWN
        elif dy < 0:
            self.direction = Direction.UP

        # 检查新位置是否可通行
        can_move = True
        for ix in range(self.size[0]):
            for iy in range(self.size[1]):
                nx = new_x + ix
                ny = new_y + iy
                if not world_map.is_walkable(nx, ny):
                    can_move = False
                    break
            if not can_move:
                break

        if can_move:
            self.x = new_x
            self.y = new_y
            return True

        return False

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        # 基本绘制
        if not self.alive:
            return

        # 根据怪物类型绘制不同外观
        x = (self.x * TILE_SIZE) - camera_offset_x
        y = (self.y * TILE_SIZE) - camera_offset_y
        w = self.size[0] * TILE_SIZE
        h = self.size[1] * TILE_SIZE

        # 绘制血条
        health_width = int((self.health / self.max_health) * w)
        health_height = 5
        pygame.draw.rect(surface, COLOR_RED, (x, y - health_height - 2, w, health_height))
        pygame.draw.rect(surface, COLOR_GREEN, (x, y - health_height - 2, health_width, health_height))

        # 根据怪物类型选择绘制方法
        if "蝙蝠" in self.name:
            self.draw_bat(surface, x, y)
        elif "骷髅" in self.name:
            self.draw_skeleton(surface, x, y)
        elif "史莱姆" in self.name:
            self.draw_slime(surface, x, y)
        elif "腐蚀怪" in self.name:
            self.draw_corrosion_monster(surface, x, y)
        elif "魔法师" in self.name:
            self.draw_magician(surface, x, y)
        elif "魔王" in self.name:
            self.draw_monster_boss(surface, x, y)
        elif "火焰骑士" in self.name:
            self.draw_fire_knight(surface, x, y)
        elif "普通巨龙" in self.name:
            self.draw_dragon(surface, x, y)
        elif "电击球" in self.name:
            self.draw_lightning_ball(surface, x, y)
        elif "冰霜巨龙" in self.name:
            self.draw_ice_dragon(surface, x, y)
        elif "闪电" in self.name:
            self.draw_lightning_boss(surface, x, y)
        elif "火焰领主" in self.name:
            self.draw_fire_lord(surface, x, y)
        else:
            # 默认绘制
            pygame.draw.rect(surface, COLOR_MONSTER, (x, y, w, h))

    # 各种怪物的绘制方法
    def draw_bat(self, surface, x, y):
        body_color = (54, 54, 54)  # 身体颜色 深灰色
        wing_color = (40, 40, 40)  # 翅膀颜色 更深的灰色
        skeleton_color = (80, 80, 80)  # 骨架颜色

        # 颜色随机反转
        if "白色" in self.name:
            body_color = tuple(255 - c for c in body_color)
            wing_color = tuple(255 - c for c in wing_color)
            skeleton_color = tuple(255 - c for c in skeleton_color)

        # 蝙蝠主体（倒挂姿态）
        head_radius = TILE_SIZE // 6
        body_width = TILE_SIZE // 3
        body_height = TILE_SIZE // 2

        # 倒挂的身体
        pygame.draw.ellipse(surface, body_color,
                            (x + TILE_SIZE // 2 - body_width // 2,
                             y + TILE_SIZE // 2 - body_height // 2,
                             body_width, body_height))

        # 头部
        pygame.draw.circle(surface, body_color,
                           (x + TILE_SIZE // 2, y + TILE_SIZE // 3),
                           head_radius)

        # 耳朵
        ear_points = [
            (x + TILE_SIZE // 2 - head_radius // 2, y + TILE_SIZE // 3 - head_radius),
            (x + TILE_SIZE // 2, y + TILE_SIZE // 3 - head_radius * 1.5),
            (x + TILE_SIZE // 2 + head_radius // 2, y + TILE_SIZE // 3 - head_radius)
        ]
        pygame.draw.polygon(surface, body_color, ear_points)

        # 翅膀（双层设计）
        # 左翼
        left_wing = [
            (x + TILE_SIZE // 4, y + TILE_SIZE // 2),
            (x + TILE_SIZE // 2 - 2, y + TILE_SIZE // 3),
            (x, y + TILE_SIZE // 4)
        ]
        pygame.draw.polygon(surface, wing_color, left_wing)
        # 右翼
        right_wing = [
            (x + 3 * TILE_SIZE // 4, y + TILE_SIZE // 2),
            (x + TILE_SIZE // 2 + 2, y + TILE_SIZE // 3),
            (x + TILE_SIZE, y + TILE_SIZE // 4)
        ]
        pygame.draw.polygon(surface, wing_color, right_wing)

        # 翅膀骨架（增加细节）
        # 左翼骨架
        pygame.draw.line(surface, skeleton_color,
                         left_wing[0], left_wing[1], 2)
        pygame.draw.line(surface, skeleton_color,
                         left_wing[1], left_wing[2], 2)
        # 右翼骨架
        pygame.draw.line(surface, skeleton_color,
                         right_wing[0], right_wing[1], 2)
        pygame.draw.line(surface, skeleton_color,
                         right_wing[1], right_wing[2], 2)

        # 眼睛（红色发光效果）
        eye_radius = 2
        pygame.draw.circle(surface, (255, 0, 0),
                           (x + TILE_SIZE // 2 - eye_radius, y + TILE_SIZE // 3 - eye_radius),
                           eye_radius)
        pygame.draw.circle(surface, (255, 0, 0),
                           (x + TILE_SIZE // 2 + eye_radius, y + TILE_SIZE // 3 - eye_radius),
                           eye_radius)

        # 阴影效果
        shadow_color = (20, 20, 20)
        pygame.draw.arc(surface, shadow_color,
                        (x + TILE_SIZE // 4, y + TILE_SIZE // 2 - 2,
                         TILE_SIZE // 2, TILE_SIZE // 4),
                        math.radians(180), math.radians(360), 2)

    def draw_skeleton(self, surface, x, y):
        # 骨骼颜色
        bone_color = (240, 240, 220)
        worn_color = (180, 180, 160)

        # 头部（带破损）
        head_center = (x + TILE_SIZE // 2, y + TILE_SIZE // 4)
        pygame.draw.circle(surface, bone_color, head_center, 10)
        # 眼部空洞
        pygame.draw.circle(surface, (30, 30, 30),
                           (head_center[0] - 4, head_center[1] - 2), 3)
        pygame.draw.circle(surface, (30, 30, 30),
                           (head_center[0] + 4, head_center[1] - 2), 3)
        # 下颚（动态开合）
        jaw_angle = math.sin(pygame.time.get_ticks() / 300) * 0.2
        jaw_points = [
            (head_center[0] - 8, head_center[1] + 5),
            (head_center[0] + 8, head_center[1] + 5),
            (head_center[0] + 6, head_center[1] + 10 + 3 * jaw_angle),
            (head_center[0] - 6, head_center[1] + 10 + 3 * jaw_angle)
        ]
        pygame.draw.polygon(surface, bone_color, jaw_points)

        # 脊椎（带破损效果）
        for i in range(5):
            seg_y = y + TILE_SIZE // 3 + i * 8
            if i % 2 == 0:
                pygame.draw.ellipse(surface, worn_color,
                                    (x + TILE_SIZE // 2 - 4, seg_y, 8, 6))
            else:
                pygame.draw.ellipse(surface, bone_color,
                                    (x + TILE_SIZE // 2 - 4, seg_y, 8, 6))

        # 肋骨（不对称破损）
        rib_points = [
            (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
            (x + TILE_SIZE // 2 + 15, y + TILE_SIZE // 2 - 10),
            (x + TILE_SIZE // 2 + 10, y + TILE_SIZE // 2 + 20),
            (x + TILE_SIZE // 2 - 15, y + TILE_SIZE // 2 + 15)
        ]
        pygame.draw.polygon(surface, bone_color, rib_points, 2)

        # 手臂
        # 右臂
        pygame.draw.line(surface, bone_color,
                         (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                         (x + TILE_SIZE, y + TILE_SIZE // 3), 4)

        # 左臂
        pygame.draw.line(surface, bone_color,
                         (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                         (x, y + TILE_SIZE // 3), 4)

        # 骨盆
        pygame.draw.arc(surface, bone_color,
                        (x + TILE_SIZE // 2 - 15, y + TILE_SIZE - 20, 30, 20),
                        math.radians(180), math.radians(360), 4)

        # 飘散的灵魂残片
        for _ in range(3):
            px = x + random.randint(10, TILE_SIZE - 10)
            py = y + random.randint(10, TILE_SIZE - 10)
            pygame.draw.circle(surface, (150, 150, 255, 100), (px, py), 2)

    def draw_slime(self, surface, x, y):
        w = self.size[0] * TILE_SIZE
        h = self.size[1] * TILE_SIZE

        # 根据不同类型设置颜色
        if "红" in self.name:
            base_color = (220, 20, 60)  # 红色
            highlight_color = (255, 99, 71)  # 番茄红
        elif "黑" in self.name:
            base_color = (35, 35, 35)  # 暗黑色
            highlight_color = (105, 105, 105)  # 暗灰色
        elif "闪光" in self.name:  # 闪光
            base_color = (50, 205, 50)
            highlight_color = (144, 238, 144)
            if random.random() < 0.6:
                base_color = (220, 20, 60)
                highlight_color = (255, 99, 71)
                if random.random() < 0.5:
                    base_color = (35, 35, 35)
                    highlight_color = (105, 105, 105)
        else:  # 普通史莱姆
            base_color = (50, 205, 50)
            highlight_color = (144, 238, 144)

        # 凝胶状身体
        body_rect = (x + 2, y + 2, w - 4, h - 4)
        pygame.draw.ellipse(surface, base_color, body_rect)

        # 高光效果
        pygame.draw.arc(surface, highlight_color, body_rect,
                        math.radians(30), math.radians(150), 2)

        # 特殊效果：黑史莱姆添加金属反光
        if "黑" in self.name:
            # 金属反光效果
            pygame.draw.line(surface, (169, 169, 169),
                             (x + w * 0.3, y + h * 0.3),
                             (x + w * 0.7, y + h * 0.7), 2)

        # 气泡效果（黑史莱姆不显示气泡）
        if "黑" not in self.name:
            for i in range(3):
                bx = x + random.randint(3, w - 6)
                by = y + random.randint(3, h - 6)
                pygame.draw.circle(surface, highlight_color, (bx, by), 1)

    def draw_corrosion_monster(self, surface, x, y):
        # 动态腐蚀肉块造型
        anim_time = pygame.time.get_ticks()
        body_color = (91, 13, 133)  # 紫黑色基底

        # 主体（动态蠕动的椭圆）
        pygame.draw.ellipse(surface, body_color,
                            (x + math.sin(anim_time / 300) * 3,
                             y + math.cos(anim_time / 250) * 2,
                             TILE_SIZE, TILE_SIZE))

        # 血色斑点（随机分布）
        for _ in range(8):
            spot_x = x + random.randint(4, 27)
            spot_y = y + random.randint(4, 27)
            pygame.draw.circle(surface, (139, 0, 0),
                               (spot_x, spot_y), random.randint(2, 4))

        # 表面蠕动效果
        for i in range(3):
            wave_y = y + TILE_SIZE // 2 + math.sin(anim_time / 200 + i) * 8
            pygame.draw.arc(surface, (70, 0, 70),
                            (x + i * 8, wave_y - 4, 16, 8),
                            math.radians(180), math.radians(360), 2)

        # 环境互动：滴落粘液
        if random.random() < 0.05:
            drop_x = x + random.randint(8, 23)
            drop_y = y + TILE_SIZE
            pygame.draw.line(surface, (139, 0, 0, 150),
                             (drop_x, drop_y), (drop_x, drop_y + 8), 3)

    def draw_magician(self, surface, x, y):
        # 长袍主体
        robe_color = (80, 0, 80)  # 深紫色
        robe_highlight = (120, 0, 120)
        pygame.draw.ellipse(surface, robe_color,
                            (x + 5, y + TILE_SIZE // 2, TILE_SIZE - 10, TILE_SIZE))

        # 魔法纹饰
        for i in range(3):
            pygame.draw.arc(surface, robe_highlight,
                            (x + i * 5, y + TILE_SIZE // 2 + i * 3,
                             TILE_SIZE - 10, TILE_SIZE - 10),
                            math.radians(0), math.radians(180), 2)

        # 悬浮法杖
        staff_x = x + TILE_SIZE // 2
        staff_y = y + TILE_SIZE // 4
        pygame.draw.line(surface, (150, 150, 150),
                         (staff_x - 15, staff_y - 5), (staff_x + 15, staff_y + 5), 5)
        # 魔法水晶
        crystal_color = (0, 200, 200)
        pygame.draw.polygon(surface, crystal_color, [
            (staff_x + 15, staff_y + 5),
            (staff_x + 25, staff_y),
            (staff_x + 15, staff_y - 5)
        ])
        # 水晶辉光
        for _ in range(5):
            px = staff_x + 20 + random.randint(-3, 3)
            py = staff_y + random.randint(-3, 3)
            pygame.draw.circle(surface, (0, 200, 200, 100), (px, py), 2)

        # 毒雾环绕
        anim_time = pygame.time.get_ticks()
        for i in range(8):
            angle = math.radians(anim_time / 10 + i * 45)
            radius = 20 + 5 * math.sin(anim_time / 200 + i)
            px = x + TILE_SIZE // 2 + radius * math.cos(angle)
            py = y + TILE_SIZE // 2 + radius * math.sin(angle)
            pygame.draw.circle(surface, (50, 200, 50, 100), (int(px), int(py)), 3)

        # 兜帽阴影
        pygame.draw.arc(surface, (30, 30, 30),
                        (x + TILE_SIZE // 4, y, TILE_SIZE // 2, TILE_SIZE // 2),
                        math.radians(180), math.radians(360), 10)

        # 发光的双眼
        pygame.draw.circle(surface, (0, 200, 200),
                           (x + TILE_SIZE // 2 - 8, y + TILE_SIZE // 3), 4)
        pygame.draw.circle(surface, (0, 200, 200),
                           (x + TILE_SIZE // 2 + 8, y + TILE_SIZE // 3), 4)

    def draw_monster_boss(self, surface, x, y):
        body_color = (30, 30, 30)  # 黑铁色基底
        trim_color = (80, 80, 80)  # 盔甲镶边
        if "圣洁" in self.name:
            body_color = tuple(255 - c for c in body_color)
            trim_color = tuple(255 - c for c in trim_color)

        # 动画参数
        anim_time = pygame.time.get_ticks()
        hammer_swing = math.sin(anim_time / 300) * 0.5  # 锤子摆动弧度
        shield_glow = abs(math.sin(anim_time / 500))  # 盾牌发光强度
        eye_glow = 100 + int(155 * abs(math.sin(anim_time / 200)))  # 眼部红光波动

        # ---- 头部系统 ----
        # 带角巨盔
        helmet_points = [
            (x + 15, y + 8),  # 左耳
            (x + 15, y + 4),  # 左角根
            (x + 8, y - 2),  # 左角尖
            (x + 24, y - 2),  # 右角尖
            (x + 17, y + 4),  # 右角根
            (x + 17, y + 8)  # 右耳
        ]
        pygame.draw.polygon(surface, (60, 60, 60), helmet_points)

        # 面甲细节
        pygame.draw.arc(surface, (100, 100, 100),
                        (x + 10, y + 5, 12, 15),
                        math.radians(220), math.radians(320), 3)  # 面甲开口
        # 发光红眼
        pygame.draw.circle(surface, (eye_glow, 0, 0),
                           (x + 16, y + 12), 3)

        # ---- 肩甲系统 ----
        # 左肩甲（带尖刺）
        left_pauldron = [
            (x + 2, y + 18),
            (x + 8, y + 22),
            (x + 2, y + 26),
            (x - 4, y + 22),
            (x + 2, y + 18)
        ]
        pygame.draw.polygon(surface, body_color, left_pauldron)
        pygame.draw.line(surface, trim_color,
                         (x + 2, y + 18), (x + 8, y + 22), 2)

        # 右肩甲（带恶魔浮雕）
        pygame.draw.rect(surface, body_color,
                         (x + 22, y + 18, 8, 10))
        # 浮雕细节
        pygame.draw.line(surface, trim_color,
                         (x + 24, y + 20), (x + 26, y + 24), 2)
        pygame.draw.line(surface, trim_color,
                         (x + 26, y + 24), (x + 28, y + 20), 2)

        # ---- 身体主装甲 ----
        # 胸甲主体
        pygame.draw.rect(surface, body_color,
                         (x + 10, y + 15, 12, 20))
        # 装甲接缝
        for i in range(3):
            y_pos = y + 17 + i * 6
            pygame.draw.line(surface, trim_color,
                             (x + 10, y_pos), (x + 22, y_pos), 1)

        # 中央符文
        rune_points = [
            (x + 16, y + 18), (x + 18, y + 20),
            (x + 16, y + 22), (x + 14, y + 20)
        ]
        pygame.draw.polygon(surface, (200, 0, 0), rune_points)

        # ---- 毁灭重锤 ----
        # 锤柄（带动态摆动）
        hammer_length = 25
        hammer_angle = math.radians(30 + hammer_swing * 15)
        hammer_base = (x + 28, y + 28)  # 右手位置
        hammer_head = (
            hammer_base[0] + math.cos(hammer_angle) * hammer_length,
            hammer_base[1] + math.sin(hammer_angle) * hammer_length
        )

        # 锤柄
        pygame.draw.line(surface, (50, 50, 50),
                         hammer_base, hammer_head, 5)

        # 锤头（带尖刺）
        pygame.draw.circle(surface, (60, 60, 60),
                           hammer_head, 10)
        # 尖刺
        for angle in [0, 90, 180, 270]:
            spike_end = (
                hammer_head[0] + math.cos(math.radians(angle)) * 15,
                hammer_head[1] + math.sin(math.radians(angle)) * 15
            )
            pygame.draw.line(surface, (80, 80, 80),
                             hammer_head, spike_end, 3)

        # 锤头裂纹
        pygame.draw.line(surface, (30, 30, 30),
                         (hammer_head[0] - 5, hammer_head[1] - 5),
                         (hammer_head[0] + 5, hammer_head[1] + 5), 2)

        # ---- 魔能护盾 ----
        shield_size = 40 * shield_glow
        shield_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(shield_surface, (100, 0, 0, 100),
                            (20 - shield_size // 2, 20 - shield_size // 2,
                             shield_size, shield_size))
        surface.blit(shield_surface, (x - 10, y - 10))

        # ---- 环境互动 ----
        # 地面裂纹
        pygame.draw.arc(surface, (60, 60, 60),
                        (x + 5, y + 35, 20, 10),
                        math.radians(180), math.radians(360), 3)
        # 环绕黑雾
        for i in range(3):
            fog_x = x + random.randint(-5, 35)
            fog_y = y + random.randint(-5, 35)
            pygame.draw.circle(surface, (30, 30, 30, 80),
                               (fog_x, fog_y), random.randint(3, 6))

    def draw_fire_knight(self, surface, x, y):
        anim_time = pygame.time.get_ticks()
        hammer_swing = math.sin(anim_time / 300) * 0.5  # 锤子摆动弧度
        shield_glow = abs(math.sin(anim_time / 500))  # 盾牌发光强度

        # 基础体型（1x1格子）
        body_color = (30, 30, 30)  # 暗黑基底色
        if "纯" in self.name:
            body_color = tuple(255 - c for c in body_color)
        body_rect = (x + TILE_SIZE // 4, y + TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2)
        pygame.draw.rect(surface, body_color, body_rect)

        # 方形头部（较小）
        head_size = TILE_SIZE // 4
        head_center = (x + TILE_SIZE // 2, y + TILE_SIZE // 4)
        # 头盔主体
        pygame.draw.rect(surface, (40, 40, 40),
                         (head_center[0] - head_size // 2, head_center[1] - head_size // 2,
                          head_size, head_size))
        # 眼部红光
        pygame.draw.rect(surface, (200, 0, 0),
                         (head_center[0] - head_size // 4, head_center[1] - head_size // 6,
                          head_size // 2, head_size // 3))
        # 恶魔之角
        pygame.draw.polygon(surface, (60, 60, 60), [
            (head_center[0] - head_size // 2, head_center[1] - head_size // 2),
            (head_center[0] - head_size // 3, head_center[1] - head_size),
            (head_center[0] - head_size // 6, head_center[1] - head_size // 2)
        ])

        # 深渊铠甲系统（紧凑版）
        armor_color = (60, 60, 60)
        if "纯" in self.name:
            armor_color = tuple(255 - c for c in armor_color)
        # 肩甲
        pygame.draw.rect(surface, armor_color,
                         (x + TILE_SIZE // 4, y + TILE_SIZE // 3,
                          TILE_SIZE // 2, TILE_SIZE // 6))
        # 胸甲（带恶魔浮雕）
        pygame.draw.rect(surface, armor_color,
                         (x + TILE_SIZE // 3, y + TILE_SIZE // 2,
                          TILE_SIZE // 3, TILE_SIZE // 3))
        # 浮雕细节
        pygame.draw.arc(surface, (80, 80, 80),
                        (x + TILE_SIZE // 3 + 2, y + TILE_SIZE // 2 + 2,
                         TILE_SIZE // 3 - 4, TILE_SIZE // 3 - 4),
                        math.radians(0), math.radians(180), 2)

        # 地狱重锤系统（紧凑版）
        hammer_length = TILE_SIZE // 2
        # 锤柄
        pygame.draw.line(surface, (70, 70, 70),
                         (x + TILE_SIZE // 2, y + TILE_SIZE // 2),
                         (x + TILE_SIZE // 2 + int(hammer_length * math.cos(hammer_swing)),
                          y + TILE_SIZE // 2 + int(hammer_length * math.sin(hammer_swing))), 4)
        # 锤头
        hammer_head = (x + TILE_SIZE // 2 + int(hammer_length * math.cos(hammer_swing)),
                       y + TILE_SIZE // 2 + int(hammer_length * math.sin(hammer_swing)))
        if "纯" in self.name:
            pygame.draw.circle(surface, (55, 205, 205), hammer_head, 6)
        else:
            pygame.draw.circle(surface, (200, 50, 50), hammer_head, 6)

        # 火焰粒子
        if "纯" in self.name:
            for _ in range(4):
                fx = hammer_head[0] + random.randint(-5, 5)
                fy = hammer_head[1] + random.randint(-5, 5)
                pygame.draw.circle(surface, (0, 255 - random.randint(100, 150), 255),
                                   (fx, fy), random.randint(1, 2))
        else:
            for _ in range(4):
                fx = hammer_head[0] + random.randint(-5, 5)
                fy = hammer_head[1] + random.randint(-5, 5)
                pygame.draw.circle(surface, (255, random.randint(100, 150), 0),
                                   (fx, fy), random.randint(1, 2))

        # 邪能盾牌系统（紧凑版）
        shield_center = (x + TILE_SIZE // 4, y + TILE_SIZE // 2)
        shield_size = TILE_SIZE // 4
        # 基底
        pygame.draw.polygon(surface, (80, 80, 80), [
            (shield_center[0], shield_center[1] - shield_size // 2),
            (shield_center[0] + shield_size // 2, shield_center[1]),
            (shield_center[0], shield_center[1] + shield_size // 2),
            (shield_center[0] - shield_size // 2, shield_center[1])
        ])
        # 发光符文
        rune_color = (50, 200, 50, int(200 * shield_glow))
        if "纯" in self.name:
            rune_color = tuple(255 - c for c in rune_color[:3]) + (rune_color[3],)
        pygame.draw.polygon(surface, rune_color, [
            (shield_center[0], shield_center[1] - shield_size // 4),
            (shield_center[0] + shield_size // 4, shield_center[1]),
            (shield_center[0], shield_center[1] + shield_size // 4),
            (shield_center[0] - shield_size // 4, shield_center[1])
        ], 2)

        # 地面阴影
        shadow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80),
                            (x + TILE_SIZE // 4, y + TILE_SIZE // 2,
                             TILE_SIZE // 2, TILE_SIZE // 4))
        surface.blit(shadow, (x, y))

    def draw_dragon(self, surface, x, y):
        # 动画参数
        anim_time = pygame.time.get_ticks()
        wing_angle = math.sin(anim_time / 200) * 0.3  # 翅膀摆动弧度
        flame_phase = int((anim_time % 300) / 100)  # 三阶段火焰循环
        eye_glow = abs(math.sin(anim_time / 500))  # 眼睛发光强度

        # ---- 基础体型(3x3) ----
        # 身体主骨架
        body_color = (80, 20, 30)  # 暗红色基底
        pygame.draw.ellipse(surface, body_color,
                            (x + TILE_SIZE, y + TILE_SIZE, TILE_SIZE, TILE_SIZE))  # 躯干

        # ---- 动态双翼系统 ----
        # 左翼
        left_wing = [
            (x + TILE_SIZE, y + TILE_SIZE),  # 翼根
            (x + int(TILE_SIZE * 0.5), y + int(TILE_SIZE * 0.5) + int(10 * wing_angle)),  # 翼尖
            (x + TILE_SIZE, y + TILE_SIZE * 2)
        ]
        # 右翼
        right_wing = [
            (x + TILE_SIZE * 2, y + TILE_SIZE),
            (x + int(TILE_SIZE * 2.5), y + int(TILE_SIZE * 0.5) + int(10 * wing_angle)),
            (x + TILE_SIZE * 2, y + TILE_SIZE * 2)
        ]

        # 翼膜绘制（带渐变透明）
        for wing in [left_wing, right_wing]:
            pygame.draw.polygon(surface, (150, 40, 40), wing)  # 翼膜
            pygame.draw.polygon(surface, (100, 20, 20), wing, 2)  # 翼骨

        # ---- 头部细节 ----
        # 龙头
        head_radius = TILE_SIZE // 3
        head_center = (x + TILE_SIZE * 2, y + TILE_SIZE // 2)
        pygame.draw.circle(surface, body_color, head_center, head_radius)

        # 龙眼
        eye_radius = head_radius // 3
        eye_center = (head_center[0] - eye_radius, head_center[1] - eye_radius)
        pygame.draw.circle(surface, (255, 240, 200), eye_center, eye_radius)  # 眼白
        pygame.draw.circle(surface, (200 * eye_glow, 0, 0), eye_center, eye_radius // 2)  # 瞳孔

        # 龙角
        pygame.draw.polygon(surface, (100, 80, 60), [
            (head_center[0] - head_radius, head_center[1] - head_radius),
            (head_center[0] - head_radius // 2, head_center[1] - head_radius * 2),
            (head_center[0], head_center[1] - head_radius)
        ])

        # ---- 火焰喷射系统 ----
        if flame_phase > 0:  # 脉冲式火焰
            flame_length = TILE_SIZE // 2 * (1 + 0.5 * flame_phase)
            flame_points = [
                (head_center[0], head_center[1] + head_radius),
                (head_center[0] - flame_length // 2, head_center[1] + head_radius + flame_length),
                (head_center[0] + flame_length // 2, head_center[1] + head_radius + flame_length)
            ]
            pygame.draw.polygon(surface, (255, 80 + flame_phase * 50, 0), flame_points)

        # ---- 尾部细节 ----
        tail_points = [
            (x + TILE_SIZE, y + TILE_SIZE * 2),
            (x + TILE_SIZE // 2, y + TILE_SIZE * 3),
            (x + TILE_SIZE * 1.5, y + TILE_SIZE * 3)
        ]
        pygame.draw.polygon(surface, body_color, tail_points)

        # ---- 地面阴影 ----
        shadow = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 3), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80),
                            (x + TILE_SIZE // 2, y + TILE_SIZE * 2, TILE_SIZE * 2, TILE_SIZE // 2))
        surface.blit(shadow, (x, y))

    def draw_ice_dragon(self, surface, x, y):
        # 动画参数
        anim_time = pygame.time.get_ticks()
        wing_angle = math.sin(anim_time / 200) * 0.3  # 翅膀摆动弧度
        breath_phase = int((anim_time % 400) / 100)  # 四阶段冰霜呼吸循环
        eye_glow = abs(math.sin(anim_time / 500))  # 眼睛发光强度

        # ---- 基础体型(3x3) ----
        # 身体主骨架
        body_color = (70, 130, 180)  # 钢蓝色基底
        pygame.draw.ellipse(surface, body_color,
                            (x + TILE_SIZE, y + TILE_SIZE, TILE_SIZE, TILE_SIZE))  # 躯干

        # ---- 动态双翼系统 ----
        # 左翼（覆盖冰晶）
        left_wing = [
            (x + TILE_SIZE, y + TILE_SIZE),  # 翼根
            (x + int(TILE_SIZE * 0.5), y + int(TILE_SIZE * 0.5) + int(10 * wing_angle)),  # 翼尖
            (x + TILE_SIZE, y + TILE_SIZE * 2)
        ]
        # 右翼
        right_wing = [
            (x + TILE_SIZE * 2, y + TILE_SIZE),
            (x + int(TILE_SIZE * 2.5), y + int(TILE_SIZE * 0.5) + int(10 * wing_angle)),
            (x + TILE_SIZE * 2, y + TILE_SIZE * 2)
        ]

        # 翼膜绘制（带冰晶纹理）
        for wing in [left_wing, right_wing]:
            pygame.draw.polygon(surface, (135, 206, 235), wing)  # 淡蓝色翼膜
            pygame.draw.polygon(surface, (70, 130, 180), wing, 2)  # 深蓝色翼骨
            # 添加随机冰晶
            for _ in range(6):
                ice_x = random.randint(wing[1][0] - 10, wing[1][0] + 10)
                ice_y = random.randint(wing[1][1] - 10, wing[1][1] + 10)
                pygame.draw.polygon(surface, (240, 255, 255), [
                    (ice_x, ice_y),
                    (ice_x + 3, ice_y + 2),
                    (ice_x + 1, ice_y + 5),
                    (ice_x - 2, ice_y + 3)
                ])

        # ---- 头部细节 ----
        # 龙头
        head_radius = TILE_SIZE // 3
        head_center = (x + TILE_SIZE * 2, y + TILE_SIZE // 2)
        pygame.draw.circle(surface, body_color, head_center, head_radius)

        # 龙眼（发光蓝眼）
        eye_radius = head_radius // 3
        eye_center = (head_center[0] - eye_radius, head_center[1] - eye_radius)
        pygame.draw.circle(surface, (240, 255, 255), eye_center, eye_radius)  # 冰白色眼白
        pygame.draw.circle(surface, (0, 191, 255, int(255 * eye_glow)), eye_center,
                           eye_radius // 2)  # 动态发光的瞳孔

        # 冰晶龙角
        pygame.draw.polygon(surface, (240, 255, 255), [
            (head_center[0] - head_radius, head_center[1] - head_radius),
            (head_center[0] - head_radius // 2, head_center[1] - head_radius * 2),
            (head_center[0], head_center[1] - head_radius)
        ])

        # ---- 冰霜呼吸特效 ----
        if breath_phase > 0:
            breath_length = TILE_SIZE * (0.5 + 0.3 * breath_phase)
            breath_points = [
                (head_center[0], head_center[1] + head_radius),
                (head_center[0] - breath_length // 2, head_center[1] + head_radius + breath_length),
                (head_center[0] + breath_length // 2, head_center[1] + head_radius + breath_length)
            ]
            # 半透明冰雾效果
            breath_surface = pygame.Surface((TILE_SIZE * 3, TILE_SIZE * 3), pygame.SRCALPHA)
            pygame.draw.polygon(breath_surface, (135, 206, 235, 150), breath_points)
            surface.blit(breath_surface, (x, y))

            # 冰锥效果
            for i in range(3):
                icicle_x = head_center[0] - breath_length // 4 + i * breath_length // 2
                icicle_y = head_center[1] + head_radius + breath_length - 10
                pygame.draw.polygon(surface, (240, 255, 255), [
                    (icicle_x, icicle_y),
                    (icicle_x + 3, icicle_y + 15),
                    (icicle_x - 3, icicle_y + 15)
                ])

        # ---- 尾部冰晶链 ----
        tail_points = [
            (x + TILE_SIZE, y + TILE_SIZE * 2),
            (x + TILE_SIZE // 2, y + TILE_SIZE * 3),
            (x + TILE_SIZE * 1.5, y + TILE_SIZE * 3)
        ]
        pygame.draw.polygon(surface, body_color, tail_points)
        # 尾部冰晶装饰
        for i in range(4):
            ice_x = x + TILE_SIZE + (i * 10)
            ice_y = y + TILE_SIZE * 2 + (i % 2) * 8
            pygame.draw.polygon(surface, (240, 255, 255), [
                (ice_x, ice_y), (ice_x + 4, ice_y + 3), (ice_x + 2, ice_y + 6), (ice_x - 2, ice_y + 4)
            ])

        # ---- 环境互动 ----
        # 地面冰霜特效
        frost_radius = TILE_SIZE // 4
        for _ in range(8):
            fx = x + random.randint(TILE_SIZE // 2, TILE_SIZE * 2)
            fy = y + random.randint(TILE_SIZE * 2, TILE_SIZE * 3)
            pygame.draw.circle(surface, (175, 238, 238, 80), (fx, fy), frost_radius // 2)
            pygame.draw.circle(surface, (240, 255, 255, 120), (fx, fy), frost_radius // 4)

    def draw_lightning_ball(self, surface, x, y):
        anim_time = pygame.time.get_ticks()
        core_color = (255, 255, 0) if (anim_time // 200) % 2 else (255, 215, 0)  # 核心颜色
        side_tact_color = (255, 255, 100)  # 随机触手颜色
        lightning_curve_color = (255, 255, 0)  # 外围电弧颜色

        if "异色" in self.name:
            core_color = (204, 0, 204)
            side_tact_color = (51, 51, 255)
            lightning_curve_color = (255, 0, 255)

        # 动态闪电核心
        pygame.draw.circle(surface, core_color,
                           (x + TILE_SIZE // 2, y + TILE_SIZE // 2), TILE_SIZE // 3)

        # 随机闪电触手
        for _ in range(6):
            angle = random.random() * math.pi * 2
            length = random.randint(8, 15)
            start = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
            end = (start[0] + math.cos(angle) * length,
                   start[1] + math.sin(angle) * length)
            pygame.draw.line(surface, side_tact_color, start, end, 2)

        # 外围电弧
        if random.random() > 0.7:
            pygame.draw.arc(surface, lightning_curve_color,
                            (x - 5, y - 5, TILE_SIZE + 10, TILE_SIZE + 10),
                            random.random() * math.pi, random.random() * math.pi, 1)

    def draw_lightning_boss(self, surface, x, y):
        """绘制闪电BOSS（支持血腥、纯青、金色三种配色）"""
        # 动态参数
        anim_time = pygame.time.get_ticks()

        # 根据BOSS名称选择配色
        if "纯青" in self.name:
            ball_colors = [(0, 191, 255), (0, 255, 255), (0, 150, 255), (0, 200, 255), (0, 100, 255), (0, 255, 200)]
        elif "金色" in self.name:
            ball_colors = [(255, 215, 0), (255, 165, 0), (255, 140, 0), (255, 200, 0), (255, 180, 0), (255, 220, 0)]
        else:  # 默认血腥闪电配色
            ball_colors = [(178, 34, 34), (139, 0, 0), (220, 20, 60), (255, 36, 0), (200, 36, 80), (150, 30, 30)]

        # 生成六个闪电球体
        lightning_balls = []
        for i in range(6):
            ball_pos = (
                x + TILE_SIZE * 1.5 + math.sin(anim_time / 200 + i) * TILE_SIZE * 1.2,
                y + TILE_SIZE * 1.5 + math.cos(anim_time / 300 + i) * TILE_SIZE * 1.2
            )
            radius = TILE_SIZE // 2.5 * abs(math.sin(anim_time / 100))
            lightning_balls.append((ball_pos, radius, ball_colors[i]))

        # 绘制闪电球体
        for i, (ball_pos, radius, color) in enumerate(lightning_balls):
            # 绘制球体核心
            pygame.draw.circle(surface, color, (int(ball_pos[0]), int(ball_pos[1])), int(radius))

            # 绘制闪电连接（仅相邻球体之间）
            next_ball = lightning_balls[(i + 1) % 6]
            self.draw_lightning_effect(surface, ball_pos, next_ball[0], 4, color)

    def draw_lightning_effect(self, surface, start, end, thickness, color):
        """绘制闪电效果，增加分叉和火花效果"""
        # 生成主路径
        main_points = []
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        segments = max(5, int(length / 10))  # 动态分段

        # 添加起点
        main_points.append(start)

        # 生成中间点
        for i in range(1, segments):
            t = i / segments
            # 基础插值
            base_x = start[0] + dx * t
            base_y = start[1] + dy * t

            # 随机偏移
            offset_range = 20 * (1 - t ** 2)
            offset_x = random.uniform(-offset_range, offset_range)
            offset_y = random.uniform(-offset_range, offset_range)

            main_points.append((int(base_x + offset_x), int(base_y + offset_y)))

        # 添加终点
        main_points.append(end)

        # 绘制主闪电
        for i in range(len(main_points) - 1):
            start_pos = main_points[i]
            end_pos = main_points[i + 1]

            # 随机变化颜色和粗细
            lthickness = random.randint(1, thickness)
            main_color = random.choice([
                color,
                (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255)),
                (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0))
            ])

            pygame.draw.line(surface, main_color, start_pos, end_pos, lthickness)

            # 偶尔添加分叉
            if random.random() < 0.3 and i < len(main_points) - 2:
                mid_point = ((start_pos[0] + end_pos[0]) // 2, (start_pos[1] + end_pos[1]) // 2)
                branch_end = (
                    mid_point[0] + random.randint(-20, 20),
                    mid_point[1] + random.randint(-20, 20)
                )

                # 绘制分叉（简化版）
                bright_color = (min(color[0] + 100, 255), min(color[1] + 100, 255), min(color[2] + 100, 255))
                pygame.draw.line(surface, bright_color, mid_point, branch_end, max(1, lthickness - 1))

    def draw_fire_lord(self, surface, x, y):
        anim_time = pygame.time.get_ticks()

        # 主体火焰核心
        if "纯" in self.name:
            core_color = (0, 155 - int(100 * math.sin(anim_time / 300)), 205 - int(50 * (-math.sin(anim_time / 300))))
        else:
            core_color = (255, 100 + int(100 * math.sin(anim_time / 300)), 50 + int(50 * (-math.sin(anim_time / 300))))

        core_pos = (x + TILE_SIZE * 1.85, y + TILE_SIZE * 1.5)
        pygame.draw.circle(surface, core_color, core_pos, 20)

        # 动态火焰轨道
        period = 5
        for i in range(period):
            if "纯" in self.name:
                flame_color = (5,
                               155 - int(100 * math.sin(anim_time / 300 + 2 * i * math.pi / period)),
                               205 - int(50 * (-math.cos(anim_time / 400 + 2 * i * math.pi / period))))
            else:
                flame_color = (250,
                               100 + int(100 * math.sin(anim_time / 300 + 2 * i * math.pi / period)),
                               50 + int(50 * (-math.cos(anim_time / 400 + 2 * i * math.pi / period))))

            flame_pos = (
            x + TILE_SIZE * 1.85 + int(TILE_SIZE * 0.9 * math.sin(anim_time / 300 + 2 * i * math.pi / period)),
            y + TILE_SIZE * 1.5 + int(TILE_SIZE * 0.9 * math.cos(anim_time / 200 + 2 * i * math.pi / period)))

            pygame.draw.circle(surface, flame_color, flame_pos, 5)

        # 头部火焰
        length_vertical = 0.45 * TILE_SIZE
        length_horizontal = 0.12 * TILE_SIZE

        flame_points = [
            (x + TILE_SIZE * 1.85 - length_horizontal, y + TILE_SIZE * 1.5),
            (x + TILE_SIZE * 1.85, y + TILE_SIZE * 1.5 + length_vertical),
            (x + TILE_SIZE * 1.85 + length_horizontal, y + TILE_SIZE * 1.5),
            (x + TILE_SIZE * 1.85, y + TILE_SIZE * 1.5 - length_vertical)
        ]

        if "纯" in self.name:
            pygame.draw.polygon(surface, (0, 100 - int(100 * math.sin(anim_time / 300)), 100), flame_points)
        else:
            pygame.draw.polygon(surface, (255, 155 + int(100 * math.sin(anim_time / 300)), 155), flame_points)

        # 双手火焰
        for i in range(2):
            hand_x = x + (100 if i else 20)
            for j in range(3):
                angle = anim_time / 200 + i * 180 + j * 30
                px = hand_x + math.cos(math.radians(angle)) * 30
                py = y + 80 + math.sin(math.radians(angle * 2)) * 30
                size = 15 - j * 4

                if "纯" in self.name:
                    pygame.draw.circle(surface, (0, 155 - j * 50, 255), (int(px), int(py)), size)
                else:
                    pygame.draw.circle(surface, (255, 100 + j * 50, 0), (int(px), int(py)), size)


# ---------- 物品类 ----------
class Item(Entity):
    def __init__(self, name, item_type, x, y, data=None):
        super().__init__(name, x, y, EntityType.ITEM)
        self.item_type = item_type
        self.data = data  # 存储物品详细数据
        self.value = 0

        # 根据数据初始化物品属性
        if data:
            if "value" in data:
                self.value = data["value"]
            elif item_type == ItemType.CHEST:
                self.value = random.randint(10, 50)  # 宝箱价值
            elif item_type in [ItemType.HP_SMALL, ItemType.HP_LARGE]:
                self.value = 20 if item_type == ItemType.HP_SMALL else 50
            elif item_type in [ItemType.ATK_GEM, ItemType.DEF_GEM]:
                self.value = 30

    def use(self, player):
        if self.item_type == ItemType.CHEST:
            coin_gain = self.value
            player.inventory.gold += coin_gain
            return f"获得了{coin_gain}金币"

        elif self.item_type == ItemType.HP_SMALL:
            heal_amount = 100 * player.level
            player.health = min(player.health + heal_amount, player.max_health)
            return f"恢复了{heal_amount}点生命值"

        elif self.item_type == ItemType.HP_LARGE:
            heal_amount = 300 * player.level
            player.health = min(player.health + heal_amount, player.max_health)
            return f"恢复了{heal_amount}点生命值"

        elif self.item_type == ItemType.ATK_GEM:
            gain = random.randint(1, 4) * player.level
            player.base_attack += gain
            player.attack += gain
            return f"攻击力增加了{gain}点"

        elif self.item_type == ItemType.DEF_GEM:
            gain = random.randint(1, 4) * player.level
            player.base_defense += gain
            player.defense += gain
            return f"防御力增加了{gain}点"

        elif self.data and "type" in self.data:
            if self.data["type"] == "weapon":
                player.equip_weapon(self)
                return f"装备了{self.name}"

            elif self.data["type"] == "armor":
                player.equip_armor(self)
                return f"装备了{self.name}"

        return "无法使用此物品"

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        x = (self.x * TILE_SIZE) - camera_offset_x
        y = (self.y * TILE_SIZE) - camera_offset_y

        # 根据物品类型绘制不同图标
        if self.item_type == ItemType.CHEST:
            self.draw_chest(surface, x, y)
        elif self.item_type in [ItemType.HP_SMALL, ItemType.HP_LARGE]:
            self.draw_potion(surface, x, y)
        elif self.item_type in [ItemType.ATK_GEM, ItemType.DEF_GEM]:
            self.draw_gem(surface, x, y)
        elif self.data and "type" in self.data:
            if self.data["type"] == "weapon":
                self.draw_weapon(surface, x, y)
            elif self.data["type"] == "armor":
                self.draw_armor(surface, x, y)
        else:
            # 默认绘制
            pygame.draw.rect(surface, COLOR_YELLOW, (x, y, TILE_SIZE, TILE_SIZE))

    def draw_chest(self, surface, x, y):
        # 动画参数
        anim_time = pygame.time.get_ticks()
        lid_offset = int(2 * math.sin(anim_time / 300))  # 箱盖微微浮动
        gem_glow = abs(math.sin(anim_time / 200)) * 255  # 宝石发光强度

        # ---- 箱体主体 ----
        # 木质箱体
        pygame.draw.rect(surface, (101, 67, 33),
                         (x + 4, y + 4 + lid_offset, TILE_SIZE - 8, TILE_SIZE - 8),
                         border_radius=4)
        # 木质纹理
        for i in range(3):
            line_y = y + 8 + i * 8 + lid_offset
            pygame.draw.line(surface, (81, 53, 28),
                             (x + 6, line_y), (x + TILE_SIZE - 6, line_y), 2)

        # ---- 金属包角 ----
        metal_color = (198, 155, 93)  # 古铜色
        # 四角装饰
        corners = [
            (x + 2, y + 2), (x + TILE_SIZE - 8, y + 2),
            (x + 2, y + TILE_SIZE - 8), (x + TILE_SIZE - 8, y + TILE_SIZE - 8)
        ]
        for cx, cy in corners:
            # 金属浮雕
            pygame.draw.polygon(surface, metal_color, [
                (cx, cy), (cx + 6, cy), (cx + 6, cy + 3), (cx + 3, cy + 6), (cx, cy + 6)
            ])
            # 高光
            pygame.draw.line(surface, (230, 200, 150),
                             (cx + 1, cy + 1), (cx + 5, cy + 1), 2)

        # ---- 锁具系统 ----
        lock_x, lock_y = x + TILE_SIZE // 2, y + TILE_SIZE // 2 + lid_offset
        # 锁体
        pygame.draw.rect(surface, (60, 60, 60),
                         (lock_x - 6, lock_y - 4, 12, 8), border_radius=2)
        # 锁孔
        pygame.draw.line(surface, (120, 120, 120),
                         (lock_x, lock_y - 2), (lock_x, lock_y + 2), 3)
        # 动态锁环
        pygame.draw.circle(surface, metal_color,
                           (lock_x, lock_y - 8), 4, width=2)

        # ---- 宝石装饰 ----
        gem_positions = [
            (x + 10, y + 10), (x + TILE_SIZE - 14, y + 10),
            (x + 10, y + TILE_SIZE - 14), (x + TILE_SIZE - 14, y + TILE_SIZE - 14)
        ]
        for gx, gy in gem_positions:
            # 宝石底座
            pygame.draw.circle(surface, (50, 50, 50), (gx, gy), 5)
            # 动态发光宝石
            pygame.draw.circle(surface,
                               (255, 215, 0, int(gem_glow)),
                               (gx, gy), 3)

        # ---- 环境光效 ----
        # 底部阴影
        shadow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50),
                            (x, y + TILE_SIZE - 8, TILE_SIZE, 8))
        surface.blit(shadow, (x, y))

        # 顶部高光
        highlight_points = [
            (x + 8, y + 4 + lid_offset), (x + TILE_SIZE // 2, y),
            (x + TILE_SIZE - 8, y + 4 + lid_offset)
        ]
        pygame.draw.polygon(surface, (255, 255, 255, 80), highlight_points)

    def draw_potion(self, surface, x, y):
        # 药水瓶尺寸
        bottle_width = TILE_SIZE - 8
        bottle_height = TILE_SIZE * 0.8
        neck_width = bottle_width * 0.4
        neck_height = TILE_SIZE * 0.15

        # 药水颜色
        if self.item_type == ItemType.HP_SMALL:
            liquid_color = (200, 50, 50)  # 鲜红色
            highlight_color = (255, 100, 100)
        else:
            liquid_color = (150, 0, 0)  # 深红色
            highlight_color = (200, 50, 50)

        # 瓶身
        bottle_rect = (x + (TILE_SIZE - bottle_width) // 2,
                       y + TILE_SIZE - bottle_height,
                       bottle_width, bottle_height)
        pygame.draw.rect(surface, (150, 150, 200), bottle_rect, border_radius=8)  # 玻璃瓶

        # 液体
        liquid_level = bottle_height * 0.8 if self.item_type == ItemType.HP_SMALL else bottle_height * 0.9
        liquid_rect = (bottle_rect[0] + 2,
                       bottle_rect[1] + bottle_height - liquid_level,
                       bottle_width - 4, liquid_level - 2)
        pygame.draw.rect(surface, liquid_color, liquid_rect, border_radius=6)

        # 液体高光
        pygame.draw.line(surface, highlight_color,
                         (liquid_rect[0] + 4, liquid_rect[1] + 4),
                         (liquid_rect[0] + liquid_rect[2] - 8, liquid_rect[1] + 4), 2)

        # 瓶口
        neck_rect = (x + (TILE_SIZE - neck_width) // 2,
                     y + TILE_SIZE - bottle_height - neck_height,
                     neck_width, neck_height)
        pygame.draw.rect(surface, (180, 180, 220), neck_rect, border_radius=4)

        # 瓶塞
        cork_rect = (neck_rect[0] + 2, neck_rect[1] - 4,
                     neck_width - 4, 6)
        pygame.draw.rect(surface, (150, 100, 50), cork_rect, border_radius=2)

        # 玻璃反光
        pygame.draw.line(surface, (200, 200, 255),
                         (bottle_rect[0] + 4, bottle_rect[1] + 4),
                         (bottle_rect[0] + bottle_width // 2, bottle_rect[1] + 8), 2)

    def draw_gem(self, surface, x, y):
        # 宝石尺寸
        gem_size = TILE_SIZE * 0.8
        gem_center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)

        # 宝石颜色
        if self.item_type == ItemType.ATK_GEM:
            gem_color = (255, 80, 0)  # 橙红色
            highlight_color = (255, 180, 50)
        else:
            gem_color = (0, 100, 200)  # 深蓝色
            highlight_color = (100, 200, 255)

        # 宝石切面
        gem_points = [
            (gem_center[0], gem_center[1] - gem_size // 2),  # 上顶点
            (gem_center[0] + gem_size // 3, gem_center[1] - gem_size // 6),  # 右上
            (gem_center[0] + gem_size // 2, gem_center[1]),  # 右顶点
            (gem_center[0] + gem_size // 3, gem_center[1] + gem_size // 6),  # 右下
            (gem_center[0], gem_center[1] + gem_size // 2),  # 下顶点
            (gem_center[0] - gem_size // 3, gem_center[1] + gem_size // 6),  # 左下
            (gem_center[0] - gem_size // 2, gem_center[1]),  # 左顶点
            (gem_center[0] - gem_size // 3, gem_center[1] - gem_size // 6)  # 左上
        ]
        pygame.draw.polygon(surface, gem_color, gem_points)

        # 切面高光
        highlight_points = [
            (gem_center[0], gem_center[1] - gem_size // 3),
            (gem_center[0] + gem_size // 4, gem_center[1] - gem_size // 8),
            (gem_center[0] + gem_size // 3, gem_center[1]),
            (gem_center[0] + gem_size // 4, gem_center[1] + gem_size // 8),
            (gem_center[0], gem_center[1] + gem_size // 3)
        ]
        pygame.draw.polygon(surface, highlight_color, highlight_points)

        # 宝石底座
        base_rect = (x + (TILE_SIZE - gem_size) // 2,
                     y + TILE_SIZE - 8,
                     gem_size, 6)
        pygame.draw.rect(surface, (100, 100, 100), base_rect, border_radius=2)

        # 宝石闪光
        if random.random() < 0.2:  # 20%概率出现闪光
            flash_points = [
                (gem_center[0] - gem_size // 4, gem_center[1] - gem_size // 4),
                (gem_center[0] + gem_size // 4, gem_center[1] + gem_size // 4)
            ]
            pygame.draw.line(surface, (255, 255, 255),
                             flash_points[0], flash_points[1], 2)

    def draw_weapon(self, surface, x, y):
        # 获取武器数据
        weapon_name = self.name.lower() if self.name else ""

        # 木剑
        if "木剑" in weapon_name:
            # 剑柄 (深棕色)
            pygame.draw.rect(surface, (101, 67, 33),
                             (x + 12, y + 10, 6, 16))  # 垂直剑柄
            # 护手 (铜色)
            pygame.draw.rect(surface, (184, 115, 51),
                             (x + 8, y + 20, 14, 4))
            # 剑身 (木质纹理)
            for i in range(3):
                pygame.draw.line(surface, (139, 69, 19),
                                 (x + 15, y + 5 - i), (x + 15, y + 25 + i), 3)
            # 装饰绳结
            pygame.draw.circle(surface, (139, 0, 0),
                               (x + 15, y + 22), 3)

        # 铜剑或铁剑
        elif "铜剑" in weapon_name or "铁剑" in weapon_name:
            # 剑身
            blade_color = (184, 115, 51) if "铜" in weapon_name else (105, 105, 105)
            pygame.draw.rect(surface, blade_color, (x + 12, y + 5, 6, 20))

            # 剑刃高光
            highlight_color = (192, 192, 192)
            pygame.draw.line(surface, highlight_color,
                             (x + 12, y + 5), (x + 12, y + 25), 2)
            pygame.draw.line(surface, highlight_color,
                             (x + 18, y + 5), (x + 18, y + 25), 2)

            # 剑柄
            pygame.draw.rect(surface, (139, 69, 19), (x + 13, y + 20, 4, 8))

        # 匕首
        elif "匕首" in weapon_name:
            blade_color = (192, 192, 192)
            if "青铜" in weapon_name:
                blade_color = (97, 153, 59)
            elif "钢" in weapon_name or "精钢" in weapon_name:
                blade_color = (220, 220, 220)

            # 刀刃
            blade_points = [
                (x + 12, y + 5), (x + 18, y + 15), (x + 12, y + 25)
            ]
            pygame.draw.polygon(surface, blade_color, blade_points)

            # 刀柄
            pygame.draw.rect(surface, (139, 69, 19), (x + 10, y + 12, 8, 8))

            # 装饰细节
            if "精钢" in weapon_name:
                # 宝石装饰
                pygame.draw.circle(surface, (255, 0, 0), (x + 14, y + 16), 2)

        # 格斯大剑
        elif "格斯大剑" in weapon_name:
            # 剑身 (暗色)
            pygame.draw.rect(surface, (50, 50, 50), (x + 8, y + 5, 14, 25))

            # 剑刃 (锯齿状)
            for i in range(5):
                pygame.draw.line(surface, (105, 105, 105),
                                 (x + 8 + i * 3, y + 5), (x + 8 + i * 3, y + 30), 2)

            # 剑柄
            pygame.draw.rect(surface, (139, 69, 19), (x + 13, y + 25, 4, 10))

            # 血迹效果
            for i in range(3):
                spot_x = x + 8 + random.randint(0, 14)
                spot_y = y + 10 + random.randint(0, 20)
                pygame.draw.circle(surface, (139, 0, 0, 150), (spot_x, spot_y), 2)

        else:
            # 默认武器绘制
            pygame.draw.rect(surface, (150, 150, 150), (x + 10, y + 5, 5, 25))
            pygame.draw.rect(surface, (100, 100, 100), (x + 5, y + 15, 15, 5))

    def draw_armor(self, surface, x, y):
        # 获取护甲数据
        armor_name = self.name.lower() if self.name else ""

        # 基础护甲
        if "木甲" in armor_name:
            # 主体 (木质)
            pygame.draw.rect(surface, (101, 67, 33), (x + 8, y + 8, 15, 20))
            # 木板纹理
            for i in range(3):
                pygame.draw.line(surface, (139, 69, 19),
                                 (x + 8, y + 10 + i * 6), (x + 23, y + 10 + i * 6), 3)
            # 铆钉装饰
            for i in range(2):
                for j in range(3):
                    pygame.draw.circle(surface, (184, 115, 51),
                                       (x + 10 + i * 10, y + 12 + j * 6), 2)

        elif "铜甲" in armor_name:
            # 主体 (铜色)
            pygame.draw.rect(surface, (184, 115, 51), (x + 8, y + 8, 15, 20))
            # 装饰条纹
            for i in range(3):
                pygame.draw.line(surface, (139, 69, 19),
                                 (x + 8, y + 10 + i * 6), (x + 23, y + 10 + i * 6), 2)
            # 随机铜锈
            for i in range(3):
                spot_x = x + 8 + random.randint(0, 15)
                spot_y = y + 8 + random.randint(0, 20)
                pygame.draw.circle(surface, (50, 205, 50, 100), (spot_x, spot_y), 2)

        elif "铁甲" in armor_name:
            # 主体 (铁灰色)
            pygame.draw.rect(surface, (105, 105, 105), (x + 8, y + 8, 15, 20))
            # 铆钉装饰
            for i in range(2):
                for j in range(3):
                    pygame.draw.circle(surface, (192, 192, 192),
                                       (x + 10 + i * 10, y + 12 + j * 6), 2)
            # 金属反光
            pygame.draw.line(surface, (255, 255, 255, 100),
                             (x + 8, y + 10), (x + 23, y + 25), 2)

        elif "钢甲" in armor_name:
            # 主体 (钢色)
            pygame.draw.rect(surface, (192, 192, 192), (x + 8, y + 8, 15, 20))
            # 装饰条纹
            for i in range(3):
                pygame.draw.line(surface, (105, 105, 105),
                                 (x + 8, y + 10 + i * 6), (x + 23, y + 10 + i * 6), 2)
            # 金属反光
            pygame.draw.line(surface, (255, 255, 255, 150),
                             (x + 8, y + 10), (x + 23, y + 25), 3)

        elif "闪电甲" in armor_name:
            # 盔甲基底
            if "红" in armor_name:
                armor_color = (139, 0, 0)
            elif "蓝" in armor_name:
                armor_color = (30, 144, 255)
            else:  # 黄闪电甲
                armor_color = (218, 165, 32)

            pygame.draw.rect(surface, armor_color, (x + 5, y + 5, 22, 22), border_radius=5)

            # 闪电纹路
            lightning_points = [
                (x + 15, y + 8), (x + 20, y + 15),
                (x + 15, y + 22), (x + 10, y + 15)
            ]

            if "红" in armor_name:
                pygame.draw.polygon(surface, (255, 50, 50), lightning_points)
            elif "蓝" in armor_name:
                pygame.draw.polygon(surface, (30, 144, 255), lightning_points)
            else:  # 黄闪电甲
                pygame.draw.polygon(surface, (255, 215, 0), lightning_points)

            # 随机闪电效果
            for i in range(2):
                start = (x + 15 + random.randint(-8, 8), y + 15 + random.randint(-8, 8))
                end = (start[0] + random.randint(-5, 5), start[1] + random.randint(-5, 5))

                if "红" in armor_name:
                    pygame.draw.line(surface, (255, 100, 100), start, end, 2)
                elif "蓝" in armor_name:
                    pygame.draw.line(surface, (100, 149, 237), start, end, 2)
                else:  # 黄闪电甲
                    pygame.draw.line(surface, (255, 255, 0), start, end, 2)

        else:
            # 默认护甲绘制
            pygame.draw.rect(surface, (150, 150, 150), (x + 8, y + 8, 15, 20))


# ---------- NPC类 ----------
class NPC(Entity):
    def __init__(self, name, x, y, dialogue, is_merchant=False, inventory=None):
        super().__init__(name, x, y, EntityType.NPC)
        self.dialogue = dialogue
        self.current_dialogue = 0
        self.is_merchant = is_merchant
        self.inventory = inventory if inventory else Inventory()

    def talk(self):
        if self.current_dialogue >= len(self.dialogue):
            self.current_dialogue = 0

        message = self.dialogue[self.current_dialogue]
        self.current_dialogue += 1

        return message

    def buy_item(self, player, item_index):
        if item_index < 0 or item_index >= len(self.inventory.items):
            return False, "无效的物品索引"

        item = self.inventory.items[item_index]
        price = item.value

        # 检查玩家是否有足够金钱
        if not player.inventory.can_afford(price):
            return False, "金币不足"

        # 从商人库存中移除物品
        success, _ = self.inventory.remove_item(item_index)
        if not success:
            return False, "从商人库存中移除物品失败"

        # 添加物品到玩家库存
        success, message = player.inventory.add_item(item)
        if not success:
            # 将物品放回商人库存
            self.inventory.add_item(item)
            return False, message

        # 扣除玩家金币
        player.inventory.spend(price)

        return True, f"购买了{item.name}，花费{price}金币"

    def sell_item(self, player, item_index):
        if item_index < 0 or item_index >= len(player.inventory.items):
            return False, "无效的物品索引"

        item = player.inventory.items[item_index]

        # 检查物品是否已装备
        if (hasattr(item, 'equipped') and item.equipped) or \
                (player.equipped_weapon and player.equipped_weapon == item) or \
                (player.equipped_armor and player.equipped_armor == item):
            return False, "无法出售已装备的物品"

        # 计算售价（50%买入价）
        price = item.value // 2

        # 从玩家库存中移除物品
        success, _ = player.inventory.remove_item(item_index)
        if not success:
            return False, "从库存中移除物品失败"

        # 添加金币到玩家
        player.inventory.gold += price

        return True, f"出售了{item.name}，获得{price}金币"

    def draw(self, surface, camera_offset_x=0, camera_offset_y=0):
        x = (self.x * TILE_SIZE) - camera_offset_x
        y = (self.y * TILE_SIZE) - camera_offset_y

        # 绘制NPC基本外观
        if self.is_merchant:
            self.draw_merchant(surface, x, y)
        else:
            self.draw_villager(surface, x, y)

    def draw_merchant(self, surface, x, y):
        # 头部
        pygame.draw.circle(surface, (255, 218, 185), (x + TILE_SIZE // 2, y + TILE_SIZE // 4), TILE_SIZE // 5)

        # 身体/长袍
        robe_color = (70, 30, 100)  # 紫色长袍
        pygame.draw.rect(surface, robe_color,
                         (x + TILE_SIZE // 4, y + TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE * 2 // 3))

        # 手臂
        pygame.draw.line(surface, (255, 218, 185),
                         (x + TILE_SIZE // 4, y + TILE_SIZE // 2),
                         (x + TILE_SIZE // 8, y + TILE_SIZE * 2 // 3), 3)
        pygame.draw.line(surface, (255, 218, 185),
                         (x + TILE_SIZE * 3 // 4, y + TILE_SIZE // 2),
                         (x + TILE_SIZE * 7 // 8, y + TILE_SIZE * 2 // 3), 3)

        # 特征（胡子、帽子）
        # 帽子
        pygame.draw.polygon(surface, (60, 20, 90), [
            (x + TILE_SIZE // 4, y + TILE_SIZE // 6),
            (x + TILE_SIZE // 2, y - TILE_SIZE // 10),
            (x + TILE_SIZE * 3 // 4, y + TILE_SIZE // 6)
        ])

        # 胡子
        beard_y = y + TILE_SIZE // 3
        for i in range(5):
            pygame.draw.line(surface, (100, 100, 100),
                             (x + TILE_SIZE // 2 - 5 + i * 2, beard_y),
                             (x + TILE_SIZE // 2 - 5 + i * 2, beard_y + i * 2), 1)

        # 商品袋子
        pygame.draw.circle(surface, (139, 69, 19), (x + TILE_SIZE * 7 // 8, y + TILE_SIZE * 2 // 3), TILE_SIZE // 6)
        pygame.draw.line(surface, (139, 69, 19),
                         (x + TILE_SIZE * 7 // 8, y + TILE_SIZE * 2 // 3 - TILE_SIZE // 6),
                         (x + TILE_SIZE * 7 // 8, y + TILE_SIZE * 2 // 3 - TILE_SIZE // 12), 2)

        # 互动提示
        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.polygon(surface, (255, 255, 255), [
                (x + TILE_SIZE // 2, y - TILE_SIZE // 3),
                (x + TILE_SIZE * 2 // 3, y - TILE_SIZE // 6),
                (x + TILE_SIZE // 3, y - TILE_SIZE // 6)
            ])
            font = pygame.font.SysFont(None, 24)
            text = font.render("!", True, (0, 0, 0))
            text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y - TILE_SIZE // 4))
            surface.blit(text, text_rect)

    def draw_villager(self, surface, x, y):
        # 头部
        pygame.draw.circle(surface, (255, 218, 185), (x + TILE_SIZE // 2, y + TILE_SIZE // 4), TILE_SIZE // 5)

        # 身体
        pygame.draw.rect(surface, (100, 150, 100),
                         (x + TILE_SIZE // 4, y + TILE_SIZE // 3, TILE_SIZE // 2, TILE_SIZE * 2 // 3))

        # 手臂
        pygame.draw.line(surface, (255, 218, 185),
                         (x + TILE_SIZE // 4, y + TILE_SIZE // 2),
                         (x + TILE_SIZE // 8, y + TILE_SIZE * 2 // 3), 3)
        pygame.draw.line(surface, (255, 218, 185),
                         (x + TILE_SIZE * 3 // 4, y + TILE_SIZE // 2),
                         (x + TILE_SIZE * 7 // 8, y + TILE_SIZE * 2 // 3), 3)

        # 眼睛
        eye_spacing = TILE_SIZE // 10
        pygame.draw.circle(surface, (0, 0, 0),
                           (x + TILE_SIZE // 2 - eye_spacing, y + TILE_SIZE // 5), 2)
        pygame.draw.circle(surface, (0, 0, 0),
                           (x + TILE_SIZE // 2 + eye_spacing, y + TILE_SIZE // 5), 2)

        # 嘴巴
        pygame.draw.arc(surface, (0, 0, 0),
                        (x + TILE_SIZE // 2 - TILE_SIZE // 8, y + TILE_SIZE // 4,
                         TILE_SIZE // 4, TILE_SIZE // 8),
                        math.radians(0), math.radians(180), 1)

        # 互动提示
        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.polygon(surface, (255, 255, 255), [
                (x + TILE_SIZE // 2, y - TILE_SIZE // 3),
                (x + TILE_SIZE * 2 // 3, y - TILE_SIZE // 6),
                (x + TILE_SIZE // 3, y - TILE_SIZE // 6)
            ])
            font = pygame.font.SysFont(None, 24)
            text = font.render("?", True, (0, 0, 0))
            text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y - TILE_SIZE // 4))
            surface.blit(text, text_rect)


# ---------- 世界地图类 ----------
class WorldMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map_data = {}  # 存储地形数据
        self.entities = []  # 存储实体
        self.rooms = []  # 房间列表
        self.exit_pos = None
        self.fountain_room = None  # 喷泉房间
        self.lava_room = None  # 岩浆房间
        self.last_spawn_time = 0  # 上次生成生物的时间
        self.corrosion_effects = []  # 腐蚀效果

        # 背景和样式
        self.background_surface = None  # 预渲染的背景
        self.tile_styles = [[None for _ in range(width)] for _ in range(height)]

        # 初始化地图
        self.generate_map()

    def generate_map(self):
        # 生成迷宫
        maze = [[TerrainType.WALL for _ in range(self.width)] for _ in range(self.height)]

        # 从中心开始生成迷宫
        start_x = self.width // 2
        start_y = self.height // 2
        maze[start_y][start_x] = TerrainType.FLOOR
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]
            neighbors = []

            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and maze[ny][nx] == TerrainType.WALL:
                    neighbors.append((nx, ny, dx, dy))

            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                maze[y + dy // 2][x + dx // 2] = TerrainType.FLOOR
                maze[ny][nx] = TerrainType.FLOOR
                stack.append((nx, ny))
            else:
                stack.pop()

        # 添加房间
        rooms = self.add_rooms(maze)

        # 选择起点和终点
        floor_tiles = [(x, y) for y in range(self.height) for x in range(self.width)
                       if maze[y][x] == TerrainType.FLOOR]

        start_pos = random.choice(floor_tiles)

        # 选择较远的点作为出口
        far_tiles = [pos for pos in floor_tiles if
                     abs(pos[0] - start_pos[0]) + abs(pos[1] - start_pos[1]) > self.width // 2]

        exit_pos = random.choice(far_tiles) if far_tiles else random.choice(floor_tiles)
        self.exit_pos = exit_pos

        # 存储地图数据
        self.map_data = {(x, y): maze[y][x] for y in range(self.height) for x in range(self.width)}
        self.rooms = rooms

        # 为墙壁和地板生成样式数据
        for y in range(self.height):
            for x in range(self.width):
                if maze[y][x] == TerrainType.WALL:
                    self.tile_styles[y][x] = self.generate_wall_style(x, y)
                else:
                    self.tile_styles[y][x] = self.generate_floor_style(x, y)

        # 生成特殊房间
        self.generate_special_rooms()

        # 预渲染背景
        self.background_surface = pygame.Surface((self.width * TILE_SIZE, self.height * TILE_SIZE))
        self.render_background()

    def add_rooms(self, maze):
        max_rooms = MAX_ROOM
        room_max_size = MAX_ROOM_SIZE

        num_rooms = random.randint(1, max_rooms)
        rooms = []

        for _ in range(num_rooms):
            w = random.randint(5, room_max_size)
            h = random.randint(5, room_max_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            # 检查是否与其他房间重叠
            overlap = False
            for other in rooms:
                if (x < other[0] + other[2] and x + w > other[0] and
                        y < other[1] + other[3] and y + h > other[1]):
                    overlap = True
                    break

            if not overlap:
                for j in range(y, y + h):
                    for i in range(x, x + w):
                        if 0 <= i < self.width and 0 <= j < self.height:
                            maze[j][i] = TerrainType.FLOOR
                rooms.append((x, y, w, h))

        return rooms

    def generate_special_rooms(self):
        # 从可用房间中选择一个作为喷泉房
        if self.rooms and random.random() < FOUNTAIN_ROOM_PROB:
            room = random.choice(self.rooms)
            x, y, w, h = room

            # 确保房间足够大
            if w >= 7 and h >= 7:
                # 计算喷泉位置（居中3x3）
                fx = x + (w - 3) // 2
                fy = y + (h - 3) // 2

                # 记录喷泉房间信息
                self.fountain_room = {
                    'x1': x, 'y1': y,
                    'x2': x + w, 'y2': y + h,
                    'center': (fx + 1, fy + 1)
                }

                # 创建喷泉区域
                for i in range(fx, fx + 3):
                    for j in range(fy, fy + 3):
                        self.map_data[(i, j)] = TerrainType.FOUNTAIN

                # 从房间列表中移除
                self.rooms.remove(room)

        # 选择另一个房间作为岩浆房
        if self.rooms and random.random() < LAVA_ROOM_PROB:
            room = random.choice(self.rooms)
            x, y, w, h = room

            # 确保房间足够大
            if w >= 7 and h >= 7:
                # 计算中心位置
                center_x = x + w // 2
                center_y = y + h // 2

                # 记录岩浆房间信息
                self.lava_room = {
                    'x1': x, 'y1': y,
                    'x2': x + w, 'y2': y + h,
                    'center': (center_x, center_y)
                }

                # 设置区域类型
                for i in range(x, x + w):
                    for j in range(y, y + h):
                        # 中心1x1为雕像
                        if i == center_x and j == center_y:
                            self.map_data[(i, j)] = TerrainType.STATUE
                        # 周围1格为岩浆
                        elif abs(i - center_x) <= 1 and abs(j - center_y) <= 1:
                            self.map_data[(i, j)] = TerrainType.LAVA
                        # 其他区域为地狱地板
                        else:
                            self.map_data[(i, j)] = TerrainType.HELL_FLOOR

                # 从房间列表中移除
                self.rooms.remove(room)

    def generate_wall_style(self, x, y):
        """生成墙壁的固定样式参数"""
        style_types = ['moss', 'cracked', 'basic', 'basic', 'basic']  # 调整概率分布
        style_type = random.choice(style_types)

        # 固定随机种子以确保可重复性
        seed = hash((x, y))
        random.seed(seed)

        if style_type == 'moss':
            return {
                'type': 'moss',
                'moss_pos': [(random.randint(2, TILE_SIZE - 2), random.randint(2, TILE_SIZE - 2))
                             for _ in range(8)]
            }
        elif style_type == 'cracked':
            start = (random.randint(2, TILE_SIZE - 2), random.randint(2, TILE_SIZE - 2))
            end = (start[0] + random.randint(-8, 8), start[1] + random.randint(8, 12))
            return {
                'type': 'cracked',
                'crack_start': start,
                'crack_end': end,
                'small_cracks': [
                    (random.randint(2, TILE_SIZE - 2), random.randint(2, TILE_SIZE - 2))
                    for _ in range(3)
                ]
            }
        else:  # basic
            return {
                'type': 'basic',
                'highlights': [
                    (random.randint(2, TILE_SIZE - 2), random.randint(2, TILE_SIZE - 2))
                    for _ in range(3)
                ]
            }

    def generate_floor_style(self, x, y):
        """生成地板的固定样式参数"""
        seed = hash((x, y))
        random.seed(seed)

        return {
            'crack_h': random.random() < 0.45,  # 45%概率有水平裂缝
            'crack_v': random.random() < 0.45,  # 45%概率有垂直裂缝
            'stain_pos': (
                random.randint(2, TILE_SIZE - 6),
                random.randint(2, TILE_SIZE - 6)
            ) if random.random() < 0.1 else None  # 10%概率有污渍
        }

    def render_background(self):
        """预渲染背景"""
        for y in range(self.height):
            for x in range(self.width):
                pos = (x, y)
                if pos in self.map_data:
                    terrain_type = self.map_data[pos]

                    if terrain_type == TerrainType.WALL:
                        self.draw_wall(x, y, self.background_surface)
                    elif terrain_type == TerrainType.FLOOR:
                        self.draw_floor(x, y, self.background_surface)
                    # 特殊地形在draw方法中动态绘制

    def draw_wall(self, x, y, surface):
        """绘制墙壁"""
        style = self.tile_styles[y][x]
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        # 绘制基础颜色
        pygame.draw.rect(surface, COLOR_STONE, rect)

        if style['type'] == 'moss':
            # 绘制青苔石墙
            for px, py in style['moss_pos']:
                pygame.draw.circle(surface, COLOR_MOSS,
                                   (rect.left + px, rect.top + py), 1)
            # 底部青苔带
            pygame.draw.rect(surface, COLOR_MOSS,
                             (rect.left + 2, rect.bottom - 4, TILE_SIZE - 4, 3))

        elif style['type'] == 'cracked':
            # 绘制裂缝石墙
            # 主裂缝
            pygame.draw.line(surface, COLOR_CRACK,
                             (rect.left + style['crack_start'][0], rect.top + style['crack_start'][1]),
                             (rect.left + style['crack_end'][0], rect.top + style['crack_end'][1]), 2)
            # 细小裂痕
            for sx, sy in style['small_cracks']:
                ex = sx + random.randint(-4, 4)
                ey = sy + random.randint(-4, 4)
                pygame.draw.line(surface, COLOR_CRACK,
                                 (rect.left + sx, rect.top + sy),
                                 (rect.left + ex, rect.top + ey), 1)
        else:
            # 绘制基础石墙
            # 砖缝
            for i in range(0, TILE_SIZE, 6):
                pygame.draw.line(surface, COLOR_SHADOW,
                                 (rect.left + i, rect.top),
                                 (rect.left + i, rect.bottom), 1)
            # 高光点
            for px, py in style['highlights']:
                pygame.draw.circle(surface, COLOR_HIGHLIGHT,
                                   (rect.left + px, rect.top + py), 1)

        # 石墙阴影
        # 左侧阴影
        shade = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 40))
        surface.blit(shade, rect.topleft)

        # 砖块凸起效果
        for i in range(0, TILE_SIZE, 6):
            for j in range(0, TILE_SIZE, 6):
                if (i + j) % 12 == 0:
                    pygame.draw.line(surface, COLOR_HIGHLIGHT,
                                     (rect.left + i, rect.top + j),
                                     (rect.left + i + 4, rect.top + j), 1)
                    pygame.draw.line(surface, COLOR_HIGHLIGHT,
                                     (rect.left + i, rect.top + j),
                                     (rect.left + i, rect.top + j + 4), 1)

        # 顶部高光
        pygame.draw.line(surface, COLOR_HIGHLIGHT,
                         (rect.left, rect.top), (rect.right, rect.top), 2)
        # 左侧高光
        pygame.draw.line(surface, COLOR_HIGHLIGHT,
                         (rect.left, rect.top), (rect.left, rect.bottom), 2)

    def draw_floor(self, x, y, surface):
        """绘制地板"""
        style = self.tile_styles[y][x]
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

        # 绘制基础地板
        pygame.draw.rect(surface, COLOR_FLOOR, rect)

        # 水平裂缝
        if style['crack_h']:
            pygame.draw.line(surface, COLOR_FLOOR_CRACK,
                             (rect.left + 2, rect.centery),
                             (rect.right - 2, rect.centery), 1)

        # 垂直裂缝
        if style['crack_v']:
            pygame.draw.line(surface, COLOR_FLOOR_CRACK,
                             (rect.centerx, rect.top + 2),
                             (rect.centerx, rect.bottom - 2), 1)

        # 污渍
        if style['stain_pos']:
            sx, sy = style['stain_pos']
            pygame.draw.ellipse(surface, (175, 175, 175, 30),
                                (rect.left + sx, rect.top + sy, 6, 6))

    def draw_special_terrain(self, surface, camera_offset_x=0, camera_offset_y=0):
        """绘制特殊地形（喷泉、岩浆等）"""
        for pos, terrain_type in self.map_data.items():
            if terrain_type in [TerrainType.FOUNTAIN, TerrainType.LAVA, TerrainType.STATUE, TerrainType.HELL_FLOOR]:
                x, y = pos
                screen_x = x * TILE_SIZE - camera_offset_x
                screen_y = y * TILE_SIZE - camera_offset_y

                # 只绘制屏幕内的地形
                if -TILE_SIZE <= screen_x <= SCREEN_WIDTH and -TILE_SIZE <= screen_y <= SCREEN_HEIGHT:
                    if terrain_type == TerrainType.FOUNTAIN:
                        self.draw_fountain_tile(screen_x, screen_y, surface)
                    elif terrain_type == TerrainType.LAVA:
                        self.draw_lava_tile(screen_x, screen_y, surface)
                    elif terrain_type == TerrainType.STATUE:
                        self.draw_obsidian_statue(screen_x, screen_y, surface)
                    elif terrain_type == TerrainType.HELL_FLOOR:
                        self.draw_hell_floor(screen_x, screen_y, surface)

    def draw_fountain_tile(self, x, y, surface):
        anim_time = pygame.time.get_ticks()
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        # 水池基底
        pygame.draw.rect(surface, (30, 144, 255), rect)  # 水池蓝色

        # 动态水波纹效果
        for i in range(3):
            wave_radius = (anim_time % 1000) / 1000 * TILE_SIZE
            alpha = 100 - i * 30
            wave_rect = rect.inflate(-wave_radius + i * 5, -wave_radius + i * 5)
            pygame.draw.ellipse(surface, (255, 255, 255, alpha), wave_rect, 2)

        # 中心喷泉特效（仅中心格）
        is_center = False
        if self.fountain_room and self.fountain_room['center']:
            center_x, center_y = self.fountain_room['center']
            is_center = (x // TILE_SIZE + self.camera_offset_x // TILE_SIZE == center_x and
                         y // TILE_SIZE + self.camera_offset_y // TILE_SIZE == center_y)

        if is_center:
            # 水柱粒子
            for _ in range(8):
                px = rect.centerx + random.randint(-8, 8)
                py = rect.centery - random.randint(0, 20)
                pygame.draw.line(surface, (255, 255, 255),
                                 (px, py), (px, py - 8), 2)

            # 彩虹光晕
            for i in range(3):
                radius = 15 + i * 5
                color = (255, 165, 0) if i == 0 else (0, 255, 0) if i == 1 else (0, 0, 255)
                alpha_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(alpha_surface, (*color, 50), (radius, radius), radius)
                surface.blit(alpha_surface, (rect.centerx - radius, rect.centery - radius))

        # 边缘装饰（喷泉外围）
        else:
            # 大理石边缘
            pygame.draw.rect(surface, (200, 200, 200), rect, 3)
            # 青铜雕像
            if (x + y) % 2 == 0:
                statue_color = (198, 155, 93)
                # 人鱼雕像
                pygame.draw.ellipse(surface, statue_color,
                                    (rect.left + 5, rect.top + 5, 10, 20))  # 身体
                pygame.draw.circle(surface, statue_color,
                                   (rect.centerx, rect.top + 15), 4)  # 头部
                # 鱼尾
                pygame.draw.polygon(surface, statue_color, [
                    (rect.left + 5, rect.bottom - 5),
                    (rect.centerx, rect.bottom - 10),
                    (rect.right - 5, rect.bottom - 5)
                ])

    def draw_lava_tile(self, x, y, surface):
        anim_time = pygame.time.get_ticks()
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        # 岩浆基底颜色动态变化
        lava_color = (
            200 + int(55 * math.sin(anim_time / 300)),
            80 + int(40 * math.cos(anim_time / 400)),
            0,
            200
        )
        pygame.draw.rect(surface, lava_color, rect)

        # 岩浆流动纹理
        for i in range(8):
            flow_x = x + random.randint(2, TILE_SIZE - 2)
            flow_y = y + (anim_time // 30 + i * 40) % (TILE_SIZE + 40)
            pygame.draw.line(surface, (255, 140, 0),
                             (flow_x, flow_y - 5), (flow_x, flow_y + 5), 3)

        # 随机气泡
        if random.random() < 0.1:
            bubble_x = x + random.randint(5, TILE_SIZE - 5)
            bubble_y = y + random.randint(5, TILE_SIZE - 5)
            pygame.draw.circle(surface, (255, 80, 0),
                               (bubble_x, bubble_y), random.randint(2, 4))

    def draw_obsidian_statue(self, x, y, surface):
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        # 雕像主体
        pygame.draw.polygon(surface, (20, 20, 20), [
            (rect.centerx, rect.top + 5),
            (rect.left + 8, rect.bottom - 5),
            (rect.right - 8, rect.bottom - 5)
        ])
        # 熔岩纹路
        lava_lines = [
            (rect.centerx - 5, rect.top + 15),
            (rect.centerx + 5, rect.top + 20),
            (rect.centerx, rect.top + 25)
        ]
        pygame.draw.lines(surface, (255, 80, 0), False, lava_lines, 3)

        # 恶魔之眼
        pygame.draw.circle(surface, (255, 0, 0),
                           (rect.centerx, rect.centery - 5), 6)
        pygame.draw.circle(surface, (0, 0, 0),
                           (rect.centerx, rect.centery - 5), 3)

    def draw_hell_floor(self, x, y, surface):
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        # 焦黑基底
        pygame.draw.rect(surface, (60, 30, 30), rect)

        # 裂纹
        for _ in range(3):
            start = (rect.left + random.randint(2, TILE_SIZE - 2),
                     rect.top + random.randint(2, TILE_SIZE - 2))
            end = (start[0] + random.randint(-8, 8), start[1] + random.randint(-8, 8))
            pygame.draw.line(surface, (80, 40, 40), start, end, 2)

        # 随机火焰
        if random.random() < 0.2:
            flame_h = random.randint(8, 15)
            flame_points = [
                (rect.centerx, rect.bottom - flame_h),
                (rect.centerx - 5, rect.bottom - flame_h // 2),
                (rect.centerx + 5, rect.bottom - flame_h // 2)
            ]
            pygame.draw.polygon(surface, (255, 140, 0), flame_points)

    def is_walkable(self, x, y):
        """检查位置是否可通行"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        pos = (x, y)
        if pos not in self.map_data:
            return False

        terrain_type = self.map_data[pos]
        return terrain_properties[terrain_type]["walkable"]

    def get_empty_positions(self, count, avoid_positions=None):
        """获取指定数量的空位置"""
        if avoid_positions is None:
            avoid_positions = set()

        empty_positions = []
        walkable_positions = [(x, y) for (x, y), terrain in self.map_data.items()
                              if terrain_properties[terrain]["walkable"] and (x, y) not in avoid_positions]

        if len(walkable_positions) < count:
            return walkable_positions

        return random.sample(walkable_positions, count)

    def place_entities(self, player, floor_level):
        """放置实体（怪物、物品等）"""
        # 清空现有实体
        self.entities = []
        avoid_positions = {(player.x, player.y), self.exit_pos}

        # 计算怪物和道具数量
        monster_count = random.randint(MONSTER_MIN, MONSTER_MAX)
        item_count = random.randint(ITEM_MIN, ITEM_MAX)

        # 生成怪物
        monster_positions = self.get_empty_positions(monster_count, avoid_positions)
        avoid_positions.update(monster_positions)

        for i, pos in enumerate(monster_positions):
            x, y = pos

            # 根据楼层等级选择怪物
            eligible_monsters = [m for m in monsters_data if m.get("level", 1) <= floor_level]
            if eligible_monsters:
                if i == 0 and floor_level >= 5:  # 第一个怪物有机会成为boss
                    boss_candidates = [m for m in eligible_monsters if m.get("level", 1) >= 5]
                    if boss_candidates and random.random() < 0.3:  # 30%几率生成boss
                        monster_data = random.choice(boss_candidates)
                        monster = Monster(monster_data, x, y, floor_level)
                        self.entities.append(monster)
                        continue

                # 根据权重选择怪物
                weights = [MONSTER_WEIGHT[monsters_data.index(m)] for m in eligible_monsters]
                monster_data = random.choices(eligible_monsters, weights=weights, k=1)[0]
                monster = Monster(monster_data, x, y, floor_level)
                self.entities.append(monster)

        # 生成物品
        item_positions = self.get_empty_positions(item_count, avoid_positions)
        avoid_positions.update(item_positions)

        for pos in item_positions:
            x, y = pos
            item_type = random.choice(list(ItemType))

            # 武器和护甲
            if random.random() < 0.2:  # 20%几率生成装备
                equip_types = [k for k, v in EQUIPMENT_TYPES.items()]
                equip_type = random.choice(equip_types)
                data = EQUIPMENT_TYPES[equip_type]
                item = Item(data["name"], ItemType.WEAPON if data["type"] == "weapon" else ItemType.ARMOR, x, y, data)
            else:
                # 其他物品
                if random.random() < 0.4:  # 40%几率生成宝箱
                    item = Item("宝箱", ItemType.CHEST, x, y)
                elif random.random() < 0.6:  # 60%几率生成小型生命药水
                    item = Item("小型生命药水", ItemType.HP_SMALL, x, y)
                else:  # 其余为大型生命药水或者宝石
                    if random.random() < 0.5:
                        item = Item("大型生命药水", ItemType.HP_LARGE, x, y)
                    else:
                        item = Item("宝石", ItemType.ATK_GEM if random.random() < 0.5 else ItemType.DEF_GEM, x, y)

            self.entities.append(item)

        # 生成NPC（每层随机1-2个）
        npc_count = random.randint(1, 2)
        npc_positions = self.get_empty_positions(npc_count, avoid_positions)

        for pos in npc_positions:
            x, y = pos

            if random.random() < 0.5:  # 50%几率为商人
                is_merchant = True
                name = random.choice(["铁匠", "炼金术士", "武器商人", "防具商人"])
                dialogue = [
                    f"欢迎来到我的店铺，冒险者！",
                    f"我这里有一些不错的商品，要看看吗？",
                    f"这些都是精心挑选的材料制作的。",
                    f"价格公道，童叟无欺！"
                ]
            else:
                is_merchant = False
                name = random.choice(["村民", "流浪者", "伤员", "探险家"])
                dialogue = [
                    f"这个地下城太危险了，到处都是怪物。",
                    f"听说更深处有强大的boss守卫着宝藏。",
                    f"小心那些红色的史莱姆，它们会造成燃烧伤害。",
                    f"我在寻找出口，你知道怎么出去吗？"
                ]

            # 创建NPC库存（如果是商人）
            inventory = None
            if is_merchant:
                inventory = Inventory()

                # 添加物品到库存
                for _ in range(5):
                    if random.random() < 0.3:  # 武器
                        equip_type = random.choice([k for k, v in EQUIPMENT_TYPES.items() if v["type"] == "weapon"])
                        data = EQUIPMENT_TYPES[equip_type]
                        item = Item(data["name"], ItemType.WEAPON, 0, 0, data)
                    elif random.random() < 0.6:  # 护甲
                        equip_type = random.choice([k for k, v in EQUIPMENT_TYPES.items() if v["type"] == "armor"])
                        data = EQUIPMENT_TYPES[equip_type]
                        item = Item(data["name"], ItemType.ARMOR, 0, 0, data)
                    else:  # 药水
                        if random.random() < 0.7:
                            item = Item("小型生命药水", ItemType.HP_SMALL, 0, 0)
                        else:
                            item = Item("大型生命药水", ItemType.HP_LARGE, 0, 0)

                    inventory.add_item(item)

            npc = NPC(name, x, y, dialogue, is_merchant, inventory)
            self.entities.append(npc)

        # 如果是喷泉房，添加史莱姆生成逻辑
        if self.fountain_room:
            self.last_spawn_time = pygame.time.get_ticks()

    def update(self, player, dt):
        """更新世界状态"""
        # 更新玩家所在喷泉/岩浆房特殊效果
        self.update_special_rooms(player, dt)

        # 更新所有实体
        for entity in self.entities[:]:
            if isinstance(entity, Monster):
                message, is_skill, effect = entity.update(player, self, dt)
                if message:
                    player.reduce_equipment_durability()
                if is_skill and effect:
                    return message, effect

                # 如果是腐蚀怪，创建腐蚀效果
                if "腐蚀怪" in entity.name:
                    self.corrosion_effects.append(CorrosionEffect(entity.x, entity.y))

        # 更新腐蚀效果
        current_time = pygame.time.get_ticks()
        self.corrosion_effects = [effect for effect in self.corrosion_effects
                                  if effect.update(current_time)]

        # 检查玩家是否在腐蚀区域
        player.debuffs['in_corrosion'] = any(
            effect.x == player.x and effect.y == player.y
            for effect in self.corrosion_effects
        )

        # 如果在腐蚀区域，造成伤害
        if player.debuffs['in_corrosion'] and current_time % 1000 < 50:
            player.health -= 50
            return "腐蚀区域造成50点伤害！", None

        return "", None

    def update_special_rooms(self, player, dt):
        """更新特殊房间效果"""
        current_time = pygame.time.get_ticks()

        # 喷泉房史莱姆生成
        if self.fountain_room and self.player_in_fountain_room(player):
            if current_time - self.last_spawn_time > FOUNTAIN_SPAWN_INTERVAL:
                self.spawn_slime()
                self.last_spawn_time = current_time

        # 岩浆房伤害和怪物生成
        if self.lava_room and self.player_in_lava_room(player):
            # 岩浆伤害
            if self.player_in_lava(player):
                player.health -= LAVA_DAMAGE * dt

            # 生成红色史莱姆
            if current_time - self.last_spawn_time > LAVA_SPAWN_INTERVAL:
                self.spawn_red_slime()
                self.last_spawn_time = current_time

    def player_in_fountain_room(self, player):
        """判断玩家是否在喷泉房间内"""
        if not self.fountain_room:
            return False

        fr = self.fountain_room
        return (fr['x1'] <= player.x < fr['x2'] and
                fr['y1'] <= player.y < fr['y2'])

    def player_in_lava_room(self, player):
        """判断玩家是否在岩浆房间内"""
        if not self.lava_room:
            return False

        lr = self.lava_room
        return (lr['x1'] <= player.x < lr['x2'] and
                lr['y1'] <= player.y < lr['y2'])

    def player_in_lava(self, player):
        """判断玩家是否站在岩浆上"""
        pos = (player.x, player.y)
        return pos in self.map_data and self.map_data[pos] == TerrainType.LAVA

    def spawn_slime(self):
        """在喷泉房生成史莱姆"""
        slime_data = next(m for m in monsters_data if m["name"] == "史莱姆")
        fr = self.fountain_room

        for _ in range(10):  # 最多尝试10次
            x = random.randint(fr['x1'], fr['x2'] - 1)
            y = random.randint(fr['y1'], fr['y2'] - 1)

            if self.is_walkable(x, y) and not any(
                    isinstance(e, Monster) and e.x == x and e.y == y
                    for e in self.entities):
                monster = Monster(slime_data, x, y, 1)
                self.entities.append(monster)
                return "喷泉中涌出了绿色史莱姆！"

        return ""

    def spawn_red_slime(self):
        """在岩浆房生成红色史莱姆"""
        slime_data = next(m for m in monsters_data if m["name"] == "红史莱姆")
        lr = self.lava_room

        for _ in range(10):  # 最多尝试10次
            x = random.randint(lr['x1'], lr['x2'] - 1)
            y = random.randint(lr['y1'], lr['y2'] - 1)

            if self.is_walkable(x, y) and not any(
                    isinstance(e, Monster) and e.x == x and e.y == y
                    for e in self.entities):
                monster = Monster(slime_data, x, y, 1)
                self.entities.append(monster)
                return "岩浆中涌出了红色史莱姆！"

        return ""

    def draw(self, surface, camera_offset_x, camera_offset_y):
        """绘制世界"""
        # 保存相机偏移以便在特殊地形绘制中使用
        self.camera_offset_x = camera_offset_x
        self.camera_offset_y = camera_offset_y

        # 绘制预渲染的背景
        surface.blit(self.background_surface, (-camera_offset_x, -camera_offset_y))

        # 绘制特殊地形
        self.draw_special_terrain(surface, camera_offset_x, camera_offset_y)

        # 绘制出口楼梯
        if self.exit_pos:
            exit_x, exit_y = self.exit_pos
            self.draw_stairs(surface, exit_x * TILE_SIZE - camera_offset_x,
                             exit_y * TILE_SIZE - camera_offset_y)

        # 绘制腐蚀效果
        for effect in self.corrosion_effects:
            effect.draw(surface)

        # 绘制实体
        for entity in sorted(self.entities, key=lambda e: 1 if isinstance(e, Monster) else 0):
            # 只绘制接近屏幕的实体
            if (abs(entity.x * TILE_SIZE - camera_offset_x - SCREEN_WIDTH / 2) < SCREEN_WIDTH and
                    abs(entity.y * TILE_SIZE - camera_offset_y - SCREEN_HEIGHT / 2) < SCREEN_HEIGHT):
                entity.draw(surface, camera_offset_x, camera_offset_y)

    def draw_stairs(self, surface, x, y):
        """绘制出口楼梯"""
        # 阶梯参数
        step_height = TILE_SIZE // 4
        step_width = TILE_SIZE
        num_steps = 4

        # 台阶颜色
        step_color = (120, 120, 120)  # 灰色
        highlight_color = (150, 150, 150)  # 高光
        shadow_color = (80, 80, 80)  # 阴影

        # 绘制台阶
        for i in range(num_steps):
            step_y = y + (num_steps - i - 1) * step_height
            step_x = x + i * (step_width // num_steps)

            # 绘制台阶主体
            pygame.draw.rect(surface, step_color,
                             (step_x, step_y, step_width - i * (step_width // num_steps), step_height))

            # 高光
            pygame.draw.line(surface, highlight_color,
                             (step_x, step_y),
                             (step_x + step_width - i * (step_width // num_steps), step_y), 2)

            # 阴影
            pygame.draw.line(surface, shadow_color,
                             (step_x, step_y + step_height),
                             (step_x + step_width - i * (step_width // num_steps), step_y + step_height), 2)

        # 魔法符文装饰
        rune_color = (0, 255, 255)  # 青色
        for i in range(num_steps):
            rune_x = x + i * (step_width // num_steps) + 5
            rune_y = y + (num_steps - i) * step_height - 5
            pygame.draw.circle(surface, rune_color, (rune_x, rune_y), 3)
            pygame.draw.line(surface, rune_color, (rune_x - 5, rune_y), (rune_x + 5, rune_y), 2)

        # 顶部传送门
        portal_radius = TILE_SIZE // 3
        portal_center_x = x + TILE_SIZE // 2
        portal_center_y = y - portal_radius

        # 传送门外圈
        pygame.draw.circle(surface, (255, 215, 0),  # 金色
                           (portal_center_x, portal_center_y), portal_radius, 2)

        # 传送门内圈发光效果
        for i in range(3):
            glow_radius = portal_radius - i * 2
            alpha = 100 - i * 30
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 215, 0, alpha),
                               (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surface, (portal_center_x - glow_radius, portal_center_y - glow_radius))

        # 传送门中心魔法漩涡
        for i in range(4):
            angle = pygame.time.get_ticks() / 200 + i * 90
            start_pos = (
                portal_center_x + math.cos(math.radians(angle)) * portal_radius * 0.5,
                portal_center_y + math.sin(math.radians(angle)) * portal_radius * 0.5
            )
            end_pos = (
                portal_center_x + math.cos(math.radians(angle + 180)) * portal_radius * 0.5,
                portal_center_y + math.sin(math.radians(angle + 180)) * portal_radius * 0.5
            )
            pygame.draw.line(surface, (255, 255, 255), start_pos, end_pos, 2)

        # 藤蔓装饰
        vine_color = (34, 139, 34)  # 绿色
        # 左侧藤蔓
        pygame.draw.arc(surface, vine_color,
                        (x - TILE_SIZE // 2, y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE),
                        math.radians(180), math.radians(270), 2)
        # 右侧藤蔓
        pygame.draw.arc(surface, vine_color,
                        (x + TILE_SIZE // 2, y - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE),
                        math.radians(270), math.radians(360), 2)


# ---------- 相机类 ----------
class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_x, target_y):
        # 让相机跟随目标
        self.offset_x = target_x * TILE_SIZE - SCREEN_WIDTH // 2
        self.offset_y = target_y * TILE_SIZE - SCREEN_HEIGHT // 2

        # 确保相机不会超出地图边界
        self.offset_x = max(0, min(self.offset_x, self.width * TILE_SIZE - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, self.height * TILE_SIZE - SCREEN_HEIGHT))


# ---------- 用户界面类 ----------
class UI:
    def __init__(self, player):
        self.player = player
        self.messages = []
        self.max_messages = 5
        self.message_timeout = 5  # 消息显示时间(秒)
        self.message_timers = []

        # 状态
        self.show_inventory = False
        self.show_stats = False
        self.show_merchant = False
        self.current_merchant = None
        self.selected_inv_item = 0
        self.dialogue_active = False
        self.current_npc = None

        # 字体
        self.font_small = pygame.font.SysFont(None, 24)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_large = pygame.font.SysFont(None, 48)

    def add_message(self, message):
        self.messages.append(message)
        self.message_timers.append(self.message_timeout)

        # 保持消息数量限制
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
            self.message_timers.pop(0)

    def update(self, dt):
        # 更新消息计时器
        for i in range(len(self.message_timers)):
            self.message_timers[i] -= dt

        # 移除过期消息
        while self.message_timers and self.message_timers[0] <= 0:
            self.messages.pop(0)
            self.message_timers.pop(0)

    def draw(self, surface):
        # 绘制左侧状态面板
        self.draw_side_panel(surface)

        # 绘制消息
        self.draw_messages(surface)

        # 绘制背包界面
        if self.show_inventory:
            self.draw_inventory(surface)

        # 绘制商人界面
        if self.show_merchant and self.current_merchant:
            self.draw_merchant_interface(surface)

        # 绘制对话界面
        if self.dialogue_active and self.current_npc:
            self.draw_dialogue(surface)

    def draw_side_panel(self, surface):
        # 侧边栏背景
        panel = pygame.Surface((SIDEBAR_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        panel.fill((30, 30, 40, 220))  # 半透明背景

        # 标题
        title = self.font_medium.render("勇者状态", True, COLOR_YELLOW)
        panel.blit(title, (20, 20))

        # 分隔线
        pygame.draw.line(panel, (80, 80, 100), (10, 60), (SIDEBAR_WIDTH - 10, 60), 2)

        # 基本属性
        y_pos = 80
        stats = [
            (f"等级: {self.player.level}", COLOR_WHITE),
            (f"生命: {self.player.health}/{self.player.max_health}", COLOR_RED),
            (f"法力: {self.player.mana}/{self.player.max_mana}", COLOR_BLUE),
            (f"攻击: {self.player.attack}", COLOR_ATK),
            (f"防御: {self.player.defense}", COLOR_DEF),
            (f"金币: {self.player.inventory.gold}", COLOR_YELLOW)
        ]

        for text, color in stats:
            stat_text = self.font_small.render(text, True, color)
            panel.blit(stat_text, (20, y_pos))
            y_pos += 30

        # 分隔线
        pygame.draw.line(panel, (80, 80, 100), (10, y_pos + 10), (SIDEBAR_WIDTH - 10, y_pos + 10), 2)

        # 装备信息
        y_pos += 30
        equip_title = self.font_small.render("装备:", True, COLOR_WHITE)
        panel.blit(equip_title, (20, y_pos))
        y_pos += 30

        # 武器
        weapon_text = "无" if not self.player.equipped_weapon else self.player.equipped_weapon["name"]
        weapon_info = self.font_small.render(f"武器: {weapon_text}", True, COLOR_WHITE)
        panel.blit(weapon_info, (20, y_pos))
        y_pos += 30

        # 护甲
        armor_text = "无" if not self.player.equipped_armor else self.player.equipped_armor["name"]
        armor_info = self.font_small.render(f"护甲: {armor_text}", True, COLOR_WHITE)
        panel.blit(armor_info, (20, y_pos))
        y_pos += 30

        # 武器耐久度
        if self.player.equipped_weapon:
            durability = self.player.equipped_weapon["durability"]
            max_durability = self.player.equipped_weapon.get("max_durability", 100)
            durability_text = self.font_small.render(f"武器耐久: {durability}/{max_durability}", True, COLOR_WHITE)
            panel.blit(durability_text, (20, y_pos))
        y_pos += 30

        # 护甲耐久度
        if self.player.equipped_armor:
            durability = self.player.equipped_armor["durability"]
            max_durability = self.player.equipped_armor.get("max_durability", 100)
            durability_text = self.font_small.render(f"护甲耐久: {durability}/{max_durability}", True, COLOR_WHITE)
            panel.blit(durability_text, (20, y_pos))
        y_pos += 30

        # 控制提示
        y_pos = SCREEN_HEIGHT - 150
        pygame.draw.line(panel, (80, 80, 100), (10, y_pos - 10), (SIDEBAR_WIDTH - 10, y_pos - 10), 2)

        tips = [
            "WASD: 移动",
            "鼠标点击: 传送至目标位置",
            "空格: 攻击最近的敌人",
            "E: 互动",
            "I: 打开/关闭背包",
            "1-5: 使用技能"
        ]

        for tip in tips:
            tip_text = self.font_small.render(tip, True, COLOR_WHITE)
            panel.blit(tip_text, (20, y_pos))
            y_pos += 25

        # 将面板绘制到屏幕
        surface.blit(panel, (MAP_WIDTH * TILE_SIZE, 0))

    def draw_messages(self, surface):
        for i, message in enumerate(self.messages):
            alpha = min(255, int(self.message_timers[i] * 255 / self.message_timeout))
            message_text = self.font_small.render(message, True, (255, 255, 255))
            surface.blit(message_text, (20, 20 + i * 30))

    def draw_inventory(self, surface):
        # 半透明背景
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        surface.blit(bg, (0, 0))

        # 背包面板
        panel_width = 600
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        # 面板背景
        pygame.draw.rect(surface, (50, 50, 70), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, (80, 80, 100), (panel_x, panel_y, panel_width, panel_height), 2)

        # 标题
        title = self.font_medium.render("物品栏", True, COLOR_WHITE)
        surface.blit(title, (panel_x + 20, panel_y + 20))

        # 物品列表
        item_height = 30
        visible_items = 10
        items = self.player.inventory.items

        # 滚动逻辑
        start_item = max(0, min(self.selected_inv_item - visible_items // 2,
                                len(items) - visible_items)) if items else 0
        end_item = min(start_item + visible_items, len(items))

        # 绘制物品
        for i in range(start_item, end_item):
            item = items[i]
            y_offset = panel_y + 70 + (i - start_item) * item_height

            # 高亮选中物品
            if i == self.selected_inv_item:
                pygame.draw.rect(surface, (80, 80, 120),
                                 (panel_x + 10, y_offset, panel_width - 20, item_height))

            # 物品名称
            name_text = self.font_small.render(item.name, True, COLOR_WHITE)
            surface.blit(name_text, (panel_x + 20, y_offset + 5))

            # 物品类型
            type_text = None
            if hasattr(item, 'item_type'):
                type_name = item.item_type.name if isinstance(item.item_type, Enum) else str(item.item_type)
                type_text = self.font_small.render(type_name, True, COLOR_WHITE)
            elif hasattr(item, 'data') and item.data and "type" in item.data:
                type_text = self.font_small.render(item.data["type"].capitalize(), True, COLOR_WHITE)

            if type_text:
                surface.blit(type_text, (panel_x + 250, y_offset + 5))

        # 选中物品详情
        if items and 0 <= self.selected_inv_item < len(items):
            item = items[self.selected_inv_item]
            detail_y = panel_y + 70 + visible_items * item_height + 20

            # 详情面板
            pygame.draw.rect(surface, (60, 60, 80),
                             (panel_x + 10, detail_y, panel_width - 20, 80))

            # 物品详情
            details = []
            if hasattr(item, 'data') and item.data:
                if "type" in item.data:
                    if item.data["type"] == "weapon":
                        details.append(f"攻击力: {item.data['atk']}")
                        details.append(f"倍率: {item.data['multiple']}x")
                        details.append(f"耐久度: {item.data['durability']}")
                    elif item.data["type"] == "armor":
                        details.append(f"防御力: {item.data['def']}")
                        details.append(f"倍率: {item.data['multiple']}x")
                        details.append(f"耐久度: {item.data['durability']}")
            elif hasattr(item, 'item_type'):
                if item.item_type == ItemType.CHEST:
                    details.append("打开可获得金币")
                elif item.item_type == ItemType.HP_SMALL:
                    details.append("恢复少量生命值")
                elif item.item_type == ItemType.HP_LARGE:
                    details.append("恢复大量生命值")
                elif item.item_type == ItemType.ATK_GEM:
                    details.append("永久提升攻击力")
                elif item.item_type == ItemType.DEF_GEM:
                    details.append("永久提升防御力")

            # 绘制详情
            for j, detail in enumerate(details):
                detail_text = self.font_small.render(detail, True, COLOR_WHITE)
                surface.blit(detail_text, (panel_x + 20, detail_y + 10 + j * 25))

            # 使用按钮
            button_rect = pygame.Rect(panel_x + panel_width - 100, detail_y + 10, 80, 30)
            pygame.draw.rect(surface, (100, 100, 150), button_rect)
            button_text = self.font_small.render("使用", True, COLOR_WHITE)
            surface.blit(button_text, (button_rect.x + 25, button_rect.y + 5))

        # 底部提示
        help_text = self.font_small.render("↑↓: 选择物品   回车: 使用   ESC: 关闭", True, COLOR_WHITE)
        surface.blit(help_text, (panel_x + 20, panel_y + panel_height - 30))

    def draw_merchant_interface(self, surface):
        # 背景
        bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        surface.blit(bg, (0, 0))

        # 商店面板
        panel_width = 700
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        # 面板背景
        pygame.draw.rect(surface, (50, 50, 70), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, (80, 80, 100), (panel_x, panel_y, panel_width, panel_height), 2)

        # 标题
        title = self.font_medium.render(f"{self.current_merchant.name}的商店", True, COLOR_WHITE)
        surface.blit(title, (panel_x + 20, panel_y + 20))

        # 玩家金币
        gold_text = self.font_small.render(f"金币: {self.player.inventory.gold}", True, COLOR_YELLOW)
        surface.blit(gold_text, (panel_x + panel_width - 150, panel_y + 25))

        # 商品列表头部
        pygame.draw.line(surface, COLOR_WHITE,
                         (panel_x + 10, panel_y + 60),
                         (panel_x + panel_width - 10, panel_y + 60), 2)

        shop_headers = [
            (panel_x + 20, "物品名称"),
            (panel_x + 350, "价格"),
            (panel_x + panel_width - 80, "")
        ]

        for x, text in shop_headers:
            header_text = self.font_small.render(text, True, COLOR_WHITE)
            surface.blit(header_text, (x, panel_y + 35))

        # 商品列表
        item_height = 30
        visible_items = 10
        items = self.current_merchant.inventory.items

        for i, item in enumerate(items[:visible_items]):
            y_offset = panel_y + 70 + i * item_height

            # 物品名称
            name_text = self.font_small.render(item.name, True, COLOR_WHITE)
            surface.blit(name_text, (panel_x + 20, y_offset + 5))

            # 价格
            price_text = self.font_small.render(f"{item.value}金币", True, COLOR_YELLOW)
            surface.blit(price_text, (panel_x + 350, y_offset + 5))

            # 购买按钮
            button_rect = pygame.Rect(panel_x + panel_width - 80, y_offset + 2, 60, 25)
            button_color = (100, 100, 150) if self.player.inventory.can_afford(item.value) else (80, 80, 80)
            pygame.draw.rect(surface, button_color, button_rect)
            button_text = self.font_small.render("购买", True, COLOR_WHITE)
            surface.blit(button_text, (button_rect.x + 15, button_rect.y + 5))

        # 分隔线
        line_y = panel_y + 70 + visible_items * item_height + 10
        pygame.draw.line(surface, COLOR_WHITE,
                         (panel_x + 10, line_y),
                         (panel_x + panel_width - 10, line_y), 2)

        # 卖出标题
        sell_title = self.font_small.render("出售物品", True, COLOR_WHITE)
        surface.blit(sell_title, (panel_x + 20, line_y + 20))

        # 玩家物品列表
        player_items = self.player.inventory.items

        for i, item in enumerate(player_items[:visible_items]):
            y_offset = line_y + 50 + i * item_height

            # 物品名称
            name_text = self.font_small.render(item.name, True, COLOR_WHITE)
            surface.blit(name_text, (panel_x + 20, y_offset + 5))

            # 价格 (50%买入价)
            sell_price = item.value // 2
            price_text = self.font_small.render(f"{sell_price}金币", True, COLOR_YELLOW)
            surface.blit(price_text, (panel_x + 350, y_offset + 5))

            # 卖出按钮 (不能卖出已装备物品)
            can_sell = True
            if ((self.player.equipped_weapon and self.player.equipped_weapon == item.data) or
                    (self.player.equipped_armor and self.player.equipped_armor == item.data)):
                can_sell = False

            button_rect = pygame.Rect(panel_x + panel_width - 80, y_offset + 2, 60, 25)
            button_color = (100, 100, 150) if can_sell else (80, 80, 80)
            pygame.draw.rect(surface, button_color, button_rect)
            button_text = self.font_small.render("卖出", True, COLOR_WHITE)
            surface.blit(button_text, (button_rect.x + 15, button_rect.y + 5))

        # 底部提示
        help_text = self.font_small.render("点击按钮购买/出售 或 按ESC关闭", True, COLOR_WHITE)
        surface.blit(help_text, (panel_x + 20, panel_y + panel_height - 30))

    def draw_dialogue(self, surface):
        # 对话面板
        panel_height = 150
        panel_y = SCREEN_HEIGHT - panel_height - 20

        panel = pygame.Surface((SCREEN_WIDTH - 40, panel_height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 220))
        surface.blit(panel, (20, panel_y))

        # NPC名称
        name_text = self.font_medium.render(self.current_npc.name, True, COLOR_YELLOW)
        surface.blit(name_text, (40, panel_y + 20))

        # 对话文本
        dialogue_text = self.current_npc.dialogue[self.current_npc.current_dialogue - 1]
        max_width = SCREEN_WIDTH - 80

        # 文本换行处理
        words = dialogue_text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            text_width = self.font_small.size(test_line)[0]

            if text_width < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)

        # 绘制文本
        for i, line in enumerate(lines):
            line_text = self.font_small.render(line, True, COLOR_WHITE)
            surface.blit(line_text, (40, panel_y + 50 + i * 25))

        # 继续提示
        if pygame.time.get_ticks() % 1000 < 500:  # 闪烁效果
            continue_text = self.font_small.render("按空格继续...", True, COLOR_WHITE)
            surface.blit(continue_text, (SCREEN_WIDTH - 150, panel_y + panel_height - 30))

    def handle_inventory_input(self, event, player):
        if event.type == pygame.KEYDOWN:
            # 导航物品列表
            if event.key == pygame.K_UP:
                self.selected_inv_item = max(0, self.selected_inv_item - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_inv_item = min(len(player.inventory.items) - 1, self.selected_inv_item)

            # 使用物品
            elif event.key == pygame.K_RETURN:
                if player.inventory.items and 0 <= self.selected_inv_item < len(player.inventory.items):
                    item = player.inventory.items[self.selected_inv_item]
                    result = item.use(player)
                    player.inventory.items.remove(item)
                    self.add_message(result)

            # 关闭背包
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.show_inventory = False

    def handle_merchant_input(self, event, player, mouse_pos):
        if event.type == pygame.KEYDOWN:
            # 关闭商店
            if event.key == pygame.K_ESCAPE:
                self.show_merchant = False
                self.current_merchant = None

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            panel_width = 700
            panel_height = 500
            panel_x = (SCREEN_WIDTH - panel_width) // 2
            panel_y = (SCREEN_HEIGHT - panel_height) // 2

            # 检查点击是否在面板内
            if not (panel_x <= mouse_pos[0] <= panel_x + panel_width and
                    panel_y <= mouse_pos[1] <= panel_y + panel_height):
                return

            # 检查点击的是否为购买按钮
            item_height = 30
            visible_items = 10

            for i, item in enumerate(self.current_merchant.inventory.items[:visible_items]):
                button_rect = pygame.Rect(panel_x + panel_width - 80,
                                          panel_y + 70 + i * item_height + 2,
                                          60, 25)

                if button_rect.collidepoint(mouse_pos) and player.inventory.can_afford(item.value):
                    # 购买物品
                    result, message = self.current_merchant.buy_item(player, i)
                    if result:
                        self.add_message(message)
                    break

            # 检查点击的是否为卖出按钮
            line_y = panel_y + 70 + visible_items * item_height + 10

            for i, item in enumerate(player.inventory.items[:visible_items]):
                button_rect = pygame.Rect(panel_x + panel_width - 80,
                                          line_y + 50 + i * item_height + 2,
                                          60, 25)

                if button_rect.collidepoint(mouse_pos):
                    # 不能卖出已装备物品
                    can_sell = True
                    if ((player.equipped_weapon and player.equipped_weapon == item.data) or
                            (player.equipped_armor and player.equipped_armor == item.data)):
                        can_sell = False

                    if can_sell:
                        result, message = self.current_merchant.sell_item(player, i)
                        if result:
                            self.add_message(message)
                        break

    def handle_dialogue_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # 继续对话
            if self.current_npc.current_dialogue < len(self.current_npc.dialogue):
                message = self.current_npc.talk()
                self.add_message(message)
            else:
                # 对话结束
                self.dialogue_active = False
                if self.current_npc.is_merchant:
                    # 如果是商人，打开商店
                    self.show_merchant = True
                    self.current_merchant = self.current_npc
                else:
                    self.current_npc = None


# ---------- 游戏界面类 ----------
class DungeonButton:
    def __init__(self, rect, text, font_size=32):
        self.rect = rect
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.hover = False
        self.flame_offset = 0  # 火焰动画偏移量

    def draw(self, surface):
        # 动态更新火焰偏移
        self.flame_offset = (self.flame_offset + 2) % 20

        # 基础石板
        self._draw_stone_base(surface)

        # 金属镶边
        self._draw_metal_trim(surface)

        # 动态火焰效果（仅悬停时）
        if self.hover:
            self._draw_flame_effect(surface)

        # 按钮文字
        self._draw_text(surface)

    def _draw_stone_base(self, surface):
        # 石板基底
        base_color = (60, 60, 60) if not self.hover else (80, 80, 80)
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)

        # 石头纹理
        for _ in range(40):  # 随机石纹斑点
            x = self.rect.x + random.randint(2, self.rect.w - 4)
            y = self.rect.y + random.randint(2, self.rect.h - 4)
            size = random.choice([1, 1, 1, 2])
            color = random.choice([(70, 70, 70), (50, 50, 50), (90, 90, 90)])
            pygame.draw.circle(surface, color, (x, y), size)

        # 立体凹痕
        pygame.draw.line(surface, (40, 40, 40),
                         (self.rect.left + 5, self.rect.centery),
                         (self.rect.right - 5, self.rect.centery), 3)
        pygame.draw.line(surface, (40, 40, 40),
                         (self.rect.centerx, self.rect.top + 5),
                         (self.rect.centerx, self.rect.bottom - 5), 3)

    def _draw_metal_trim(self, surface):
        # 青铜镶边
        trim_color1 = (198, 155, 93)  # 青铜色
        trim_color2 = (150, 120, 70)  # 暗部
        border_rect = self.rect.inflate(-4, -4)

        # 渐变金属效果
        for i in range(4):
            color = (
                trim_color1[0] + (trim_color2[0] - trim_color1[0]) * i / 4,
                trim_color1[1] + (trim_color2[1] - trim_color1[1]) * i / 4,
                trim_color1[2] + (trim_color2[2] - trim_color1[2]) * i / 4
            )
            pygame.draw.rect(surface, color, border_rect.inflate(-i * 2, -i * 2),
                             border_radius=8 - i, width=2)

        # 铆钉装饰
        for x in [border_rect.left + 8, border_rect.right - 8]:
            for y in [border_rect.top + 8, border_rect.bottom - 8]:
                pygame.draw.circle(surface, (250, 250, 200), (x, y), 3)
                pygame.draw.circle(surface, (150, 150, 100), (x, y), 3, 1)

    def _draw_flame_effect(self, surface):
        # 火焰粒子效果
        for i in range(3):
            offset = self.flame_offset + i * 7
            if offset > 20: continue

            # 火焰主体
            flame_rect = pygame.Rect(
                self.rect.centerx - 15 + offset,
                self.rect.top - 15,
                30, 30
            )

            # 火焰颜色渐变
            for j, color in enumerate([(255, 100, 0, 150), (255, 200, 0, 80), (255, 255, 200, 40)]):
                temp_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.ellipse(temp_surf, color, (0, j * 5, 30, 30 - j * 10))
                surface.blit(temp_surf, flame_rect)

            # 火星粒子
            for _ in range(5):
                x = flame_rect.centerx + random.randint(-8, 8)
                y = flame_rect.centery + random.randint(-5, 5)
                pygame.draw.circle(surface, (255, 255, 200, 150), (x, y), 1)

    def _draw_text(self, surface):
        # 文字阴影效果
        text_surf = self.font.render(self.text, True, (30, 30, 30))
        shadow_rect = text_surf.get_rect(center=(self.rect.centerx + 2, self.rect.centery + 2))
        surface.blit(text_surf, shadow_rect)

        # 主文字
        text_color = (200, 160, 60) if not self.hover else (255, 200, 100)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 72)
        self.background = self.create_stone_texture()
        self.torch_frames = self.create_torch_frames()
        self.torch_index = 0
        self.torch_timer = 0

        # 使用 DungeonButton 创建按钮
        button_width, button_height = 300, 80
        self.start_button = DungeonButton(
            pygame.Rect(0, 0, button_width, button_height),
            "进入地下城", 36
        )
        self.start_button.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)

        self.settings_button = DungeonButton(
            pygame.Rect(0, 0, 280, 70),
            "设置", 32
        )
        self.settings_button.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)

    def create_stone_texture(self):
        texture = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        # 绘制石头纹理
        for i in range(0, SCREEN_WIDTH, 20):
            for j in range(0, SCREEN_HEIGHT, 20):
                color = random.choice([(80, 80, 80), (70, 70, 70), (90, 90, 90)])
                pygame.draw.rect(texture, color, (i, j, 20, 20), border_radius=3)
                # 添加苔藓斑点
                if random.random() < 0.1:
                    pygame.draw.circle(texture, COLOR_MOSS,
                                       (i + random.randint(2, 18), j + random.randint(2, 18)),
                                       random.randint(2, 4))
        return texture

    def create_torch_frames(self):
        torch_width = 4 * TILE_SIZE  # 3格宽
        torch_height = 8 * TILE_SIZE  # 6格高
        frames = []

        for i in range(8):  # 8帧动画
            frame = pygame.Surface((torch_width, torch_height), pygame.SRCALPHA)

            # ------ 火焰核心 -------
            # 动态火焰形状参数
            flame_radius = 30 + i * 5  # 火焰半径动态变化
            flame_points = []
            for angle in range(0, 360, 10):
                # 动态扭曲效果
                distortion = math.sin(math.radians(angle * 2 + i * 45)) * 10
                x = torch_width // 2 + math.cos(math.radians(angle)) * (flame_radius + distortion)
                y = torch_height - 50 - angle / 3  # 火焰向上延伸
                flame_points.append((x, y))

            # 多层火焰（从内到外）
            flame_layers = [
                {'color': (255, 200, 50, 200), 'offset': 0},  # 核心亮黄色
                {'color': (255, 100, 0, 150), 'offset': 5},  # 中层橙色
                {'color': (200, 50, 0, 100), 'offset': 10},  # 外围深红色
                {'color': (100, 20, 0, 50), 'offset': 15}  # 边缘暗红色
            ]

            for layer in flame_layers:
                offset_points = [(x + random.randint(-2, 2), y + layer['offset'] + random.randint(-2, 2))
                                 for x, y in flame_points]
                pygame.draw.polygon(frame, layer['color'], offset_points)

            # ------ 火星粒子系统 -------
            for _ in range(20):  # 增加粒子数量
                life = random.randint(0, 3)
                if life > 0:
                    alpha = 200 - life * 50
                    # 粒子起始位置在火焰底部
                    start_x = torch_width // 2 + random.randint(-15, 15)
                    start_y = torch_height - 50 - life * 5 + i * 3  # 粒子向上运动
                    # 粒子拖影效果
                    end_x = start_x + random.randint(-4, 4)
                    end_y = start_y + random.randint(-4, 4)
                    pygame.draw.line(frame, (255, 150, 50, alpha),
                                     (start_x, start_y), (end_x, end_y), 2)

            # ------ 光晕效果 -------
            glow = pygame.Surface((torch_width, torch_height), pygame.SRCALPHA)
            radius = 25 + i * 2  # 动态光晕半径
            for r in range(radius, 0, -2):
                alpha = max(0, 30 - r)  # 透明度递减
                glow_color = (255, 200, 100, alpha)
                temp_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, glow_color, (r, r), r)
                glow.blit(temp_surface, (torch_width // 2 - r, torch_height - 50 - r))

            frame.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # ------ 随机闪烁亮点 -------
            for _ in range(3):
                x = torch_width // 2 + random.randint(-15, 15)
                y = torch_height - random.randint(50, 80)
                pygame.draw.circle(frame, (255, 255, 200, 100),
                                   (x, y), random.randint(2, 4))

            # ------ 火炬金属支架 -------
            # 垂直支架
            pygame.draw.rect(frame, (80, 80, 80),
                             (torch_width // 2 - 5, torch_height - 50, 10, 50))
            # 支架底座
            pygame.draw.polygon(frame, (100, 100, 100), [
                (torch_width // 2 - 15, torch_height - 40),
                (torch_width // 2 + 15, torch_height - 40),
                (torch_width // 2 + 20, torch_height - 30),
                (torch_width // 2 - 20, torch_height - 30)
            ])
            # 支架装饰
            for j in range(3):
                pygame.draw.circle(frame, (120, 120, 120),
                                   (torch_width // 2, torch_height - 50 + j * 15), 3)

            frames.append(frame)
        return frames

    def draw(self):
        # 绘制背景纹理
        self.screen.blit(self.background, (0, 0))

        # 绘制标题
        title_surf = self.font_title.render("魔塔地下城", True, COLOR_UI_TEXT)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_surf, title_rect)

        # 按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.hover = self.start_button.rect.collidepoint(mouse_pos)
        self.settings_button.hover = self.settings_button.rect.collidepoint(mouse_pos)

        # 绘制按钮
        self.start_button.draw(self.screen)
        self.settings_button.draw(self.screen)

        # 计算火炬位置
        torch_spacing = 50  # 标题与火炬间距

        # 左侧火炬
        torch_left_x = title_rect.left - torch_spacing - 3 * TILE_SIZE
        torch_left_y = title_rect.centery - 3 * TILE_SIZE  # 垂直居中

        # 右侧火炬
        torch_right_x = title_rect.right + torch_spacing

        # 绘制动态火炬
        self.torch_timer += 1
        if self.torch_timer >= 5:  # 加快动画速度
            self.torch_index = (self.torch_index + 1) % 8
            self.torch_timer = 0

        # 左侧火炬
        self.screen.blit(self.torch_frames[self.torch_index],
                         (torch_left_x, torch_left_y))

        # 右侧火炬（镜像）
        flipped_torch = pygame.transform.flip(self.torch_frames[self.torch_index], True, False)
        self.screen.blit(flipped_torch,
                         (torch_right_x, torch_left_y))

        # 添加标题装饰
        pygame.draw.line(self.screen, COLOR_UI_TEXT,
                         (title_rect.left - 50, title_rect.centery),
                         (title_rect.right + 50, title_rect.centery), 3)

        # 返回按钮区域用于点击检测
        return [self.start_button.rect, self.settings_button.rect]


class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.back_button = pygame.Rect(50, 400, 200, 50)
        self.apply_button = pygame.Rect(300, 400, 200, 50)
        self.sliders = [
            {"label": "地图宽度", "value": MAP_WIDTH, "min": 21, "max": 51,
             "rect": pygame.Rect(100, 100, 400, 20)},
            {"label": "地图高度", "value": MAP_HEIGHT, "min": 21, "max": 51,
             "rect": pygame.Rect(100, 150, 400, 20)},
            {"label": "格子大小", "value": TILE_SIZE, "min": 20, "max": 80,
             "rect": pygame.Rect(100, 200, 400, 20)}
        ]
        self.dragging = None

    def draw_slider(self, slider):
        pygame.draw.rect(self.screen, (200, 200, 200), slider["rect"])
        ratio = (slider["value"] - slider["min"]) / (slider["max"] - slider["min"])
        handle_x = slider["rect"].x + ratio * (slider["rect"].width - 20)
        pygame.draw.rect(self.screen, (0, 128, 255), (handle_x, slider["rect"].y - 10, 20, 40))

        label = self.font.render(f"{slider['label']}: {slider['value']}", True, (255, 255, 255))
        self.screen.blit(label, (slider["rect"].x, slider["rect"].y - 40))

    def draw(self):
        self.screen.fill((30, 30, 50))
        for slider in self.sliders:
            self.draw_slider(slider)

        # 绘制按钮
        pygame.draw.rect(self.screen, (70, 70, 70), self.back_button)
        back_text = self.font.render("返回", True, (255, 255, 255))
        self.screen.blit(back_text, (self.back_button.x + 70, self.back_button.y + 15))

        pygame.draw.rect(self.screen, (70, 70, 70), self.apply_button)
        apply_text = self.font.render("应用", True, (255, 255, 255))
        self.screen.blit(apply_text, (self.apply_button.x + 70, self.apply_button.y + 15))

        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, slider in enumerate(self.sliders):
                if slider["rect"].collidepoint(event.pos):
                    self.dragging = i
            if self.back_button.collidepoint(event.pos):
                return "menu"
            elif self.apply_button.collidepoint(event.pos):
                global MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
                MAP_WIDTH = self.sliders[0]["value"]
                MAP_HEIGHT = self.sliders[1]["value"]
                TILE_SIZE = self.sliders[2]["value"]
                SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE + SIDEBAR_WIDTH
                SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE
                return "apply"

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = None

        elif event.type == pygame.MOUSEMOTION and self.dragging is not None:
            slider = self.sliders[self.dragging]
            x = min(max(event.pos[0], slider["rect"].x), slider["rect"].x + slider["rect"].width)
            ratio = (x - slider["rect"].x) / slider["rect"].width
            slider["value"] = int(slider["min"] + ratio * (slider["max"] - slider["min"]))

        return "settings"


class DeathScreen:
    def __init__(self, screen, player, floor):
        self.screen = screen
        self.player = player
        self.floor = floor
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_stats = pygame.font.SysFont(None, 32)
        self.blood_texture = self.create_blood_texture()

    def create_blood_texture(self):
        texture = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # 血渍效果
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            radius = random.randint(10, 30)
            alpha = random.randint(100, 150)
            pygame.draw.circle(texture, (139, 0, 0, alpha), (x, y), radius)
            # 血滴飞溅
            for _ in range(5):
                dx = random.randint(-20, 20)
                dy = random.randint(-20, 20)
                pygame.draw.line(texture, (139, 0, 0, alpha),
                                 (x, y), (x + dx, y + dy), 3)
        return texture

    def draw(self):
        # 暗红色覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(self.blood_texture, (0, 0))

        # 破碎盾牌装饰
        shield = pygame.Surface((256, 256), pygame.SRCALPHA)
        # 绘制盾牌基底
        pygame.draw.polygon(shield, (150, 150, 150), [
            (128, 20), (220, 80), (220, 176), (128, 236), (36, 176), (36, 80)
        ])
        # 添加裂痕效果
        pygame.draw.line(shield, (80, 80, 80), (100, 100), (156, 156), 5)
        pygame.draw.line(shield, (80, 80, 80), (156, 100), (100, 156), 5)
        self.screen.blit(shield, (SCREEN_WIDTH // 2 - 128, SCREEN_HEIGHT // 2 - 100))

        # 标题
        title_surf = self.font_title.render("你死了", True, COLOR_DEATH_RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_surf, title_rect)

        # 统计信息
        stats = [
            f"达到第 {self.floor} 层",
            f"攻击力: {self.player.attack}",
            f"防御力: {self.player.defense}"
        ]
        y_start = 300
        for text in stats:
            text_surf = self.font_stats.render(text, True, (200, 200, 200))
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y_start))
            self.screen.blit(text_surf, text_rect)
            y_start += 50

        # 重新开始按钮
        button_rect = pygame.Rect(0, 0, 280, 70)
        button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos)

        # 按钮样式
        button_color = COLOR_BUTTON_HOVER if is_hover else COLOR_BUTTON
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_DEATH_RED, button_rect.inflate(-10, -10), border_radius=5)

        # 按钮文字
        text_surf = self.font_stats.render("重新开始", True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)

        return button_rect


# ---------- 商店界面 ----------
def shop_screen(screen, player, floor):
    # 使用半透明遮罩层实现模态对话框效果
    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()
    running = True

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # 半透明黑色背景

    shop_window = pygame.Surface((400, 380))
    shop_rect = shop_window.get_rect(center=screen.get_rect().center)

    while running:
        clock.tick(15)

        # 绘制背景遮罩
        screen.blit(overlay, (0, 0))

        # 绘制商店窗口
        shop_window.fill((50, 50, 50))
        title = font.render("[游戏商店]", True, COLOR_TEXT)
        shop_window.blit(title, (20, 20))

        # 显示商店选项
        option1 = font.render(f"1. 生命值 +{1000 * floor} (花费 {100 * floor} 金币)", True, COLOR_TEXT)
        option2 = font.render(f"2. 攻击力 +{5 * floor} (花费 {100 * floor} 金币)", True, COLOR_TEXT)
        option3 = font.render(f"3. 防御力 +{5 * floor} (花费 {100 * floor} 金币)", True, COLOR_TEXT)
        option4 = font.render(f"4. 生命值 +{10000 * floor} (花费 {1000 * floor} 金币)", True, COLOR_TEXT)
        option5 = font.render(f"5. 攻击力 +{50 * floor} (花费 {1000 * floor} 金币)", True, COLOR_TEXT)
        option6 = font.render(f"6. 防御力 +{50 * floor} (花费 {1000 * floor} 金币)", True, COLOR_TEXT)

        shop_window.blit(option1, (20, 60))
        shop_window.blit(option2, (20, 100))
        shop_window.blit(option3, (20, 140))
        shop_window.blit(option4, (20, 180))
        shop_window.blit(option5, (20, 220))
        shop_window.blit(option6, (20, 260))

        info = font.render(f"当前金币: [{player.inventory.gold}]", True, (255, 255, 0))
        shop_window.blit(info, (20, 300))

        prompt = font.render("按数字键购买，按ESC退出", True, COLOR_TEXT)
        shop_window.blit(prompt, (20, 340))

        # 将商店窗口居中显示
        screen.blit(shop_window, shop_rect.topleft)
        pygame.display.flip()

        # 处理输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    if player.inventory.gold >= 100 * floor:
                        player.health = min(player.health + 1000 * floor, player.max_health)
                        player.inventory.gold -= 100 * floor
                elif event.key == pygame.K_2:
                    if player.inventory.gold >= 100 * floor:
                        player.base_attack += 5 * floor
                        player.attack += 5 * floor
                        player.inventory.gold -= 100 * floor
                elif event.key == pygame.K_3:
                    if player.inventory.gold >= 100 * floor:
                        player.base_defense += 5 * floor
                        player.defense += 5 * floor
                        player.inventory.gold -= 100 * floor
                elif event.key == pygame.K_4:
                    if player.inventory.gold >= 1000 * floor:
                        player.health = min(player.health + 10000 * floor, player.max_health)
                        player.inventory.gold -= 1000 * floor
                elif event.key == pygame.K_5:
                    if player.inventory.gold >= 1000 * floor:
                        player.base_attack += 50 * floor
                        player.attack += 50 * floor
                        player.inventory.gold -= 1000 * floor
                elif event.key == pygame.K_6:
                    if player.inventory.gold >= 1000 * floor:
                        player.base_defense += 50 * floor
                        player.defense += 50 * floor
                        player.inventory.gold -= 1000 * floor


# ---------- 游戏类 ----------
class Game:
    def __init__(self):
        # 初始化
        pygame.init()
        pygame.display.set_caption("魔塔地下城")

        # 创建窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),
                                              pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.game_state = "menu"  # menu, playing, settings, dead
        self.main_menu = MainMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen)
        self.death_screen = None

        # 重置游戏
        self.reset_game()

    def reset_game(self):
        # 游戏数据
        self.floor = 1
        self.world_map = WorldMap(MAP_WIDTH, MAP_HEIGHT)
        self.player = Player("勇者", 1, 1)
        self.camera = Camera(MAP_WIDTH, MAP_HEIGHT)
        self.ui = UI(self.player)

        # 放置玩家到起点
        floor_tiles = [(x, y) for (x, y), terrain in self.world_map.map_data.items()
                       if terrain == TerrainType.FLOOR]
        if floor_tiles:
            self.player.x, self.player.y = random.choice(floor_tiles)

        # 放置实体
        self.world_map.place_entities(self.player, self.floor)

        # 特殊效果
        self.skill_effects = []

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # 转换为秒

            if self.game_state == "menu":
                self.handle_menu()
            elif self.game_state == "settings":
                self.handle_settings()
            elif self.game_state == "playing":
                self.handle_playing(dt)
            elif self.game_state == "dead":
                self.handle_dead()

            pygame.display.flip()

    def handle_menu(self):
        button_rects = self.main_menu.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rects[0].collidepoint(event.pos):  # 开始按钮
                    self.game_state = "playing"
                    self.reset_game()
                elif button_rects[1].collidepoint(event.pos):  # 设置按钮
                    self.game_state = "settings"

    def handle_settings(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            result = self.settings_menu.handle_event(event)
            if result == "menu":
                self.game_state = "menu"
            elif result == "apply":
                # 重置游戏
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.reset_game()
                self.game_state = "menu"

        self.settings_menu.draw()

    def handle_playing(self, dt):
        # 处理输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 根据UI状态处理输入
            if self.ui.show_inventory:
                self.ui.handle_inventory_input(event, self.player)
            elif self.ui.show_merchant:
                mouse_pos = pygame.mouse.get_pos()
                self.ui.handle_merchant_input(event, self.player, mouse_pos)
            elif self.ui.dialogue_active:
                self.ui.handle_dialogue_input(event)
            else:
                # 常规游戏输入
                self.handle_game_input(event)

        # 更新游戏状态
        if self.game_state == "playing":
            # 更新玩家
            self.player.update()

            # 更新特殊效果
            for effect in self.skill_effects[:]:
                if not effect.update(dt):
                    self.skill_effects.remove(effect)

            # 更新世界和实体
            message, effect = self.world_map.update(self.player, dt)
            if message:
                self.ui.add_message(message)
            if effect:
                self.skill_effects.append(effect)

            # 更新UI
            self.ui.update(dt)

            # 更新相机
            self.camera.update(self.player.x, self.player.y)

            # 检查是否到达出口
            if (self.player.x, self.player.y) == self.world_map.exit_pos:
                self.next_floor()

            # 检查玩家是否死亡
            if self.player.health <= 0:
                self.game_state = "dead"
                self.death_screen = DeathScreen(self.screen, self.player, self.floor)

        # 绘制游戏
        self.draw()

    def handle_dead(self):
        button_rect = self.death_screen.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    self.game_state = "menu"
                    self.reset_game()

    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            # 动作限制检查
            in_stun = pygame.time.get_ticks() < self.player.debuffs.get('stun_end', 0)
            in_paralyze = pygame.time.get_ticks() < self.player.debuffs.get('paralyze_end', 0)
            frozen = self.player.debuffs.get('frozen_area', False)

            if in_stun:
                self.ui.add_message("眩晕中无法行动")
                return
            elif in_paralyze:
                self.ui.add_message("麻痹中无法行动")
                return
            elif frozen:
                self.ui.add_message("冰冻区域无法移动")
                return

            # 移动 (WASD或方向键)
            if event.key in [pygame.K_w, pygame.K_UP]:
                self.player.move(0, -1, self.world_map)
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                self.player.move(0, 1, self.world_map)
            elif event.key in [pygame.K_a, pygame.K_LEFT]:
                self.player.move(-1, 0, self.world_map)
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.player.move(1, 0, self.world_map)

            # 背包 (I)
            elif event.key == pygame.K_i:
                self.ui.show_inventory = not self.ui.show_inventory
                self.ui.selected_inv_item = 0

            # 互动 (E)
            elif event.key == pygame.K_e:
                self.interact()

            # 商店 (B)
            elif event.key == pygame.K_b:
                shop_screen(self.screen, self.player, self.floor)

            # 技能快捷键 (1-5)
            elif pygame.K_1 <= event.key <= pygame.K_5:
                skill_index = event.key - pygame.K_1
                if skill_index < len(self.player.skills):
                    # 自动选择最近的敌人作为目标
                    nearest = self.find_nearest_enemy()
                    success, message = self.player.use_skill(skill_index, nearest)
                    self.ui.add_message(message)
                    if success:
                        self.player.reduce_equipment_durability()

            # 退出游戏 (ESC)
            elif event.key == pygame.K_ESCAPE:
                self.game_state = "menu"

    def find_nearest_enemy(self):
        """寻找最近的敌人"""
        nearest = None
        min_dist = float('inf')
        for entity in self.world_map.entities:
            if isinstance(entity, Monster) and entity.alive:
                dist = abs(entity.x - self.player.x) + abs(entity.y - self.player.y)
                if dist < min_dist:
                    min_dist = dist
                    nearest = entity
        return nearest

    def interact(self):
        """与周围实体互动"""
        directions = [
            (0, -1),  # 上
            (1, 0),  # 右
            (0, 1),  # 下
            (-1, 0)  # 左
        ]

        for dx, dy in directions:
            check_x = self.player.x + dx
            check_y = self.player.y + dy
            for entity in self.world_map.entities:
                if (entity.x == check_x and entity.y == check_y and
                        isinstance(entity, (NPC, Item))):
                    if isinstance(entity, NPC):
                        self.handle_npc_interaction(entity)
                        return
                    elif isinstance(entity, Item):
                        self.handle_item_interaction(entity)
                        return
        self.ui.add_message("附近没有可互动的对象")

    def handle_npc_interaction(self, npc):
        """处理与NPC的互动"""
        self.ui.dialogue_active = True
        self.ui.current_npc = npc
        message = npc.talk()
        self.ui.add_message(message)

    def handle_item_interaction(self, item):
        """处理物品互动"""
        success, message = self.player.inventory.add_item(item)
        if success:
            self.world_map.entities.remove(item)
        self.ui.add_message(message)

    def next_floor(self):
        """进入下一层"""
        self.floor += 1
        self.ui.add_message(f"进入第 {self.floor} 层！")

        # 生成新地图
        self.world_map = WorldMap(MAP_WIDTH, MAP_HEIGHT)
        self.world_map.place_entities(self.player, self.floor)

        # 重置玩家位置到新地图起点
        floor_tiles = [(x, y) for (x, y), terrain in self.world_map.map_data.items()
                       if terrain == TerrainType.FLOOR]
        if floor_tiles:
            self.player.x, self.player.y = random.choice(floor_tiles)

        # 每5层触发商店
        if self.floor % 5 == 0:
            shop_screen(self.screen, self.player, self.floor)

    def draw(self):
        """绘制整个游戏画面"""
        # 绘制世界地图
        self.world_map.draw(self.screen, self.camera.offset_x, self.camera.offset_y)

        # 绘制技能特效
        for effect in self.skill_effects:
            effect.draw(self.screen)

        # 绘制玩家
        self.player.draw(self.screen, self.camera.offset_x, self.camera.offset_y)

        # 绘制UI
        self.ui.draw(self.screen)

        # 在小地图上绘制出口位置
        exit_x, exit_y = self.world_map.exit_pos
        pygame.draw.rect(self.screen, COLOR_EXIT,
                         (exit_x * TILE_SIZE - self.camera.offset_x,
                          exit_y * TILE_SIZE - self.camera.offset_y,
                          TILE_SIZE, TILE_SIZE))


if __name__ == "__main__":
    game = Game()
    game.run()