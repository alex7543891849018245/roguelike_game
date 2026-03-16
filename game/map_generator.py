import random
import math
from .config import GOLD, BLUE, RED

class Tile:
    """
    Map tile class
    """
    def __init__(self, x, y, tile_type='wall'):
        self.x = x
        self.y = y
        self.type = tile_type
        self.walkable = tile_type != 'wall' and tile_type != 'water' and tile_type != 'lava'
        self.transparent = tile_type != 'wall'
        self.visible = False
        self.explored = False
        self.light_level = 0
        
        # Настройка цвета
        if tile_type == 'wall':
            self.color = (0.4, 0.4, 0.4, 1)
        elif tile_type == 'floor':
            self.color = (0.2, 0.2, 0.2, 1)
        elif tile_type == 'stairs_down':
            self.color = GOLD
        elif tile_type == 'stairs_up':
            self.color = GOLD
        elif tile_type == 'water':
            self.color = BLUE
            self.walkable = False
        elif tile_type == 'lava':
            self.color = RED
            self.walkable = False
        elif tile_type == 'treasure':
            self.color = GOLD

class Room:
    """
    Room class for dungeon generation
    """
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.center_x = x + w // 2
        self.center_y = y + h // 2
        self.connected = False
        self.type = 'normal'  # normal, treasure, boss, shop, start
        
    def intersects(self, other):
        """
        Check if rooms intersect
        """
        return not (self.x + self.w < other.x or
                   self.x > other.x + other.w or
                   self.y + self.h < other.y or
                   self.y > other.y + other.h)
    
    def distance_to(self, other):
        """
        Calculate distance to another room
        """
        return math.sqrt((self.center_x - other.center_x)**2 + 
                        (self.center_y - other.center_y)**2)

