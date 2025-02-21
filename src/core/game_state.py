
class GameState:
    def __init__(self,game):
        """
        Constructor de la clase GameState que maneja el estado general del juego.
        Parámetros:
        - game: Referencia al objeto principal del juego
        Inicializa:
        - score: Puntuación del jugador (comienza en 0)
        - game_time: Tiempo transcurrido de juego (comienza en 0)
        - is_game_over: Estado de fin de juego (comienza en False)
        """
        self.game = game
        self.score = 0
        self.game_time = 0
        self.is_game_over = False

    def update(self):
        """
        Actualiza el estado del juego en cada frame.
        Si el juego no ha terminado, incrementa el tiempo de juego
        usando el delta_time del juego para mantener un tiempo preciso.
        """
        if not self.is_game_over:
            self.game_time += self.game.delta_time

    def add_score(self, points):
        """
        Incrementa la puntuación del jugador.
        Parámetros:
        - points: Cantidad de puntos a añadir al score actual
        """
        self.score += points