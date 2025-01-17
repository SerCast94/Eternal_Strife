class GameState:
    def __init__(self):
        self.score = 0
        self.game_time = 0
        self.is_game_over = False

    def update(self, delta_time):
        if not self.is_game_over:
            self.game_time += delta_time

    def add_score(self, points):
        self.score += points