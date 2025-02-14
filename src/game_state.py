
class GameState:
    def __init__(self,game):
        self.game = game
        self.score = 0
        self.game_time = 0
        self.is_game_over = False

    def update(self):
        if not self.is_game_over:
            self.game_time += self.game.delta_time

    def add_score(self, points):
        self.score += points