# src/game.py

import pygame
import sys
import threading
from game_state import GameState
from settings import Settings
from player import Player
from profiler import Profiler
from tilemap import TileMap
from enemy_manager import EnemyManager
from ui_manager import UIManager
from animation_manager import AnimationManager
from game_over_screen import GameOverScreen
import random

class Game:
    def __init__(self, screen, debug_mode=False):
        self.screen = screen
        self.settings = Settings()
        self.clock = pygame.time.Clock()
        self.debug_mode = debug_mode
        self.profiler = Profiler() if debug_mode else None

        # Generate stars for loading screen
        self.num_stars = 100
        self.stars = []
        for _ in range(self.num_stars):
            x = random.randint(0, self.settings.screen_width)
            y = random.randint(0, self.settings.screen_height)
            radius = random.randint(1, 3)
            self.stars.append([x, y, radius, random.randint(0, 255)])
        
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
        self.tilemap.generate()
        self.log("TileMap inicializado")

        self.log("Inicializando EnemyManager...")
        self.enemy_manager = EnemyManager(self.settings, None, self.animation_manager, self.tilemap)
        self.log("EnemyManager inicializado")

        self.log("Inicializando Player...")
        self.player = Player(self.settings, self.animation_manager, self.enemy_manager)
        self.enemy_manager.player = self.player  # Asignar el jugador al EnemyManager
        self.log("Player inicializado")

        self.log("Inicializando UIManager...")
        self.ui_manager = UIManager(self.settings)
        self.log("UIManager inicializado")

        self.log("Juego inicializado correctamente")

        # Crear un evento para sincronización
        self.update_event = threading.Event()



    def log(self, message):
        print(message)
        self.show_loading_screen()

    def show_loading_screen(self):
        try:
            loading_font = pygame.font.SysFont(None, 48)
            loading_text = loading_font.render("Generando nivel...", True, (255, 255, 255))
            self.screen.fill((0, 0, 0))

            # Draw stars
            for star in self.stars:
                pygame.draw.circle(self.screen, (255, 255, 255), (star[0], star[1]), star[2])

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
                    self.game_state.is_game_over = True
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        print("Reiniciando juego...")
                        self.restart_game()
                    if event.key == pygame.K_F1 and self.debug_mode:
                        self.profiler.show_graphs()
                    if event.key == pygame.K_F2 and self.debug_mode:
                        self.profiler.export_data()
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
            self.tilemap.generate()
            self.log("Mapa regenerado")
            
            # Reiniciar jugador
            self.log("Reiniciando jugador...")
            self.player = Player(self.settings, self.animation_manager, self.enemy_manager)
            self.log("Jugador reiniciado")
            
            # Reiniciar enemigos
            self.log("Reiniciando EnemyManager...")
            self.enemy_manager = EnemyManager(self.settings, self.player, self.animation_manager, self.tilemap)
            self.log("EnemyManager reiniciado")
            
            self.log("Componentes del juego reiniciados correctamente")
        except Exception as e:
            self.log(f"Error reiniciando el juego: {e}")

    def update(self, delta_time):
        try:
            if self.debug_mode:
                self.profiler.start("update_animation_manager")
            self.animation_manager.update(delta_time)  # Actualizar animaciones globalmente
            if self.debug_mode:
                self.profiler.stop()

            if self.debug_mode:
                self.profiler.start("update_player")
            self.game_state.update(delta_time)  # Actualizar el tiempo de juego
            self.player.update(delta_time, self.tilemap)
            if self.debug_mode:
                self.profiler.stop()

            if self.debug_mode:
                self.profiler.start("update_enemy_manager")
            self.enemy_manager.update(delta_time, self.tilemap)
            if self.debug_mode:
                self.profiler.stop()

            if self.debug_mode:
                self.profiler.start("update_tilemap")
            self.tilemap.update_camera(self.player.rect.centerx, self.player.rect.centery)
            if self.debug_mode:
                self.profiler.stop()
            
            # Verificar si la vida del jugador llega a 0
            if self.player.health <= 0:
                self.game_state.is_game_over = True
        except Exception as e:
            self.log(f"Error actualizando el juego: {e}")

    def draw(self):
        try:
            if self.debug_mode:
                self.profiler.start("draw_clear_surface")
            self.render_surface.fill((0, 0, 0))
            if self.debug_mode:
                self.profiler.stop()

            # Renderizado de capas base y medium
            if self.debug_mode:
                self.profiler.start("draw_background")
            self.tilemap.draw_background_layers(self.render_surface)
            if self.debug_mode:
                self.profiler.stop()

            # Renderizado de entidades
            if self.debug_mode:
                self.profiler.start("draw_entities")
            self.player.draw(self.render_surface, self.tilemap.camera_x, self.tilemap.camera_y)
            self.enemy_manager.draw(self.render_surface, self.tilemap.camera_x, self.tilemap.camera_y)
            for item in self.enemy_manager.items:
                item.draw(self.render_surface, self.tilemap.camera_x, self.tilemap.camera_y)
            if self.debug_mode:
                self.profiler.stop()

            # Renderizado de capa overlay
            if self.debug_mode:
                self.profiler.start("draw_overlay")
            self.tilemap.draw_overlay_layer(self.render_surface)
            if self.debug_mode:
                self.profiler.stop()

            # UI
            if self.debug_mode:
                self.profiler.start("draw_ui")
            self.ui_manager.draw(self.render_surface, self.player, self.game_state, self.enemy_manager)
            if self.debug_mode:
                self.profiler.stop()

            # Escalado final y presentación
            if self.debug_mode:
                self.profiler.start("draw_final")
            self.screen.blit(pygame.transform.scale(self.render_surface, self.screen.get_size()), (0, 0))
            pygame.display.flip()
            if self.debug_mode:
                self.profiler.stop()
        except Exception as e:
            self.log(f"Error dibujando el juego: {e}")

    def run(self):
        try:
            while not self.game_state.is_game_over:
                delta_time = self.clock.tick(self.settings.FPS) / 1000.0
                if not self.handle_events():
                    break
                self.update(delta_time)
                self.draw()
                
            # Mostrar pantalla de Game Over si el juego ha terminado
            if self.game_state.is_game_over:
                game_over_screen = GameOverScreen(self.screen, self.game_state, self.player.score)
                game_over_screen.run()
        except Exception as e:
            self.log(f"Error en el bucle principal: {e}")
