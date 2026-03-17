"""
Screen classes for the game
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import platform
import random
import math

from .widgets import MapWidget, TouchJoystick, ActionButton, MessageLog, HealthBar, StatusPanel, BackgroundWidget
from .visual_effects import VisualEffects, SplashEffect, LoadingEffect


class SplashScreen(Screen):
    """
    AlexStudio Code presents screen with fade effect
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.splash_effect = None
        self.effects_added = False
        
    def on_enter(self):
        """Called when screen is entered"""
        # Создаем эффект сплэша
        if not self.effects_added:
            self.splash_effect = SplashEffect()
            self.add_widget(self.splash_effect)
            self.effects_added = True
        
        # Запускаем анимацию
        self.splash_effect.start_splash()
        Clock.schedule_interval(self.check_splash_finished, 0.1)
    
    def check_splash_finished(self, dt):
        """Check if splash animation is finished"""
        if self.splash_effect and self.splash_effect.state == 3:  # Finished
            Clock.unschedule(self.check_splash_finished)
            self.manager.current = 'loading'
    
    def on_leave(self):
        """Called when leaving screen"""
        if self.splash_effect:
            self.remove_widget(self.splash_effect)
            self.effects_added = False


class LoadingScreen(Screen):
    """
    Loading screen with progress bar and tips
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_effect = None
        self.effects_added = False
        self.loading_start_time = 0
        
    def on_enter(self):
        """Called when screen is entered"""
        # Запоминаем время начала загрузки
        self.loading_start_time = Clock.get_time()
        
        # Создаем эффект загрузки
        if not self.effects_added:
            self.loading_effect = LoadingEffect()
            self.add_widget(self.loading_effect)
            self.effects_added = True
        
        # Запускаем загрузку
        self.loading_effect.start_loading()
        
        # Планируем проверку
        Clock.schedule_interval(self.check_loading, 0.1)
    
    def check_loading(self, dt):
        """Check if loading should finish"""
        # Прошло уже 2 секунды?
        if Clock.get_time() - self.loading_start_time > 2.0:
            Clock.unschedule(self.check_loading)
            
            # Переходим в игру или меню
            app = App.get_running_app()
            if app.player and app.current_map:
                self.manager.current = 'game'
            else:
                self.manager.current = 'menu'
            return False
        
        return True  # продолжаем проверку
    
    def on_leave(self):
        """Called when leaving screen"""
        Clock.unschedule(self.check_loading)
        if self.loading_effect:
            self.remove_widget(self.loading_effect)
            self.effects_added = False


class MenuScreen(Screen):
    """
    Main menu screen
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def new_game(self):
        """Start new game"""
        app = App.get_running_app()
        app.new_game()
        self.manager.current = 'loading'
    
    def load_game(self):
        """Load saved game"""
        app = App.get_running_app()
        if app.load_game(0):
            self.manager.current = 'loading'
        else:
            self.show_no_save_message()
    
    def show_no_save_message(self):
        """Show message when no save exists"""
        self.ids.message_label.text = "Нет сохраненной игры!"
        Clock.schedule_once(lambda dt: self.clear_message(), 2)
    
    def clear_message(self):
        """Clear message"""
        self.ids.message_label.text = ""
    
    def open_settings(self):
        """Open settings screen"""
        self.manager.current = 'settings'
    
    def quit_game(self):
        """Quit the game"""
        App.get_running_app().stop()


