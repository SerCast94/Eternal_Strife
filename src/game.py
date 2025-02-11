from queue import Queue
import time
import pygame
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
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
        self.godmode = False
        self.last_fps = 0
        self.fps_update_time = 0
        self.fps_update_interval = 0.5
        
        # Add log messages list initialization
        self.log_messages = []  # Initialize log messages list
        
        # Rest of initialization...
        self.collision_thread = None
        self.collision_queue = Queue()
        self.collision_results = Queue()
        self.collision_event = threading.Event()
        self.collision_running = True
        self.update_thread_pool = ThreadPoolExecutor(max_workers=4)

        self.frame_start_time = 0
        self.frame_end_time = 0
        self.target_frame_time = 1.0 / 60.0  # Target 60 FPS
        self.thread_sync_event = threading.Event()
        
        # Rendering optimization
        self.render_surface = pygame.Surface(
            (self.settings.screen_width, self.settings.screen_height)
        ).convert_alpha()
        
        # Pre-render surfaces
        self.background_surface = pygame.Surface(
            (self.settings.screen_width, self.settings.screen_height)
        ).convert_alpha()
        
        # Batch rendering buffers
        self.entity_buffer = []
        self.visible_entities_cache = []
        self.last_camera_pos = None
        
        # Start collision thread
        self.collision_thread = threading.Thread(target=self._collision_worker)
        self.collision_thread.daemon = True
        self.collision_thread.start()

        self._init_game_components()

    def _init_game_components(self):
        """Initialize game components with proper error handling"""
        try:
            self.game_state = GameState()
            self.animation_manager = AnimationManager(self.settings)
            self.tilemap = TileMap(self.settings)
            self.tilemap.generate()
            self.enemy_manager = EnemyManager(self.settings, None, self.animation_manager, self.tilemap)
            self.player = Player(self.settings, self.animation_manager, self.enemy_manager)
            self.enemy_manager.player = self.player
            self.ui_manager = UIManager(self.settings)
        except Exception as e:
            self.log(f"Error initializing game components: {e}")
            raise

    def _collision_worker(self):
        """Dedicated thread for collision processing"""
        while self.collision_running:
            try:
                if not self.collision_queue.empty():
                    collision_data = self.collision_queue.get()
                    results = self.enemy_manager.process_collisions(
                        collision_data["enemies"],
                        collision_data["player"]
                    )
                    self.collision_results.put(results)
                    self.collision_event.set()
                else:
                    time.sleep(0.001)
            except Exception as e:
                self.log(f"Error in collision thread: {e}")

    def update(self, delta_time):
        try:
            self.delta_time = delta_time

            # Queue collision processing in separate thread
            self.collision_queue.put({
                "enemies": self.enemy_manager.enemies,
                "player": self.player
            })

            # Update game state synchronously
            self.game_state.update(delta_time)
            self.animation_manager.update(delta_time)
            self.player.update(delta_time, self.tilemap)
            self.enemy_manager.update(delta_time, self.tilemap)

            # Process collision results if available
            if self.collision_event.is_set():
                self._apply_collision_results(self.collision_results.get())
                self.collision_event.clear()

            # Update camera
            self.tilemap.update_camera(self.player.rect.centerx, self.player.rect.centery)

            if not self.godmode and self.player.health <= 0:
                self.game_state.is_game_over = True

        except Exception as e:
            self.log(f"Error updating game: {e}")

    def draw(self):
        try:
            if self.debug_mode:
                self.profiler.start("draw_full")

            # Clear render surface
            self.render_surface.fill((0, 0, 0))

            # Draw background and tilemap layers
            self.tilemap.draw_background_layers(self.render_surface)

            # Get all visible entities and sort them by Y position for proper layering
            visible_entities = []
            
            # Add visible enemies
            for enemy in self.enemy_manager.enemies:
                screen_x = (enemy.rect.x - self.tilemap.camera_x) * self.settings.zoom
                screen_y = (enemy.rect.y - self.tilemap.camera_y) * self.settings.zoom
                if (0 <= screen_x <= self.settings.screen_width and 
                    0 <= screen_y <= self.settings.screen_height):
                    visible_entities.append((enemy, enemy.rect.bottom))

            # Add visible projectiles
            for projectile in self.enemy_manager.projectile_pool.active_projectiles:
                screen_x = (projectile.rect.x - self.tilemap.camera_x) * self.settings.zoom
                screen_y = (projectile.rect.y - self.tilemap.camera_y) * self.settings.zoom
                if (0 <= screen_x <= self.settings.screen_width and 
                    0 <= screen_y <= self.settings.screen_height):
                    visible_entities.append((projectile, projectile.rect.bottom))

            # Add player
            visible_entities.append((self.player, self.player.rect.bottom))

            # Sort all entities by Y position (bottom) for proper layering
            visible_entities.sort(key=lambda x: x[1])

            # Draw all entities in order
            for entity, _ in visible_entities:
                entity.draw(self.render_surface, self.tilemap.camera_x, self.tilemap.camera_y)

            # Draw overlay layers (like tiles that should be in front)
            self.tilemap.draw_overlay_layer(self.render_surface)

            # Draw UI
            self.ui_manager.draw(self.render_surface, self.player, self.game_state, self.enemy_manager)

            if self.debug_mode:
                self.draw_debug_info()

            # Scale and display final render
            pygame.transform.scale(
                self.render_surface,
                (self.settings.screen_width, self.settings.screen_height),
                self.screen
            )
            pygame.display.flip()

            if self.debug_mode:
                self.profiler.stop()

        except Exception as e:
            self.log(f"Error drawing game: {e}")

    def _apply_collision_results(self, collision_results):
        """Apply collision results from the collision thread"""
        try:
            for collision_type, obj1, obj2 in collision_results:
                if collision_type == "enemy-enemy":
                    # Calculate push direction
                    direction = pygame.Vector2(
                        obj1.rect.centerx - obj2.rect.centerx,
                        obj1.rect.centery - obj2.rect.centery
                    )
                    if direction.length() > 0:
                        direction.normalize_ip()
                        push_strength = 2.0  # Reduced from 5.0 for smoother movement
                        
                        # Push both enemies apart
                        obj1.move(
                            obj1.rect.x + direction.x * push_strength,
                            obj1.rect.y + direction.y * push_strength
                        )
                        obj2.move(
                            obj2.rect.x - direction.x * push_strength,
                            obj2.rect.y - direction.y * push_strength
                        )
                
                elif collision_type == "enemy-player" and not self.godmode:
                    # Apply damage to player
                    self.player.health -= obj1.damage * self.delta_time
                    
                    # Push player away from enemy
                    direction = pygame.Vector2(
                        self.player.rect.centerx - obj1.rect.centerx,
                        self.player.rect.centery - obj1.rect.centery
                    )
                    if direction.length() > 0:
                        direction.normalize_ip()
                        self.player.move(
                            self.player.rect.x + direction.x * 3.0,
                            self.player.rect.y + direction.y * 3.0
                        )
        
        except Exception as e:
            self.log(f"Error applying collision results: {e}")

    def _get_visible_entities(self):
        """Get entities within the camera view with spatial optimization"""
        camera_rect = pygame.Rect(
            self.tilemap.camera_x - self.settings.culling_margin,
            self.tilemap.camera_y - self.settings.culling_margin,
            self.settings.screen_width + self.settings.culling_margin * 2,
            self.settings.screen_height + self.settings.culling_margin * 2
        )

        visible_entities = []
        cells = self.enemy_manager.get_active_cells_in_view(camera_rect)
        
        for cell in cells:
            for enemy in self.enemy_manager.spatial_grid.get(cell, []):
                if camera_rect.colliderect(enemy.rect):
                    visible_entities.append(enemy)

        return visible_entities

    def cleanup(self):
        """Clean up resources and threads"""
        self.collision_running = False
        if self.collision_thread:
            self.collision_thread.join(timeout=1.0)
        self.update_thread_pool.shutdown(wait=True)

    def run(self):
        """Main game loop"""
        try:
            self.clock.tick()  # Initial tick to prevent first huge delta
            last_update_time = time.time()
            
            while not self.game_state.is_game_over:
                self.frame_start_time = time.time()
                
                # Calculate frame timing
                current_time = time.time()
                frame_time = current_time - last_update_time
                
                # Force synchronization with target frame rate
                if frame_time < self.target_frame_time:
                    time.sleep(self.target_frame_time - frame_time)
                    current_time = time.time()
                    frame_time = current_time - last_update_time
                
                last_update_time = current_time
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.game_state.is_game_over = True
                        elif event.key == pygame.K_F1 and self.debug_mode:
                            self.profiler.show_graphs()
                        elif event.key == pygame.K_F2 and self.debug_mode:
                            self.profiler.export_data()
                        elif event.key == pygame.K_g and self.debug_mode:
                            self.godmode = not self.godmode
                    self.player.handle_input(event)

                # Calculate delta time with hard cap
                delta_time = min(frame_time, 0.1)
                
                # Signal threads to start processing this frame
                self.thread_sync_event.set()
                
                # Update game state
                self.update(delta_time)
                
                # Wait for collision thread to finish if it's still processing
                if self.collision_event.is_set():
                    self._apply_collision_results(self.collision_results.get())
                    self.collision_event.clear()
                
                # Draw frame
                self.draw()
                
                # Reset thread sync event for next frame
                self.thread_sync_event.clear()

                # Update debug metrics
                if self.debug_mode:
                    current_time = time.time()
                    if current_time - self.fps_update_time >= self.fps_update_interval:
                        self.last_fps = 1.0 / frame_time if frame_time > 0 else 0
                        self.fps_update_time = current_time
                        if self.profiler:
                            self.profiler.add_metric("fps", self.last_fps)
                            self.profiler.add_metric("enemy_count", len(self.enemy_manager.enemies))
                            self.profiler.add_metric("frame_time", frame_time * 1000)
                            self.profiler.add_metric("thread_sync_time", 
                                (time.time() - self.frame_start_time) * 1000)

                # Ensure we don't exceed target frame rate
                self.frame_end_time = time.time()
                total_frame_time = self.frame_end_time - self.frame_start_time
                if total_frame_time < self.target_frame_time:
                    time.sleep(self.target_frame_time - total_frame_time)

            # Show game over screen
            game_over = GameOverScreen(self.screen, self.game_state, self.player.score)
            game_over.run()
            
            # Cleanup
            self.cleanup()

        except Exception as e:
            self.log(f"Error in game loop: {e}")

    def log(self, message):
        """Log a debug message"""
        if self.debug_mode:
            print(f"[DEBUG] {message}")
            self.log_messages.append(message)
            
            # Keep only last 100 messages to avoid memory issues
            if len(self.log_messages) > 100:
                self.log_messages.pop(0)

    def draw_debug_info(self):
        """Draw debug information on screen"""
        if not self.debug_mode:
            return
            
        font = pygame.font.Font(None, 24)
        y = 100
        
        # Display FPS
        fps_text = font.render(f"FPS: {int(self.last_fps)}", True, (255, 255, 255))
        self.render_surface.blit(fps_text, (10, y))
        y += 20
        
        # Display enemy count
        enemy_count = len(self.enemy_manager.enemies)
        enemy_text = font.render(f"Enemies: {enemy_count}", True, (255, 255, 255))
        self.render_surface.blit(enemy_text, (10, y))
        y += 20
        
        # Display last few log messages
        for message in self.log_messages[-5:]:
            text = font.render(message[:50], True, (255, 255, 255))
            self.render_surface.blit(text, (10, y))
            y += 20