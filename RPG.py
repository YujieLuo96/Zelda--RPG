from enum import Enum
import pygame
import random
import math
from pygame.locals import *
from collections import defaultdict
import copy
from perlin_noise import PerlinNoise  # 需要安装 perlin-noise 库

# 颜色定义
COLORS = {
    # Existing colors
    "grass": (34, 139, 34),  # 草原青草
    "mud": (139, 115, 85),  # 泥土地
    "small_tree": (0, 100, 0),  # 小树
    "dark_grass": (16, 56, 16),  # 深色草丛
    "big_tree": (0, 50, 0),  # 大树
    "thorns": (139, 139, 0),  # 荆棘
    "rock": (128, 128, 128),  # 岩石
    "sandstone": (210, 180, 140),  # 砂岩
    "sand": (244, 164, 96),  # 沙漠
    "basalt": (75, 75, 75),  # 玄武岩
    "lava": (255, 69, 0),  # 熔岩
    "water": (30, 144, 255),  # 水

    # New colors
    "shallow_water": (100, 185, 237),  # 浅水
    "cliff": (90, 90, 90),  # 悬崖
    "meadow": (124, 252, 0),  # 草甸
    "swamp": (53, 94, 59),  # 沼泽
    "house_grass": (160, 82, 45),  # 草原房屋
    "house_forest": (101, 67, 33),  # 森林房屋
    "house_desert": (205, 133, 63),  # 沙漠房屋
    "house_volcano": (153, 76, 0),  # 火山房屋
    "village_center": (210, 105, 30),  # 村庄中心
    "path": (222, 184, 135),  # 道路/小径

    # Existing non-terrain colors
    "player": (0, 0, 255),
    "enemy": (255, 0, 0),
    "item": (255, 255, 0),
    "crit": (255, 165, 0),
    "ui_bg": (30, 30, 30, 200),  # UI背景色
    "ui_text": (255, 255, 255),  # UI文字颜色
    "coin_gold": (255, 215, 0),
    "coin_silver": (192, 192, 192),
    "coin_copper": (184, 115, 51),
    "npc": (0, 255, 255),
    "potion_red": (255, 0, 0),
    "potion_blue": (0, 0, 255),
}

# 游戏配置
TILE_SIZE = 2
PLAYER_SPEED = 5
SCREEN_WIDTH, SCREEN_HEIGHT = 2400, 1200
CHUNK_SIZE = 32  # 每个区块包含16x16的瓷砖

# 生态系统类型
class Ecosystem(Enum):
    GRASSLAND = 1  # 草原泥土地
    DARK_FOREST = 2  # 黑森林
    DESERT = 3  # 山岭地带
    VOLCANO = 4  # 沙漠熔岩地

# 生态系统生成参数
ECOSYSTEM_OCTAVES = 4      # 噪声的octave数
ECOSYSTEM_SCALE = 100 * TILE_SIZE    # 控制生态系统的规模
MOUNTAIN_HEIGHT_THRESHOLD = 0.7  # 熔岩生态系统最小高度阈值
ECOSYSTEM_SEED = 12345     # 生态系统噪声种子

# 生态系统类型对应的噪声阈值范围
ECOSYSTEM_THRESHOLDS = {
    Ecosystem.GRASSLAND: (-0.8, -0.2),  # 草原泥土地
    Ecosystem.DARK_FOREST: (-0.2, 0.3), # 黑森林
    Ecosystem.DESERT: (0.3, 0.6),     # 山岭地带
    Ecosystem.VOLCANO: (0.6, 1.0)   # 沙漠熔岩地
}

# 地形类型
class Terrain(Enum):
    GRASS = 0       # 草原青草
    MUD = 1         # 泥土地
    SMALL_TREE = 2  # 小树
    DARK_GRASS = 3  # 深色草丛
    BIG_TREE = 4    # 大树
    THORNS = 5      # 荆棘
    ROCK = 6        # 岩石
    SANDSTONE = 7   # 砂岩
    SAND = 8        # 沙漠
    BASALT = 9      # 玄武岩
    LAVA = 10       # 熔岩
    WATER = 11      # 水
    SHALLOW_WATER = 12  # 浅水
    CLIFF = 13      # 悬崖
    MEADOW = 14     # 草甸
    SWAMP = 15      # 沼泽
    HOUSE_GRASS = 16  # 草原房屋
    HOUSE_FOREST = 17  # 森林房屋
    HOUSE_DESERT = 18  # 沙漠房屋
    HOUSE_VOLCANO = 19  # 火山房屋
    VILLAGE_CENTER = 20  # 村庄中心
    PATH = 21       # 道路/小径

# 地形通行性配置
TERRAIN_PASSABLE = {
    Terrain.GRASS: True,
    Terrain.MUD: True,
    Terrain.SMALL_TREE: True,
    Terrain.DARK_GRASS: True,
    Terrain.BIG_TREE: False,  # Changed to False for better gameplay
    Terrain.THORNS: False,    # Changed to False for better gameplay
    Terrain.ROCK: False,      # Changed to False for better gameplay
    Terrain.SANDSTONE: True,
    Terrain.SAND: True,
    Terrain.BASALT: False,    # Changed to False for better gameplay
    Terrain.LAVA: False,      # Changed to False (lava should be dangerous)
    Terrain.WATER: False,     # Changed to False (can't walk on water)
    Terrain.SHALLOW_WATER: True,  # You can walk in shallow water
    Terrain.CLIFF: False,     # You can't walk on cliffs
    Terrain.MEADOW: True,
    Terrain.SWAMP: True,      # Can walk, but maybe should slow down the player
    Terrain.HOUSE_GRASS: True,
    Terrain.HOUSE_FOREST: True,
    Terrain.HOUSE_DESERT: True,
    Terrain.HOUSE_VOLCANO: True,
    Terrain.VILLAGE_CENTER: True,
    Terrain.PATH: True,
}


# 在所有生态系统地形权重
ECOSYSTEM_TERRAIN_WEIGHTS = {
    Ecosystem.GRASSLAND: [
        (Terrain.GRASS, 75),
        (Terrain.MUD, 10),
        (Terrain.SMALL_TREE, 5),
        (Terrain.MEADOW, 10)
    ],
    Ecosystem.DARK_FOREST: [
        (Terrain.DARK_GRASS, 35),
        (Terrain.BIG_TREE, 45),
        (Terrain.THORNS, 5),
        (Terrain.SWAMP, 15)
    ],
    Ecosystem.DESERT: [
        (Terrain.ROCK, 10),
        (Terrain.SAND, 65),
        (Terrain.SANDSTONE, 20),
        (Terrain.CLIFF, 5)
    ],
    Ecosystem.VOLCANO: [
        (Terrain.BASALT, 65),
        (Terrain.ROCK, 20),
        (Terrain.LAVA, 10),
        (Terrain.CLIFF, 5)
    ]
}


# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("像素RPG")
clock = pygame.time.Clock()

# 建筑生成

