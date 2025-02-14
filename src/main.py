import pygame
import sys
from menu import Menu
from game import Game
from music_player import MusicPlayer

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Eternal Strife")
        self.clock = pygame.time.Clock()
        self.running = True
        self.music_player = MusicPlayer(self.screen)
        self.music_player.set_volume(0.1)
        
        # Optimizar PyGame
        pygame.display.set_mode((800, 600), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
        
        # Threads para rendering
        if hasattr(pygame, 'set_num_threads'):
            pygame.set_num_threads(4)

    def run(self):
        while self.running:
            menu = Menu(self.screen, self.music_player)
            menu.run()
            if menu.start_game:
                game = Game(self.screen,self.music_player, debug_mode=menu.debug_mode)
                game.run()
                if game.game_state.is_game_over:
                    continue  # Volver al menú principal después de la pantalla de Game Over
            else:
                self.running = False

if __name__ == "__main__":
    main = Main()
    main.run()