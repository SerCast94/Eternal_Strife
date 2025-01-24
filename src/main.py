import pygame
import sys
import math
import threading
from game_state import GameState
from settings import Settings
from player import Player
from tilemap import TileMap
from enemy_manager import EnemyManager
from ui_manager import UIManager
from animation_manager import AnimationManager

class Game:
    def __init__(self):
        try:
            print("Inicializando Pygame...")
            pygame.init()
            self.settings = Settings()
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
            pygame.display.set_caption("Eternal Strife")
            self.clock = pygame.time.Clock()
            
            # Superficie de renderizado intermedia
            self.render_surface = pygame.Surface(
                (self.settings.screen_width, self.settings.screen_height))

            # Mostrar pantalla de carga
            self.show_loading_screen()

            # Inicializar componentes del juego
            self.log("Inicializando GameState...")
            self.game_state = GameState()
            self.log("GameState inicializado")

            self.log("Inicializando AnimationManager...")
            self.animation_manager = AnimationManager(self.settings)
            self.log("AnimationManager inicializado")

            self.log("Inicializando TileMap...")
            self.tilemap = TileMap(self.settings)
            self.log("TileMap inicializado")

            self.log("Inicializando Player...")
            self.player = Player(self.settings, self.animation_manager)
            self.log("Player inicializado")

            self.log("Inicializando EnemyManager...")
            self.enemy_manager = EnemyManager(self.settings, self.player, self.animation_manager, self.tilemap)
            self.log("EnemyManager inicializado")

            self.log("Inicializando UIManager...")
            self.ui_manager = UIManager(self.settings)
            self.log("UIManager inicializado")

            self.log("Juego inicializado correctamente")

            # Crear un evento para sincronización
            self.update_event = threading.Event()

        except Exception as e:
            self.log(f"Error durante la inicialización: {e}")
            pygame.quit()
            sys.exit(1)

    def log(self, message):
        print(message)
        self.show_loading_screen()

    def show_loading_screen(self):
        try:
            loading_font = pygame.font.SysFont(None, 48)
            loading_text = loading_font.render("Cargando...", True, (255, 255, 255))
            self.screen.fill((0, 0, 0))
            self.screen.blit(loading_text, (self.settings.screen_width // 2 - loading_text.get_width() // 2,
                                            self.settings.screen_height // 2 - loading_text.get_height() // 2))
            pygame.display.flip()
        except Exception as e:
            print(f"Error mostrando la pantalla de carga: {e}")

    def handle_events(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Evento de salida detectado")
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    print("Reiniciando juego...")
                    self.restart_game()
                self.player.handle_input(event)
            return True
        except Exception as e:
            print(f"Error manejando eventos: {e}")
            return False

    def restart_game(self):
        try:
            print("Reiniciando componentes del juego...")
            # Mostrar pantalla de carga
            self.show_loading_screen()
            
            # Regenerar el mapa
            self.log("Regenerando el mapa...")
            self.tilemap = TileMap(self.settings)
            self.log("Mapa regenerado")
            
            # Reiniciar jugador
            self.log("Reiniciando jugador...")
            self.player = Player(self.settings, self.animation_manager)
            self.log("Jugador reiniciado")
            
            # Reiniciar enemigos
            self.log("Reiniciando enemigos...")
            self.enemy_manager.stop()
            self.enemy_manager = EnemyManager(self.settings, self.player, self.animation_manager, self.tilemap)
            self.log("Enemigos reiniciados")
            
            # Reiniciar estado del juego
            self.log("Reiniciando estado del juego...")
            self.game_state = GameState()
            self.log("Estado del juego reiniciado")
            self.log("Juego reiniciado")

            # Reiniciar el evento de sincronización
            self.update_event.clear()

        except Exception as e:
            self.log(f"Error reiniciando el juego: {e}")

    def update(self):
        try:
            if not self.game_state.is_game_over:
                delta_time = self.clock.get_time() / 1000.0
                
                # Actualizar componentes
                self.player.update(delta_time, self.tilemap)
                self.game_state.update(delta_time)
                
                # Actualizar la cámara para seguir al jugador
                self.tilemap.update_camera(self.player.rect.x, self.player.rect.y)
                
                # Comprobar condición de game over
                if self.player.health <= 0:
                    self.game_state.is_game_over = True
                    print("Game Over")
        except Exception as e:
            print(f"Error actualizando el juego: {e}")

    def update_enemies(self):
        while not self.game_state.is_game_over:
            self.update_event.wait()  # Esperar a que el evento sea activado
            delta_time = self.clock.get_time() / 1000.0
            self.enemy_manager.update(delta_time, self.tilemap)
            self.update_event.clear()  # Limpiar el evento después de la actualización

    def render(self):
        try:
            self.render_surface.fill((0, 0, 0))
            
            # Dibujar el mapa
            self.tilemap.draw(self.render_surface)
            
            # Dibujar entidades
            self.player.draw(self.render_surface, self.tilemap.camera_x, self.tilemap.camera_y)
            self.enemy_manager.draw(self.render_surface, self.tilemap.camera_x, self.tilemap.camera_y)
            
            # Escalar la superficie de renderizado según el factor de zoom
            zoomed_surface = pygame.transform.scale(
                self.render_surface, 
                (int(self.settings.screen_width * self.settings.zoom), 
                 int(self.settings.screen_height * self.settings.zoom))
            )
            
            # Dibujar la superficie escalada en la pantalla
            self.screen.blit(zoomed_surface, (0, 0))
            
            # Dibujar UI sin aplicar zoom
            self.ui_manager.draw(self.screen, self.player, self.game_state, self.enemy_manager)
            
            pygame.display.flip()
        except Exception as e:
            print(f"Error renderizando el juego: {e}")

    def run(self):
        running = True
        try:
            # Iniciar el hilo de actualización de enemigos después de la inicialización
            self.enemy_thread = threading.Thread(target=self.update_enemies)
            self.enemy_thread.start()

            while running:
                running = self.handle_events()
                self.update()
                self.update_event.set()  # Activar el evento para actualizar los enemigos
                self.render()
                self.clock.tick(self.settings.FPS)
                # print("Frame actualizado")
        except Exception as e:
            print(f"Se produjo un error: {e}")
        finally:
            self.enemy_manager.stop()
            pygame.quit()
            print("Pygame cerrado correctamente")

if __name__ == "__main__":
    print("Iniciando el juego...")
    game = Game()
    game.run()
    print("Juego terminado")