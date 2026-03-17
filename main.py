from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.lang import Builder
import os
import sys

# Настройка ориентации для Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    
    # Запрос разрешений
    request_permissions([
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE
    ])
    
    # Установка горизонтальной ориентации (landscape)
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    activity.setRequestedOrientation(0)  # 0 = landscape
    
    resource_add_path('/sdcard/roguelike/')

# Импорт наших модулей
from game.config import Config
from game.entities import Player, Enemy, Item
from game.map_generator import GameMap
from game.combat_system import CombatSystem
from game.save_system import save_game, load_game, load_settings, save_settings
from ui.screens import SplashScreen, MenuScreen, GameScreen, InventoryScreen, SettingsScreen, GameOverScreen, LoadingScreen
from ui.widgets import MapWidget, TouchJoystick, ActionButton, MessageLog, HealthBar, StatusPanel, BackgroundWidget

class RoguelikeApp(App):
    """
    Главный класс приложения
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()
        self.player = None
        self.current_map = None
        self.combat_system = None
        self.game_state = 'menu'
        self.settings = load_settings()
        self.sounds = {}
        
    def build(self):
        """
        Создание и настройка приложения
        """
        # Настройка окна для Windows (тестирование в landscape)
        if platform == 'win':
            Window.size = (900, 550)
            Window.minimum_width = 800
            Window.minimum_height = 480
        
        # Загрузка звуков
        self.load_sounds()
        
        # Создание менеджера экранов
        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))
        
        # Добавление экранов
        self.sm.add_widget(SplashScreen(name='splash'))
        self.sm.add_widget(LoadingScreen(name='loading'))
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(GameScreen(name='game'))
        self.sm.add_widget(InventoryScreen(name='inventory'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(GameOverScreen(name='game_over'))
        
        # Установка начального экрана
        self.sm.current = 'splash'
        
        # Планирование перехода с заставки
        Clock.schedule_once(self.go_to_menu, 2)
        
        return self.sm
    
    def go_to_menu(self, dt):
        """
        Переход в главное меню
        """
        self.sm.current = 'menu'
    
    def load_sounds(self):
        """
        Загрузка звуковых эффектов
        """
        sound_files = {
            'attack': 'attack.wav',
            'hit': 'hit.wav',
            'death': 'death.wav',
            'level_up': 'level_up.wav',
            'click': 'click.wav',
            'potion': 'potion.wav',
            'gold': 'gold.wav',
            'door': 'door.wav'
        }
        
        sounds_path = os.path.join('assets', 'sounds')
        if os.path.exists(sounds_path):
            for name, filename in sound_files.items():
                path = os.path.join(sounds_path, filename)
                if os.path.exists(path):
                    self.sounds[name] = SoundLoader.load(path)
                    if self.sounds[name]:
                        self.sounds[name].volume = self.settings.get('sound_volume', 70) / 100
    
    def play_sound(self, name):
        """
        Воспроизведение звука
        """
        if name in self.sounds and self.settings.get('sound_enabled', True):
            self.sounds[name].play()
    
    def new_game(self):
        """
        Начало новой игры
        """
        # Создание игрока
        self.player = Player(25, 25)
        
        # Создание карты
        self.current_map = GameMap(50, 50, 1)
        
        # Создание боевой системы
        self.combat_system = CombatSystem(self)
        
        # Передаем данные в игровой экран
        game_screen = self.sm.get_screen('game')
        game_screen.setup_game(self.player, self.current_map, self.combat_system)
        
        # Переход на экран загрузки
        self.sm.current = 'loading'
        self.play_sound('click')
    
    def load_game(self, save_slot=0):
        """
        Загрузка сохраненной игры
        """
        save_data = load_game(save_slot)
        
        if save_data:
            self.player = Player.from_dict(save_data['player'])
            self.current_map = GameMap.from_dict(save_data['map'])
            self.combat_system = CombatSystem(self)
            
            game_screen = self.sm.get_screen('game')
            game_screen.setup_game(self.player, self.current_map, self.combat_system)
            
            self.sm.current = 'loading'
            self.play_sound('click')
            return True
        return False
    
    def save_game(self, save_slot=0):
        """
        Сохранение игры
        """
        if not self.player or not self.current_map:
            return False
            
        save_data = {
            'player': self.player.to_dict(),
            'map': self.current_map.to_dict(),
            'depth': self.current_map.depth
        }
        result = save_game(save_data, save_slot)
        if result:
            self.play_sound('click')
        return result
    
    def on_pause(self):
        """
        Обработка паузы приложения (для Android)
        """
        return True
    
    def on_resume(self):
        """
        Возобновление после паузы
        """
        pass

if __name__ == '__main__':
    RoguelikeApp().run()