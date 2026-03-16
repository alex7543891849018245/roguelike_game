"""
Combat system module
"""

import random
from kivy.app import App

class CombatSystem:
    """
    Handles combat mechanics
    """
    def __init__(self, game):
        self.game = game
        self.combat_log = []
        self.combat_active = False
        
    def player_attack(self, player, enemy, attack_type='normal'):
        """
        Player attacks enemy
        """
        damage = 0
        crit = False
        
        # Hit chance
        hit_chance = 0.8 + (player.stats.agility / 100)
        if random.random() > hit_chance:
            return {
                'hit': False,
                'damage': 0,
                'crit': False,
                'enemy_hp': enemy.stats.hp
            }
        
        # Base damage
        if attack_type == 'normal':
            damage = self.calculate_damage(player.stats.strength, 
                                          enemy.stats.defense)
        elif attack_type == 'heavy':
            damage = self.calculate_damage(int(player.stats.strength * 1.5), 
                                          enemy.stats.defense)
            player.stats.mana -= 2
        
        # Critical hit
        crit_chance = player.stats.luck / 100
        if random.random() < crit_chance:
            damage = int(damage * 1.5)
            crit = True
        
        # Apply damage
        actual_damage = enemy.take_damage(damage)
        
        return {
            'hit': True,
            'damage': actual_damage,
            'crit': crit,
            'enemy_hp': enemy.stats.hp
        }
    
    def calculate_damage(self, attack, defense):
        """
        Calculate damage with variance
        """
        base_damage = max(1, attack - defense // 2)
        variance = random.uniform(0.8, 1.2)
        return int(base_damage * variance)