"""
Save/load system for the game
"""

import json
import os
from kivy.utils import platform
from kivy.app import App

def get_save_path():
    """Get save directory path based on platform"""
    app = App.get_running_app()
    
    if platform == 'android':
        from android.storage import primary_external_storage_path
        base_path = primary_external_storage_path() + '/roguelike/'
    else:
        base_path = app.config.base_path
    
    save_path = os.path.join(base_path, 'saves/')
    os.makedirs(save_path, exist_ok=True)
    return save_path

def save_game(game_data, slot=0):
    """Save game to file"""
    try:
        save_path = get_save_path()
        filename = os.path.join(save_path, f'save_{slot}.json')
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, indent=2, ensure_ascii=False)
        
        # Save meta data
        save_meta(slot, game_data)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def load_game(slot=0):
    """Load game from file"""
    try:
        save_path = get_save_path()
        filename = os.path.join(save_path, f'save_{slot}.json')
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Load error: {e}")
    return None

def save_meta(slot, game_data):
    """Save meta information about save"""
    try:
        save_path = get_save_path()
        meta_file = os.path.join(save_path, 'meta.json')
        
        meta = load_meta()
        meta[str(slot)] = {
            'level': game_data['player']['stats']['level'],
            'depth': game_data.get('depth', 1),
            'timestamp': str(datetime.now())
        }
        
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)
    except:
        pass

def load_meta():
    """Load meta information"""
    try:
        save_path = get_save_path()
        meta_file = os.path.join(save_path, 'meta.json')
        
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def delete_save(slot=0):
    """Delete save file"""
    try:
        save_path = get_save_path()
        filename = os.path.join(save_path, f'save_{slot}.json')
        
        if os.path.exists(filename):
            os.remove(filename)
        
        # Update meta
        meta = load_meta()
        if str(slot) in meta:
            del meta[str(slot)]
            
            meta_file = os.path.join(save_path, 'meta.json')
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)
        
        return True
    except:
        return False

def load_settings():
    """Load settings from file"""
    try:
        save_path = get_save_path()
        settings_file = os.path.join(save_path, 'settings.json')
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    # Default settings
    return {
        'sound_enabled': True,
        'music_enabled': True,
        'sound_volume': 70,
        'music_volume': 50,
        'touch_controls': False,
        'difficulty': 'normal',
        'show_fps': False
    }

def save_settings(settings):
    """Save settings to file"""
    try:
        save_path = get_save_path()
        settings_file = os.path.join(save_path, 'settings.json')
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        return True
    except:
        return False

# Import for timestamp
from datetime import datetime