class GameScreen(Screen):
    """
    Main game screen with map and controls
    """
    player = ObjectProperty(None)
    game_map = ObjectProperty(None)
    combat_system = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touch_joystick = None
        self.move_direction = (0, 0)
        self.enemy_turn_scheduled = False
        self.visual_effects = VisualEffects()
        self.effects_added = False
        
    def on_enter(self):
        """Called when screen is entered"""
        app = App.get_running_app()
        
        # Добавляем визуальные эффекты на экран
        if not self.effects_added:
            self.add_widget(self.visual_effects)
            self.effects_added = True
        
        # Настройка управления
        if platform == 'android' or app.settings.get('touch_controls', False):
            self.setup_touch_controls()
        
        # Запуск игрового цикла
        Clock.schedule_interval(self.game_loop, 1.0/60.0)
    
    def setup_game(self, player, game_map, combat_system):
        """Setup game with player and map"""
        self.player = player
        self.game_map = game_map
        self.combat_system = combat_system
        
        # Передача данных виджетам
        self.ids.map_widget.set_game(player, game_map)
        self.ids.map_widget.set_visual_effects(self.visual_effects)
        self.ids.status_panel.set_player(player)
        self.ids.message_log.add_message("Добро пожаловать в подземелье!")
        self.ids.message_log.add_message(f"Уровень: {game_map.depth}")
    
    def setup_touch_controls(self):
        """Setup touch controls for mobile"""
        layout = self.ids.controls_layout
        
        # Очищаем layout
        layout.clear_widgets()
        
        # Создание джойстика
        self.touch_joystick = TouchJoystick()
        layout.add_widget(self.touch_joystick)
        
        # Кнопки действий
        attack_btn = ActionButton(text="⚔️")
        attack_btn.background_color = (1, 0, 0, 0.8)
        attack_btn.bind(on_press=self.attack_nearest)
        layout.add_widget(attack_btn)
        
        potion_btn = ActionButton(text="🧪")
        potion_btn.background_color = (0, 1, 0, 0.8)
        potion_btn.bind(on_press=self.use_potion)
        layout.add_widget(potion_btn)
        
        inventory_btn = ActionButton(text="🎒")
        inventory_btn.background_color = (0, 0, 1, 0.8)
        inventory_btn.bind(on_press=self.open_inventory)
        layout.add_widget(inventory_btn)
    
    def get_joystick_direction(self):
        """Get direction from joystick"""
        if self.touch_joystick:
            return self.touch_joystick.get_direction()
        return (0, 0)
    
    def game_loop(self, dt):
        """Main game loop"""
        if not self.player or not self.game_map:
            return
        
        # Обновление карты
        self.game_map.update_fov(self.player)
        
        # Обновление визуальных эффектов
        self.visual_effects.update(dt)
        
        # Получаем смещение от тряски камеры
        shake_x, shake_y = self.visual_effects.get_shake_offset()
        
        # Обработка движения от джойстика
        dx, dy = self.get_joystick_direction()
        if (dx, dy) != (0, 0):
            self.move_player(dx, dy)
        
        # Ход врагов (если игрок сделал ход)
        if self.move_direction != (0, 0) and not self.enemy_turn_scheduled:
            self.enemy_turn_scheduled = True
            Clock.schedule_once(self.process_enemy_turn, 0.1)
        
        # Обновление UI с учетом тряски
        self.ids.map_widget.update_camera(self.player)
        self.ids.map_widget.set_shake_offset(shake_x, shake_y)
        self.ids.map_widget.redraw()
        self.ids.status_panel.update_stats()
    
    def process_enemy_turn(self, dt):
        """Process enemy turns"""
        if not self.player or not self.game_map:
            self.enemy_turn_scheduled = False
            return
        
        # Обновление эффектов игрока
        self.player.update()
        
        # Ход врагов
        enemies_to_remove = []
        for enemy in self.game_map.entities[:]:
            if enemy.is_alive:
                result = enemy.ai_turn(self.player, self.game_map)
                if result['action'] == 'attack':
                    damage = result.get('damage', 0)
                    self.visual_effects.add_damage_number(
                        self.player.x, self.player.y, damage, 
                        is_player=True, tile_size=self.ids.map_widget.tile_size
                    )
                    self.visual_effects.add_particles(
                        self.player.x, self.player.y, (1, 0, 0), 
                        10, self.ids.map_widget.tile_size
                    )
                    self.visual_effects.shake_screen(3)
                    
                    self.ids.message_log.add_message(
                        f"{enemy.name} атакует! ({damage} урона)")
            else:
                enemies_to_remove.append(enemy)
        
        # Удаление мертвых врагов
        for enemy in enemies_to_remove:
            if enemy in self.game_map.entities:
                self.game_map.entities.remove(enemy)
                self.player.gain_exp(enemy.stats.exp)
                self.player.stats.gold += enemy.stats.gold
                self.ids.message_log.add_message(
                    f"Победа! +{enemy.stats.exp} опыта")
        
        self.move_direction = (0, 0)
        self.enemy_turn_scheduled = False
        
        # Проверка смерти игрока
        if self.player.stats.hp <= 0:
            self.game_over()
    
    def move_player(self, dx, dy):
        """Move player"""
        if not self.player or not self.game_map:
            return
        
        if self.player.move(dx, dy, self.game_map):
            self.move_direction = (dx, dy)
            
            # Проверка лестниц
            tile = self.game_map.tiles[self.player.y][self.player.x]
            if tile.type == 'stairs_down':
                self.next_level()
            elif tile.type == 'stairs_up':
                self.previous_level()
            
            # Подбор предметов
            for item in self.game_map.items[:]:
                if item.x == self.player.x and item.y == self.player.y:
                    result = item.use(self.player)
                    if result['used']:
                        self.game_map.items.remove(item)
                        self.ids.message_log.add_message(result['effect'])
                        
                        # Эффекты для предметов
                        if item.type == 'gold':
                            self.visual_effects.add_particles(
                                item.x, item.y, (1, 0.84, 0), 
                                15, self.ids.map_widget.tile_size
                            )
                            app = App.get_running_app()
                            app.play_sound('gold')
                        elif item.type == 'potion':
                            self.visual_effects.add_particles(
                                item.x, item.y, (0, 1, 0), 
                                20, self.ids.map_widget.tile_size
                            )
                            app = App.get_running_app()
                            app.play_sound('potion')
                    else:
                        # Добавление в инвентарь
                        self.player.inventory.append(item)
                        self.game_map.items.remove(item)
                        self.ids.message_log.add_message(
                            f"Подобрано: {item.name} ({item.rarity})")
    
    def attack_nearest(self, *args):
        """Attack nearest enemy"""
        if not self.player or not self.game_map:
            return
        
        nearest = None
        min_dist = float('inf')
        
        for enemy in self.game_map.entities:
            dist = self.player.distance_to(enemy)
            if dist < min_dist and dist <= 1.5:
                min_dist = dist
                nearest = enemy
        
        if nearest:
            # Расчет урона
            damage = self.player.stats.strength + random.randint(-2, 3)
            actual = nearest.take_damage(damage)
            
            # Визуальные эффекты
            self.visual_effects.add_damage_number(
                nearest.x, nearest.y, actual, 
                is_player=False, tile_size=self.ids.map_widget.tile_size
            )
            self.visual_effects.add_particles(
                nearest.x, nearest.y, (1, 0, 0), 
                15, self.ids.map_widget.tile_size
            )
            self.visual_effects.shake_screen(3)
            
            self.ids.message_log.add_message(f"Атака! {actual} урона")
            
            # Анимация
            self.player.animation_frame = 5
            nearest.animation_frame = 5
            
            # Звук
            app = App.get_running_app()
            app.play_sound('attack')
            
            self.move_direction = (1, 0)  # Триггер хода врагов
        else:
            self.ids.message_log.add_message("Нет врагов рядом!")
    
    def use_potion(self, *args):
        """Use health potion"""
        if not self.player:
            return
        
        for item in self.player.inventory:
            if item.type == 'potion':
                old_hp = self.player.stats.hp
                result = item.use(self.player)
                if result['used']:
                    self.player.inventory.remove(item)
                    heal_amount = self.player.stats.hp - old_hp
                    
                    if heal_amount > 0:
                        self.visual_effects.add_damage_number(
                            self.player.x, self.player.y, heal_amount, 
                            is_player=False, tile_size=self.ids.map_widget.tile_size
                        )
                        self.visual_effects.add_particles(
                            self.player.x, self.player.y, (0, 1, 0), 
                            20, self.ids.map_widget.tile_size
                        )
                    
                    self.ids.message_log.add_message(result['effect'])
                    
                    # Звук
                    app = App.get_running_app()
                    app.play_sound('potion')
                return
        
        self.ids.message_log.add_message("Нет зелий!")
    
    def next_level(self):
        """Go to next level"""
        self.ids.message_log.add_message("Спуск глубже...")
        
        # Эффект перехода
        self.visual_effects.add_particles(
            self.player.x, self.player.y, (0, 0, 1), 
            30, self.ids.map_widget.tile_size
        )
        
        new_depth = self.game_map.depth + 1
        self.game_map = GameMap(50, 50, new_depth)
        
        if self.game_map.up_stairs:
            self.player.x, self.player.y = self.game_map.up_stairs
        
        self.ids.map_widget.set_game(self.player, self.game_map)
        
        # Звук
        app = App.get_running_app()
        app.play_sound('door')
    
    def previous_level(self):
        """Go to previous level"""
        if self.game_map.depth > 1:
            self.ids.message_log.add_message("Подъем выше...")
            
            # Эффект перехода
            self.visual_effects.add_particles(
                self.player.x, self.player.y, (0, 1, 1), 
                30, self.ids.map_widget.tile_size
            )
            
            new_depth = self.game_map.depth - 1
            self.game_map = GameMap(50, 50, new_depth)
            
            if self.game_map.down_stairs:
                self.player.x, self.player.y = self.game_map.down_stairs
            
            self.ids.map_widget.set_game(self.player, self.game_map)
            
            # Звук
            app = App.get_running_app()
            app.play_sound('door')
    
    def open_inventory(self, *args):
        """Open inventory screen"""
        self.manager.current = 'inventory'
    
    def game_over(self):
        """Game over"""
        self.ids.message_log.add_message("Вы погибли...")
        
        # Эффект смерти
        self.visual_effects.add_particles(
            self.player.x, self.player.y, (1, 0, 0), 
            50, self.ids.map_widget.tile_size
        )
        self.visual_effects.shake_screen(10)
        
        Clock.schedule_once(lambda dt: self.go_to_game_over(), 1)
    
    def go_to_game_over(self):
        """Go to game over screen"""
        self.manager.current = 'game_over'
    
    def on_leave(self):
        """Called when leaving screen"""
        Clock.unschedule(self.game_loop)
        if self.effects_added:
            self.remove_widget(self.visual_effects)
            self.effects_added = False


