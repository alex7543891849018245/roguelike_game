"""
Sprite management for the game - Kivy version
Keeps the same structure as the original Pygame version
"""

from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget
from kivy.utils import platform
from kivy.core.window import Window
import os
from kivy.graphics import Color

class SpriteManager:
    """
    Manages loading and caching of sprites
    """
    def __init__(self):
        self.sprites = {}
        self.backgrounds = {}
        self.load_all_sprites()
        
    def load_all_sprites(self):
        """Загружает все спрайты из папки images"""
        
        # Определяем базовый путь к images
        if platform == 'android':
            self.base_path = '/sdcard/roguelike/images/'
        else:
            # Для Windows - путь к папке images в корне проекта
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.base_path = os.path.join(current_dir, 'assets\images')
        
        print(f"\n📁 Загрузка спрайтов из: {self.base_path}")
        
        # Проверяем существует ли папка
        if not os.path.exists(self.base_path):
            print(f"❌ Папка не найдена: {self.base_path}")
            return
        
        # Тайлы подземелья
        dungeon_tiles = [
            ('dungeon/wall', os.path.join('dungeon', 'wall.png')),
            ('dungeon/floor', os.path.join('dungeon', 'floor.png')),
            ('dungeon/door', os.path.join('dungeon', 'door.png')),
            ('dungeon/stairs_down', os.path.join('dungeon', 'stairs_down.png')),
            ('dungeon/stairs_up', os.path.join('dungeon', 'stairs_up.png')),
            ('dungeon/water', os.path.join('dungeon', 'water.png')),
            ('dungeon/lava', os.path.join('dungeon', 'lava.png')),
            ('dungeon/column', os.path.join('dungeon', 'column.png')),
            ('dungeon/altar', os.path.join('dungeon', 'altar.png')),
        ]
        
        # Спрайты игрока
        player_sprites = [
            ('player_idle', os.path.join('player', 'idle.png')),
            ('player_attack', os.path.join('player', 'attack.png')),
        ]
        
        # Враги
        enemy_sprites = [
            ('goblin', os.path.join('enemies', 'goblin.png')),
            ('skeleton', os.path.join('enemies', 'skeleton.png')),
            ('orc', os.path.join('enemies', 'orc.png')),
            ('dragon', os.path.join('enemies', 'dragon.png')),
        ]
        
        # Предметы
        items = [
            ('items/treasure', os.path.join('items', 'treasure.png')),
            ('items/potion', os.path.join('items', 'potion.png')),
            ('items/gold', os.path.join('items', 'gold.png')),
            ('items/sword', os.path.join('items', 'weapons', 'sword.png')),
            ('items/axe', os.path.join('items', 'weapons', 'axe.png')),
            ('items/bow', os.path.join('items', 'weapons', 'bow.png')),
        ]
        
        # Эффекты
        effects = [
            ('effects/explosion', os.path.join('effects', 'explosion.png')),
            ('effects/heal', os.path.join('effects', 'heal.png')),
            ('effects/magic', os.path.join('effects', 'magic.png')),
            ('effects/fog', os.path.join('effects', 'fog.png')),
            ('effects/portal', os.path.join('effects', 'portal.png')),
        ]
        
        # Фоны
        backgrounds = [
            ('dungeon_bg', os.path.join('backgrounds', 'dungeon_bg.png')),
            ('cave_bg', os.path.join('backgrounds', 'cave_bg.png')),
            ('throne_bg', os.path.join('backgrounds', 'throne_bg.png')),
            ('menu_bg', os.path.join('backgrounds', 'menu_bg.png')),
        ]
        
        # Загружаем тайлы подземелья
        print("\n--- Загрузка тайлов подземелья ---")
        for name, path in dungeon_tiles:
            self.load_sprite(name, path)
        
        # Загружаем спрайты игрока
        print("\n--- Загрузка спрайтов игрока ---")
        for name, path in player_sprites:
            self.load_sprite(name, path)
        
        # Загружаем спрайты врагов
        print("\n--- Загрузка спрайтов врагов ---")
        for name, path in enemy_sprites:
            self.load_sprite(name, path)
        
        # Загружаем предметы
        print("\n--- Загрузка предметов ---")
        for name, path in items:
            self.load_sprite(name, path)
        
        # Загружаем эффекты
        print("\n--- Загрузка эффектов ---")
        for name, path in effects:
            self.load_sprite(name, path)
        
        # Загружаем фоны
        print("\n--- Загрузка фонов ---")
        for name, path in backgrounds:
            self.load_background(name, path)
        
        print(f"\n✅ Загружено спрайтов: {len(self.sprites)}")
        print(f"✅ Загружено фонов: {len(self.backgrounds)}")
    
    def load_sprite(self, name, path):
        """Загружает спрайт"""
        full_path = os.path.join(self.base_path, path)
        try:
            if os.path.exists(full_path):
                image = CoreImage(full_path)
                self.sprites[name] = image
                print(f"  ✅ Загружен спрайт: {name}")
            else:
                print(f"  ❌ Файл не найден: {full_path}")
                self.sprites[name] = None
        except Exception as e:
            print(f"  ❌ Ошибка загрузки {name}: {e}")
            self.sprites[name] = None
    
    def load_background(self, name, path):
        """Загружает фон"""
        full_path = os.path.join(self.base_path, path)
        try:
            if os.path.exists(full_path):
                image = CoreImage(full_path)
                self.backgrounds[name] = image
                print(f"  ✅ Загружен фон: {name}")
            else:
                print(f"  ❌ Файл не найден: {full_path}")
                self.backgrounds[name] = None
        except Exception as e:
            print(f"  ❌ Ошибка загрузки фона {name}: {e}")
            self.backgrounds[name] = None
    
    def create_placeholder(self, name, size=(32, 32), is_background=False):
        """Создает заглушку для Kivy"""
        from kivy.graphics import Color, Rectangle
        from kivy.uix.widget import Widget
        
        widget = Widget(size=size)
        
        with widget.canvas:
            if is_background:
                # Градиент для фона
                Color(0.1, 0.1, 0.15, 1)
                Rectangle(pos=(0, 0), size=size)
            else:
                # Цветной прямоугольник для спрайтов
                colors = {
                    'wall': (0.3, 0.3, 0.3, 1),
                    'floor': (0.2, 0.2, 0.2, 1),
                    'door': (0.4, 0.26, 0.13, 1),
                    'water': (0, 0.4, 0.8, 1),
                    'lava': (0.8, 0.2, 0, 1),
                    'treasure': (1, 0.84, 0, 1),
                    'potion': (1, 0, 0, 1),
                    'gold': (1, 1, 0, 1),
                    'player': (0, 0.4, 1, 1),
                    'goblin': (0, 1, 0, 1),
                    'skeleton': (0.8, 0.8, 0.8, 1),
                    'orc': (0, 0.6, 0, 1),
                    'dragon': (1, 0, 0, 1),
                }
                
                color = (1, 0, 1, 1)  # Розовый по умолчанию
                for key, col in colors.items():
                    if key in name:
                        color = col
                        break
                
                Color(*color)
                Rectangle(pos=(0, 0), size=size)
        
        return widget
    
    def get_sprite(self, name):
        """Возвращает спрайт"""
        if name in self.sprites and self.sprites[name]:
            return self.sprites[name].texture
        return None
    
    def get_background(self, name):
        """Возвращает фон"""
        if name in self.backgrounds and self.backgrounds[name]:
            return self.backgrounds[name].texture
        return None
    
    def get_hurt_sprite(self, name):
        """Возвращает спрайт с красным эффектом"""
        sprite = self.get_sprite(name)
        # В Kivy сложнее сделать эффект, пока возвращаем обычный спрайт
        return sprite


