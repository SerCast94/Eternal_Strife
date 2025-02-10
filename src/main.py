import pygame
import sys
from menu import Menu
from game import Game

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Eternal Strife")
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            menu = Menu(self.screen)
            menu.run()
            if menu.start_game:
                game = Game(self.screen)
                game.run()
                if game.game_state.is_game_over:
                    continue  # Volver al menú principal después de la pantalla de Game Over
            else:
                self.running = False

if __name__ == "__main__":
    main = Main()
    main.run()