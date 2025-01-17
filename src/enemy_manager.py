import pygame
import random
import math
#enemy manager
class EnemyManager:
    def __init__(self, settings, player):
        self.settings = settings
        self.player = player
        self.enemies = []
        self.spawn_timer = 0
        self.time_elapsed = 0  # Variable para rastrear el tiempo transcurrido

    def spawn_enemy(self):
        # Calcular posición de spawn relativa al jugador
        angle = random.uniform(0, 2 * math.pi)
        distance = 800  # Distancia de spawn
        spawn_x = self.player.position.x + math.cos(angle) * distance
        spawn_y = self.player.position.y + math.sin(angle) * distance

        # Asegurar que el spawn está dentro del mapa
        spawn_x = max(0, min(spawn_x,
            self.settings.map_width * self.settings.tile_size - self.settings.enemy_size[0]))
        spawn_y = max(0, min(spawn_y,
            self.settings.map_height * self.settings.tile_size - self.settings.enemy_size[1]))

        self.enemies.append(Enemy(self.settings, (spawn_x, spawn_y)))

    def update(self, delta_time, tilemap):
        self.time_elapsed += delta_time  # Actualizar el tiempo transcurrido
        self.spawn_timer += delta_time

        # Ajustar la tasa de aparición de enemigos en función del tiempo transcurrido
        spawn_rate = max(0.1, self.settings.enemy_spawn_rate - self.time_elapsed * 0.01)

        if self.spawn_timer >= 1.0 / spawn_rate:
            self.spawn_enemy()
            self.spawn_timer = 0

        for enemy in self.enemies[:]:
            direction = pygame.Vector2(self.player.position - enemy.position)
            if direction.length() > 0:
                direction = direction.normalize()
            
            # Guardar posición anterior
            old_position = enemy.position.copy()
            
            # Intentar mover al enemigo en la dirección del jugador
            enemy.position += direction * self.settings.enemy_speed * delta_time
            enemy.rect.x = enemy.position.x
            enemy.rect.y = enemy.position.y
            
            # Comprobar colisiones con el mapa
            if tilemap.check_collision(enemy.rect):
                enemy.position = old_position
                enemy.rect.x = enemy.position.x
                enemy.rect.y = enemy.position.y
                direction = self.avoid_collisions(enemy, direction, tilemap)
                enemy.position += direction * self.settings.enemy_speed * delta_time
                enemy.rect.x = enemy.position.x
                enemy.rect.y = enemy.position.y
            
            # Comprobar distancia mínima con otros enemigos
            for other_enemy in self.enemies:
                if other_enemy != enemy:
                    distance = enemy.position.distance_to(other_enemy.position)
                    min_distance = self.settings.enemy_size[0]  # Distancia mínima entre enemigos
                    if distance < min_distance:
                        # Ajustar posiciones para mantener la distancia mínima
                        overlap = min_distance - distance
                        direction = (enemy.position - other_enemy.position).normalize()
                        enemy.position += direction * (overlap / 2)
                        other_enemy.position -= direction * (overlap / 2)
                        enemy.rect.x = enemy.position.x
                        enemy.rect.y = enemy.position.y
                        other_enemy.rect.x = other_enemy.position.x
                        other_enemy.rect.y = other_enemy.position.y
            
            # Comprobar colisión con el jugador
            if enemy.rect.colliderect(self.player.rect):
                self.player.health -= 10
                self.enemies.remove(enemy)
                continue

    def avoid_collisions(self, enemy, direction, tilemap):
        # Detectar colisiones y ajustar la dirección
        directions = [
            pygame.Vector2(-direction.y, direction.x),  # Girar 90 grados
            pygame.Vector2(direction.y, -direction.x),  # Girar 90 grados en la otra dirección
            pygame.Vector2(-direction.x, -direction.y)  # Girar 180 grados
        ]
        for new_direction in directions:
            future_position = enemy.position + new_direction * self.settings.enemy_speed
            enemy.rect.x = future_position.x
            enemy.rect.y = future_position.y
            if not tilemap.check_collision(enemy.rect):
                return new_direction
        return direction

    def check_collision(self, position, tilemap):
        # Implementar la lógica de detección de colisiones
        tile_x = int(position.x // self.settings.tile_size)
        tile_y = int(position.y // self.settings.tile_size)
        if tilemap.check_collision(pygame.Rect(tile_x * self.settings.tile_size, tile_y * self.settings.tile_size, self.settings.tile_size, self.settings.tile_size)):
            return True
        return False

    def draw(self, screen, camera_x, camera_y):
        for enemy in self.enemies:
            pygame.draw.rect(screen, (255, 0, 0),
                pygame.Rect(
                    enemy.position.x - camera_x,
                    enemy.position.y - camera_y,
                    self.settings.enemy_size[0],
                    self.settings.enemy_size[1]
                )
            )

class Enemy:
    def __init__(self, settings, position):
        self.settings = settings
        self.position = pygame.Vector2(position)
        self.rect = pygame.Rect(
            position[0],
            position[1],
            settings.enemy_size[0],
            settings.enemy_size[1]
        )
        self.speed = settings.enemy_speed