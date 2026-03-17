"""
Configuration module for the game
"""

import os
import json
from kivy.utils import platform
from kivy.core.window import Window

class Config:
    """
    Game configuration class
    """
    def __init__(self):
        self.load_config()
        self.setup_paths()
        
    def load_config(self):
        """
        Load configuration from file or set defaults
        """
        self.tile_size = 32
        self.map_width = 50
        self.map_height = 50
        self.fps = 60
        self.difficulty = 'normal'
        
        # Настройки для разных платформ
        if platform == 'android':
            self.touch_controls = True
            self.vibration = True
        else:
            self.touch_controls = False
            self.vibration = False
    
    def setup_paths(self):
        if platform == 'android':
            # ИСПОЛЬЗУЕМ ВНУТРЕННЕЕ ХРАНИЛИЩЕ (не требует разрешений)
            from jnius import autoclass
            
            # Получаем контекст приложения
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            
            # getFilesDir() возвращает путь к внутреннему хранилищу приложения
            # Например: /data/user/0/org.alexstudiocode.roguelike.roguelike/files
            self.base_path = context.getFilesDir().getAbsolutePath() + '/'
            
            # Папка для сохранений внутри приватного хранилища
            self.save_path = os.path.join(self.base_path, 'saves/')
            
            # Ассеты читаются из APK, путь относительный
            self.assets_path = 'assets/'
            
        else:
            # Для Windows/других платформ
            self.base_path = os.path.dirname(os.path.dirname(__file__)) + '/'
            self.save_path = os.path.join(self.base_path, 'saves/')
            self.assets_path = os.path.join(self.base_path, 'assets/')
        
        # Создаём папки если их нет
        os.makedirs(self.save_path, exist_ok=True)

# Глобальные константы (для запасных вариантов, если нет спрайтов)
BLACK = (0, 0, 0, 1)
WHITE = (1, 1, 1, 1)
RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)
BLUE = (0, 0, 1, 1)
GOLD = (1, 0.84, 0, 1)
PURPLE = (0.5, 0, 0.5, 1)
GRAY = (0.5, 0.5, 0.5, 1)
DARK_GRAY = (0.25, 0.25, 0.25, 1)