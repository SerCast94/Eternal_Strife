import pygame

class UIManager:
    def __init__(self, settings):
        """
        Constructor del gestor de interfaz de usuario.
        
        Inicializa:
        - Configuraciones generales
        - Fuente para textos
        - Dimensiones de la barra de vida (30x3 píxeles)
        
        Parámetros:
        - settings: Configuraciones generales del juego
        """
        self.settings = settings
        self.font = pygame.font.Font(None, 36)
        # Reducir dimensiones de la barra de vida
        self.health_bar_width = 30  # Reducido de 50 a 30
        self.health_bar_height = 3  # Reducido de 5 a 3

    def draw(self, screen, player, game_state, enemy_manager, game):
        """
        Dibuja todos los elementos de la interfaz de usuario.
        
        Parámetros:
        - screen: Superficie donde dibujar
        - player: Objeto jugador para datos de vida y nivel
        - game_state: Estado actual del juego
        - enemy_manager: Gestor de enemigos para datos de dificultad
        - game: Objeto principal del juego para tiempo y cámara
        
        Elementos que dibuja:
        - Barra de vida sobre el jugador (rojo/verde)
        - Tiempo de juego (esquina superior izquierda)
        - Barra de progreso de nivel (inferior)
            * Fondo gris
            * Progreso con efecto arcoíris
            * Nivel actual centrado
        - Mensaje de GAME OVER (cuando corresponde)
        """
        # Ajustar posición vertical para que esté más cerca del jugador
        health_bar_x = (player.rect.centerx - self.health_bar_width/2) * self.settings.zoom - game.tilemap.camera_x * self.settings.zoom
        health_bar_y = (player.rect.top - 8) * self.settings.zoom - game.tilemap.camera_y * self.settings.zoom
        
        health_percentage = max(0, player.health / player.max_health)
        
        # Dibujar barra de vida con dimensiones actualizadas
        pygame.draw.rect(screen, (255, 0, 0),
            (health_bar_x, health_bar_y, self.health_bar_width * self.settings.zoom, self.health_bar_height * self.settings.zoom))
        pygame.draw.rect(screen, (0, 255, 0),
            (health_bar_x, health_bar_y, (self.health_bar_width * health_percentage) * self.settings.zoom, self.health_bar_height * self.settings.zoom))

        # Puntuación y tiempo
        # score_text = self.font.render(f"Puntuación: {player.score}", True, (255, 255, 255))
        time_text = self.font.render(f"Tiempo: {game.game_time:.2f}s", True, (255, 255, 255))
        # screen.blit(score_text, (10, 40))
        screen.blit(time_text, (10, 10))

        # Dificultad (velocidad de aparición de enemigos)
        # difficulty_text = self.font.render(f"Dificultad: {enemy_manager.spawn_rate:.2f}", True, (255, 255, 255))
        # screen.blit(difficulty_text, (self.settings.screen_width - difficulty_text.get_width() - 10, 10))

        # Barra de nivel con efecto arcoíris
        level_bar_height = 10
        level_bar_y = self.settings.screen_height - level_bar_height
        level_progress = player.scoreToLevelUp / player.exp_to_next_level
        
        # Dibujar fondo de la barra
        pygame.draw.rect(screen, (50, 50, 50),
            (0, level_bar_y, self.settings.screen_width, level_bar_height))
        
        # Dibujar barra de progreso con efecto arcoíris
        if level_progress > 0:
            bar_width = int(self.settings.screen_width * level_progress)
            for x in range(bar_width):
                # Calcular color HSV (matiz varía a lo largo de la barra)
                hue = (x / self.settings.screen_width + game_state.game_time / 2) % 1.0
                rgb = self._hsv_to_rgb(hue, 1.0, 1.0)
                pygame.draw.line(screen, rgb, 
                    (x, level_bar_y), 
                    (x, level_bar_y + level_bar_height))

        # Mostrar nivel actual
        level_text = self.font.render(f"Nivel {player.level}", True, (255, 255, 255))
        level_text_pos = (
            self.settings.screen_width // 2 - level_text.get_width() // 2,
            level_bar_y - level_text.get_height() - 5
        )
        screen.blit(level_text, level_text_pos)

        if game_state.is_game_over:
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text,
                (self.settings.screen_width // 2 - game_over_text.get_width() // 2,
                self.settings.screen_height // 2 - game_over_text.get_height() // 2))

    def _hsv_to_rgb(self, h, s, v):
        """
        Convierte un color del espacio HSV a RGB.
        
        Parámetros:
        - h: Matiz (0-1)
        - s: Saturación (0-1)
        - v: Valor (0-1)
        
        Retorna:
        - Tupla (r, g, b) con valores RGB (0-255)
        
        Utilizado para crear el efecto arcoíris en la barra de nivel
        """
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))