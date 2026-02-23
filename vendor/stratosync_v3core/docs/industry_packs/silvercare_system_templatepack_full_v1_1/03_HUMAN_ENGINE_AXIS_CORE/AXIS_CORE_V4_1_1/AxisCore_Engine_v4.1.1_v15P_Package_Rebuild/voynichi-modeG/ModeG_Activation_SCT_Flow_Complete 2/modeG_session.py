
class ModeGSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.themes_used = 0
        self.max_themes = 3
        self.sct_required = 3

    def use_theme(self):
        self.themes_used += 1
        if self.themes_used >= self.max_themes:
            return "ask_renewal"  # → UIへアナウンス
        return "continue"

    def reset(self):
        self.themes_used = 0
