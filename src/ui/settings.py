# src/ui/settings.py
import json
import os
from ..utils.logging import logger

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'config.json')

def get_settings():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults.")
        return {'source_lang': 'en', 'target_lang': 'vi'}

def save_settings(settings):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(settings, f)