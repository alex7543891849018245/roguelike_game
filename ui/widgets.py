"""
Custom widgets for the game - With sprite support
"""

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, BooleanProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform
import math

from .sprite_manager import SpriteManager


class MapWidget(Widget):
    """
    Widget for rendering the game map with sprites
    """
    player = ObjectProperty(None)
    game_map = ObjectProperty(None)
    camera_x = NumericProperty(0)
    camera_y = NumericProperty(0)
    tile_size = NumericProperty(32)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite_manager = SpriteManager()
        self.bind(pos=self.redraw, size=self.redraw)
        
        # Адаптивный размер тайлов
        if platform == 'android':
            self.tile_size = dp(28)
    
    def set_game(self, player, game_map):
        """Set player and map references"""
        self.player = player
        self.game_map = game_map
        self.redraw()
    
    def update_camera(self, player):
        """Update camera position to follow player"""
        if not player or not self.game_map:
            return
        
        target_x = player.x * self.tile_size - self.width / 2
        target_y = player.y * self.tile_size - self.height / 2
        
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        max_x = self.game_map.width * self.tile_size - self.width
        max_y = self.game_map.height * self.tile_size - self.height
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))
    
    def redraw(self, *args):
        """Redraw the map with sprites"""
        if not self.game_map or not self.player:
            return
        
        self.canvas.clear()
        
        with self.canvas:
            # Рисование тайлов
            for y in range(self.game_map.height):
                for x in range(self.game_map.width):
                    tile = self.game_map.tiles[y][x]
                    
                    if not tile.explored:
                        continue
                    
                    screen_x = x * self.tile_size - self.camera_x + self.x
                    screen_y = y * self.tile_size - self.camera_y + self.y
                    
                    if (screen_x + self.tile_size < self.x or 
                        screen_x > self.x + self.width or
                        screen_y + self.tile_size < self.y or 
                        screen_y > self.y + self.height):
                        continue
                    
                    # Определяем яркость (освещение)
                    if tile.visible:
                        brightness = getattr(tile, 'light_level', 1.0)
                    else:
                        brightness = 0.5
                    
                    # Получаем текстуру тайла
                    texture = self.sprite_manager.get_tile_texture(tile.type)
                    
                    if texture:
                        # Рисуем с изменением яркости
                        Color(brightness, brightness, brightness, 1)
                        Rectangle(texture=texture,
                                pos=(screen_x, screen_y),
                                size=(self.tile_size, self.tile_size))
                    else:
                        # Запасной вариант - цветной прямоугольник
                        Color(*tile.color[:3], 1 if tile.visible else 0.5)
                        Rectangle(pos=(screen_x, screen_y),
                                size=(self.tile_size, self.tile_size))
            
            # Рисование предметов
            for item in self.game_map.items:
                tile = self.game_map.tiles[item.y][item.x]
                if not tile.visible and not tile.explored:
                    continue
                
                screen_x = item.x * self.tile_size - self.camera_x + self.x
                screen_y = item.y * self.tile_size - self.camera_y + self.y
                
                texture = self.sprite_manager.get_item_texture(item.type)
                
                if texture:
                    alpha = 1.0 if tile.visible else 0.7
                    Color(1, 1, 1, alpha)
                    Rectangle(texture=texture,
                            pos=(screen_x + self.tile_size//4,
                                 screen_y + self.tile_size//4),
                            size=(self.tile_size//2, self.tile_size//2))
                else:
                    Color(*item.color[:3], 1.0 if tile.visible else 0.7)
                    Ellipse(pos=(screen_x + self.tile_size//4,
                                screen_y + self.tile_size//4),
                           size=(self.tile_size//2, self.tile_size//2))
            
            # Рисование врагов
            for enemy in self.game_map.entities:
                if not enemy.is_alive:
                    continue
                
                tile = self.game_map.tiles[enemy.y][enemy.x]
                if not tile.visible and not tile.explored:
                    continue
                
                screen_x = enemy.x * self.tile_size - self.camera_x + self.x
                screen_y = enemy.y * self.tile_size - self.camera_y + self.y
                
                # Выбор текстуры в зависимости от типа врага
                texture = self.sprite_manager.get_enemy_texture(enemy.enemy_type)
                
                # Эффект пульсации при анимации
                if enemy.animation_frame > 0:
                    offset = -2
                    size = self.tile_size + 4
                else:
                    offset = 0
                    size = self.tile_size
                
                if texture:
                    alpha = 1.0 if tile.visible else 0.7
                    Color(1, 1, 1, alpha)
                    Rectangle(texture=texture,
                            pos=(screen_x + offset, screen_y + offset),
                            size=(size, size))
                else:
                    Color(*enemy.color[:3], 1.0 if tile.visible else 0.7)
                    RoundedRectangle(pos=(screen_x + offset, screen_y + offset),
                                    size=(size, size),
                                    radius=[5, 5, 5, 5])
            
            # Рисование игрока
            if self.player:
                screen_x = self.player.x * self.tile_size - self.camera_x + self.x
                screen_y = self.player.y * self.tile_size - self.camera_y + self.y
                
                # Выбор текстуры игрока (idle или attack)
                if self.player.animation_frame > 0:
                    texture = self.sprite_manager.get_player_texture('attack')
                else:
                    texture = self.sprite_manager.get_player_texture('idle')
                
                if texture:
                    Color(1, 1, 1, 1)
                    Rectangle(texture=texture,
                            pos=(screen_x, screen_y),
                            size=(self.tile_size, self.tile_size))
                else:
                    Color(0, 0, 1, 1)
                    RoundedRectangle(pos=(screen_x, screen_y),
                                    size=(self.tile_size, self.tile_size),
                                    radius=[5, 5, 5, 5])


class TouchJoystick(Widget):
    """
    Touch joystick for mobile controls - Optimized for landscape
    """
    active = BooleanProperty(False)
    direction = ListProperty([0, 0])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(100), dp(100))
        self.pos_hint = {'right': 0.9, 'y': 0.05}
        self.touch_pos = (0, 0)
        self.base_center = (0, 0)
        
        # Обновляем позицию при изменении
        self.bind(pos=self.update_position, size=self.update_position)
        
        with self.canvas:
            # База джойстика (прозрачный круг)
            Color(0.3, 0.3, 0.3, 0.5)
            self.base = Ellipse(pos=self.pos, size=self.size)
            
            # Джойстик
            Color(0.7, 0.7, 0.7, 0.8)
            self.stick = Ellipse(pos=self.pos, size=(dp(40), dp(40)))
    
    def update_position(self, *args):
        """Update position of joystick elements"""
        self.base.pos = self.pos
        self.base_center = (self.x + self.width/2, self.y + self.height/2)
        
        if not self.active:
            self.stick.pos = (self.base_center[0] - dp(20), 
                             self.base_center[1] - dp(20))
    
    def on_touch_down(self, touch):
        """Handle touch down"""
        if self.collide_point(*touch.pos):
            self.active = True
            self.touch_pos = touch.pos
            self.update_stick_position()
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch move"""
        if self.active:
            self.touch_pos = touch.pos
            self.update_stick_position()
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up"""
        if self.active:
            self.active = False
            self.direction = [0, 0]
            self.stick.pos = (self.base_center[0] - dp(20), 
                             self.base_center[1] - dp(20))
            return True
        return super().on_touch_up(touch)
    
    def update_stick_position(self):
        """Update joystick stick position based on touch"""
        dx = self.touch_pos[0] - self.base_center[0]
        dy = self.touch_pos[1] - self.base_center[1]
        distance = math.sqrt(dx**2 + dy**2)
        max_distance = self.width / 2
        
        if distance > max_distance:
            # Ограничение радиуса
            dx = dx * max_distance / distance
            dy = dy * max_distance / distance
            self.direction = [dx/max_distance, dy/max_distance]
        else:
            self.direction = [dx/max_distance if max_distance > 0 else 0,
                            dy/max_distance if max_distance > 0 else 0]
        
        self.stick.pos = (self.base_center[0] + dx - dp(20),
                         self.base_center[1] + dy - dp(20))
    
    def get_direction(self):
        """Get normalized direction vector"""
        if not self.active:
            return (0, 0)
        
        # Преобразование в целые направления (-1, 0, 1)
        dx, dy = self.direction
        if abs(dx) < 0.3:
            dx = 0
        else:
            dx = 1 if dx > 0 else -1
        
        if abs(dy) < 0.3:
            dy = 0
        else:
            dy = 1 if dy > 0 else -1
        
        return (dx, dy)


class ActionButton(Button):
    """
    Action button for mobile controls - Landscape optimized
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(60), dp(60))
        self.background_normal = ''
        self.background_color = (0.2, 0.2, 0.2, 0.8)
        self.font_size = dp(24)
        self.bold = True


class MessageLog(ScrollView):
    """
    Scrollable message log widget - Landscape optimized
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_list = []
        self.message_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.message_grid.bind(minimum_height=self.message_grid.setter('height'))
        self.add_widget(self.message_grid)
        self.do_scroll_x = False
        self.do_scroll_y = True
        self.scroll_type = ['content']
        self.bar_width = dp(4)
    
    def add_message(self, text):
        """Add message to log"""
        self.message_list.append(text)
        if len(self.message_list) > 10:
            self.message_list.pop(0)
        
        self.update_display()
        # Автоскролл вниз
        Clock.schedule_once(lambda dt: self.scroll_to_end(), 0.1)
    
    def scroll_to_end(self):
        """Scroll to the end of the log"""
        if self.message_grid.height > self.height:
            self.scroll_y = 0
    
    def update_display(self):
        """Update message display"""
        self.message_grid.clear_widgets()
        
        for msg in self.message_list[-8:]:  # Показываем последние 8 сообщений
            label = Label(
                text=msg,
                size_hint_y=None,
                height=dp(18),
                halign='left',
                valign='middle',
                color=(1, 1, 1, 1),
                font_size=dp(11),
                shorten=True,
                shorten_from='right'
            )
            label.bind(size=label.setter('text_size'))
            self.message_grid.add_widget(label)


class HealthBar(Widget):
    """
    Health bar widget - Landscape optimized
    """
    current = NumericProperty(50)
    maximum = NumericProperty(100)
    bar_color = ListProperty([1, 0, 0, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.redraw, size=self.redraw, 
                  current=self.redraw, maximum=self.redraw)
    
    def redraw(self, *args):
        """Redraw the bar"""
        self.canvas.clear()
        
        with self.canvas:
            # Фон
            Color(0.2, 0.2, 0.2, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[5, 5, 5, 5])
            
            # Заполнение
            if self.maximum > 0:
                fill_width = self.width * (self.current / self.maximum)
                Color(*self.bar_color)
                RoundedRectangle(
                    pos=self.pos,
                    size=(fill_width, self.height),
                    radius=[5, 5, 5, 5]
                )
            
            # Контур
            Color(1, 1, 1, 1)
            Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, 5),
                width=1.5
            )


class StatusPanel(BoxLayout):
    """
    Panel displaying player stats - Compact for landscape
    """
    player = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(3)
        self.spacing = dp(3)
        
        # Health bar
        self.health_label = Label(
            text="HP",
            size_hint_y=None,
            height=dp(14),
            halign='left',
            font_size=dp(11),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.add_widget(self.health_label)
        
        self.health_bar = HealthBar(size_hint_y=None, height=dp(14))
        self.add_widget(self.health_bar)
        
        # Mana bar
        self.mana_label = Label(
            text="MP",
            size_hint_y=None,
            height=dp(14),
            halign='left',
            font_size=dp(11),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.add_widget(self.mana_label)
        
        self.mana_bar = HealthBar(bar_color=[0, 0, 1, 1], size_hint_y=None, height=dp(14))
        self.add_widget(self.mana_bar)
        
        # Exp bar
        self.exp_label = Label(
            text="EXP",
            size_hint_y=None,
            height=dp(14),
            halign='left',
            font_size=dp(11),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.add_widget(self.exp_label)
        
        self.exp_bar = HealthBar(bar_color=[1, 0.84, 0, 1], size_hint_y=None, height=dp(14))
        self.add_widget(self.exp_bar)
        
        # Stats label (compact)
        self.stats_label = Label(
            text="",
            size_hint_y=None,
            height=dp(24),
            halign='left',
            valign='middle',
            font_size=dp(11)
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        self.add_widget(self.stats_label)
    
    def set_player(self, player):
        """Set player reference"""
        self.player = player
        self.update_stats()
    
    def update_stats(self):
        """Update stats display"""
        if not self.player:
            return
        
        self.health_bar.current = self.player.stats.hp
        self.health_bar.maximum = self.player.stats.max_hp
        self.health_label.text = f"HP: {self.player.stats.hp}/{self.player.stats.max_hp}"
        
        self.mana_bar.current = self.player.stats.mana
        self.mana_bar.maximum = self.player.stats.max_mana
        self.mana_label.text = f"MP: {self.player.stats.mana}/{self.player.stats.max_mana}"
        
        self.exp_bar.current = self.player.stats.exp
        self.exp_bar.maximum = self.player.stats.exp_to_next
        self.exp_label.text = f"EXP: {self.player.stats.exp}/{self.player.stats.exp_to_next}"
        
        self.stats_label.text = (
            f"Lv.{self.player.stats.level} | "
            f"⚔️{self.player.stats.strength} | "
            f"🛡️{self.player.stats.defense} | "
            f"💰{self.player.stats.gold}"
        )


class BackgroundWidget(Widget):
    """
    Widget for rendering backgrounds
    """
    background_name = StringProperty('menu_bg')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite_manager = SpriteManager()
        self.bind(pos=self.redraw, size=self.redraw, background_name=self.redraw)
    
    def redraw(self, *args):
        """Redraw background"""
        self.canvas.clear()
        
        texture = self.sprite_manager.get_background(self.background_name)
        if texture:
            with self.canvas:
                Color(1, 1, 1, 1)
                # Масштабируем фон под размер виджета
                Rectangle(texture=texture,
                         pos=self.pos,
                         size=self.size)