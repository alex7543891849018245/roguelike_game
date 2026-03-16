"""
Visual effects for the game - Particles, damage numbers, screen shake
"""

from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, PushMatrix, PopMatrix, Translate, Rotate
from kivy.graphics.instructions import InstructionGroup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import random
import math


class VisualEffects(Widget):
    """
    Visual effects manager - Particles, damage numbers, screen shake
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.damage_numbers = []
        self.screen_shake = 0
        self.shake_offset = (0, 0)
        
        # Запускаем обновление эффектов
        Clock.schedule_interval(self.update_effects, 1.0/60.0)
    
    def add_particles(self, x, y, color, count=10, tile_size=32):
        """Add particle effect at position"""
        center_x = x * tile_size + tile_size // 2
        center_y = y * tile_size + tile_size // 2
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'life': random.randint(20, 40),
                'size': random.randint(2, 4)
            })
    
    def add_damage_number(self, x, y, damage, is_player=False, tile_size=32):
        """Add damage number at position"""
        self.damage_numbers.append({
            'x': x * tile_size + tile_size // 2,
            'y': y * tile_size,
            'damage': damage,
            'life': 60,
            'offset_y': 0,
            'is_player': is_player  # True для урона по игроку (красный), False для урона врагу (белый)
        })
    
    def shake_screen(self, intensity=5):
        """Add screen shake effect"""
        self.screen_shake = intensity
    
    def update_effects(self, dt):
        """Update all effects"""
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravity
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Update damage numbers
        for number in self.damage_numbers[:]:
            number['offset_y'] -= 1  # Float up
            number['life'] -= 1
            if number['life'] <= 0:
                self.damage_numbers.remove(number)
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
            self.shake_offset = (
                random.randint(-self.screen_shake, self.screen_shake),
                random.randint(-self.screen_shake, self.screen_shake)
            )
        else:
            self.shake_offset = (0, 0)
        
        # Trigger redraw
        self.canvas.ask_update()
    
    def draw_effects(self, camera_x=0, camera_y=0, tile_size=32):
        """Draw all effects - to be called from MapWidget"""
        self.canvas.clear()
        
        with self.canvas:
            # Draw particles
            for particle in self.particles:
                screen_x = particle['x'] - camera_x
                screen_y = particle['y'] - camera_y
                
                # Skip if off screen
                if (screen_x < -50 or screen_x > Window.width + 50 or
                    screen_y < -50 or screen_y > Window.height + 50):
                    continue
                
                # Calculate alpha based on life
                alpha = particle['life'] / 40.0
                r, g, b = particle['color']
                
                Color(r, g, b, alpha)
                Ellipse(
                    pos=(screen_x - particle['size'], 
                         screen_y - particle['size']),
                    size=(particle['size'] * 2, particle['size'] * 2)
                )
            
            # Draw damage numbers
            for number in self.damage_numbers:
                screen_x = number['x'] - camera_x
                screen_y = number['y'] - camera_y + number['offset_y']
                
                if (screen_x < -50 or screen_x > Window.width + 50 or
                    screen_y < -50 or screen_y > Window.height + 50):
                    continue
                
                # Color based on damage type
                if number['is_player']:
                    color = (1, 0, 0, number['life'] / 60.0)  # Red for player damage
                else:
                    if number['damage'] > 0:
                        color = (1, 1, 1, number['life'] / 60.0)  # White for enemy damage
                    else:
                        color = (0, 1, 0, number['life'] / 60.0)  # Green for healing
                
                # We'll use Label for text in the main game screen
                # This is just a placeholder - actual text rendering happens in GameScreen
                Color(*color)
                Rectangle(
                    pos=(screen_x - 10, screen_y - 5),
                    size=(20, 10)
                )
    
    def get_shake_offset(self):
        """Get current screen shake offset"""
        return self.shake_offset


class LoadingEffect(Widget):
    """
    Loading screen with rotating crystals and progress bar
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress = 0
        self.rotation_angle = 0
        self.loading_time = 0
        self.max_loading_time = 3
        self.tips = [
            "Совет: Собирайте золото для покупки артефактов!",
            "Совет: Используйте зелья в критических ситуациях",
            "Совет: Разные враги имеют разные слабости",
            "Совет: Исследуйте каждый угол - там могут быть сокровища",
            "Совет: Прокачка силы увеличивает урон",
            "Совет: Защита снижает получаемый урон",
            "Совет: Смерть перманентна - будьте осторожны!",
            "Совет: Находите скрытые комнаты для лучшей добычи"
        ]
        self.current_tip = random.choice(self.tips)
        self.gradient_colors = [
            (1, 0.84, 0, 1),    # Gold
            (1, 0.55, 0, 1),    # Orange
            (1, 0, 0, 1),       # Red
            (0.5, 0, 0.5, 1),   # Purple
            (0, 0, 1, 1),       # Blue
            (0, 1, 1, 1),       # Cyan
            (0, 1, 0, 1)        # Green
        ]
        
        Clock.schedule_interval(self.update_loading, 1.0/60.0)
    
    def start_loading(self):
        """Start loading animation"""
        self.progress = 0
        self.loading_time = 0
        self.current_tip = random.choice(self.tips)
    
    def update_loading(self, dt):
        """Update loading animation"""
        self.loading_time += dt
        self.progress = min(1.0, self.loading_time / self.max_loading_time)
        self.rotation_angle += dt * 50
        
        # Change tip every 2 seconds
        if int(self.loading_time * 2) != int((self.loading_time - dt) * 2):
            self.current_tip = random.choice(self.tips)
        
        self.canvas.ask_update()
    
    def draw(self, width, height):
        """Draw loading screen"""
        self.canvas.clear()
        
        with self.canvas:
            # Gradient background
            for i in range(height):
                color_val = 0.1 + i / height * 0.1
                Color(color_val, color_val * 0.5, color_val * 1.5, 1)
                Rectangle(pos=(0, i), size=(width, 1))
            
            # Rotating crystals
            center_x = width // 2
            center_y = height // 3
            
            for i in range(8):
                angle = self.rotation_angle + i * 45
                rad = math.radians(angle)
                x = center_x + math.cos(rad) * 80
                y = center_y + math.sin(rad) * 80
                
                color = self.gradient_colors[i % len(self.gradient_colors)]
                Color(*color)
                
                size = 20 + math.sin(angle) * 5
                
                # Draw crystal (hexagon)
                points = []
                for j in range(6):
                    a = rad + j * 60
                    r = size
                    points.extend([x + math.cos(a) * r, y + math.sin(a) * r])
                
                from kivy.graphics import Mesh
                # Simplified - we'll use rectangles for now
                Rectangle(pos=(x - size/2, y - size/2), size=(size, size))
    
    def is_finished(self):
        """Check if loading is complete"""
        return self.loading_time >= self.max_loading_time


