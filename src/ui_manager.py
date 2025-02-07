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
        score_text = self.font.render(f"Puntuación: {player.score}", True, (255, 255, 255))  # Mostrar el score del jugador
        time_text = self.font.render(f"Tiempo: {int(game_state.game_time)}s", True, (255, 255, 255))
        screen.blit(score_text, (10, 40))
        screen.blit(time_text, (10, 70))

        # Dificultad (velocidad de aparición de enemigos)
        difficulty_text = self.font.render(f"Dificultad: {enemy_manager.spawn_rate:.2f}", True, (255, 255, 255))
        screen.blit(difficulty_text, (self.settings.screen_width - difficulty_text.get_width() - 10, 10))

        if game_state.is_game_over:
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text,
                (self.settings.screen_width // 2 - game_over_text.get_width() // 2,
                 self.settings.screen_height // 2 - game_over_text.get_height() // 2))