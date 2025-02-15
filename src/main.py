import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Lista de dependencias necesarias
dependencies = ["pygame", "matplotlib", "pillow"]

# Verificar e instalar las dependencias
for dependency in dependencies:
    try:
        __import__(dependency)
        print(f"{dependency} ya está instalado.")
    except ImportError:
        print(f"{dependency} no está instalado. Instalando...")
        install(dependency)
        
import pygame
import sys
from screens.menu import Menu
from core.game import Game
from managers.music_player import MusicPlayer

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
                # Guardar volumen actual antes de iniciar el juego
                game_volume = self.music_player.get_volume()
                game = Game(self.screen, self.music_player, debug_mode=menu.debug_mode)
                game.run()
                # Restaurar volumen al volver al menú
                self.music_player.set_volume(game_volume)
                if game.game_state.is_game_over:
                    continue  # Volver al menú principal después de la pantalla de Game Over
            else:
                self.running = False

if __name__ == "__main__":
    main = Main()
    main.run()