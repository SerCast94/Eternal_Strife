import pygame

class UIManager:
    def __init__(self, settings):
        self.settings = settings
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen, player, game_state, enemy_manager):
        # Barra de vida
        health_bar_width = 200
        health_bar_height = 20
        health_percentage = max(0, player.health / player.max_health)
        
        pygame.draw.rect(screen, (255, 0, 0),
            (10, 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0),
            (10, 10, health_bar_width * health_percentage, health_bar_height))

        # Puntuación y tiempo
        score_text = self.font.render(f"Puntuación: {player.score}", True, (255, 255, 255))
        time_text = self.font.render(f"Tiempo: {int(game_state.game_time)}s", True, (255, 255, 255))
        screen.blit(score_text, (10, 40))
        screen.blit(time_text, (10, 70))

        # Dificultad (velocidad de aparición de enemigos)
        difficulty_text = self.font.render(f"Dificultad: {enemy_manager.spawn_rate:.2f}", True, (255, 255, 255))
        screen.blit(difficulty_text, (self.settings.screen_width - difficulty_text.get_width() - 10, 10))

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
        """Convierte color HSV a RGB"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))