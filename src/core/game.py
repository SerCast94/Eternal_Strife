# src/game.py

import pygame
import sys
import threading
from core.game_state import GameState
from core.settings import Settings
from entities.player import Player
from utils.profiler import Profiler
from screens.level_up_screen import LevelUpScreen
from managers.music_player import MusicPlayer
from world.tilemap import TileMap
from managers.enemy_manager import EnemyManager
from managers.ui_manager import UIManager
from managers.animation_manager import AnimationManager
from screens.game_over_screen import GameOverScreen
import random

class Game:
    def __init__(self, screen,music_player,debug_mode=False):
        """
        Constructor de la clase Game que inicializa el juego y todos sus componentes.
        Parámetros:
        - screen: Superficie de pygame donde se renderizará el juego
        - music_player: Gestor de música del juego
        - debug_mode: Modo de depuración (por defecto False)
        Inicializa:
        - Configuraciones básicas (settings, clock, debug)
        - Sistema de tiempo y delta_time
        - Gestores (animación, enemigos, UI)
        - Jugador y mapa
        """
        self.screen = screen
        self.settings = Settings()
        self.clock = pygame.time.Clock()
        self.debug_mode = debug_mode
        self.profiler = Profiler() if debug_mode else None
        self.paused = False
        self.game_time = 0
        self.game_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.game_timer, 1000 // self.settings.FPS)
        self.last_tick = pygame.time.get_ticks()
        self.delta_time = 0
        self.music_player = music_player

        self.debug_info = {
            "fps": 0,
            "enemy_calc_time": 0,
            "frame_time": 0,
            "god_mode": False,
            # Añadir nuevas métricas
            "enemy_count": 0,
            "spawn_rate": 0,
            "collision_time": 0,
            "pathfinding_time": 0,
            "enemy_render_time": 0,
            "spatial_grid_time": 0
        }

        self.debug_font = pygame.font.SysFont(None, 24)

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
        self.game_state = GameState(self)
        self.log("GameState inicializado")

        self.log("Inicializando AnimationManager...")
        self.animation_manager = AnimationManager(self.settings, self)
        self.log("AnimationManager inicializado")

        self.log("Inicializando TileMap...")
        self.tilemap = TileMap(self.settings)
        self.tilemap.generate()
        self.log("TileMap inicializado")

        self.log("Inicializando EnemyManager...")
        self.enemy_manager = EnemyManager(self.settings, None, self.animation_manager, self.tilemap,self)
        self.log("EnemyManager inicializado")

        self.log("Inicializando Player...")
        self.player = Player(self.settings, self.animation_manager, self.enemy_manager, self)
        self.enemy_manager.player = self.player  # Asignar el jugador al EnemyManager
        self.log("Player inicializado")

        self.log("Inicializando UIManager...")
        self.ui_manager = UIManager(self.settings)
        self.log("UIManager inicializado")

        self.log("Juego inicializado correctamente")
        

    def log(self, message):
        """
        Registra mensajes en la consola y actualiza la pantalla de carga.
        Parámetros:
        - message: Mensaje a mostrar en la consola
        """
        print(message)
        self.show_loading_screen()

    def show_loading_screen(self):
        """
        Muestra la pantalla de carga con animación de estrellas.
        Renderiza el texto "Generando nivel..." y estrellas animadas
        para dar feedback visual durante la carga.
        """
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
        """
        Maneja los eventos de entrada del juego.
        Procesa:
        - Eventos de cierre de ventana
        - Teclas de depuración (F1, F2, F3, H, L)
        - Tecla de reinicio (R)
        - Entrada del jugador
        Retorna:
        - True si el juego debe continuar
        - False si el juego debe cerrarse
        """
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
                    if event.key == pygame.K_h and self.debug_mode:
                        self.debug_info["god_mode"] = not self.debug_info["god_mode"]
                        self.player.is_invincible = self.debug_info["god_mode"]
                    if event.key == pygame.K_F3 and self.debug_mode:
                        self.enemy_manager.multiplicadorRatioSpawn += 3
                    if event.key == pygame.K_l and self.debug_mode:
                        self.player.level += 1
                        self.mostarVentanaLevelup()
                self.player.handle_input(event)
            return True
        except Exception as e:
            print(f"Error manejando eventos: {e}")
            return False
        
    def run(self):
        """
        Bucle principal del juego.
        Gestiona:
        - Reproducción de música
        - Bucle de eventos
        - Actualización de estados
        - Renderizado
        - Control de FPS
        - Pantalla de game over
        """
        try:
            self.music_player.change_playlist("game")
            self.music_player.play_random()
            while not self.game_state.is_game_over:
                # Process all events first
                if not self.handle_events():
                    return
                    
                # Only update and draw if game timer event occurred and not paused
                current_time = pygame.time.get_ticks()
                self.delta_time = (current_time - self.last_tick) / 1000.0
                self.last_tick = current_time
                
                if not self.paused:
                    self.update()
                
                self.draw()
                self.clock.tick(self.settings.FPS)
                
                if self.game_state.is_game_over:
                    current_volume = self.music_player.get_volume()
                    game_over_screen = GameOverScreen(self.screen, self.game_state, self.player.score,self.player.level,self)
                    self.music_player.set_volume(0.7)
                    self.music_player.play_once("game_over",False)
                    game_over_screen = GameOverScreen(self.screen, self.game_state, self.player.score,self.player.level,self)
                    game_over_screen.run()
                        
        except Exception as e:
            self.log(f"Error en el bucle principal: {e}")
                    
        except Exception as e:
            self.log(f"Error en el bucle principal: {e}")

    def update(self):
        """
        Actualiza el estado del juego en cada frame.
        Actualiza:
        - Animaciones
        - Estado del jugador
        - Gestión de enemigos
        - Cámara
        - Información de depuración
        """
        try:
            if self.paused:
                return
                
            frame_start = pygame.time.get_ticks()

            # Update animations only if not paused
            if self.debug_mode:
                self.profiler.start("update_animation_manager")
            self.animation_manager.update()
            if self.debug_mode:
                self.profiler.stop()

            # Update player only if not paused
            if not self.paused:
                self.updatePlayer()
                self.game_time += self.delta_time
            
            # Update enemies only if not paused
            if self.debug_mode:
                self.profiler.start("enemy_management")
            enemy_calc_start = pygame.time.get_ticks()
            self.enemy_manager.update(self.tilemap)
            self.debug_info["enemy_calc_time"] = pygame.time.get_ticks() - enemy_calc_start
            if self.debug_mode:
                self.profiler.stop()

            # Update camera only if not paused
            if not self.paused:
                self.tilemap.update_camera(self.player.rect.centerx, self.player.rect.centery)

                # Check game over
                if self.player.health <= 0 and not self.debug_info["god_mode"]:
                    self.game_state.is_game_over = True

                # Update debug info
                self.debug_info["frame_time"] = pygame.time.get_ticks() - frame_start
                self.debug_info["fps"] = self.clock.get_fps()
                self.debug_info["enemy_count"] = len(self.enemy_manager.enemies)

        except Exception as e:
            self.log(f"Error actualizando el juego: {e}")

    def restart_game(self):
        """
        Reinicia todos los componentes del juego a su estado inicial.
        Reinicia:
        - Mapa
        - Gestor de enemigos
        - Jugador
        - Estado del juego
        - Temporizadores
        """
        try:
            print("Reiniciando componentes del juego...")
            # Mostrar pantalla de carga
            self.show_loading_screen()
            
            # Regenerar el mapa
            self.log("Regenerando el mapa...")
            self.tilemap = TileMap(self.settings)
            self.tilemap.generate()
            self.log("Mapa regenerado")

            # Reiniciar EnemyManager primero (sin el jugador por ahora)
            self.log("Reiniciando EnemyManager...")
            self.enemy_manager = EnemyManager(self.settings, None, self.animation_manager, self.tilemap, self)
            self.log("EnemyManager reiniciado")
            
            # Reiniciar jugador con la referencia al nuevo EnemyManager
            self.log("Reiniciando jugador...")
            self.player = Player(self.settings, self.animation_manager, self.enemy_manager, self)
            self.log("Jugador reiniciado")
            
            # Actualizar la referencia al jugador en el EnemyManager
            self.enemy_manager.player = self.player
            
            # Reiniciar estado del juego
            self.game_state.is_game_over = False
            self.game_time = 0
            self.delta_time = 0
            self.last_tick = pygame.time.get_ticks()
            
            self.log("Componentes del juego reiniciados correctamente")
        except Exception as e:
            self.log(f"Error reiniciando el juego: {e}")

    
            
    def draw_debug_info(self):
        """
        Dibuja información de depuración en la pantalla cuando el modo de depuración está activado.
        """
        if not self.debug_mode:
            return
        debug_text = [
            f"FPS: {self.debug_info['fps']:.1f}",
            f"Enemy Calc Time: {self.debug_info['enemy_calc_time']:.2f}ms",
            f"Frame Time: {self.debug_info['frame_time']:.2f}ms",
            f"Enemy Count: {self.debug_info['enemy_count']}",
            f"Spawn Rate: {self.debug_info['spawn_rate']:.2f}",
            f"Escala Vida enemigos: {self.enemy_manager.health_scale:.2f}",
            f"Escala Damage enemigos: {self.enemy_manager.damage_scale:.2f}",
            f"Spatial Grid Time: {self.debug_info['spatial_grid_time']:.2f}ms",
            f"Pathfinding Time: {self.debug_info['pathfinding_time']:.2f}ms",
            f"Current level {self.player.level}",
            f"Exp to next level {self.player.exp_to_next_level}",
            f"Exp increase rate {self.player.exp_increase_rate}",
            f"Game time {self.game_time:.2f}",
            f"Delta time {self.delta_time:.2f}",
            "",
            "Controles de Debug:",
            "F1: Mostrar graficos de rendimiento",
            "F2: Exportar datos de rendimiento",
            "F3: Aumentar dificultad",
            "L: Mostar ventana de level up",
            "H: Activar god mode ({})".format("ON" if self.debug_info["god_mode"] else "OFF"),
            "R: Reiniciar juego"
            ]

        y_offset = 40
        for text in debug_text:
            text_surface = self.debug_font.render(text, True, (255, 255, 255))
            self.render_surface.blit(text_surface, (10, y_offset))
            y_offset += 20

    def draw(self):
        """
        Renderiza todos los elementos del juego en la pantalla.
        Dibuja en orden:
        - Fondo y capas medias del mapa
        - Entidades (jugador, enemigos, items)
        - Capa de superposición del mapa
        - Interfaz de usuario
        - Información de depuración
        - Reproductor de música
        """
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
            self.ui_manager.draw(self.render_surface, self.player, self.game_state, self.enemy_manager,self)
            if self.debug_mode:
                self.profiler.stop()
                
            if self.debug_mode:
                self.profiler.start("draw_debug")
                self.draw_debug_info()
                self.profiler.stop()

            self.music_player.draw(self.render_surface)
            # Escalado final y presentación
            if self.debug_mode:
                self.profiler.start("draw_final")
            self.screen.blit(pygame.transform.scale(self.render_surface, self.screen.get_size()), (0, 0))
            pygame.display.flip()
            if self.debug_mode:
                self.profiler.stop()
        except Exception as e:
            self.log(f"Error dibujando el juego: {e}")
            
    def updatePlayer(self):
        """
        Actualiza el estado del jugador y verifica si ha subido de nivel.
        Si el jugador sube de nivel, muestra la ventana de level up.
        """
    # Update player and check for level up
        result = self.player.update(self.tilemap)
        if result:
            self.mostarVentanaLevelup()

    def mostarVentanaLevelup(self):
        """
        Muestra la ventana de selección de mejoras al subir de nivel.
        Gestiona:
        - Pausa del juego
        - Efectos de sonido
        - Interfaz de selección de mejoras
        - Estado del jugador
        - Restauración del estado del juego
        """
        try:
            # Hacer una copia del estado actual de la pantalla
            current_surface = self.screen.copy()
            self.music_player.play_once("level_up",False)
            
            # Pausar el juego y detener el timer
            self.paused = True
            pygame.time.set_timer(self.game_timer, 0)
            self.animation_manager.pause()
            
            # Detener completamente al jugador
            saved_velocity = self.player.velocity.copy()
            self.player.velocity.x = 0
            self.player.velocity.y = 0
            
            # Crear la ventana de level up
            level_up_screen = LevelUpScreen(self.screen, self.player, self.settings, self)
            
            while not level_up_screen.done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    level_up_screen.handle_event(event)
                
                # Restaurar el estado guardado de la pantalla
                self.screen.blit(current_surface, (0, 0))
                
                # Crear y aplicar overlay semitransparente
                dim_surface = pygame.Surface(self.screen.get_size()).convert_alpha()
                dim_surface.fill((0, 0, 0, 128))
                self.screen.blit(dim_surface, (0, 0))
                
                # Dibujar la ventana de level up
                level_up_screen.draw()
                pygame.display.flip()
                                
                self.clock.tick(self.settings.FPS)
            
            # Restaurar el estado del juego
            self.paused = False
            pygame.time.set_timer(self.game_timer, 1000 // self.settings.FPS)
            self.last_tick = pygame.time.get_ticks()  # Resetear el último tick
            self.animation_manager.resume()

            self.music_player.restore_previous_state()
            
            # Restaurar velocidad del jugador
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_w] and not keys[pygame.K_s]:
                self.player.velocity.y = saved_velocity.y
            if not keys[pygame.K_a] and not keys[pygame.K_d]:
                self.player.velocity.x = saved_velocity.x
            
                
        except Exception as e:
            print(f"Error en ventana de level up: {e}")
            
    
        