class SplashEffect(Widget):
    """
    Splash screen with fade in/out effect
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alpha = 0
        self.fade_direction = 1
        self.timer = 0
        self.state = 0  # 0: fade in, 1: hold, 2: fade out
        self.fade_speed = 0.05
        
        Clock.schedule_interval(self.update_fade, 1.0/60.0)
    
    def start_splash(self):
        """Start splash animation"""
        self.alpha = 0
        self.fade_direction = 1
        self.timer = 0
        self.state = 0
    
    def update_fade(self, dt):
        """Update fade animation"""
        self.timer += dt
        
        if self.state == 0:  # Fade in
            self.alpha += self.fade_speed
            if self.alpha >= 1:
                self.alpha = 1
                self.state = 1
                self.timer = 0
                
        elif self.state == 1:  # Hold
            if self.timer > 2.0:  # Hold for 2 seconds
                self.state = 2
                
        elif self.state == 2:  # Fade out
            self.alpha -= self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                return True  # Finished
        
        self.canvas.ask_update()
        return False
    
    def draw(self, width, height):
        """Draw splash screen"""
        self.canvas.clear()
        
        with self.canvas:
            # Black background
            Color(0, 0, 0, 1)
            Rectangle(pos=(0, 0), size=(width, height))
            
            # Logo text with alpha
            Color(1, 0.84, 0, self.alpha)  # Gold
            # We'll use Label for text - this is just a placeholder
            Rectangle(pos=(width//2 - 100, height//2 - 30), size=(200, 60))
            
            # "presents" text with alpha (appears later)
            if self.alpha > 0.5:
                Color(1, 1, 1, self.alpha)
                Rectangle(pos=(width//2 - 50, height//2 + 20), size=(100, 30))