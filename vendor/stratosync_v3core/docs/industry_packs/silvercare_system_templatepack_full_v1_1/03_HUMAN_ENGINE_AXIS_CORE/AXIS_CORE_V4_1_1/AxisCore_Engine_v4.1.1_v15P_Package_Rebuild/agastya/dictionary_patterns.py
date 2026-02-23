
# dictionary_patterns.py

import json
import random

class AgastyaDictionary:
    def __init__(self, path='agastya_leaf_dictionary_v1.json'):
        with open(path, encoding='utf-8') as f:
            self.data = json.load(f)

    def get_category(self, category):
        return self.data.get(category, [])

    def random_phrase(self, category):
        phrases = self.get_category(category)
        return random.choice(phrases) if phrases else None

    def list_categories(self):
        return list(self.data.keys())

    def search_phrase(self, keyword):
        results = []
        for cat, phrases in self.data.items():
            for phrase in phrases:
                if keyword in phrase:
                    results.append((cat, phrase))
        return results