class GameMap:
    """
    Main game map class
    """
    def __init__(self, width, height, depth=1):
        self.width = width
        self.height = height
        self.depth = depth
        self.tiles = [[Tile(x, y, 'wall') for x in range(width)] for y in range(height)]
        self.rooms = []
        self.entities = []
        self.items = []
        self.up_stairs = None
        self.down_stairs = None
        
        self.generate_dungeon()
        
    def generate_dungeon(self):
        """
        Generate dungeon based on depth
        """
        if self.depth % 5 == 0:
            self.generate_boss_room()
        elif self.depth % 3 == 0:
            self.generate_cavern()
        else:
            self.generate_classic_dungeon()
    
    def generate_classic_dungeon(self):
        """
        Generate classic dungeon with rooms and corridors
        """
        # Создание комнат
        num_rooms = random.randint(8, 15)
        rooms = []
        
        for _ in range(num_rooms * 2):
            w = random.randint(5, 12)
            h = random.randint(5, 10)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            
            new_room = Room(x, y, w, h)
            
            if not any(new_room.intersects(room) for room in rooms):
                rooms.append(new_room)
                self.create_room(new_room)
                
                if len(rooms) >= num_rooms:
                    break
        
        self.rooms = rooms
        
        # Соединение комнат коридорами
        rooms.sort(key=lambda r: r.x + r.y)
        
        for i in range(1, len(rooms)):
            self.create_corridor(rooms[i-1], rooms[i])
        
        # Добавление дополнительных соединений
        for _ in range(len(rooms) // 3):
            i = random.randint(0, len(rooms) - 2)
            j = random.randint(i + 1, len(rooms) - 1)
            if random.random() < 0.3:
                self.create_corridor(rooms[i], rooms[j])
        
        # Установка лестниц
        if len(rooms) > 0:
            # Начальная комната
            rooms[0].type = 'start'
            self.up_stairs = (rooms[0].center_x, rooms[0].center_y)
            self.tiles[rooms[0].center_y][rooms[0].center_x].type = 'stairs_up'
            
            # Выход
            rooms[-1].type = 'exit'
            self.down_stairs = (rooms[-1].center_x, rooms[-1].center_y)
            self.tiles[rooms[-1].center_y][rooms[-1].center_x].type = 'stairs_down'
            
            # Сокровищница
            if len(rooms) > 3:
                treasure_idx = random.randint(1, len(rooms) - 2)
                rooms[treasure_idx].type = 'treasure'
        
        # Заполнение данжена
        self.populate_dungeon()
    
    def generate_cavern(self):
        """
        Generate cavern using cellular automata
        """
        # Инициализация случайными значениями
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.45:
                    self.tiles[y][x].type = 'floor'
                    self.tiles[y][x].walkable = True
                else:
                    self.tiles[y][x].type = 'wall'
                    self.tiles[y][x].walkable = False
        
        # Применение клеточного автомата
        for _ in range(4):
            new_tiles = [[Tile(x, y, 'wall') for x in range(self.width)] 
                        for y in range(self.height)]
            
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    walls = self.count_walls(x, y)
                    
                    if self.tiles[y][x].type == 'wall':
                        if walls >= 5:
                            new_tiles[y][x].type = 'wall'
                        else:
                            new_tiles[y][x].type = 'floor'
                            new_tiles[y][x].walkable = True
                    else:
                        if walls >= 4:
                            new_tiles[y][x].type = 'wall'
                            new_tiles[y][x].walkable = False
                        else:
                            new_tiles[y][x].type = 'floor'
                            new_tiles[y][x].walkable = True
            
            self.tiles = new_tiles
        
        # Поиск комнат
        self.rooms = self.find_cavern_rooms()
        
        if not self.rooms:
            self.generate_classic_dungeon()
            return
        
        # Установка лестниц
        start_room = self.rooms[0]
        exit_room = self.rooms[-1]
        
        self.up_stairs = (start_room.center_x, start_room.center_y)
        self.down_stairs = (exit_room.center_x, exit_room.center_y)
        
        self.tiles[start_room.center_y][start_room.center_x].type = 'stairs_up'
        self.tiles[exit_room.center_y][exit_room.center_x].type = 'stairs_down'
        
        # Добавление озер
        for _ in range(random.randint(2, 5)):
            x = random.randint(5, self.width - 5)
            y = random.randint(5, self.height - 5)
            self.create_lake(x, y, random.choice(['water', 'lava']))
        
        self.populate_cavern()
    
    def generate_boss_room(self):
        """
        Generate boss room
        """
        center_x = self.width // 2
        center_y = self.height // 2
        room_w = 25
        room_h = 20
        
        # Создание комнаты
        for y in range(center_y - room_h//2, center_y + room_h//2):
            for x in range(center_x - room_w//2, center_x + room_w//2):
                if 0 < x < self.width-1 and 0 < y < self.height-1:
                    self.tiles[y][x].type = 'floor'
                    self.tiles[y][x].walkable = True
        
        # Добавление колонн
        for x in [center_x - room_w//2 + 3, center_x + room_w//2 - 4]:
            for y in [center_y - room_h//2 + 3, center_y + room_h//2 - 4]:
                self.tiles[y][x].type = 'wall'
                self.tiles[y][x].walkable = False
        
        # Лестницы
        self.up_stairs = (center_x - 8, center_y)
        self.down_stairs = (center_x + 8, center_y)
        
        self.tiles[center_y][center_x - 8].type = 'stairs_up'
        self.tiles[center_y][center_x + 8].type = 'stairs_down'
        
        # Создание комнаты босса
        boss_room = Room(center_x - room_w//2, center_y - room_h//2, room_w, room_h)
        boss_room.type = 'boss'
        self.rooms = [boss_room]
        
        # Сокровища
        for x in [center_x - 5, center_x + 5]:
            for y in [center_y - 3, center_y + 3]:
                self.tiles[y][x].type = 'treasure'
    
    def create_room(self, room):
        """
        Create a room on the map
        """
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                if 0 < y < self.height-1 and 0 < x < self.width-1:
                    self.tiles[y][x].type = 'floor'
                    self.tiles[y][x].walkable = True
    
    def create_corridor(self, room1, room2):
        """
        Create corridor between rooms
        """
        x1, y1 = room1.center_x, room1.center_y
        x2, y2 = room2.center_x, room2.center_y
        
        if random.random() < 0.5:
            self.create_h_tunnel(x1, x2, y1)
            self.create_v_tunnel(y1, y2, x2)
        else:
            self.create_v_tunnel(y1, y2, x1)
            self.create_h_tunnel(x1, x2, y2)
    
    def create_h_tunnel(self, x1, x2, y):
        """
        Create horizontal tunnel
        """
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 < y < self.height-1 and 0 < x < self.width-1:
                self.tiles[y][x].type = 'floor'
                self.tiles[y][x].walkable = True
    
    def create_v_tunnel(self, y1, y2, x):
        """
        Create vertical tunnel
        """
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 < y < self.height-1 and 0 < x < self.width-1:
                self.tiles[y][x].type = 'floor'
                self.tiles[y][x].walkable = True
    
    def create_lake(self, center_x, center_y, lake_type):
        """
        Create a lake of specified type
        """
        radius = random.randint(3, 7)
        for y in range(max(0, center_y - radius), min(self.height, center_y + radius)):
            for x in range(max(0, center_x - radius), min(self.width, center_x + radius)):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if dist < radius:
                    self.tiles[y][x].type = lake_type
                    self.tiles[y][x].walkable = (lake_type != 'lava')
    
    def find_cavern_rooms(self):
        """
        Find rooms in cavern using BFS
        """
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        rooms = []
        
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].type == 'floor' and not visited[y][x]:
                    # BFS для поиска связной области
                    queue = [(x, y)]
                    room_tiles = []
                    min_x, max_x = x, x
                    min_y, max_y = y, y
                    
                    while queue:
                        cx, cy = queue.pop(0)
                        if visited[cy][cx]:
                            continue
                        
                        visited[cy][cx] = True
                        room_tiles.append((cx, cy))
                        
                        min_x = min(min_x, cx)
                        max_x = max(max_x, cx)
                        min_y = min(min_y, cy)
                        max_y = max(max_y, cy)
                        
                        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                            nx, ny = cx + dx, cy + dy
                            if (0 <= nx < self.width and 0 <= ny < self.height and 
                                self.tiles[ny][nx].type == 'floor' and not visited[ny][nx]):
                                if (nx, ny) not in queue:
                                    queue.append((nx, ny))
                    
                    if len(room_tiles) > 10:
                        room = Room(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
                        rooms.append(room)
        
        rooms.sort(key=lambda r: r.w * r.h, reverse=True)
        return rooms[:5]
    
    def count_walls(self, x, y):
        """
        Count walls around a cell
        """
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.tiles[ny][nx].type == 'wall':
                        count += 1
        return count
    
    def populate_dungeon(self):
        """
        Populate dungeon with enemies and items
        """
        from .entities import Enemy, Item
        
        for room in self.rooms:
            if room.type == 'start':
                continue
            
            # Враги
            if room.type != 'boss':
                num_enemies = random.randint(0, 3)
                if room.type == 'treasure':
                    num_enemies += 2
                
                for _ in range(num_enemies):
                    x = random.randint(room.x + 1, room.x + room.w - 2)
                    y = random.randint(room.y + 1, room.y + room.h - 2)
                    
                    if self.depth < 3:
                        enemy_type = random.choice(['goblin', 'skeleton'])
                    elif self.depth < 7:
                        enemy_type = random.choice(['skeleton', 'orc'])
                    else:
                        enemy_type = random.choice(['orc', 'dragon'])
                    
                    self.entities.append(Enemy(x, y, enemy_type, self.depth))
            
            # Предметы
            num_items = 0
            if room.type == 'treasure':
                num_items = random.randint(3, 6)
            elif room.type == 'shop':
                num_items = random.randint(2, 4)
            else:
                num_items = random.randint(0, 2)
            
            for _ in range(num_items):
                x = random.randint(room.x + 1, room.x + room.w - 2)
                y = random.randint(room.y + 1, room.y + room.h - 2)
                
                if room.type == 'shop':
                    item_type = random.choice(['potion', 'mana_potion', 'weapon', 'armor'])
                elif room.type == 'treasure':
                    item_type = random.choice(['gold', 'weapon', 'armor', 'ring', 'amulet'])
                else:
                    item_type = random.choice(['potion', 'gold'])
                
                if room.type == 'treasure':
                    rarity = random.choices(['common', 'rare', 'epic', 'legendary'],
                                           weights=[0.3, 0.4, 0.2, 0.1])[0]
                elif room.type == 'shop':
                    rarity = random.choices(['common', 'rare', 'epic'],
                                           weights=[0.5, 0.3, 0.2])[0]
                else:
                    rarity = random.choices(['common', 'rare'],
                                           weights=[0.8, 0.2])[0]
                
                self.items.append(Item(x, y, item_type, rarity))
    
    def populate_cavern(self):
        """
        Populate cavern with enemies and items
        """
        from .entities import Enemy, Item
        
        for room in self.rooms:
            # Враги
            num_enemies = random.randint(2, 5)
            for _ in range(num_enemies):
                x = random.randint(room.x + 1, room.x + room.w - 2)
                y = random.randint(room.y + 1, room.y + room.h - 2)
                
                if self.depth < 3:
                    enemy_type = random.choice(['goblin', 'skeleton'])
                elif self.depth < 7:
                    enemy_type = random.choice(['skeleton', 'orc'])
                else:
                    enemy_type = random.choice(['orc', 'dragon'])
                
                self.entities.append(Enemy(x, y, enemy_type, self.depth))
            
            # Предметы
            num_items = random.randint(0, 3)
            for _ in range(num_items):
                x = random.randint(room.x + 1, room.x + room.w - 2)
                y = random.randint(room.y + 1, room.y + room.h - 2)
                item_type = random.choice(['potion', 'gold'])
                self.items.append(Item(x, y, item_type, 'common'))
    
    def update_fov(self, player, light_radius=8):
        """
        Update field of view
        """
        for y in range(self.height):
            for x in range(self.width):
                visible = self.is_in_fov(x, y, player.x, player.y, light_radius)
                self.tiles[y][x].visible = visible
                
                if visible:
                    self.tiles[y][x].explored = True
                    dist = math.sqrt((x - player.x)**2 + (y - player.y)**2)
                    light_level = max(0, 1 - dist / light_radius)
                    self.tiles[y][x].light_level = light_level
    
    def is_in_fov(self, x, y, px, py, radius):
        """
        Check if a tile is in field of view
        """
        dist = math.sqrt((x - px)**2 + (y - py)**2)
        if dist > radius:
            return False
        
        return self.has_line_of_sight(px, py, x, y)
    
    def has_line_of_sight(self, x1, y1, x2, y2):
        """
        Check line of sight using Bresenham's line algorithm
        """
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x = x1
        y = y1
        n = 1 + dx + dy
        x_inc = 1 if x2 > x1 else -1
        y_inc = 1 if y2 > y1 else -1
        error = dx - dy
        dx *= 2
        dy *= 2
        
        for _ in range(n):
            if not self.tiles[y][x].transparent:
                return False
            
            if error > 0:
                x += x_inc
                error -= dy
            elif error < 0:
                y += y_inc
                error += dx
            else:
                x += x_inc
                y += y_inc
                error -= dy
                error += dx
        
        return True
    
    def to_dict(self):
        """
        Convert map to dictionary for saving
        """
        return {
            'width': self.width,
            'height': self.height,
            'depth': self.depth,
            'tiles': [[{
                'type': tile.type,
                'explored': tile.explored
            } for tile in row] for row in self.tiles],
            'up_stairs': self.up_stairs,
            'down_stairs': self.down_stairs,
            'entities': [{
                'x': e.x, 'y': e.y,
                'type': e.enemy_type if hasattr(e, 'enemy_type') else 'player',
                'hp': e.stats.hp,
                'max_hp': e.stats.max_hp
            } for e in self.entities],
            'items': [{
                'x': i.x, 'y': i.y,
                'type': i.type,
                'rarity': i.rarity
            } for i in self.items]
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create map from dictionary
        """
        game_map = cls(data['width'], data['height'], data['depth'])
        
        # Восстановление тайлов
        for y in range(data['height']):
            for x in range(data['width']):
                tile_data = data['tiles'][y][x]
                game_map.tiles[y][x].type = tile_data['type']
                game_map.tiles[y][x].explored = tile_data['explored']
                game_map.tiles[y][x].walkable = tile_data['type'] != 'wall'
                game_map.tiles[y][x].transparent = tile_data['type'] != 'wall'
        
        game_map.up_stairs = data['up_stairs']
        game_map.down_stairs = data['down_stairs']
        
        # Восстановление врагов
        from .entities import Enemy
        for e_data in data['entities']:
            if e_data['type'] != 'player':
                enemy = Enemy(e_data['x'], e_data['y'], e_data['type'], data['depth'])
                enemy.stats.hp = e_data['hp']
                game_map.entities.append(enemy)
        
        # Восстановление предметов
        from .entities import Item
        for i_data in data['items']:
            item = Item(i_data['x'], i_data['y'], i_data['type'], i_data['rarity'])
            game_map.items.append(item)
        
        return game_map