class Building:
    def __init__(self, position, building_type, size=(3, 3)):
        """
        Initialize a building structure

        Args:
            position (tuple): (x, y) coordinates for the building center
            building_type (Terrain): The terrain type for this building
            size (tuple): Width and height of the building in tiles
        """
        self.position = position
        self.type = building_type
        self.size = size
        self.tiles = set()  # Set of tile positions that make up the building
        self.generate_structure()

    def generate_structure(self):
        """Generate the building's structure and add tiles to the set"""
        center_x, center_y = self.position
        width, height = self.size

        # Calculate the top-left corner
        start_x = center_x - (width // 2)
        start_y = center_y - (height // 2)

        # Add building tiles
        for y in range(height):
            for x in range(width):
                self.tiles.add((start_x + x, start_y + y))

        # Add paths leading to the building
        self.add_paths()

    def add_paths(self):
        """Add paths leading to/from the building"""
        center_x, center_y = self.position

        # Determine path length (random between 3-7 tiles)
        path_length = random.randint(3, 7)

        # Choose a random direction for the path (0=North, 1=East, 2=South, 3=West)
        direction = random.randint(0, 3)

        # Add path tiles
        if direction == 0:  # North
            for i in range(1, path_length + 1):
                self.tiles.add((center_x, center_y - (self.size[1] // 2) - i))
        elif direction == 1:  # East
            for i in range(1, path_length + 1):
                self.tiles.add((center_x + (self.size[0] // 2) + i, center_y))
        elif direction == 2:  # South
            for i in range(1, path_length + 1):
                self.tiles.add((center_x, center_y + (self.size[1] // 2) + i))
        else:  # West
            for i in range(1, path_length + 1):
                self.tiles.add((center_x - (self.size[0] // 2) - i, center_y))

# 新增枚举类型
class WeaponType(Enum):
    SPEAR = 1  # 枪
    DAGGER = 2  # 匕首
    GREATSWORD = 3  # 大剑
    SHORTSWORD = 4  # 短剑


class SkillType(Enum):
    FIREBALL = 1
    HEAL = 2
    CHARGE = 3
    POISON = 4


class MonsterType(Enum):
    WOLF = 1
    GOBLIN = 2
    TROLL = 3
    DRAGON = 4


class ItemType(Enum):
    WEAPON = 1
    ARMOR = 2
    POTION = 3
    COIN = 4

# 生态系统 --------------------------------------------------

# 生态系统商店配置
ECOSYSTEM_SHOPS = {
    Ecosystem.GRASSLAND: {
        "items": [
            (ItemType.POTION, {"potion_red": 0.7, "potion_blue": 0.3}),
            (ItemType.WEAPON, {WeaponType.SHORTSWORD: 0.6, WeaponType.SPEAR: 0.4}),
            (ItemType.ARMOR, {"leather": 1.0})
        ],
        "color": (0, 255, 0)  # 绿色主题
    },
    Ecosystem.DARK_FOREST: {
        "items": [
            (ItemType.POTION, {"potion_red": 0.4, "potion_blue": 0.6}),
            (ItemType.WEAPON, {WeaponType.DAGGER: 0.8, WeaponType.SHORTSWORD: 0.2}),
            (ItemType.ARMOR, {"chainmail": 1.0})
        ],
        "color": (0, 100, 0)  # 深绿主题
    },
    Ecosystem.DESERT: {
        "items": [
            (ItemType.POTION, {"potion_red": 0.5, "potion_blue": 0.5}),
            (ItemType.WEAPON, {WeaponType.GREATSWORD: 0.7, WeaponType.SPEAR: 0.3}),
            (ItemType.ARMOR, {"plate": 1.0})
        ],
        "color": (128, 128, 128)  # 灰色主题
    },
    Ecosystem.VOLCANO: {
        "items": [
            (ItemType.POTION, {"potion_red": 0.9, "potion_blue": 0.1}),
            (ItemType.WEAPON, {WeaponType.GREATSWORD: 0.5, WeaponType.SPEAR: 0.5}),
            (ItemType.ARMOR, {"plate": 0.7, "chainmail": 0.3})
        ],
        "color": (255, 69, 0)  # 熔岩主题
    }
}

def get_ecosystem_value(gx, gy):
    """生成连贯的生态系统值"""
    value = (math.sin(gx * 0.01) + math.sin(gy * 0.01) +
             math.sin((gx + gy) * 0.05) * 0.5 +
             math.sin(gx * 0.02) * 0.5 +
             math.cos(gy * 0.03) * 0.5)
    return (value + 4) / 8  # 归一化到0-1之间


def get_ecosystem_blend(gx, gy):
    """获取生态系统的混合权重（增加山地区域连贯性）

    参数:
        gx (int): 全局X坐标
        gy (int): 全局Y坐标

    返回:
        list: 包含生态系统和对应权重的列表
    """
    # 使用Perlin噪声生成基础生态系统值
    value = (math.sin(gx * 0.01) + math.sin(gy * 0.01) +
             math.sin((gx + gy) * 0.05) * 0.5 +
             math.sin(gx * 0.02) * 0.5 +
             math.cos(gy * 0.03) * 0.5)
    value = (value + 4) / 8  # 归一化到0-1之间
    value = max(0.0, min(1.0, value))  # 确保值在0-1之间

    # 根据value值确定生态系统混合权重
    if value < 0.25:
        # 草原区域
        return [(Ecosystem.GRASSLAND, 1.0)]
    elif value < 0.35:
        # 草原到黑森林的过渡
        weight = (0.35 - value) / 0.1
        return [(Ecosystem.GRASSLAND, weight), (Ecosystem.DARK_FOREST, 1 - weight)]
    elif value < 0.55:
        # 黑森林区域
        return [(Ecosystem.DARK_FOREST, 1.0)]
    elif value < 0.65:
        # 黑森林到山地的过渡
        weight = (0.65 - value) / 0.1
        return [(Ecosystem.DARK_FOREST, weight), (Ecosystem.DESERT, 1 - weight)]
    elif value < 0.75:
        # 山地到熔岩地的过渡（新增）
        weight = (0.75 - value) / 0.1
        return [(Ecosystem.DESERT, weight), (Ecosystem.VOLCANO, 1 - weight)]
    elif value < 0.85:
        # 熔岩地区域
        return [(Ecosystem.VOLCANO, 1.0)]
    else:
        # 极端熔岩地区域（新增）
        return [(Ecosystem.VOLCANO, 1.0)]


def get_combined_weights(blend):
    """合并不同生态系统的地形权重"""
    combined = {}
    for ecosystem, weight in blend:
        for terrain, prob in ECOSYSTEM_TERRAIN_WEIGHTS[ecosystem]:
            combined[terrain] = combined.get(terrain, 0) + prob * weight
    return list(combined.items())


def choose_terrain(weights):
    """根据权重随机选择地形"""
    total = sum(w for _, w in weights)
    r = random.uniform(0, total)
    current = 0
    for terrain, weight in weights:
        current += weight
        if r < current:
            return terrain
    return weights[-1][0]

# 地图生成 --------------------------------------------------

class Camera:
    def __init__(self):
        self.camera = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.smooth_speed = 5

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + SCREEN_WIDTH // 2
        y = -target.rect.y + SCREEN_HEIGHT // 2
        self.camera.x += (x - self.camera.x) / self.smooth_speed
        self.camera.y += (y - self.camera.y) / self.smooth_speed

    def collidepoint(self, point):
        """检查点是否在相机范围内"""
        return self.camera.collidepoint(point)


class GameMap:
    def __init__(self):
        self.terrain_map = {}  # 存储地形数据
        self.chunk_size = CHUNK_SIZE  # 区块大小
        self.river_network = set()  # 河流坐标
        self.lake_areas = set()  # 湖泊坐标
        self.generated_chunks = set()  # 记录已生成的区块
        self.buildings = {}  # Dictionary to store building structures keyed by chunk coordinates

        # 初始化随机种子
        self.seed = random.randint(0, 999999)
        detail_seed = 7 * self.seed % 117
        river_seed = 13 * self.seed % 91
        cliff_seed = 19 * self.seed % 67
        building_seed = 23 * self.seed % 73

        # 地形高度噪声生成器
        self.base_noise = PerlinNoise(octaves=2, seed=self.seed)
        self.detail_noise = PerlinNoise(octaves=4, seed=detail_seed)
        self.river_noise = PerlinNoise(octaves=3, seed=river_seed)
        self.cliff_noise = PerlinNoise(octaves=5, seed=cliff_seed)
        self.building_noise = PerlinNoise(octaves=2, seed=building_seed)

        # 噪声参数
        self.height_scale = 256.0  # 增大采样范围
        self.detail_scale = 64.0  # 细节噪声采样范围
        self.river_scale = 150.0  # 河流噪声采样范围
        self.cliff_scale = 100.0  # 悬崖噪声采样范围
        self.building_scale = 500.0  # 建筑物噪声采样范围
        self.detail_strength = 0.3  # 细节噪声强度
        self.mountain_threshold = 0.35  # 山地阈值
        self.river_threshold = 0.92  # 河流生成阈值
        self.building_threshold = 0.85  # 建筑物生成阈值

        # 独立生态系统噪声生成器
        self.ecosystem_noise = PerlinNoise(
            octaves=ECOSYSTEM_OCTAVES,
            seed=self.seed + 2  # 使用独立随机种子
        )

        # Village generation parameters
        self.village_density = 0.02  # Chance of village center per chunk
        self.building_cluster_radius = 15  # Radius for building clusters around village centers
        self.min_building_distance = 5  # Minimum distance between buildings
        self.village_buildings = {}  # Dictionary to track village centers and surrounding buildings

    def get_height(self, x, y):
        """获取平滑的高度值（0-1）"""
        # 基础低频噪声（大范围变化）
        base = self.base_noise([x / self.height_scale, y / self.height_scale])

        # 高频细节噪声（小范围变化）
        detail = self.detail_noise([x / self.detail_scale, y / self.detail_scale])

        # 混合噪声（细节噪声影响较小）
        height = base + detail * self.detail_strength

        # 使用smoothstep函数柔化过渡
        height = self.smoothstep(height)

        # 归一化到0-1范围
        return height

    def get_river_value(self, x, y):
        """获取河流噪声值"""
        return self.river_noise([x / self.river_scale, y / self.river_scale])

    def get_cliff_value(self, x, y):
        """获取悬崖噪声值"""
        return self.cliff_noise([x / self.cliff_scale, y / self.cliff_scale])

    def get_building_value(self, x, y):
        """获取建筑物噪声值"""
        return self.building_noise([x / self.building_scale, y / self.building_scale])

    def smoothstep(self, value):
        """S曲线过渡函数"""
        value = max(0, min(1, (value + 1) / 2))  # 先归一化到0-1
        return value * value * (3 - 2 * value)

    def smooth_transition(self, value, start, end):
        """平滑过渡计算"""
        t = (value - start) / (end - start)
        t = max(0, min(1, t))
        return t * t * (3 - 2 * t)  # 三次平滑曲线

    def is_valid_spawn_position(self, x, y):
        """
        检查某个位置是否适合生成敌人或 NPC。
        返回 True 如果位置有效（不在水中或岩浆中），否则返回 False。
        """
        terrain = self.get_terrain(x, y)
        # If the terrain is water, lava, cliff, or any other impassable terrain, it's invalid
        return TERRAIN_PASSABLE.get(terrain, True)

    def is_valid_building_position(self, x, y, size_x=3, size_y=3):
        """
        检查位置是否适合放置建筑物

        Args:
            x, y: 建筑物中心位置
            size_x, size_y: 建筑物尺寸

        Returns:
            Boolean: 是否是有效的建筑位置
        """
        # Check if the entire building footprint is on valid terrain
        start_x = x - (size_x // 2)
        start_y = y - (size_y // 2)

        for check_y in range(start_y, start_y + size_y):
            for check_x in range(start_x, start_x + size_x):
                terrain = self.get_terrain(check_x, check_y)

                # Cannot build on water, lava, cliff, or existing structures
                if terrain in (Terrain.WATER, Terrain.LAVA, Terrain.CLIFF,
                               Terrain.SHALLOW_WATER, Terrain.BIG_TREE,
                               Terrain.HOUSE_GRASS, Terrain.HOUSE_FOREST,
                               Terrain.HOUSE_DESERT, Terrain.HOUSE_VOLCANO,
                               Terrain.VILLAGE_CENTER):
                    return False

        # Check for nearby buildings (avoid overcrowding)
        for b_chunk in self.buildings.values():
            for building in b_chunk:
                if abs(building.position[0] - x) < self.min_building_distance and \
                        abs(building.position[1] - y) < self.min_building_distance:
                    return False

        return True

    def determine_ecosystem(self, gx, gy, height):
        """根据坐标和高度确定生态系统（改进版）"""
        # 高海拔区域强制为熔岩生态系统
        if height >= MOUNTAIN_HEIGHT_THRESHOLD:
            return Ecosystem.VOLCANO

        # 河流和湖泊区域
        if (gx, gy) in self.river_network or (gx, gy) in self.lake_areas:
            # Determine the ecosystem for water features based on surroundings
            # Sample ecosystem values in a 3x3 area around the water
            ecosystem_votes = []
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue

                    # Get the ecosystem value at this surrounding tile
                    eco_value = self.ecosystem_noise([(gx + dx) / ECOSYSTEM_SCALE, (gy + dy) / ECOSYSTEM_SCALE])

                    # Convert to ecosystem type
                    if eco_value < -0.23:
                        ecosystem_votes.append(Ecosystem.DARK_FOREST)
                    elif eco_value < 0.1:
                        ecosystem_votes.append(Ecosystem.GRASSLAND)
                    elif eco_value < 0.5:
                        ecosystem_votes.append(Ecosystem.DESERT)
                    else:
                        ecosystem_votes.append(Ecosystem.VOLCANO)

            # Return the most common ecosystem
            if ecosystem_votes:
                return max(set(ecosystem_votes), key=ecosystem_votes.count)

        # 其他区域根据生态系统噪声确定
        eco_value = self.ecosystem_noise([gx / ECOSYSTEM_SCALE, gy / ECOSYSTEM_SCALE])

        # Enhanced thresholds with more natural distribution
        if eco_value < -0.23:
            return Ecosystem.DARK_FOREST
        elif eco_value < 0.1:
            return Ecosystem.GRASSLAND
        elif eco_value < 0.5:
            return Ecosystem.DESERT
        else:
            return Ecosystem.VOLCANO

    def generate_rivers(self, chunk_x, chunk_y):
        """Generate rivers within a chunk using improved flow algorithm"""
        chunk_start_x = chunk_x * self.chunk_size
        chunk_start_y = chunk_y * self.chunk_size

        # Check if this chunk might have a river (optimization)
        chunk_center_x = chunk_start_x + self.chunk_size // 2
        chunk_center_y = chunk_start_y + self.chunk_size // 2
        chunk_river_value = abs(self.get_river_value(chunk_center_x, chunk_center_y))

        if chunk_river_value < 0.85:  # Skip chunks unlikely to have rivers
            return set()

        # River generation for this chunk
        river_tiles = set()
        for y in range(chunk_start_y, chunk_start_y + self.chunk_size):
            for x in range(chunk_start_x, chunk_start_x + self.chunk_size):
                # Get river noise value
                river_value = abs(self.get_river_value(x, y))

                # River main channels (high threshold for main waterways)
                if river_value > self.river_threshold:
                    river_tiles.add((x, y))

                    # River banks (shallow water)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        bank_x, bank_y = x + dx, y + dy
                        if (bank_x, bank_y) not in river_tiles:
                            # Use a lower threshold for river banks
                            if abs(self.get_river_value(bank_x, bank_y)) > self.river_threshold - 0.04:
                                # Add as shallow water
                                self.shallow_water_tiles.add((bank_x, bank_y))

        return river_tiles

    def generate_lakes(self, chunk_x, chunk_y):
        """Generate lakes within a chunk"""
        chunk_start_x = chunk_x * self.chunk_size
        chunk_start_y = chunk_y * self.chunk_size

        lake_tiles = set()
        self.shallow_water_tiles = set()  # Initialize set for shallow water

        # Use height and river values to determine lake placement
        for y in range(chunk_start_y, chunk_start_y + self.chunk_size):
            for x in range(chunk_start_x, chunk_start_x + self.chunk_size):
                height = self.get_height(x, y)

                # Lakes form in low areas
                if height < 0.31:
                    # Deep water in very low areas
                    if height < 0.28:
                        lake_tiles.add((x, y))
                    # Shallow water around lakes
                    elif height < 0.31:
                        self.shallow_water_tiles.add((x, y))

        return lake_tiles

    def generate_base_terrain(self, chunk_x, chunk_y):
        """生成基础地形（改进版）"""
        chunk = []
        # Add shallow water tracking for this chunk
        self.shallow_water_tiles = set()

        # Generate rivers and lakes for this chunk
        river_tiles = self.generate_rivers(chunk_x, chunk_y)
        lake_tiles = self.generate_lakes(chunk_x, chunk_y)

        # Update global water networks
        self.river_network.update(river_tiles)
        self.lake_areas.update(lake_tiles)

        # Generate village center if appropriate
        village_center = None
        if random.random() < self.village_density:
            # Try to place a village center in this chunk
            center_x = chunk_x * self.chunk_size + random.randint(5, self.chunk_size - 6)
            center_y = chunk_y * self.chunk_size + random.randint(5, self.chunk_size - 6)

            if self.is_valid_building_position(center_x, center_y, 5, 5):
                village_center = (center_x, center_y)
                self.village_buildings[(chunk_x, chunk_y)] = village_center

        for local_y in range(self.chunk_size):
            row = []
            for local_x in range(self.chunk_size):
                gx = chunk_x * self.chunk_size + local_x
                gy = chunk_y * self.chunk_size + local_y

                # Check if this tile is part of a river or lake
                if (gx, gy) in river_tiles or (gx, gy) in lake_tiles:
                    row.append(Terrain.WATER)
                    continue

                # Check if this tile is shallow water
                if (gx, gy) in self.shallow_water_tiles:
                    row.append(Terrain.SHALLOW_WATER)
                    continue

                # Check if this is a village center
                if village_center and gx == village_center[0] and gy == village_center[1]:
                    row.append(Terrain.VILLAGE_CENTER)
                    continue

                # 生成高度值
                height = self.get_height(gx, gy)

                # Cliffs based on height gradient and cliff noise
                cliff_value = self.get_cliff_value(gx, gy)
                if height > 0.6 and cliff_value > 0.7:
                    row.append(Terrain.CLIFF)
                    continue

                # 确定生态系统
                ecosystem = self.determine_ecosystem(gx, gy, height)

                # Generate base terrain based on ecosystem and height
                if height < 0.35:
                    if height < 0.29:
                        terrain = Terrain.WATER
                    elif height < 0.31:
                        terrain = Terrain.SHALLOW_WATER
                    else:
                        # Low-lying areas near water can be swampy or muddy
                        if ecosystem == Ecosystem.DARK_FOREST:
                            terrain = random.choice([Terrain.SWAMP, Terrain.MUD])
                        else:
                            mud_weight = self.smooth_transition(height, 0.31, 0.35)
                            terrain = random.choices(
                                [Terrain.GRASS, Terrain.MUD],
                                weights=[mud_weight * 100, (1 - mud_weight) * 100]
                            )[0]
                elif height < 0.6:
                    # 低地区域，使用生态系统对应的低地地形
                    weights = ECOSYSTEM_TERRAIN_WEIGHTS[ecosystem]
                    terrain = choose_terrain(weights)

                    # Add meadows in grassland (more natural distribution)
                    if ecosystem == Ecosystem.GRASSLAND and random.random() < 0.2:
                        terrain = Terrain.MEADOW

                    # Add more swamps in dark forest
                    if ecosystem == Ecosystem.DARK_FOREST and height < 0.4 and random.random() < 0.3:
                        terrain = Terrain.SWAMP
                else:
                    # 高地区域，根据生态系统生成不同岩石
                    if ecosystem in [Ecosystem.GRASSLAND, Ecosystem.DARK_FOREST]:
                        terrain = Terrain.ROCK
                    elif ecosystem == Ecosystem.DESERT:
                        terrain = Terrain.SANDSTONE
                    elif ecosystem == Ecosystem.VOLCANO:
                        terrain = Terrain.BASALT

                # Place paths (if near village center)
                if village_center:
                    distance_to_village = math.sqrt((gx - village_center[0]) ** 2 + (gy - village_center[1]) ** 2)
                    if distance_to_village <= 20:  # Maximum path distance from village center
                        # Use noise to create organic paths
                        path_noise = self.building_noise([gx / 10, gy / 10])
                        if abs(path_noise) < 0.05 and terrain not in [Terrain.WATER, Terrain.LAVA, Terrain.CLIFF]:
                            terrain = Terrain.PATH

                row.append(terrain)
            chunk.append(row)

        # Post-process the chunk
        chunk = self.post_process_chunk(chunk)

        # Generate buildings after terrain is established
        self.generate_buildings(chunk_x, chunk_y, chunk, village_center)

        return chunk

    def generate_buildings(self, chunk_x, chunk_y, chunk, village_center=None):
        """
        Generate buildings within a chunk

        Args:
            chunk_x, chunk_y: Chunk coordinates
            chunk: The terrain chunk data
            village_center: Optional coordinates of a village center in this chunk
        """
        chunk_buildings = []
        chunk_start_x = chunk_x * self.chunk_size
        chunk_start_y = chunk_y * self.chunk_size

        # Determine number of buildings to generate
        num_buildings = 0

        if village_center:
            # More buildings around a village center (5-10)
            num_buildings = random.randint(5, 10)
        else:
            # Less likely to have isolated buildings
            if random.random() < 0.15:  # 15% chance for isolated buildings
                num_buildings = random.randint(1, 3)

        # Try to place buildings
        for _ in range(num_buildings):
            # Determine building position
            if village_center:
                # Place around village center in a cluster
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(5, self.building_cluster_radius)
                bx = int(village_center[0] + distance * math.cos(angle))
                by = int(village_center[1] + distance * math.sin(angle))
            else:
                # Random position within chunk
                bx = chunk_start_x + random.randint(3, self.chunk_size - 4)
                by = chunk_start_y + random.randint(3, self.chunk_size - 4)

            # Check if position is valid for building
            if not self.is_valid_building_position(bx, by):
                continue

            # Determine building type based on ecosystem
            local_x = bx - chunk_start_x
            local_y = by - chunk_start_y

            # Make sure we're within valid chunk range
            if 0 <= local_x < self.chunk_size and 0 <= local_y < self.chunk_size:
                base_terrain = chunk[local_y][local_x]

                # Map ecosystem to building type
                if base_terrain in [Terrain.GRASS, Terrain.MEADOW, Terrain.MUD]:
                    building_type = Terrain.HOUSE_GRASS
                elif base_terrain in [Terrain.DARK_GRASS, Terrain.THORNS]:
                    building_type = Terrain.HOUSE_FOREST
                elif base_terrain in [Terrain.SAND, Terrain.SANDSTONE]:
                    building_type = Terrain.HOUSE_DESERT
                elif base_terrain in [Terrain.BASALT, Terrain.ROCK]:
                    building_type = Terrain.HOUSE_VOLCANO
                else:
                    continue  # Invalid terrain for building

                # Randomize building size
                if random.random() < 0.2:  # 20% chance for larger building
                    size = (4, 4)
                else:
                    size = (3, 3)

                # Create and add the building
                building = Building((bx, by), building_type, size)
                chunk_buildings.append(building)

                # Apply building to terrain
                for tile_x, tile_y in building.tiles:
                    local_tile_x = tile_x - chunk_start_x
                    local_tile_y = tile_y - chunk_start_y

                    # Check if coordinates are within this chunk
                    if (0 <= local_tile_x < self.chunk_size and
                            0 <= local_tile_y < self.chunk_size):

                        # Check if we're placing a path or a building
                        if (tile_x, tile_y) == (bx, by):
                            # Center tile is the actual building
                            chunk[local_tile_y][local_tile_x] = building_type
                        elif chunk[local_tile_y][local_tile_x] not in [Terrain.WATER, Terrain.LAVA, Terrain.CLIFF]:
                            # Surrounding tiles that are valid get replaced with either building or path
                            if abs(tile_x - bx) <= size[0] // 2 and abs(tile_y - by) <= size[1] // 2:
                                # Building tiles
                                chunk[local_tile_y][local_tile_x] = building_type
                            else:
                                # Path tiles (outside building footprint)
                                chunk[local_tile_y][local_tile_x] = Terrain.PATH

        # Store the buildings for this chunk
        if chunk_buildings:
            self.buildings[(chunk_x, chunk_y)] = chunk_buildings

    def post_process_chunk(self, chunk):
        """区块后处理（优化后的版本）"""
        # 水域平滑
        chunk = self.apply_cellular_automaton(chunk,
                                              targets=[Terrain.WATER],
                                              replace=Terrain.SHALLOW_WATER,
                                              min_neighbors=4,
                                              iterations=3)

        # 熔岩区域平滑
        chunk = self.apply_cellular_automaton(chunk,
                                              targets=[Terrain.LAVA],
                                              replace=Terrain.BASALT,
                                              min_neighbors=3,
                                              iterations=2)

        # 岩石区域平滑
        chunk = self.apply_cellular_automaton(chunk,
                                              targets=[Terrain.ROCK, Terrain.BASALT],
                                              replace=Terrain.SANDSTONE,
                                              min_neighbors=5,
                                              iterations=2)

        # Swamp smoothing
        chunk = self.apply_cellular_automaton(chunk,
                                              targets=[Terrain.SWAMP],
                                              replace=Terrain.DARK_GRASS,
                                              min_neighbors=3,
                                              iterations=1)

        # Path connections (make sure paths connect properly)
        chunk = self.smooth_paths(chunk)

        return chunk

    def smooth_paths(self, chunk):
        """Make paths more continuous and connected"""
        new_chunk = [row.copy() for row in chunk]

        for y in range(1, self.chunk_size - 1):
            for x in range(1, self.chunk_size - 1):
                if chunk[y][x] != Terrain.PATH:
                    # Count adjacent path tiles
                    path_neighbors = 0
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if chunk[y + dy][x + dx] == Terrain.PATH:
                            path_neighbors += 1

                    # If surrounded by paths on two or more sides, convert to path
                    if path_neighbors >= 2 and chunk[y][x] not in [Terrain.WATER, Terrain.LAVA, Terrain.CLIFF,
                                                                   Terrain.HOUSE_GRASS, Terrain.HOUSE_FOREST,
                                                                   Terrain.HOUSE_DESERT, Terrain.HOUSE_VOLCANO,
                                                                   Terrain.VILLAGE_CENTER]:
                        new_chunk[y][x] = Terrain.PATH

        return new_chunk

    def apply_cellular_automaton(self, chunk, targets, replace, min_neighbors, iterations=2):
        """优化的细胞自动机方法"""
        for _ in range(iterations):
            new_chunk = [row.copy() for row in chunk]
            for y in range(1, self.chunk_size - 1):
                for x in range(1, self.chunk_size - 1):
                    if chunk[y][x] not in targets:
                        continue

                    # 计算8邻域内同类数量
                    neighbors = sum(
                        1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                        if (dx, dy) != (0, 0) and chunk[y + dy][x + dx] in targets
                    )

                    if neighbors < min_neighbors:
                        new_chunk[y][x] = replace
            chunk = new_chunk
        return chunk

    def apply_water(self, chunk, chunk_x, chunk_y):
        """应用水系到区块"""
        chunk_start_x = chunk_x * self.chunk_size
        chunk_start_y = chunk_y * self.chunk_size

        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                global_x = chunk_start_x + x
                global_y = chunk_start_y + y
                if (global_x, global_y) in self.river_network:
                    chunk[y][x] = Terrain.WATER
                elif (global_x, global_y) in self.lake_areas:
                    chunk[y][x] = Terrain.WATER
                elif (global_x, global_y) in self.shallow_water_tiles:
                    chunk[y][x] = Terrain.SHALLOW_WATER

    def is_passable(self, x, y):
        terrain = self.get_terrain(x, y)
        return TERRAIN_PASSABLE.get(terrain, True)

    def get_terrain(self, x, y):
        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        if (chunk_x, chunk_y) not in self.terrain_map:
            self.generate_chunk(chunk_x, chunk_y)
        local_x = x % self.chunk_size
        local_y = y % self.chunk_size
        return self.terrain_map[(chunk_x, chunk_y)][local_y][local_x]

    def generate_chunk(self, chunk_x, chunk_y):
        """生成地图区块"""
        chunk = self.generate_base_terrain(chunk_x, chunk_y)
        # River and lake application now integrated into generate_base_terrain
        self.terrain_map[(chunk_x, chunk_y)] = chunk

    def draw(self, surface, camera):
        """绘制地图"""
        cam_left = -camera.camera.x
        cam_top = -camera.camera.y
        cam_right = cam_left + SCREEN_WIDTH
        cam_bottom = cam_top + SCREEN_HEIGHT

        start_x = int(cam_left // TILE_SIZE) - 1
        start_y = int(cam_top // TILE_SIZE) - 1
        end_x = int(cam_right // TILE_SIZE) + 1
        end_y = int(cam_bottom // TILE_SIZE) + 1

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                terrain = self.get_terrain(x, y)
                color = COLORS["grass"]  # 默认颜色

                # Map terrain type to color
                if terrain == Terrain.GRASS:
                    color = COLORS["grass"]
                elif terrain == Terrain.MUD:
                    color = COLORS["mud"]
                elif terrain == Terrain.SMALL_TREE:
                    color = COLORS["small_tree"]
                elif terrain == Terrain.DARK_GRASS:
                    color = COLORS["dark_grass"]
                elif terrain == Terrain.BIG_TREE:
                    color = COLORS["big_tree"]
                elif terrain == Terrain.THORNS:
                    color = COLORS["thorns"]
                elif terrain == Terrain.ROCK:
                    color = COLORS["rock"]
                elif terrain == Terrain.SANDSTONE:
                    color = COLORS["sandstone"]
                elif terrain == Terrain.SAND:
                    color = COLORS["sand"]
                elif terrain == Terrain.BASALT:
                    color = COLORS["basalt"]
                elif terrain == Terrain.LAVA:
                    color = COLORS["lava"]
                elif terrain == Terrain.WATER:
                    color = COLORS["water"]
                elif terrain == Terrain.SHALLOW_WATER:
                    color = COLORS["shallow_water"]
                elif terrain == Terrain.CLIFF:
                    color = COLORS["cliff"]
                elif terrain == Terrain.MEADOW:
                    color = COLORS["meadow"]
                elif terrain == Terrain.SWAMP:
                    color = COLORS["swamp"]
                elif terrain == Terrain.HOUSE_GRASS:
                    color = COLORS["house_grass"]
                elif terrain == Terrain.HOUSE_FOREST:
                    color = COLORS["house_forest"]
                elif terrain == Terrain.HOUSE_DESERT:
                    color = COLORS["house_desert"]
                elif terrain == Terrain.HOUSE_VOLCANO:
                    color = COLORS["house_volcano"]
                elif terrain == Terrain.VILLAGE_CENTER:
                    color = COLORS["village_center"]
                elif terrain == Terrain.PATH:
                    color = COLORS["path"]

                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                screen_rect = camera.apply_rect(rect)
                pygame.draw.rect(surface, color, screen_rect)

# 技能系统 --------------------------------------------------
class Skill:
    def __init__(self, name, skill_type, cost, effect, cooldown=0, range=1, target_type="single", description=""):
        """
        初始化技能
        :param name: 技能名称
        :param skill_type: 技能类型（枚举值）
        :param cost: 消耗的MP
        :param effect: 技能效果函数
        :param cooldown: 冷却时间（回合数）
        :param range: 技能范围（格子数）
        :param target_type: 目标类型（"single" 单体 / "aoe" 群体）
        :param description: 技能描述
        """
        self.name = name
        self.type = skill_type
        self.cost = cost
        self.effect = effect
        self.cooldown = cooldown
        self.current_cooldown = 0  # 当前冷却时间
        self.range = range
        self.target_type = target_type
        self.description = description

    def can_use(self, caster):
        """检查技能是否可以使用"""
        return caster.stats["mp"] >= self.cost and self.current_cooldown <= 0

    def use(self, caster, target):
        """
        使用技能
        :param caster: 施法者（Player 或 Enemy）
        :param target: 目标（可以是单个目标或目标列表）
        :return: 技能使用结果（字符串）
        """
        if not self.can_use(caster):
            return f"无法使用 {self.name}：MP不足或技能冷却中"

        # 消耗MP
        caster.stats["mp"] -= self.cost

        # 执行技能效果
        result = self.effect(caster, target)

        # 设置冷却时间
        self.current_cooldown = self.cooldown

        return result

    def update_cooldown(self):
        """更新技能冷却时间"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def get_info(self):
        """获取技能信息"""
        info = f"{self.name} ({self.cost} MP)\n"
        info += f"类型: {self.target_type.capitalize()}\n"
        info += f"范围: {self.range} 格\n"
        info += f"冷却: {self.cooldown} 回合\n"
        info += f"描述: {self.description}"
        return info


# 预定义技能效果函数
def fireball(caster, target):
    """火球术：对单个目标造成伤害"""
    dmg = caster.stats["attack"] * 2 - target.stats["defense"]
    dmg = max(dmg, 1)
    target.stats["hp"] -= dmg
    return f"{caster.name} 使用了火球术！对 {target.name} 造成了 {dmg} 点伤害！"

def heal(caster, target):
    """治疗术：恢复目标生命值"""
    heal_amt = caster.stats["max_hp"] // 2
    target.stats["hp"] = min(target.stats["max_hp"], target.stats["hp"] + heal_amt)
    return f"{caster.name} 使用了治疗术！恢复了 {heal_amt} 点生命值！"

def poison(caster, target):
    """毒刃：对目标施加中毒效果"""
    dmg = caster.stats["attack"] - target.stats["defense"] // 2
    dmg = max(dmg, 1)
    target.stats["hp"] -= dmg
    target.status_effects.append({"type": "poison", "duration": 3, "damage": 2})
    return f"{caster.name} 使用了毒刃！对 {target.name} 造成了 {dmg} 点伤害并施加中毒效果！"

def charge(caster, target):
    """冲锋：对目标造成伤害并击退"""
    dmg = caster.stats["attack"] * 1.5 - target.stats["defense"]
    dmg = max(dmg, 1)
    target.stats["hp"] -= dmg
    # 击退逻辑（假设有位置系统）
    if hasattr(target, "rect"):
        target.rect.x += 50 if caster.rect.x < target.rect.x else -50
    return f"{caster.name} 使用了冲锋！对 {target.name} 造成了 {dmg} 点伤害并击退！"


# 预定义技能
SKILLS = {
    SkillType.FIREBALL: Skill(
        name="火球术",
        skill_type=SkillType.FIREBALL,
        cost=10,
        effect=fireball,
        cooldown=2,
        range=3,
        description="发射一枚火球，对单个目标造成大量伤害。"
    ),
    SkillType.HEAL: Skill(
        name="治疗术",
        skill_type=SkillType.HEAL,
        cost=8,
        effect=heal,
        cooldown=3,
        range=1,
        description="恢复目标的生命值。"
    ),
    SkillType.POISON: Skill(
        name="毒刃",
        skill_type=SkillType.POISON,
        cost=6,
        effect=poison,
        cooldown=4,
        range=1,
        description="用毒刃攻击目标，造成伤害并施加中毒效果。"
    ),
    SkillType.CHARGE: Skill(
        name="冲锋",
        skill_type=SkillType.CHARGE,
        cost=12,
        effect=charge,
        cooldown=5,
        range=2,
        description="冲向目标，造成伤害并击退敌人。"
    )
}


# 技能管理器
class SkillManager:
    def __init__(self):
        self.skills = []

    def add_skill(self, skill):
        """添加技能"""
        if skill not in self.skills:
            self.skills.append(skill)

    def remove_skill(self, skill):
        """移除技能"""
        if skill in self.skills:
            self.skills.remove(skill)

    def get_skill_by_name(self, name):
        """通过名称获取技能"""
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None

    def update_cooldowns(self):
        """更新所有技能的冷却时间"""
        for skill in self.skills:
            skill.update_cooldown()

    def get_available_skills(self, caster):
        """获取当前可用的技能"""
        return [skill for skill in self.skills if skill.can_use(caster)]


# 装备系统 --------------------------------------------------
class Equipment:
    def __init__(self, name, item_type, stats, skill=None, range=1, value=0):
        self.name = name
        self.type = item_type
        self.stats = stats  # 属性加成字典
        self.skill = skill  # 绑定技能
        self.range = range  # 攻击距离
        self.value = value  # 物品价值（用于商店）
        self.equipped = False

    @property
    def atk_bonus(self):
        return self.stats.get("attack", 0)

    @property
    def def_bonus(self):
        return self.stats.get("defense", 0)

    @property
    def crit_bonus(self):
        return self.stats.get("crit", 0)

    @property
    def agility_bonus(self):
        return self.stats.get("agility", 0)

    @property
    def hp_bonus(self):
        return self.stats.get("hp", 0)

    @property
    def mp_bonus(self):
        return self.stats.get("mp", 0)


# 武器预设
WEAPONS = {
    WeaponType.SPEAR: Equipment(
        "龙纹长枪", ItemType.WEAPON,
        {"attack": 18, "crit": 8, "agility": -2},
        skill=SkillType.CHARGE, range=3, value=50
    ),
    WeaponType.DAGGER: Equipment(
        "淬毒匕首", ItemType.WEAPON,
        {"attack": 12, "crit": 25, "agility": 15},
        skill=SkillType.POISON, range=1, value=35
    ),
    WeaponType.GREATSWORD: Equipment(
        "玄铁重剑", ItemType.WEAPON,
        {"attack": 25, "crit": 5, "agility": -5},
        skill=SkillType.CHARGE, range=2, value=70
    ),
    WeaponType.SHORTSWORD: Equipment(
        "骑士短剑", ItemType.WEAPON,
        {"attack": 15, "crit": 10, "agility": 8},
        range=1, value=40
    )
}

# 防具预设（示例）
ARMORS = {
    "leather": Equipment(
        "皮质护甲", ItemType.ARMOR,
        {"defense": 10, "agility": 5, "hp": 20},
        value=30
    ),
    "chainmail": Equipment(
        "锁子甲", ItemType.ARMOR,
        {"defense": 18, "agility": -3, "hp": 40},
        value=50
    ),
    "plate": Equipment(
        "板甲", ItemType.ARMOR,
        {"defense": 25, "agility": -8, "hp": 60},
        value=80
    )
}

# 药水预设
POTIONS = [
    Equipment("Small HP Potion", ItemType.POTION, {"hp": 20}),
    Equipment("Large HP Potion", ItemType.POTION, {"hp": 50}),
    Equipment("Small MP Potion", ItemType.POTION, {"mp": 20}),
    Equipment("Large MP Potion", ItemType.POTION, {"mp": 50})
]


# NPC类 --------------------------------------------------
class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, shop_items):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

        self.rect = self.image.get_rect(topleft=pos)
        self.shop_items = shop_items
        self.interact_radius = 50

    def can_interact(self, player_pos):
        """检查玩家是否在可交互范围内"""
        return pygame.math.Vector2(self.rect.center).distance_to(player_pos) <= self.interact_radius


# 扩展的敌人类 --------------------------------------------------
# 敌人精灵类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, name="Enemy", color=COLORS["enemy"]):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)
        self.name = name
        self.level = 1
        self.exp_value = 10  # 基础经验值
        self.status_effects = []  # 状态效果列表
        self.skills = []  # 技能列表

        # 基础属性
        self.base_stats = {
            "hp": 50,
            "max_hp": 50,
            "attack": 10,
            "defense": 5,
            "crit": 5,
            "agility": 5
        }
        self.stats = self.base_stats.copy()

    def take_damage(self, damage):
        self.stats["hp"] = max(0, self.stats["hp"] - damage)
        return self.stats["hp"] > 0

    def use_skill(self, target):
        if self.skills:
            skill = random.choice(self.skills)
            if skill.can_use(self):
                return skill.use(self, target)
        return None


class Monster(Enemy):
    def __init__(self, pos, monster_type):
        # 根据类型设置基础属性
        self.type = monster_type
        color_map = {
            MonsterType.WOLF: (150, 150, 150),
            MonsterType.GOBLIN: (0, 200, 0),
            MonsterType.TROLL: (100, 50, 0),
            MonsterType.DRAGON: (255, 0, 0)
        }
        name_map = {
            MonsterType.WOLF: "狼",
            MonsterType.GOBLIN: "哥布林",
            MonsterType.TROLL: "巨魔",
            MonsterType.DRAGON: "幼龙"
        }

        super().__init__(
            pos=pos,
            name=name_map[monster_type],
            color=color_map[monster_type]
        )

        # 初始化怪物类型特有属性
        self.init_monster()

    def init_monster(self):
        if self.type == MonsterType.WOLF:
            self.stats.update({
                "hp": 80,
                "max_hp": 80,
                "attack": 15,
                "agility": 12,
                "crit": 10
            })
            self.skills.append(SKILLS[SkillType.CHARGE])
            self.exp_value = 20

        elif self.type == MonsterType.GOBLIN:
            self.stats.update({
                "hp": 60,
                "max_hp": 60,
                "attack": 12,
                "defense": 8,
                "crit": 15
            })
            self.skills.append(SKILLS[SkillType.POISON])
            self.exp_value = 15

        elif self.type == MonsterType.TROLL:
            self.stats.update({
                "hp": 150,
                "max_hp": 150,
                "attack": 25,
                "defense": 15,
                "agility": 3
            })
            self.exp_value = 50

        elif self.type == MonsterType.DRAGON:
            self.stats.update({
                "hp": 200,
                "max_hp": 200,
                "attack": 35,
                "defense": 20,
                "crit": 20
            })
            self.skills.append(SKILLS[SkillType.FIREBALL])
            self.exp_value = 100

        # 同步当前属性
        self.stats["hp"] = self.stats["max_hp"]


# 物品实体类 --------------------------------------------------
class Item(pygame.sprite.Sprite):
    def __init__(self, pos, equipment):
        super().__init__()
        self.equipment = equipment
        self.image = pygame.Surface((16, 16))
        self.set_appearance()
        self.rect = self.image.get_rect(center=pos)

    def set_appearance(self):
        if self.equipment.type == ItemType.POTION:
            color = COLORS["potion_red"] if "HP" in self.equipment.name else COLORS["potion_blue"]
            self.image.fill(color)
        elif self.equipment.type == ItemType.COIN:
            coin_type = random.choices([ItemType.COIN], weights=[0.1, 0.3, 0.6], k=1)[0]
            self.image.fill(COLORS[f"coin_{coin_type.name.lower()}"])
        else:
            self.image.fill(COLORS["item"])


# 扩展玩家类 --------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLORS["player"])
        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)

        # 玩家名称
        self.name = "Player"

        # 基础属性
        self.base_stats = {
            "hp": 100,
            "max_hp": 100,
            "mp": 50,
            "max_mp": 50,
            "attack": 10,
            "defense": 5,
            "crit": 5,
            "agility": 8,
            "exp": 0,  # 经验值
            "level": 1  # 等级
        }
        self.stats = self.base_stats.copy()  # 当前属性（包含装备加成）
        self.exp_to_next_level = 100  # 升级所需经验值

        # 装备系统
        self.equipped = {
            "weapon": None,  # 武器
            "armor": None,   # 防具
            "accessory": None  # 饰品（可选）
        }
        self.attack_range = 1  # 默认攻击范围
        self.inventory = []  # 物品栏
        self.skills = [SKILLS[SkillType.FIREBALL], SKILLS[SkillType.HEAL]]  # 初始技能
        self.coins = {"gold": 0, "silver": 0, "copper": 0}  # 货币

    def check_level_up(self):
        """检查玩家是否升级"""
        if self.stats["exp"] >= self.exp_to_next_level:
            self.stats["level"] += 1
            self.stats["exp"] -= self.exp_to_next_level
            self.exp_to_next_level = int(self.exp_to_next_level * 1.5)  # 每次升级所需经验值增加
            self.level_up_stats()  # 升级后提升属性
            return True
        return False

    def level_up_stats(self):
        """升级后提升玩家属性"""
        self.stats["max_hp"] += 10
        self.stats["hp"] = self.stats["max_hp"]  # 恢复满血
        self.stats["max_mp"] += 5
        self.stats["mp"] = self.stats["max_mp"]  # 恢复满蓝
        self.stats["attack"] += 2
        self.stats["defense"] += 1
        self.stats["crit"] += 1
        self.stats["agility"] += 1

    def update_stats(self):
        """更新装备加成后的属性"""
        # 重置为基础属性
        self.stats = self.base_stats.copy()

        # 应用装备加成
        for slot in self.equipped.values():
            if slot:
                for stat, value in slot.stats.items():
                    if stat in ["max_hp", "max_mp"]:
                        self.stats[stat] += value
                        # 确保当前值不超过最大值
                        if stat == "max_hp":
                            self.stats["hp"] = min(self.stats["hp"], self.stats["max_hp"])
                        elif stat == "max_mp":
                            self.stats["mp"] = min(self.stats["mp"], self.stats["max_mp"])
                    else:
                        self.stats[stat] += value

    def equip_item(self, item):
        """装备物品"""
        if item.type == ItemType.WEAPON:
            if self.equipped["weapon"]:
                self.unequip_item(self.equipped["weapon"])
            self.equipped["weapon"] = item
            self.attack_range = item.range
        elif item.type == ItemType.ARMOR:
            if self.equipped["armor"]:
                self.unequip_item(self.equipped["armor"])
            self.equipped["armor"] = item
        elif item.type == ItemType.ACCESSORY:
            if self.equipped["accessory"]:
                self.unequip_item(self.equipped["accessory"])
            self.equipped["accessory"] = item

        item.equipped = True
        self.update_stats()

    def unequip_item(self, item):
        """卸下装备"""
        for slot, eq in self.equipped.items():
            if eq == item:
                self.equipped[slot] = None
                item.equipped = False
                self.inventory.append(item)
                self.update_stats()
                return True
        return False

    def get_effective_stats(self):
        """获取当前有效属性（包含装备加成）"""
        return self.stats

    def move(self, dx, dy, game_map):
        """移动玩家（新增碰撞检测）"""
        new_x = self.rect.x + dx * PLAYER_SPEED
        new_y = self.rect.y + dy * PLAYER_SPEED

        # 转换坐标到地图格子
        tile_x = new_x // TILE_SIZE
        tile_y = new_y // TILE_SIZE

        if game_map.is_passable(tile_x, tile_y):
            self.rect.x = new_x
            self.rect.y = new_y
        else:
            # 尝试分别检测X和Y方向的碰撞
            if game_map.is_passable(tile_x, self.rect.y // TILE_SIZE):
                self.rect.x = new_x
            elif game_map.is_passable(self.rect.x // TILE_SIZE, tile_y):
                self.rect.y = new_y

    def add_to_inventory(self, item):
        """添加物品到背包"""
        self.inventory.append(item)

    def remove_from_inventory(self, item):
        """从背包移除物品"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def get_item_by_name(self, name):
        """通过名称获取背包中的物品"""
        for item in self.inventory:
            if item.name == name:
                return item
        return None

    def can_equip(self, item):
        """检查是否可以装备物品"""
        if item.type == ItemType.WEAPON:
            return True  # 所有玩家都可以装备武器
        elif item.type == ItemType.ARMOR:
            return True  # 所有玩家都可以装备防具
        return False

    def get_equipment_bonus(self, stat):
        """获取指定属性的装备加成"""
        bonus = 0
        for slot in self.equipped.values():
            if slot and stat in slot.stats:
                bonus += slot.stats[stat]
        return bonus

    def get_equipment_description(self):
        """获取当前装备的描述"""
        description = []
        if self.equipped["weapon"]:
            description.append(f"武器: {self.equipped['weapon'].name}")
        if self.equipped["armor"]:
            description.append(f"防具: {self.equipped['armor'].name}")
        if self.equipped["accessory"]:
            description.append(f"饰品: {self.equipped['accessory'].name}")
        return "\n".join(description) if description else "无装备"

    def get_inventory_summary(self):
        """获取背包物品摘要"""
        summary = defaultdict(int)
        for item in self.inventory:
            summary[item.name] += 1
        return summary

    def has_item(self, item_name):
        """检查背包中是否有指定物品"""
        return any(item.name == item_name for item in self.inventory)

    def take_damage(self, damage):
        """承受伤害"""
        self.stats["hp"] = max(0, self.stats["hp"] - damage)
        return self.stats["hp"] > 0

    def heal(self, amount):
        """恢复生命值"""
        self.stats["hp"] = min(self.stats["max_hp"], self.stats["hp"] + amount)

    def restore_mp(self, amount):
        """恢复魔力值"""
        self.stats["mp"] = min(self.stats["max_mp"], self.stats["mp"] + amount)

    def add_skill(self, skill):
        """学习新技能"""
        if skill not in self.skills:
            self.skills.append(skill)

    def can_use_skill(self, skill):
        """检查是否可以使用技能"""
        return skill in self.skills and self.stats["mp"] >= skill.cost

    def use_skill(self, skill, target):
        """使用技能"""
        if self.can_use_skill(skill):
            self.stats["mp"] -= skill.cost
            return skill.effect(self, target)
        return "无法使用技能"

    def get_coin_total(self):
        """获取总货币值"""
        return (self.coins["gold"] * 100) + (self.coins["silver"] * 10) + self.coins["copper"]

    def add_coins(self, gold=0, silver=0, copper=0):
        """增加货币"""
        self.coins["gold"] += gold
        self.coins["silver"] += silver
        self.coins["copper"] += copper
        # 自动进位
        if self.coins["copper"] >= 10:
            self.coins["silver"] += self.coins["copper"] // 10
            self.coins["copper"] %= 10
        if self.coins["silver"] >= 10:
            self.coins["gold"] += self.coins["silver"] // 10
            self.coins["silver"] %= 10

    def spend_coins(self, amount):
        """花费货币"""
        total = self.get_coin_total()
        if total >= amount:
            remaining = amount
            self.coins["gold"] = max(0, self.coins["gold"] - (remaining // 100))
            remaining %= 100
            self.coins["silver"] = max(0, self.coins["silver"] - (remaining // 10))
            remaining %= 10
            self.coins["copper"] = max(0, self.coins["copper"] - remaining)
            return True
        return False

# 游戏主类 --------------------------------------------------
class Game:
    def __init__(self):
        # 初始化游戏
        self.map = GameMap()
        self.player = Player()
        self.camera = Camera()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.generated_chunks = set()  # 记录已生成的地形区块
        self.generated_npc_chunks = set()  # 记录已生成 NPC 的区块
        self.damage_texts = []
        self.npcs = pygame.sprite.Group()
        self.selected_item_index = 0  # 当前选中的物品索引
        self.selected_skill = None  # 当前选中的技能
        self.selected_shop_item = 0  # 当前选中的商店商品索引
        self.in_shop = False  # 是否正在与商店交互
        self.game_over = False
        self.check_chunks()  # 初始化区块生成

    def is_valid_spawn_position(self, x, y):
        """检查是否是有效的生成位置（不在水中或岩浆中）"""
        terrain = self.map.get_terrain(x, y)
        return terrain not in (Terrain.WATER, Terrain.LAVA)

    def generate_npc_in_chunk(self, chunk_x, chunk_y, ecosystem):
        """在指定区块生成NPC（5%概率）"""
        if random.random() > 0.05:  # 95%概率不生成
            return

        # 获取商店配置
        shop_config = ECOSYSTEM_SHOPS[ecosystem]

        # 生成有效位置（最多尝试10次）
        valid_pos = False
        attempts = 0
        while not valid_pos and attempts < 10:
            # 随机生成位置（区块内的随机位置）
            tile_x = chunk_x * CHUNK_SIZE + random.randint(2, CHUNK_SIZE - 3)
            tile_y = chunk_y * CHUNK_SIZE + random.randint(2, CHUNK_SIZE - 3)
            # 检查位置是否有效（不在水中或岩浆中）
            valid_pos = self.is_valid_spawn_position(tile_x, tile_y)
            attempts += 1

        if not valid_pos:
            return  # 如果找不到有效位置，跳过生成

        npc_pos = (tile_x * TILE_SIZE, tile_y * TILE_SIZE)

        # 生成商店物品
        shop_items = []
        for item_type, probabilities in shop_config["items"]:
            # 随机选择具体物品
            item_name = random.choices(
                list(probabilities.keys()),
                weights=list(probabilities.values())
            )[0]

            if item_type == ItemType.WEAPON:
                item = copy.deepcopy(WEAPONS[item_name])
            elif item_type == ItemType.ARMOR:
                item = copy.deepcopy(ARMORS[item_name])
            elif item_type == ItemType.POTION:
                potion_type = "HP" if "red" in item_name else "MP"
                item = Equipment(
                    f"{potion_type} Potion",
                    ItemType.POTION,
                    {"hp": 30} if "red" in item_name else {"mp": 20}
                )

            # 设置合理价格
            item.value = random.randint(15, 50)
            shop_items.append(item)

        # 创建NPC
        npc = NPC(npc_pos, shop_items)
        npc.image.fill(shop_config["color"])
        npc.dialogue = self.get_random_dialogue(ecosystem)

        # 添加到游戏世界
        self.npcs.add(npc)
        self.all_sprites.add(npc)

    def find_nearest_npc(self):
        """找到距离玩家最近的 NPC"""
        nearest_npc = None
        min_distance = float('inf')  # 初始化为无穷大

        for npc in self.npcs:
            # 计算 NPC 与玩家的距离
            distance = pygame.math.Vector2(npc.rect.center).distance_to(self.player.rect.center)
            if distance < min_distance:
                min_distance = distance
                nearest_npc = npc

        return nearest_npc, min_distance

    def draw_npc_direction(self):
        """绘制最近 NPC 的方向指引"""
        nearest_npc, distance = self.find_nearest_npc()
        if nearest_npc is None:
            return  # 如果没有 NPC，则不绘制

        # 获取玩家和 NPC 的位置
        player_pos = pygame.math.Vector2(self.player.rect.center)
        npc_pos = pygame.math.Vector2(nearest_npc.rect.center)

        # 计算方向向量
        direction = (npc_pos - player_pos).normalize()

        # 如果 NPC 在屏幕外，绘制箭头
        if not self.camera.camera.collidepoint(npc_pos):
            # 计算箭头在屏幕边缘的位置
            screen_center = pygame.math.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            edge_point = screen_center + direction * 200  # 200 是箭头距离屏幕中心的距离

            # 绘制箭头
            arrow_size = 20
            angle = direction.angle_to(pygame.math.Vector2(1, 0))  # 计算箭头角度
            arrow_points = [
                edge_point + pygame.math.Vector2(-arrow_size, -arrow_size).rotate(-angle),
                edge_point + pygame.math.Vector2(-arrow_size, arrow_size).rotate(-angle),
                edge_point + pygame.math.Vector2(arrow_size, 0).rotate(-angle)
            ]
            pygame.draw.polygon(screen, (255, 255, 0), arrow_points)  # 黄色箭头

        # 显示距离信息
        font = pygame.font.Font(None, 24)
        distance_text = font.render(f"Nearest NPC: {int(distance)}px", True, (255, 255, 0))
        screen.blit(distance_text, (10, SCREEN_HEIGHT - 60))

    def get_random_dialogue(self, ecosystem):
        """获取符合生态系统的随机对话"""
        dialogues = {
            Ecosystem.GRASSLAND: [
                "草原的風帶來了好買賣！",
                "新鮮的藥草和武器，來看看吧！"
            ],
            Ecosystem.DARK_FOREST: [
                "迷途的旅人...需要幫助嗎？",
                "小心森林中的陷阱，買些裝備吧"
            ],
            Ecosystem.DESERT: [
                "堅固的裝備才能征服高山！",
                "礦石打造的精品武器，不看看嗎？"
            ],
            Ecosystem.VOLCANO: [
                "炎熱之地必備的生存裝備！",
                "用火山礦打造的稀有武器！"
            ]
        }
        return random.choice(dialogues[ecosystem])

    def handle_npc_interaction(self):
        """处理NPC交互"""
        for npc in self.npcs:
            if npc.can_interact(self.player.rect.center):
                # 显示交互提示
                self.draw_interaction_prompt(npc.rect.top)
                # 处理按键交互
                keys = pygame.key.get_pressed()
                if keys[K_e]:
                    self.current_shop_npc = npc
                    self.in_shop = True
                return

    def draw_interaction_prompt(self, y_pos):
        """绘制交互提示"""
        font = pygame.font.Font(None, 28)
        text = font.render("按 E 交易", True, (255, 255, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_pos - 20))
        pygame.draw.rect(screen, (0, 0, 0, 150), text_rect.inflate(10, 5))
        screen.blit(text, text_rect)

    def check_chunks(self):
        """检查并生成玩家周围的区块"""
        # 计算玩家所在的区块坐标
        player_tile_x = self.player.rect.x // TILE_SIZE
        player_tile_y = self.player.rect.y // TILE_SIZE
        chunk_x = player_tile_x // CHUNK_SIZE
        chunk_y = player_tile_y // CHUNK_SIZE

        # 遍历玩家周围的区块（3x3 区域）
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                current_chunk = (chunk_x + dx, chunk_y + dy)

                # 如果区块未生成，则生成区块
                if current_chunk not in self.generated_chunks:
                    # 生成地形
                    self.map.generate_chunk(*current_chunk)

                    # 获取区块的中心坐标
                    gx = current_chunk[0] * CHUNK_SIZE + CHUNK_SIZE // 2
                    gy = current_chunk[1] * CHUNK_SIZE + CHUNK_SIZE // 2

                    # 获取区块的高度值
                    height = self.map.get_height(gx, gy)  # 通过 self.map 调用 get_height

                    # 获取区块的主要生态系统
                    ecosystem = self.map.determine_ecosystem(gx, gy, height)  # 通过 self.map 调用 determine_ecosystem

                    # 生成敌人
                    self.generate_enemies_in_chunk(*current_chunk)

                    # 生成 NPC（5% 概率）
                    if random.random() < 0.05:  # 5% 概率生成 NPC
                        self.generate_npc_in_chunk(current_chunk[0], current_chunk[1])

                    # 标记区块为已生成
                    self.generated_chunks.add(current_chunk)

    def generate_npc_in_chunk(self, chunk_x, chunk_y):
        """在指定区块生成NPC（5%概率）"""
        if random.random() > 0.05:  # 95%概率不生成
            return

        # 获取区块的中心坐标
        gx = chunk_x * CHUNK_SIZE + CHUNK_SIZE // 2
        gy = chunk_y * CHUNK_SIZE + CHUNK_SIZE // 2

        # 获取区块的高度值
        height = self.map.get_height(gx, gy)  # 通过 self.map 调用 get_height

        # 根据高度和坐标确定生态系统
        ecosystem = self.map.determine_ecosystem(gx, gy, height)  # 通过 self.map 调用 determine_ecosystem

        # 获取商店配置
        shop_config = ECOSYSTEM_SHOPS[ecosystem]

        # 生成有效位置（最多尝试10次）
        valid_pos = False
        attempts = 0
        while not valid_pos and attempts < 10:
            # 随机生成位置（区块内的随机位置）
            tile_x = chunk_x * CHUNK_SIZE + random.randint(2, CHUNK_SIZE - 3)
            tile_y = chunk_y * CHUNK_SIZE + random.randint(2, CHUNK_SIZE - 3)
            # 检查位置是否有效（不在水中或岩浆中）
            valid_pos = self.map.is_valid_spawn_position(tile_x, tile_y)  # 通过 self.map 调用 is_valid_spawn_position
            attempts += 1

        if not valid_pos:
            return  # 如果找不到有效位置，跳过生成

        npc_pos = (tile_x * TILE_SIZE, tile_y * TILE_SIZE)

        # 生成商店物品
        shop_items = []
        for item_type, probabilities in shop_config["items"]:
            # 随机选择具体物品
            item_name = random.choices(
                list(probabilities.keys()),
                weights=list(probabilities.values())
            )[0]

            if item_type == ItemType.WEAPON:
                item = copy.deepcopy(WEAPONS[item_name])
            elif item_type == ItemType.ARMOR:
                item = copy.deepcopy(ARMORS[item_name])
            elif item_type == ItemType.POTION:
                potion_type = "HP" if "red" in item_name else "MP"
                item = Equipment(
                    f"{potion_type} Potion",
                    ItemType.POTION,
                    {"hp": 30} if "red" in item_name else {"mp": 20}
                )

            # 设置合理价格
            item.value = random.randint(15, 50)
            shop_items.append(item)

        # 创建NPC
        npc = NPC(npc_pos, shop_items)
        npc.image.fill(shop_config["color"])
        npc.dialogue = self.get_random_dialogue(ecosystem)

        # 添加到游戏世界
        self.npcs.add(npc)
        self.all_sprites.add(npc)

    def generate_enemies_in_chunk(self, chunk_x, chunk_y):
        """在区块中生成敌人和 NPC"""
        start_x = chunk_x * CHUNK_SIZE
        start_y = chunk_y * CHUNK_SIZE
        end_x = start_x + CHUNK_SIZE
        end_y = start_y + CHUNK_SIZE

        # 获取区块的中心坐标
        gx = chunk_x * CHUNK_SIZE + CHUNK_SIZE // 2
        gy = chunk_y * CHUNK_SIZE + CHUNK_SIZE // 2

        # 获取区块的高度值
        height = self.map.get_height(gx, gy)  # 通过 self.map 调用 get_height

        # 根据高度和坐标确定生态系统
        ecosystem = self.map.determine_ecosystem(gx, gy, height)  # 通过 self.map 调用 determine_ecosystem

        # 生成敌人
        num_enemies = random.randint(1, 4)  # 每个区块生成 1-4 个敌人
        for _ in range(num_enemies):
            # 尝试生成有效位置（最多尝试10次）
            valid_pos = False
            attempts = 0
            while not valid_pos and attempts < 10:
                # 随机生成敌人的位置
                tile_x = random.randint(start_x, end_x - 1)
                tile_y = random.randint(start_y, end_y - 1)
                # 检查位置是否有效（不在水中或岩浆中）
                valid_pos = self.map.is_valid_spawn_position(tile_x, tile_y)  # 通过 self.map 调用 is_valid_spawn_position
                attempts += 1

            if not valid_pos:
                continue  # 如果找不到有效位置，跳过生成

            # 根据生态系统生成对应类型的怪物
            monster_type = self.get_monster_type(ecosystem)
            monster = Monster(
                pos=(tile_x * TILE_SIZE, tile_y * TILE_SIZE),
                monster_type=monster_type
            )

            # 将敌人添加到游戏世界
            self.enemies.add(monster)
            self.all_sprites.add(monster)

    def get_monster_type(self, ecosystem):
        """根据生态系统选择怪物类型"""
        type_weights = {
            Ecosystem.GRASSLAND: [
                (MonsterType.WOLF, 40),
                (MonsterType.GOBLIN, 30),
                (MonsterType.TROLL, 5)
            ],
            Ecosystem.DARK_FOREST: [
                (MonsterType.GOBLIN, 50),
                (MonsterType.TROLL, 30),
                (MonsterType.WOLF, 20)
            ],
            Ecosystem.DESERT: [
                (MonsterType.TROLL, 60),
                (MonsterType.DRAGON, 10)
            ],
            Ecosystem.VOLCANO: [
                (MonsterType.DRAGON, 70),
                (MonsterType.TROLL, 30)
            ]
        }

        # 根据权重随机选择怪物类型
        total = sum(w for _, w in type_weights[ecosystem])
        r = random.uniform(0, total)
        current = 0
        for t, w in type_weights[ecosystem]:
            current += w
            if r < current:
                return t
        return MonsterType.WOLF  # 默认返回狼

    def handle_combat(self):
        """处理战斗逻辑"""
        collisions = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in collisions:
            # 初始化玩家和敌人的状态变量
            player_stats = self.player.get_effective_stats()
            enemy_stats = enemy.stats

            # 玩家选择使用技能
            if self.player.skills and random.random() < 0.5:
                skill = random.choice(self.player.skills)
                if self.player.can_use_skill(skill):
                    result = self.player.use_skill(skill, enemy)
                    self.show_damage_text(enemy.rect.center, result, (255, 255, 255))
            else:
                # 普通攻击
                if self.calculate_hit(player_stats, enemy_stats):
                    is_crit = self.calculate_crit(player_stats)
                    dmg = player_stats["attack"] - enemy_stats["defense"] // 2
                    dmg = max(dmg, 1)
                    if is_crit:
                        dmg *= 2
                        self.show_damage_text(self.player.rect.center, "CRIT!", COLORS["crit"])
                    enemy.stats["hp"] -= dmg
                    self.show_damage_text(enemy.rect.center, str(dmg), (255, 255, 255))

            # 检查敌人是否存活后再处理反击
            if enemy.stats["hp"] > 0:
                # 更新状态以反映可能的变更
                player_stats = self.player.get_effective_stats()
                enemy_stats = enemy.stats

                if self.calculate_hit(enemy_stats, player_stats):
                    is_crit = self.calculate_crit(enemy_stats)
                    dmg = enemy_stats["attack"] - player_stats["defense"] // 2
                    dmg = max(dmg, 1)
                    if is_crit:
                        dmg *= 2
                        self.show_damage_text(enemy.rect.center, "CRIT!", COLORS["crit"])
                    self.player.stats["hp"] -= dmg
                    self.show_damage_text(self.player.rect.center, str(dmg), (255, 0, 0))
            else:
                self.generate_loot(enemy)
                enemy.kill()

    def calculate_hit(self, attacker, defender):
        """计算命中率"""
        agility_diff = attacker["agility"] - defender["agility"]
        hit_chance = 80 + agility_diff / 2
        return random.random() * 100 < hit_chance

    def calculate_crit(self, attacker_stats):
        """计算暴击率"""
        return random.random() * 100 < attacker_stats["crit"]

    def show_damage_text(self, pos, text, color):
        """显示伤害文本"""
        self.damage_texts.append({
            "text": text,
            "pos": pos,
            "color": color,
            "timer": 60
        })

    def generate_loot(self, enemy):
        """生成掉落物品"""
        if isinstance(enemy, Monster):
            # 金币掉落
            coin_types = [
                ("gold", 0.1),
                ("silver", 0.3),
                ("copper", 0.6)
            ]
            for _ in range(random.randint(1, 3)):
                coin_type = random.choices(
                    [c[0] for c in coin_types],
                    weights=[c[1] for c in coin_types]
                )[0]
                self.player.add_coins(**{coin_type: 1})

            # 装备掉落
            if random.random() < 0.3:
                if enemy.type == MonsterType.DRAGON:
                    item = WEAPONS[WeaponType.GREATSWORD]
                else:
                    item = random.choice([
                        *WEAPONS.values(),
                        *ARMORS.values()
                    ])
                self.items.add(Item(enemy.rect.center, item))

            # 经验值奖励
            self.player.stats["exp"] += enemy.exp_value
            if self.player.check_level_up():
                print(f"Level up! You are now level {self.player.stats['level']}")

    def handle_items(self):
        """处理物品拾取逻辑"""
        collisions = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in collisions:
            self.player.inventory.append(item.equipment)
            # 自动装备更高级的武器
            if item.equipment.type == ItemType.WEAPON:
                current_weapon = self.player.equipped["weapon"]
                if not current_weapon or item.equipment.atk_bonus > current_weapon.atk_bonus:
                    self.player.equip_item(item.equipment)

    def draw_ui(self):
        """绘制用户界面"""
        # 左侧血条和属性
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 200, 20))  # 红色血条背景
        pygame.draw.rect(screen, (0, 255, 0),
                         (10, 10, 200 * (self.player.stats["hp"] / self.player.stats["max_hp"]), 20))  # 绿色血条

        # 玩家属性显示
        font = pygame.font.Font(None, 24)
        text = font.render(f"HP: {self.player.stats['hp']}/{self.player.stats['max_hp']}", True, COLORS["ui_text"])
        screen.blit(text, (10, 40))
        text = font.render(f"MP: {self.player.stats['mp']}/{self.player.stats['max_mp']}", True, COLORS["ui_text"])
        screen.blit(text, (10, 60))
        text = font.render(f"ATK: {self.player.stats['attack']}", True, COLORS["ui_text"])
        screen.blit(text, (10, 80))
        text = font.render(f"DEF: {self.player.stats['defense']}", True, COLORS["ui_text"])
        screen.blit(text, (10, 100))
        text = font.render(f"CRIT: {self.player.stats['crit']}%", True, COLORS["ui_text"])
        screen.blit(text, (10, 120))
        text = font.render(f"AGI: {self.player.stats['agility']}", True, COLORS["ui_text"])
        screen.blit(text, (10, 140))

        # 钱币显示
        coin_text = f"Gold: {self.player.coins['gold']}  Silver: {self.player.coins['silver']}  Copper: {self.player.coins['copper']}"
        text_surface = font.render(coin_text, True, (255, 215, 0))  # 金色文字
        screen.blit(text_surface, (10, SCREEN_HEIGHT - 40))

        # 右侧边栏
        sidebar_width = 400
        sidebar_rect = pygame.Rect(SCREEN_WIDTH - sidebar_width, 0, sidebar_width, SCREEN_HEIGHT)
        pygame.draw.rect(screen, COLORS["ui_bg"], sidebar_rect)  # 右侧边栏背景

        # 分两列
        left_column_width = sidebar_width // 2
        right_column_width = sidebar_width // 2

        # 左列：玩家装备、物品栏和技能
        self.draw_player_info(screen, pygame.Rect(
            SCREEN_WIDTH - sidebar_width, 0, left_column_width, SCREEN_HEIGHT))

        # 右列：附近怪物
        self.draw_nearby_enemies(screen, pygame.Rect(
            SCREEN_WIDTH - right_column_width, 0, right_column_width, SCREEN_HEIGHT))

        # 如果处于商店界面，绘制商店UI
        if self.in_shop:
            self.draw_shop_ui()

        # 绘制最近 NPC 的方向指引
        self.draw_npc_direction()

    def draw_player_info(self, surface, left_column_rect):
        """绘制玩家信息"""
        font = pygame.font.Font(None, 22)
        y = 50

        # 装备信息标题
        screen.blit(font.render("-- Equipment --", True, (200, 200, 200)),
                    (left_column_rect.x + 10, y))
        y += 30

        # 武器信息
        weapon = self.player.equipped["weapon"]
        weapon_text = f"Weapon: {weapon.name}" if weapon else "Weapon: None"
        screen.blit(font.render(weapon_text, True, COLORS["ui_text"]),
                    (left_column_rect.x + 15, y))
        y += 25

        # 防具信息
        armor = self.player.equipped["armor"]
        armor_text = f"Armor: {armor.name}" if armor else "Armor: None"
        screen.blit(font.render(armor_text, True, COLORS["ui_text"]),
                    (left_column_rect.x + 15, y))
        y += 40

        # 物品栏标题
        screen.blit(font.render("-- Inventory --", True, (200, 200, 200)),
                    (left_column_rect.x + 10, y))
        y += 30

        # 物品栏内容（最多显示5个）
        for i, item in enumerate(self.player.inventory[:5]):
            text = f"{i + 1}. {item.name}"
            screen.blit(font.render(text, True, COLORS["ui_text"]),
                        (left_column_rect.x + 15, y))
            y += 25
        y += 40

        # 技能标题
        screen.blit(font.render("-- Skills --", True, (200, 200, 200)),
                    (left_column_rect.x + 10, y))
        y += 30

        # 技能列表
        for skill in self.player.skills:
            text = f"{skill.name} ({skill.cost} MP)"
            screen.blit(font.render(text, True, COLORS["ui_text"]),
                        (left_column_rect.x + 15, y))
            y += 25

    def draw_nearby_enemies(self, surface, right_column_rect):
        """绘制附近敌人信息和技能释放状态"""
        font = pygame.font.Font(None, 22)
        y = 50

        # 标题
        screen.blit(font.render("-- Nearby Enemies --", True, (200, 200, 200)),
                    (right_column_rect.x + 10, y))
        y += 30

        # 获取附近敌人（300像素内）
        nearby_enemies = []
        for enemy in self.enemies:
            distance = pygame.math.Vector2(enemy.rect.center).distance_to(
                self.player.rect.center)
            if distance < 300:
                nearby_enemies.append(enemy)

        if not nearby_enemies:
            screen.blit(font.render("No enemies nearby", True, (150, 150, 150)),
                        (right_column_rect.x + 15, y))
            y += 20
        else:
            # 显示附近敌人属性（最多3个）
            for enemy in nearby_enemies[:3]:
                # 血条
                hp_percent = enemy.stats["hp"] / enemy.stats.get("max_hp", 100)
                pygame.draw.rect(screen, (255, 0, 0),
                                 (right_column_rect.x + 15, y, 100, 12))
                pygame.draw.rect(screen, (0, 255, 0),
                                 (right_column_rect.x + 15, y, 100 * hp_percent, 12))
                y += 15

                # 属性文本
                text = f"ATK: {enemy.stats['attack']}  DEF: {enemy.stats['defense']}"
                screen.blit(font.render(text, True, COLORS["ui_text"]),
                            (right_column_rect.x + 15, y))
                y += 20

                # 暴击和敏捷
                text = f"CRIT: {enemy.stats['crit']}%  AGI: {enemy.stats['agility']}"
                screen.blit(font.render(text, True, COLORS["ui_text"]),
                            (right_column_rect.x + 15, y))
                y += 30

        # 绘制玩家等级信息
        y += 20
        screen.blit(font.render("-- Player Info --", True, (200, 200, 200)),
                    (right_column_rect.x + 10, y))
        y += 30

        # 玩家等级
        level_text = f"Level: {self.player.stats['level']}"
        screen.blit(font.render(level_text, True, COLORS["ui_text"]),
                    (right_column_rect.x + 15, y))
        y += 25

        # 玩家经验值
        exp_text = f"Exp: {self.player.stats['exp']}/{self.player.exp_to_next_level}"
        screen.blit(font.render(exp_text, True, COLORS["ui_text"]),
                    (right_column_rect.x + 15, y))
        y += 25

        # 技能释放状态
        y += 20
        screen.blit(font.render("-- Skill Status --", True, (200, 200, 200)),
                    (right_column_rect.x + 10, y))
        y += 30

        for skill in self.player.skills:
            skill_text = f"{skill.name}: "
            if skill.current_cooldown > 0:
                skill_text += f"Cooldown ({skill.current_cooldown} turns)"
            else:
                skill_text += "Ready"
            screen.blit(font.render(skill_text, True, COLORS["ui_text"]),
                        (right_column_rect.x + 15, y))
            y += 25

    def handle_npc_interaction(self):
        collisions = pygame.sprite.spritecollide(self.player, self.npcs, False)
        if collisions:
            self.current_shop_npc = collisions[0]
            keys = pygame.key.get_pressed()
            if keys[K_e]:
                self.in_shop = True
        else:
            self.current_shop_npc = None

    def draw_shop_ui(self):
        """绘制商店界面"""
        if not self.in_shop or not self.current_shop_npc:
            return

        # 创建半透明背景
        shop_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200, 500, 400)
        shop_surface = pygame.Surface((500, 400), pygame.SRCALPHA)
        shop_surface.fill((30, 30, 30, 200))
        screen.blit(shop_surface, shop_rect.topleft)

        # 绘制商店内容
        font = pygame.font.Font(None, 28)
        title = font.render(f"{self.current_shop_npc.dialogue}", True, COLORS["ui_text"])
        screen.blit(title, (shop_rect.x + 20, shop_rect.y + 20))

        # 商品列表
        y_pos = shop_rect.y + 60
        for idx, item in enumerate(self.current_shop_npc.shop_items):
            color = (255, 215, 0) if idx == self.selected_shop_item else (255, 255, 255)
            text = font.render(f"{item.name} - {item.value} Gold", True, color)
            screen.blit(text, (shop_rect.x + 40, y_pos))
            y_pos += 40

        # 玩家金币显示
        coin_text = f"你的金币: {self.player.get_coin_total()}"
        text = font.render(coin_text, True, COLORS["coin_gold"])
        screen.blit(text, (shop_rect.x + 20, shop_rect.y + 350))

        # 操作提示
        help_text = font.render("[↑↓] 选择商品 [回车] 购买 [ESC] 离开", True, (180, 180, 180))
        screen.blit(help_text, (shop_rect.x + 20, shop_rect.y + 380))

    def get_target_at_position(self, pos):
        """根据位置获取目标"""
        for enemy in self.enemies:
            if enemy.rect.collidepoint(pos):
                return enemy
        return None

    def cast_skill(self, target_pos):
        """释放选中的技能"""
        if self.selected_skill is not None and self.selected_skill < len(self.player.skills):
            skill = self.player.skills[self.selected_skill]
            if skill.can_use(self.player):
                # 计算目标位置
                target = self.get_target_at_position(target_pos)
                if target:
                    result = skill.use(self.player, target)
                    print(result)  # 打印技能使用结果
                else:
                    print("没有找到目标")
            else:
                print("无法使用技能：MP不足或技能冷却中")
        self.selected_skill = None  # 释放技能后重置选择

    def handle_input(self, event):
        """处理输入事件"""
        if event.type == KEYDOWN:
            # 商店界面中的输入处理
            if self.in_shop:
                # 选择商品
                if event.key == K_UP:
                    self.selected_shop_item = max(0, self.selected_shop_item - 1)
                elif event.key == K_DOWN:
                    self.selected_shop_item = min(
                        len(self.current_shop_npc.shop_items) - 1,
                        self.selected_shop_item + 1
                    )
                # 购买商品
                elif event.key == K_RETURN:
                    self.buy_item()
                # 退出商店
                elif event.key == K_ESCAPE:
                    self.in_shop = False
                return  # 在商店界面时，不处理其他输入

            # 技能选择
            elif event.key == K_1:
                if len(self.player.skills) > 0:
                    self.selected_skill = 0
            elif event.key == K_2:
                if len(self.player.skills) > 1:
                    self.selected_skill = 1
            elif event.key == K_3:
                if len(self.player.skills) > 2:
                    self.selected_skill = 2
            elif event.key == K_4:
                if len(self.player.skills) > 3:
                    self.selected_skill = 3

            # 物品栏选择
            elif event.key == K_UP:
                self.selected_item_index = max(0, self.selected_item_index - 1)
            elif event.key == K_DOWN:
                self.selected_item_index = min(len(self.player.inventory) - 1,
                                               self.selected_item_index + 1)

            # 装备操作
            elif event.key == K_e:
                if len(self.player.inventory) > 0:
                    item = self.player.inventory[self.selected_item_index]
                    if item.type in [ItemType.WEAPON, ItemType.ARMOR]:
                        self.player.equip_item(item)
                        del self.player.inventory[self.selected_item_index]

            # 卸下操作
            elif event.key == K_u:
                if self.player.equipped["weapon"]:
                    self.player.unequip_item(self.player.equipped["weapon"])
                elif self.player.equipped["armor"]:
                    self.player.unequip_item(self.player.equipped["armor"])

            # 丢弃物品
            elif event.key == K_q:
                if len(self.player.inventory) > 0:
                    del self.player.inventory[self.selected_item_index]
                    self.selected_item_index = max(0, self.selected_item_index - 1)

            # 与NPC交互
            elif event.key == K_e:
                collisions = pygame.sprite.spritecollide(self.player, self.npcs, False)
                if collisions:
                    self.current_shop_npc = collisions[0]
                    self.in_shop = True

        # 处理鼠标点击事件（用于技能释放）
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                if self.selected_skill is not None:
                    self.cast_skill(pygame.mouse.get_pos())

    def buy_item(self):
        if not self.current_shop_npc:
            return

        item = copy.deepcopy(self.current_shop_npc.shop_items[self.selected_shop_item])
        if self.player.get_coin_total() >= item.value:
            if self.player.spend_coins(item.value):
                self.player.add_to_inventory(item)

    def run(self):
        """运行游戏主循环"""
        running = True
        while running:
            # 填充背景色
            screen.fill((0, 0, 0))

            # 更新相机位置
            self.camera.update(self.player)

            # 绘制地图
            self.map.draw(screen, self.camera)

            # 然后按顺序绘制其他实体：
            # 1. 物品
            for item in self.items:
                screen.blit(item.image, self.camera.apply(item))

            # 2. 敌人
            for enemy in self.enemies:
                screen.blit(enemy.image, self.camera.apply(enemy))

            # 3. 玩家
            screen.blit(self.player.image, self.camera.apply(self.player))

            # 4. 最后绘制NPC（确保在最上层）
            for npc in self.npcs:
                screen.blit(npc.image, self.camera.apply(npc))

            # 处理输入
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[K_a]: dx = -1
            if keys[K_d]: dx = 1
            if keys[K_w]: dy = -1
            if keys[K_s]: dy = 1
            self.player.move(dx, dy, self.map)

            # 更新游戏状态
            self.check_chunks()
            self.handle_combat()
            self.handle_items()
            self.handle_npc_interaction()  # 处理NPC交互

            # 更新技能冷却时间
            for skill in self.player.skills:
                skill.update_cooldown()

            # 绘制游戏对象
            for sprite in self.all_sprites:
                screen.blit(sprite.image, self.camera.apply(sprite))

            # 绘制伤害文本
            for damage_text in self.damage_texts:
                font = pygame.font.Font(None, 24)
                text_surface = font.render(damage_text["text"], True, damage_text["color"])
                screen.blit(text_surface, damage_text["pos"])
                damage_text["timer"] -= 1
            self.damage_texts = [dt for dt in self.damage_texts if dt["timer"] > 0]

            # 绘制UI
            self.draw_ui()

            # 如果处于商店界面，绘制商店UI
            if self.in_shop:
                self.draw_shop_ui()

            # 更新显示
            pygame.display.flip()
            clock.tick(60)

            # 处理事件
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                self.handle_input(event)  # 处理输入事件

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()