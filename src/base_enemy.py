from animation_manager import AnimatedSprite
import pygame
from abc import ABC, abstractmethod

class BaseEnemy(AnimatedSprite):
    def __init__(self, settings, position, animation_manager, enemy_data, game):
        super().__init__(animation_manager, enemy_data['idle_animation'], position, enemy_data['size'], settings,game)
        self.settings = settings
        self.speed = enemy_data['speed']
        self.health = enemy_data['health']
        self.damage = enemy_data['damage']
        self.game = game
        self.scale_sprite(enemy_data['scale'])
        self.detection_radius = enemy_data['detection_radius']
        self.collision_radius = max(enemy_data['size'][0], enemy_data['size'][1]) * 0.4
        self.enemy_data = enemy_data  # Asegúrate de que enemy_data esté definido
        
    def check_collision_with_enemy(self, other_enemy):
        """Comprueba si hay colisión con otro enemigo usando círculos"""
        distance = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(other_enemy.rect.center))
        return distance < (self.collision_radius + other_enemy.collision_radius)

    def resolve_collision(self, other_enemy):
        """Resuelve la colisión entre dos enemigos empujándolos en direcciones opuestas"""
        direction = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(other_enemy.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
            push_strength = 1.0
            
            # Mover ambos enemigos en direcciones opuestas
            self.move(
                self.rect.x + direction.x * push_strength,
                self.rect.y + direction.y * push_strength
            )
            other_enemy.move(
                other_enemy.rect.x - direction.x * push_strength,
                other_enemy.rect.y - direction.y * push_strength
            )

    @abstractmethod
    def update_behavior(self, tilemap, player_pos):
        """Comportamiento específico de cada tipo de enemigo"""
        pass

    def update(self, tilemap, player_pos):
        if self.game.paused:
            return
        super().update()  # Llama al update de AnimatedSprite
        self.update_behavior(tilemap, player_pos)

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
        
    def draw(self, screen, camera_x, camera_y):
        """Dibuja el enemigo en la pantalla teniendo en cuenta la posición de la cámara"""
        super().draw(screen, camera_x, camera_y)