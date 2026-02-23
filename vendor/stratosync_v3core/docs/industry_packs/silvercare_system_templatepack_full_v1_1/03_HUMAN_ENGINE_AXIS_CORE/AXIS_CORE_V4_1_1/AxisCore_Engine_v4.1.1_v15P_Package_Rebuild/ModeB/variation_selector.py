
import random
import json

def select_style(style):
    if style == 'random':
        with open('style_profiles.json', 'r') as f:
            profiles = json.load(f)
        return random.choice(list(profiles.keys()))
    return style
