import pygame
import random
import math
from enemy_types import SlimeEnemy, RangedEnemy
from item import Item, Gem, Tuna
from projectile import Projectile

class EnemyManager:
    def __init__(self, settings, player, animation_manager, tilemap, game):
        self.settings = settings
        self.game = game
        self.player = player
        self.animation_manager = animation_manager
        self.tilemap = tilemap
        self.enemies = []
        self.items = []
        self.projectiles = []
        self.spawn_timer = 0
        self.time_elapsed = 0
        self.spawn_rate = self.settings.enemy_spawn_rate
        self.multiplicadorRatioSpawn = 1

        self.difficulty_multiplier = 1.0  # Factor base de dificultad
        self.health_scale = 1.0  # Escala de vida
        self.damage_scale = 1.0  # Escala de daño

        # Debug info
        self.debug_info = {
            "difficulty": 1.0,
            "spawn_rate": self.spawn_rate,
            "health_multiplier": 1.0,
            "damage_multiplier": 1.0
        }

        
        # Rejilla espacial para optimización de colisiones
        self.cell_size = 64
        self.grid_width = self.settings.map_width * self.settings.tile_size // self.cell_size + 1
        self.grid_height = self.settings.map_height * self.settings.tile_size // self.cell_size + 1
        self.spatial_grid = {}
        
        # Tipos de enemigos con sus pesos
        self.enemy_types = {
            "slime": {"class": SlimeEnemy, "weight": 0.9},
            "ranged": {"class": RangedEnemy, "weight": 0.1}
        }

    def _get_grid_cell(self, position):
        """Obtiene la celda de la rejilla para una posición dada"""
        return (int(position[0] // self.cell_size),
                int(position[1] // self.cell_size))
                
    def _update_spatial_grid(self):
        """Actualiza la rejilla espacial con las posiciones actuales de los enemigos"""
        self.spatial_grid.clear()
        for enemy in self.enemies:
            cell = self._get_grid_cell(enemy.rect.center)
            if cell not in self.spatial_grid:
                self.spatial_grid[cell] = []
            self.spatial_grid[cell].append(enemy)
            
    def _get_nearby_enemies(self, position, radius):
        """Obtiene enemigos cercanos a una posición usando la rejilla espacial"""
        nearby = set()
        cell_radius = int(radius // self.cell_size) + 1
        center_cell = self._get_grid_cell(position)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.spatial_grid:
                    nearby.update(self.spatial_grid[cell])
        
        return nearby

    def _is_in_view(self, pos, camera_pos):
        """Determina si una posición está dentro del área visible"""
        dx = pos[0] - camera_pos[0]
        dy = pos[1] - camera_pos[1]
        return (dx * dx + dy * dy) <= (self.settings.enemy_culling_distance * self.settings.enemy_culling_distance)

    def _get_random_enemy_type(self):
        """Selecciona un tipo de enemigo aleatorio basado en los pesos"""
        enemy_classes = list(self.enemy_types.values())
        weights = [enemy["weight"] for enemy in enemy_classes]
        return random.choices(enemy_classes, weights=weights, k=1)[0]["class"]

    def spawn_enemy(self):
        """Genera un nuevo enemigo en una posición aleatoria alrededor del jugador"""
        if len(self.enemies) >= self.settings.max_enemies:
            return

        angle = random.uniform(0, 2 * math.pi)
        distance = 300
        spawn_x = self.player.rect.x + math.cos(angle) * distance
        spawn_y = self.player.rect.y + math.sin(angle) * distance

        # Mantener dentro de los límites del mapa
        spawn_x = max(0, min(spawn_x, 
            self.settings.map_width * self.settings.tile_size - self.settings.enemy_size[0]))
        spawn_y = max(0, min(spawn_y, 
            self.settings.map_height * self.settings.tile_size - self.settings.enemy_size[1]))

        enemy_class = self._get_random_enemy_type()
        enemy = enemy_class(self.settings, (spawn_x, spawn_y), self.animation_manager, self, self.game)
        
        # Aplicar escalado de estadísticas
        enemy.health *= self.health_scale
        enemy.damage *= self.damage_scale
        
        self.enemies.append(enemy)

    def update(self, tilemap):
        if self.game.paused:
            return
        
        # Actualizar temporizadores y factores de dificultad
        self.time_elapsed += self.game.delta_time
        self.spawn_timer += self.game.delta_time
        
        # Calcular factores de dificultad
        self.difficulty_multiplier = 1.0 + (self.time_elapsed * 0.005)
        self.spawn_rate = self.settings.enemy_spawn_rate * self.difficulty_multiplier * self.multiplicadorRatioSpawn
        self.health_scale = 1.0 + (self.time_elapsed * 0.004)  # Incremento más lento que el spawn rate
        self.damage_scale = 1.0 + (self.time_elapsed * 0.002)  # Incremento aún más lento
        
        # Actualizar información de debug
        self.debug_info.update({
            "difficulty": self.difficulty_multiplier,
            "spawn_rate": self.spawn_rate,
            "health_multiplier": self.health_scale,
            "damage_multiplier": self.damage_scale
        })

        # Generar nuevos enemigos
        if self.spawn_timer >= 1.0 / self.spawn_rate:
            self.spawn_enemy()
            self.spawn_timer = 0

        # Actualizar rejilla espacial
        self._update_spatial_grid()

        # Actualizar enemigos
        for enemy in self.enemies[:]:
            if self._is_in_view(enemy.rect.center, (self.player.rect.centerx, self.player.rect.centery)):
                enemy.update(tilemap, self.player.rect.center)
                
                # Comprobar colisiones con otros enemigos
                nearby_enemies = self._get_nearby_enemies(enemy.rect.center, enemy.collision_radius * 2)
                for other_enemy in nearby_enemies:
                    if enemy != other_enemy and enemy.check_collision_with_enemy(other_enemy):
                        enemy.resolve_collision(other_enemy)

                # Comprobar colisión con el jugador
                if enemy.hitbox.colliderect(self.player.hitbox):
                    self.player.health -= enemy.damage * self.game.delta_time
                    push_dir = pygame.Vector2(enemy.rect.center) - pygame.Vector2(self.player.rect.center)
                    if push_dir.length() > 0:
                        push_dir = push_dir.normalize() * 5
                        enemy.move(enemy.rect.x + push_dir.x, enemy.rect.y + push_dir.y)

            # Eliminar enemigos muertos
            if enemy.health <= 0:
                self.remove_enemy(enemy)

        # Actualizar proyectiles
        for projectile in self.projectiles[:]:
            if projectile.update(self.player, self):
                self.projectiles.remove(projectile)

    def remove_enemy(self, enemy):
        """Elimina un enemigo y genera un ítem en su posición"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            self.drop_item(enemy.rect.center)

    def drop_item(self, position):
        """Genera un ítem aleatorio en la posición dada"""
        if random.random() < 0.99:
            item = Gem(self.settings, self.animation_manager, position,self.game)
        else:
            item = Tuna(self.settings, self.animation_manager, position,self.game)
        self.items.append(item)

    def add_projectile(self, projectile):
        """Añade un nuevo proyectil a la lista de proyectiles"""
        self.projectiles.append(projectile)

    def draw(self, screen, camera_x, camera_y):
        """Dibuja todos los enemigos y proyectiles visibles"""
        # Dibujar enemigos
        for enemy in self.enemies:
            if self._is_in_view(enemy.rect.center, (camera_x, camera_y)):
                enemy.draw(screen, camera_x, camera_y)
        
        # Dibujar proyectiles
        for projectile in self.projectiles:
            if self._is_in_view(projectile.rect.center, (camera_x, camera_y)):
                projectile.draw(screen, camera_x, camera_y)