class InventoryScreen(Screen):
    """
    Inventory screen
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0
        
    def on_enter(self):
        """Called when screen is entered"""
        self.update_inventory()
    
    def update_inventory(self):
        """Update inventory display"""
        app = App.get_running_app()
        grid = self.ids.inventory_grid
        grid.clear_widgets()
        
        if not app.player or not app.player.inventory:
            grid.add_widget(Label(
                text="Инвентарь пуст",
                size_hint_y=None,
                height=50,
                color=(1, 1, 1, 1)
            ))
            return
        
        for i, item in enumerate(app.player.inventory):
            # Цвет в зависимости от редкости
            if item.rarity == 'common':
                color = (1, 1, 1, 1)
            elif item.rarity == 'rare':
                color = (0, 0, 1, 1)
            elif item.rarity == 'epic':
                color = (0.5, 0, 0.5, 1)
            else:  # legendary
                color = (1, 0.84, 0, 1)
            
            btn = Button(
                text=f"{item.name} ({item.rarity})",
                size_hint_y=None,
                height=50,
                background_color=color,
                background_normal='',
                color=(0, 0, 0, 1) if item.rarity == 'common' else (1, 1, 1, 1)
            )
            btn.item = item
            btn.index = i
            btn.bind(on_press=self.use_item)
            
            if i == self.selected_index:
                btn.background_color = (1, 1, 0, 1)
            
            grid.add_widget(btn)
    
    def use_item(self, instance):
        """Use selected item"""
        app = App.get_running_app()
        item = instance.item
        result = item.use(app.player)
        
        if result['used']:
            app.player.inventory.remove(item)
            app.play_sound('potion')
            self.update_inventory()
            self.manager.current = 'game'
        else:
            # Экипировка
            if app.player.equip(item):
                app.player.inventory.remove(item)
                self.update_inventory()
    
    def close_inventory(self):
        """Close inventory screen"""
        self.manager.current = 'game'


class SettingsScreen(Screen):
    """
    Settings screen
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_enter(self):
        """Called when screen is entered"""
        app = App.get_running_app()
        
        # Загрузка настроек
        self.ids.sound_switch.active = app.settings.get('sound_enabled', True)
        self.ids.music_switch.active = app.settings.get('music_enabled', True)
        self.ids.touch_switch.active = app.settings.get('touch_controls', platform == 'android')
        self.ids.sound_slider.value = app.settings.get('sound_volume', 70)
        self.ids.music_slider.value = app.settings.get('music_volume', 50)
    
    def save_settings(self):
        """Save settings"""
        app = App.get_running_app()
        
        app.settings['sound_enabled'] = self.ids.sound_switch.active
        app.settings['music_enabled'] = self.ids.music_switch.active
        app.settings['touch_controls'] = self.ids.touch_switch.active
        app.settings['sound_volume'] = self.ids.sound_slider.value
        app.settings['music_volume'] = self.ids.music_slider.value
        
        # Применение настроек
        for sound in app.sounds.values():
            if sound:
                sound.volume = app.settings['sound_volume'] / 100
        
        from game.save_system import save_settings
        save_settings(app.settings)
    
    def back_to_menu(self):
        """Return to menu"""
        self.save_settings()
        self.manager.current = 'menu'


class GameOverScreen(Screen):
    """
    Game over screen
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def on_enter(self):
        """Called when screen is entered"""
        app = App.get_running_app()
        
        if app.player:
            self.ids.stats_label.text = (
                f"Достигнутый уровень: {app.player.stats.level}\n"
                f"Собрано золота: {app.player.stats.gold}"
            )
    
    def new_game(self):
        """Start new game"""
        app = App.get_running_app()
        app.new_game()
        self.manager.current = 'loading'
    
    def back_to_menu(self):
        """Return to menu"""
        self.manager.current = 'menu'


# Импорт App в конце для избежания циклических импортов
from kivy.app import App
from game.map_generator import GameMap