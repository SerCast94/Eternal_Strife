import time
import pygame
import random
import math
import threading
import concurrent.futures
from collections import defaultdict
from enemy_types import SlimeEnemy, RangedEnemy
from item import Item, Gem, Tuna
from projectile import Projectile
from concurrent.futures import ThreadPoolExecutor
import numpy as np

class ProjectilePool:
    def __init__(self, max_size=2000):
        self.active_projectiles = set()
        self.inactive_projectiles = []
        self.max_size = max_size

    def get_projectile(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name):
        if self.inactive_projectiles:
            projectile = self.inactive_projectiles.pop()
            projectile.reset(settings, animation_manager, position, target_position, damage, speed, target_type, animation_name)
        else:
            projectile = Projectile(settings, animation_manager, position, target_position, damage, speed, target_type, animation_name)
        
        self.active_projectiles.add(projectile)
        return projectile

    def return_projectile(self, projectile):
        if projectile in self.active_projectiles:
            self.active_projectiles.remove(projectile)
            if len(self.inactive_projectiles) < self.max_size:
                self.inactive_projectiles.append(projectile)

class EnemyManager:
    def __init__(self, settings, player, animation_manager, tilemap):
        self.settings = settings
        self.player = player
        self.animation_manager = animation_manager
        self.tilemap = tilemap
        self.enemies = []
        self.items = []

        self.last_update_time = 0
        self.min_update_interval = 1.0 / 60.0  # Minimum time between updates

        # Spatial partitioning optimization
        self.cell_size = 128
        self.grid_width = settings.map_width // (self.cell_size // settings.tile_size)
        self.grid_height = settings.map_height // (self.cell_size // settings.tile_size)
        self.spatial_grid = {}
        self.active_cells = set()
        self.neighbor_cells_cache = {}
        
        # Numpy arrays for vectorized calculations
        self.position_array = np.zeros((2000, 2))
        self.velocity_array = np.zeros((2000, 2))
        
        # Threading optimization
        self.thread_pool = ThreadPoolExecutor(max_workers=settings.thread_pool_size)
        self.batch_size = 200
        
        # Enemy type configuration
        self.enemy_types = {
            "slime": {"class": SlimeEnemy, "weight": 0.7},
            "ranged": {"class": RangedEnemy, "weight": 0.3}
        }
        
        # Object pooling
        self.projectile_pool = ProjectilePool()
        
        # Game state
        self.spawn_timer = 0
        self.time_elapsed = 0
        self.spawn_rate = settings.enemy_spawn_rate
        self.multiplicadorSpawnRate = 1

    def _get_grid_cell(self, position):
        return (int(position[0] // self.cell_size), 
                int(position[1] // self.cell_size))

    def _get_neighbor_cells(self, cell):
        if cell not in self.neighbor_cells_cache:
            neighbors = []
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    neighbor_x = cell[0] + dx
                    neighbor_y = cell[1] + dy
                    if (0 <= neighbor_x < self.grid_width and 
                        0 <= neighbor_y < self.grid_height):
                        neighbors.append((neighbor_x, neighbor_y))
            self.neighbor_cells_cache[cell] = neighbors
        return self.neighbor_cells_cache[cell]

    def _update_spatial_grid(self):
        self.spatial_grid.clear()
        self.active_cells.clear()
        
        # Vectorized position update
        for i, enemy in enumerate(self.enemies):
            self.position_array[i] = enemy.rect.center
            cell = self._get_grid_cell(enemy.rect.center)
            if cell not in self.spatial_grid:
                self.spatial_grid[cell] = []
            self.spatial_grid[cell].append(enemy)
            self.active_cells.add(cell)

    def get_active_cells_in_view(self, view_rect):
        """Get active grid cells in view rectangle"""
        left = max(0, int(view_rect.left // self.cell_size))
        top = max(0, int(view_rect.top // self.cell_size))
        right = min(self.grid_width - 1, int(view_rect.right // self.cell_size))
        bottom = min(self.grid_height - 1, int(view_rect.bottom // self.cell_size))
        
        return [cell for cell in self.active_cells 
                if left <= cell[0] <= right and top <= cell[1] <= bottom]

    def _process_enemy_batch(self, enemy_batch):
        """Process a batch of enemies in parallel"""
        for enemy in enemy_batch:
            enemy.update(self.delta_time, self.tilemap, self.player.rect.center)

    def update(self, delta_time, tilemap):
        try:
            # Wait for thread sync event
            current_time = time.time()
            time_since_last_update = current_time - self.last_update_time
            
            if time_since_last_update < self.min_update_interval:
                time.sleep(self.min_update_interval - time_since_last_update)
            
            self.delta_time = min(delta_time, 0.1)  # Cap delta time
            self.last_update_time = time.time()
            
            # Update timing
            self.time_elapsed += self.delta_time
            self.spawn_timer += self.delta_time
            
            # Update spawn rate with time-based scaling
            self.spawn_rate = (self.settings.enemy_spawn_rate + 
                            self.time_elapsed * 0.01 * 
                            self.multiplicadorSpawnRate)

            # Spawn enemies
            if self.spawn_timer >= 1.0 / self.spawn_rate:
                self.spawn_enemy()
                self.spawn_timer = 0

            # Update spatial grid
            self._update_spatial_grid()

            # Update enemies with capped delta time
            for enemy in self.enemies:
                enemy.update(self.delta_time, tilemap, self.player.rect.center)

            # Update projectiles
            for projectile in list(self.projectile_pool.active_projectiles):
                if projectile.update(self.delta_time, self.player, self):
                    self.projectile_pool.return_projectile(projectile)

        except Exception as e:
            print(f"Error updating enemies: {e}")

    def add_projectile(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name):
        """Create a new projectile or get one from the pool"""
        return self.projectile_pool.get_projectile(
            settings, animation_manager, position, target_position,
            damage, speed, target_type, animation_name
        )

    def process_collisions(self, enemies, player):
        """Process collisions between entities"""
        collision_results = []
        
        # Process enemy-enemy collisions using spatial grid
        for cell in self.active_cells:
            enemies_in_cell = self.spatial_grid.get(cell, [])
            for i, enemy1 in enumerate(enemies_in_cell):
                # Check nearby cells
                for neighbor_cell in self._get_neighbor_cells(cell):
                    for enemy2 in self.spatial_grid.get(neighbor_cell, []):
                        if enemy1 != enemy2:
                            dx = enemy1.rect.centerx - enemy2.rect.centerx
                            dy = enemy1.rect.centery - enemy2.rect.centery
                            dist_squared = dx * dx + dy * dy
                            
                            if dist_squared < (enemy1.collision_radius + enemy2.collision_radius) ** 2:
                                collision_results.append(("enemy-enemy", enemy1, enemy2))

        # Process enemy-player collisions
        player_cell = self._get_grid_cell(player.rect.center)
        for cell in self._get_neighbor_cells(player_cell):
            for enemy in self.spatial_grid.get(cell, []):
                if enemy.rect.colliderect(player.rect):
                    collision_results.append(("enemy-player", enemy, player))
                    
        return collision_results

    def _get_random_enemy_type(self):
        """Select random enemy type based on weights"""
        enemy_types = list(self.enemy_types.values())
        weights = [enemy_type["weight"] for enemy_type in enemy_types]
        chosen_type = random.choices(enemy_types, weights=weights, k=1)[0]
        return chosen_type["class"]

    def spawn_enemy(self):
        """Spawn enemy at random position around player"""
        angle = random.uniform(0, 2 * math.pi)
        spawn_distance = 300
        
        spawn_x = self.player.rect.x + math.cos(angle) * spawn_distance
        spawn_y = self.player.rect.y + math.sin(angle) * spawn_distance

        spawn_x = max(0, min(spawn_x, 
            self.settings.map_width * self.settings.tile_size - self.settings.enemy_size[0]))
        spawn_y = max(0, min(spawn_y, 
            self.settings.map_height * self.settings.tile_size - self.settings.enemy_size[1]))

        enemy_class = self._get_random_enemy_type()
        enemy = enemy_class(self.settings, (spawn_x, spawn_y), 
                          self.animation_manager, self)
        self.enemies.append(enemy)

    def remove_enemy(self, enemy):
        """Remove enemy and potentially drop item"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            self.drop_item(enemy.rect.center)

    def drop_item(self, position):
        """Drop item at position with probability"""
        try:
            if random.random() < 0.70:  # 70% chance for gem
                item = Gem(self.settings, self.animation_manager, position)
            else:  # 30% chance for health
                item = Tuna(self.settings, self.animation_manager, position)
            self.items.append(item)
        except Exception as e:
            print(f"Error dropping item: {e}")