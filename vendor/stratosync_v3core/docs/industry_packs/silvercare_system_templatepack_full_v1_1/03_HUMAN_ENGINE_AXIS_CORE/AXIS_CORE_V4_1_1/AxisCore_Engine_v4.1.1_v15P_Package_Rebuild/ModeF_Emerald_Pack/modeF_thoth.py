# modeF_thoth.py
# ModeF (Thoth Oracle) 強化版 - Emerald Tablet 統合対応

import json
from dictionaries import THOTH_DICT, THOTH_EMERALD_DICT

class ThothOracle:
    def __init__(self):
        self.thoth_dict = THOTH_DICT
        self.emerald_dict = THOTH_EMERALD_DICT

    def consult(self, query, mode="integrated"):
        response = {"query": query}
        if mode == "thoth":
            response["oracle"] = self._search_dict(query, self.thoth_dict)
        elif mode == "emerald":
            response["oracle"] = self._search_dict(query, self.emerald_dict)
        else:  # integrated
            response["oracle"] = {
                "thoth": self._search_dict(query, self.thoth_dict),
                "emerald": self._search_dict(query, self.emerald_dict)
            }
        return response

    def _search_dict(self, query, dictionary):
        for k, v in dictionary.items():
            if k.lower() in query.lower():
                return v
        return "The oracle remains silent, awaiting deeper alignment."