class DungeonRenderer:
    """Класс для отрисовки подземелья с графикой - Kivy version"""
    def __init__(self, sprite_manager):
        self.sprite_manager = sprite_manager
        self.current_background = None
        self.tile_size = 32
        
    def set_background(self, bg_name):
        """Устанавливает текущий фон"""
        self.current_background = self.sprite_manager.get_background(bg_name)
    
    def set_tile_size(self, size):
        """Устанавливает размер тайлов"""
        self.tile_size = size
    
    def draw_tile(self, canvas, tile, x, y, camera_x, camera_y, light_level=1.0):
        """Рисует один тайл на canvas"""
        screen_x = x * self.tile_size - camera_x
        screen_y = y * self.tile_size - camera_y
        
        # Получаем спрайт для тайла
        sprite_name = self.get_tile_sprite_name(tile)
        texture = self.sprite_manager.get_sprite(sprite_name)
        
        if texture:
            # Рисуем с освещением
            if light_level < 1.0:
                from kivy.graphics import Color, Rectangle
                Color(light_level, light_level, light_level, 1)
                Rectangle(texture=texture, pos=(screen_x, screen_y),
                         size=(self.tile_size, self.tile_size))
            else:
                from kivy.graphics import Color, Rectangle
                Color(1, 1, 1, 1)
                Rectangle(texture=texture, pos=(screen_x, screen_y),
                         size=(self.tile_size, self.tile_size))
    
    def get_tile_sprite_name(self, tile):
        """Определяет имя спрайта для тайла"""
        mapping = {
            'wall': 'dungeon/wall',
            'floor': 'dungeon/floor',
            'stairs_down': 'dungeon/stairs_down',
            'stairs_up': 'dungeon/stairs_up',
            'water': 'dungeon/water',
            'lava': 'dungeon/lava',
            'door': 'dungeon/door',
            'treasure': 'items/treasure',
        }
        return mapping.get(tile.type, 'dungeon/floor')
    
    def draw_entity(self, canvas, entity, x, y, camera_x, camera_y):
        """Рисует сущность (игрока или врага)"""
        screen_x = x * self.tile_size - camera_x
        screen_y = y * self.tile_size - camera_y
        
        # Определяем имя спрайта
        if hasattr(entity, 'enemy_type'):
            sprite_name = entity.enemy_type
        else:
            sprite_name = 'player_idle'
            if hasattr(entity, 'animation_frame') and entity.animation_frame > 0:
                sprite_name = 'player_attack'
        
        texture = self.sprite_manager.get_sprite(sprite_name)
        
        from kivy.graphics import Color, Rectangle
        if texture:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture, pos=(screen_x, screen_y),
                     size=(self.tile_size, self.tile_size))
        else:
            # Запасной вариант - цветной прямоугольник
            color = getattr(entity, 'color', (1, 1, 1, 1))
            Color(*color)
            Rectangle(pos=(screen_x, screen_y),
                     size=(self.tile_size, self.tile_size))
    
    def draw_item(self, canvas, item, x, y, camera_x, camera_y):
        """Рисует предмет"""
        screen_x = x * self.tile_size - camera_x
        screen_y = y * self.tile_size - camera_y
        
        sprite_name = f"items/{item.type}"
        texture = self.sprite_manager.get_sprite(sprite_name)
        
        from kivy.graphics import Color, Rectangle, Ellipse
        if texture:
            Color(1, 1, 1, 1)
            Rectangle(texture=texture,
                     pos=(screen_x + self.tile_size//4,
                          screen_y + self.tile_size//4),
                     size=(self.tile_size//2, self.tile_size//2))
        else:
            # Запасной вариант
            color = getattr(item, 'color', (1, 1, 0, 1))
            Color(*color)
            Ellipse(pos=(screen_x + self.tile_size//4,
                        screen_y + self.tile_size//4),
                   size=(self.tile_size//2, self.tile_size//2))
    
    def draw_background(self, canvas, width, height):
        """Рисует фоновое изображение"""
        from kivy.graphics import Color, Rectangle
        
        if self.current_background:
            Color(1, 1, 1, 1)
            Rectangle(texture=self.current_background, pos=(0, 0),
                     size=(width, height))
        else:
            # Темный фон по умолчанию
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=(0, 0), size=(width, height))