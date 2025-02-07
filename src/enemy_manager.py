import pygame
import random
import math
import threading
from enemy_types import SlimeEnemy, RangedEnemy
from item import Item, Gem, Tuna
from projectile import Projectile

class EnemyManager:
    def __init__(self, settings, player, animation_manager, tilemap):
        self.settings = settings
        self.player = player
        self.animation_manager = animation_manager
        self.tilemap = tilemap  # Almacenar tilemap
        self.enemies = []
        self.items = []  # Lista de ítems dropeados
        self.projectiles = []  # Lista de proyectiles
        self.spawn_timer = 0
        self.time_elapsed = 0
        self.spawn_rate = self.settings.enemy_spawn_rate
        self.lock = threading.Lock()
        
        # Spatial grid for collision optimization
        self.cell_size = 64  # Size of each cell in the grid
        self.grid_width = self.settings.map_width * self.settings.tile_size // self.cell_size + 1
        self.grid_height = self.settings.map_height * self.settings.tile_size // self.cell_size + 1
        self.spatial_grid = {}
        
        # Define enemy types and their spawn probabilities
        self.enemy_types = {
            "slime": {"class": SlimeEnemy, "weight": 0.7},
            "ranged": {"class": RangedEnemy, "weight": 0.3}
        }

        # Thread management
        self.num_threads = 10
        self.threads = []
        self.thread_events = [threading.Event() for _ in range(self.num_threads)]
        self.thread_locks = [threading.Lock() for _ in range(self.num_threads)]
        self.thread_enemies = [[] for _ in range(self.num_threads)]
        self.stop_threads = False
        self.delta_time = 0  # Almacenar delta time

        for i in range(self.num_threads):
            thread = threading.Thread(target=self.update_thread, args=(i,))
            thread.start()
            self.threads.append(thread)

    def _get_grid_cell(self, position):
        """Get the grid cell for a given position"""
        return (int(position[0] // self.cell_size),
                int(position[1] // self.cell_size))
                
    def _update_spatial_grid(self):
        """Update the spatial grid with the current positions of enemies"""
        self.spatial_grid.clear()
        for enemy in self.enemies:
            cell = self._get_grid_cell(enemy.rect.center)
            if cell not in self.spatial_grid:
                self.spatial_grid[cell] = []
            self.spatial_grid[cell].append(enemy)
            
    def _get_nearby_enemies(self, position, radius):
        """Get enemies near a position using the spatial grid"""
        nearby = set()
        cell_radius = int(radius // self.cell_size) + 1
        center_cell = self._get_grid_cell(position)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.spatial_grid:
                    nearby.update(self.spatial_grid[cell])
        
        return nearby

    def _is_in_view(self, enemy_pos, camera_pos):
        """Determine if an enemy is within the visible area"""
        dx = enemy_pos[0] - camera_pos[0]
        dy = enemy_pos[1] - camera_pos[1]
        return (dx * dx + dy * dy) <= (self.settings.enemy_culling_distance * self.settings.enemy_culling_distance)

    def _get_random_enemy_type(self):
        enemy_classes = list(self.enemy_types.values())
        weights = [enemy["weight"] for enemy in enemy_classes]
        return random.choices(enemy_classes, weights=weights, k=1)[0]["class"]

    def spawn_enemy(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = 300
        spawn_x = self.player.rect.x + math.cos(angle) * distance
        spawn_y = self.player.rect.y + math.sin(angle) * distance

        spawn_x = max(0, min(spawn_x, 
            self.settings.map_width * self.settings.tile_size - self.settings.enemy_size[0]))
        spawn_y = max(0, min(spawn_y, 
            self.settings.map_height * self.settings.tile_size - self.settings.enemy_size[1]))

        with self.lock:
            enemy_class = self._get_random_enemy_type()
            enemy = enemy_class(self.settings, (spawn_x, spawn_y), self.animation_manager, self)
            self.enemies.append(enemy)
            # Assign the enemy to a thread
            thread_index = len(self.enemies) % self.num_threads
            self.thread_enemies[thread_index].append(enemy)

    def update(self, delta_time, tilemap):
        self.time_elapsed += delta_time
        self.spawn_timer += delta_time
        self.spawn_rate = self.settings.enemy_spawn_rate + self.time_elapsed * 0.01
        self.delta_time = delta_time  # Actualizar delta time

        if self.spawn_timer >= 1.0 / self.spawn_rate:
            self.spawn_enemy()
            self.spawn_timer = 0

        with self.lock:
            # Update spatial grid
            self._update_spatial_grid()
            
            # Center of the camera for culling
            camera_center = (
                self.player.rect.centerx,
                self.player.rect.centery
            )
            
            # Signal threads to update
            for event in self.thread_events:
                event.set()

            # Wait for threads to finish
            for event in self.thread_events:
                event.wait()
                event.clear()

        # Actualizar proyectiles
        for projectile in self.projectiles[:]:
            if projectile.update(delta_time, self.player, self):
                self.projectiles.remove(projectile)

    def update_thread(self, thread_index):
        while not self.stop_threads:
            self.thread_events[thread_index].wait()
            with self.thread_locks[thread_index]:
                for enemy in self.thread_enemies[thread_index]:
                    if self._is_in_view(enemy.rect.center, (self.player.rect.centerx, self.player.rect.centery)):
                        enemy.update(self.delta_time, self.tilemap, self.player.rect.center)
                        
                        # Check collisions with other enemies
                        nearby_enemies = self._get_nearby_enemies(enemy.rect.center, enemy.collision_radius * 2)
                        for other_enemy in nearby_enemies:
                            if enemy != other_enemy and enemy.check_collision_with_enemy(other_enemy):
                                enemy.resolve_collision(other_enemy)

                        # Check collision with the player
                        if enemy.hitbox.colliderect(self.player.hitbox):
                            self.player.health -= enemy.damage * self.delta_time
                            push_dir = pygame.Vector2(enemy.rect.center) - pygame.Vector2(self.player.rect.center)
                            if push_dir.length() > 0:
                                push_dir = push_dir.normalize() * 5
                                enemy.move(
                                    enemy.rect.x + push_dir.x,
                                    enemy.rect.y + push_dir.y
                                )
                # Eliminar enemigos muertos y dropear ítems
                for enemy in self.thread_enemies[thread_index][:]:
                    if enemy.health <= 0:
                        self.remove_enemy(enemy)
            self.thread_events[thread_index].clear()

    def remove_enemy(self, enemy):
        with self.lock:
            for thread_enemies in self.thread_enemies:
                if enemy in thread_enemies:
                    thread_enemies.remove(enemy)
            if enemy in self.enemies:
                self.enemies.remove(enemy)
            self.drop_item(enemy.rect.center)

    def drop_item(self, position):
        # Dropear un ítem aleatorio (gema o atún)
        if random.random() < 0.95:
            item = Gem(self.settings, self.animation_manager, position)
        else:
            item = Tuna(self.settings, self.animation_manager, position)
        self.items.append(item)

    def add_projectile(self, projectile):
        self.projectiles.append(projectile)

    def draw(self, screen, camera_x, camera_y):
        # Dibujar enemigos
        for enemy in self.enemies:
            enemy.draw(screen, camera_x, camera_y)
        
        # Dibujar proyectiles
        for projectile in self.projectiles:
            projectile.draw(screen, camera_x, camera_y)