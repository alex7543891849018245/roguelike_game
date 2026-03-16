"""
Entity classes for the game
"""

import random
import math
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, StringProperty
from .config import WHITE, RED, GREEN, BLUE, GOLD, PURPLE, GRAY, DARK_GRAY, BLACK

class Stats:
    """
    Character statistics class
    """
    def __init__(self, hp=50, max_hp=50, mana=20, max_mana=20,
                 strength=8, defense=3, agility=5, luck=5,
                 level=1, exp=0, exp_to_next=100, gold=0):
        self.hp = hp
        self.max_hp = max_hp
        self.mana = mana
        self.max_mana = max_mana
        self.strength = strength
        self.defense = defense
        self.agility = agility
        self.luck = luck
        self.level = level
        self.exp = exp
        self.exp_to_next = exp_to_next
        self.gold = gold
    
    def to_dict(self):
        return {
            'hp': self.hp, 'max_hp': self.max_hp,
            'mana': self.mana, 'max_mana': self.max_mana,
            'strength': self.strength, 'defense': self.defense,
            'agility': self.agility, 'luck': self.luck,
            'level': self.level, 'exp': self.exp,
            'exp_to_next': self.exp_to_next, 'gold': self.gold
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Entity:
    """
    Base entity class
    """
    def __init__(self, x, y, name, entity_type, stats, color=WHITE):
        self.x = x
        self.y = y
        self.name = name
        self.type = entity_type
        self.stats = stats
        self.color = color
        self.inventory = []
        self.effects = []
        self.is_alive = True
        self.animation_frame = 0
        
    def move(self, dx, dy, game_map):
        """
        Move entity on the map
        """
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 0 <= new_x < game_map.width and 0 <= new_y < game_map.height:
            if game_map.tiles[new_y][new_x].walkable:
                self.x = new_x
                self.y = new_y
                self.animation_frame = 5
                return True
        return False
    
    def take_damage(self, damage, damage_type="physical"):
        """
        Apply damage to entity
        """
        # Проверка на уклонение
        if random.random() < self.stats.luck / 100:
            damage = 0
            return 0
            
        actual_damage = max(1, damage - self.stats.defense // 2)
        self.stats.hp -= actual_damage
        
        if self.stats.hp <= 0:
            self.stats.hp = 0
            self.is_alive = False
            
        return actual_damage
    
    def heal(self, amount):
        """
        Heal entity
        """
        self.stats.hp = min(self.stats.max_hp, self.stats.hp + amount)
        return amount
    
    def distance_to(self, other):
        """
        Calculate distance to another entity
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def update(self):
        """
        Update entity state
        """
        if self.animation_frame > 0:
            self.animation_frame -= 1

class Player(Entity):
    """
    Player class
    """
    def __init__(self, x, y):
        stats = Stats(
            hp=50, max_hp=50,
            mana=20, max_mana=20,
            strength=8, defense=3,
            agility=5, luck=5,
            level=1, exp=0,
            exp_to_next=100, gold=100
        )
        super().__init__(x, y, "Hero", "player", stats, BLUE)
        
        # Инвентарь и способности
        self.spells = ['fireball', 'heal', 'lightning']
        self.equipment = {
            'weapon': None, 'armor': None,
            'helmet': None, 'boots': None,
            'ring': None, 'amulet': None
        }
        self.skills = {
            'sword_mastery': 1,
            'magic_mastery': 1,
            'defense_mastery': 1
        }
        self.achievements = []
        
    def gain_exp(self, amount):
        """
        Gain experience points
        """
        self.stats.exp += amount
        while self.stats.exp >= self.stats.exp_to_next:
            self.level_up()
            
    def level_up(self):
        """
        Level up player
        """
        self.stats.level += 1
        self.stats.exp -= self.stats.exp_to_next
        self.stats.exp_to_next = int(self.stats.exp_to_next * 1.5)
        
        # Увеличение характеристик
        hp_gain = random.randint(8, 15)
        mana_gain = random.randint(3, 8)
        str_gain = random.randint(1, 3)
        def_gain = random.randint(1, 2)
        
        self.stats.max_hp += hp_gain
        self.stats.hp = self.stats.max_hp
        self.stats.max_mana += mana_gain
        self.stats.mana = self.stats.max_mana
        self.stats.strength += str_gain
        self.stats.defense += def_gain
        
        return {
            'hp': hp_gain, 'mana': mana_gain,
            'strength': str_gain, 'defense': def_gain
        }
    
    def equip(self, item):
        """
        Equip item
        """
        if item.type in self.equipment:
            # Снимаем текущий предмет
            if self.equipment[item.type]:
                old_item = self.equipment[item.type]
                self.stats.strength -= old_item.bonus_strength
                self.stats.defense -= old_item.bonus_defense
                self.stats.max_hp -= old_item.bonus_hp
            
            # Надеваем новый
            self.equipment[item.type] = item
            self.stats.strength += item.bonus_strength
            self.stats.defense += item.bonus_defense
            self.stats.max_hp += item.bonus_hp
            self.stats.hp = min(self.stats.hp, self.stats.max_hp)
            return True
        return False
    
    def to_dict(self):
        """
        Convert player to dictionary for saving
        """
        return {
            'x': self.x, 'y': self.y,
            'name': self.name,
            'stats': self.stats.to_dict(),
            'spells': self.spells,
            'inventory': [item.to_dict() for item in self.inventory],
            'equipment': {
                slot: item.to_dict() if item else None 
                for slot, item in self.equipment.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create player from dictionary
        """
        player = cls(data['x'], data['y'])
        player.name = data['name']
        player.stats = Stats.from_dict(data['stats'])
        player.spells = data['spells']
        
        # Загрузка предметов
        from .entities import Item
        player.inventory = [Item.from_dict(item) for item in data['inventory']]
        
        return player

class Enemy(Entity):
    """
    Enemy class
    """
    def __init__(self, x, y, enemy_type, level):
        self.enemy_type = enemy_type
        
        # Данные врагов
        enemy_data = ENEMY_DATA[enemy_type]
        
        # Масштабирование по уровню
        level_mult = 1 + (level - 1) * 0.2
        
        stats = Stats(
            hp=int(enemy_data['hp'] * level_mult),
            max_hp=int(enemy_data['hp'] * level_mult),
            mana=enemy_data.get('mana', 0),
            max_mana=enemy_data.get('mana', 0),
            strength=int(enemy_data['strength'] * level_mult),
            defense=int(enemy_data['defense'] * level_mult),
            agility=enemy_data.get('agility', 3),
            luck=enemy_data.get('luck', 1),
            level=level,
            exp=enemy_data['exp'],
            exp_to_next=0,
            gold=random.randint(enemy_data['gold_min'], enemy_data['gold_max'])
        )
        
        super().__init__(x, y, enemy_type, enemy_type, stats, enemy_data['color'])
        
        self.behavior = enemy_data.get('behavior', 'aggressive')
        self.vision_range = enemy_data.get('vision', 8)
        self.attack_range = enemy_data.get('attack_range', 1)
        self.special_abilities = enemy_data.get('abilities', [])
        
    def ai_turn(self, player, game_map):
        """
        AI decision making
        """
        distance = self.distance_to(player)
        
        if distance <= self.vision_range:
            if distance <= self.attack_range:
                return self.attack(player)
            else:
                return self.move_towards(player, game_map)
        else:
            return self.wander(game_map)
    
    def attack(self, target):
        """
        Attack target
        """
        damage = self.stats.strength + random.randint(-2, 3)
        
        # Использование способности
        if self.special_abilities and random.random() < 0.2:
            ability = random.choice(self.special_abilities)
            return self.use_ability(ability, target)
        
        actual_damage = target.take_damage(damage)
        return {
            'action': 'attack',
            'damage': actual_damage,
            'target': target
        }
    
    def use_ability(self, ability, target):
        """
        Use special ability
        """
        if ability == 'poison':
            # Эффект отравления
            return {'action': 'poison', 'target': target}
        elif ability == 'heal':
            self.heal(10)
            return {'action': 'heal', 'amount': 10}
        elif ability == 'rage':
            self.stats.strength += 5
            return {'action': 'rage', 'effect': 'strength_up'}
        elif ability == 'fire_breath':
            damage = random.randint(15, 25)
            actual_damage = target.take_damage(damage)
            return {'action': 'fire_breath', 'damage': actual_damage}
        
        return self.attack(target)
    
    def move_towards(self, target, game_map):
        """
        Move towards target
        """
        dx = target.x - self.x
        dy = target.y - self.y
        
        if abs(dx) > abs(dy):
            move_x = 1 if dx > 0 else -1
            if self.move(move_x, 0, game_map):
                return {'action': 'move', 'dx': move_x, 'dy': 0}
        else:
            move_y = 1 if dy > 0 else -1
            if self.move(0, move_y, game_map):
                return {'action': 'move', 'dx': 0, 'dy': move_y}
        
        return {'action': 'wait'}
    
    def wander(self, game_map):
        """
        Wander randomly
        """
        if random.random() < 0.3:
            direction = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
            self.move(direction[0], direction[1], game_map)
        return {'action': 'wander'}

class Item:
    """
    Item class
    """
    def __init__(self, x, y, item_type, rarity='common'):
        self.x = x
        self.y = y
        self.type = item_type
        self.rarity = rarity
        self.picked_up = False
        
        # Данные предметов
        item_data = ITEM_DATA[item_type]
        
        self.name = item_data['name']
        self.char = item_data['char']
        self.color = item_data['color']
        self.value = item_data.get('value', 0)
        self.effect = item_data.get('effect')
        self.effect_value = item_data.get('effect_value', 0)
        
        # Бонусы
        self.bonus_strength = item_data.get('bonus_strength', 0)
        self.bonus_defense = item_data.get('bonus_defense', 0)
        self.bonus_hp = item_data.get('bonus_hp', 0)
        self.bonus_agility = item_data.get('bonus_agility', 0)
        self.bonus_luck = item_data.get('bonus_luck', 0)
        
        # Множитель редкости
        rarity_mult = RARITY_MULT[rarity]
        self.value = int(self.value * rarity_mult)
        self.effect_value = int(self.effect_value * rarity_mult)
        
    def use(self, player):
        """
        Use item
        """
        if self.type == 'potion':
            player.heal(self.effect_value)
            return {'used': True, 'effect': f"Восстановлено {self.effect_value} HP"}
        elif self.type == 'mana_potion':
            player.stats.mana = min(player.stats.max_mana, 
                                   player.stats.mana + self.effect_value)
            return {'used': True, 'effect': f"Восстановлено {self.effect_value} MP"}
        elif self.type == 'gold':
            player.stats.gold += self.value
            return {'used': True, 'effect': f"Найдено {self.value} золота"}
        elif self.type in ['weapon', 'armor', 'helmet', 'boots', 'ring', 'amulet']:
            return {'used': False, 'effect': 'equip'}
        
        return {'used': False, 'effect': None}
    
    def to_dict(self):
        """
        Convert item to dictionary
        """
        return {
            'x': self.x, 'y': self.y,
            'type': self.type,
            'rarity': self.rarity,
            'picked_up': self.picked_up
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create item from dictionary
        """
        item = cls(data['x'], data['y'], data['type'], data['rarity'])
        item.picked_up = data['picked_up']
        return item

# Данные врагов
ENEMY_DATA = {
    "goblin": {
        'hp': 15, 'strength': 4, 'defense': 1, 'exp': 30,
        'gold_min': 5, 'gold_max': 15, 'color': GREEN,
        'behavior': 'coward', 'vision': 6, 'abilities': []
    },
    "skeleton": {
        'hp': 25, 'strength': 6, 'defense': 2, 'exp': 60,
        'gold_min': 10, 'gold_max': 25, 'color': WHITE,
        'behavior': 'aggressive', 'vision': 7, 'abilities': ['poison']
    },
    "orc": {
        'hp': 40, 'strength': 9, 'defense': 4, 'exp': 120,
        'gold_min': 20, 'gold_max': 40, 'color': RED,
        'behavior': 'aggressive', 'vision': 5, 'abilities': ['rage']
    },
    "dragon": {
        'hp': 100, 'strength': 15, 'defense': 8, 'exp': 300,
        'gold_min': 100, 'gold_max': 300, 'color': GOLD,
        'behavior': 'aggressive', 'vision': 10, 'abilities': ['fire_breath']
    }
}

# Данные предметов
ITEM_DATA = {
    'potion': {'name': 'Зелье здоровья', 'char': '!', 'color': RED, 
               'value': 10, 'effect': 'heal', 'effect_value': 20},
    'mana_potion': {'name': 'Зелье маны', 'char': '!', 'color': BLUE,
                    'value': 15, 'effect': 'mana', 'effect_value': 15},
    'gold': {'name': 'Золото', 'char': '$', 'color': GOLD,
             'value': 10, 'effect': 'gold'},
    'weapon': {'name': 'Оружие', 'char': '/', 'color': WHITE,
               'bonus_strength': 3},
    'armor': {'name': 'Броня', 'char': ']', 'color': GRAY,
              'bonus_defense': 2, 'bonus_hp': 10},
    'helmet': {'name': 'Шлем', 'char': '^', 'color': GRAY,
               'bonus_defense': 1, 'bonus_hp': 5},
    'boots': {'name': 'Ботинки', 'char': '>', 'color': GRAY,
              'bonus_agility': 2},
    'ring': {'name': 'Кольцо', 'char': 'o', 'color': GOLD,
             'bonus_luck': 2},
    'amulet': {'name': 'Амулет', 'char': '@', 'color': PURPLE,
               'bonus_hp': 15}
}

# Множители редкости
RARITY_MULT = {
    'common': 1.0,
    'rare': 1.5,
    'epic': 2.0,
    'legendary': 3.0
}