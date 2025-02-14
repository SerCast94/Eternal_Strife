import pygame
from sprite_object import SpriteObject
import game
from animation_manager import AnimatedSprite

class Projectile(AnimatedSprite):
    def __init__(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name, game):
        size = (32, 32) if target_type == 'enemy' else (16, 16)
        
        # Initialize AnimatedSprite
        super().__init__(
            animation_manager,
            animation_name,
            position,
            size,
            settings,
            game,
            0.05  # Animation update frequency
        )
        
        self.target_position = pygame.Vector2(target_position)
        self.velocity = self.calculate_velocity(speed)
        self.damage = damage
        self.target_type = target_type
        self.puntoDeIOrigen = position
        

    def calculate_velocity(self, speed):
        direction = pygame.Vector2(
            self.target_position.x - self.rect.centerx,
            self.target_position.y - self.rect.centery
        )
        
        if direction.length_squared() > 0:
            direction = direction.normalize()
            return direction * speed
        return pygame.Vector2(1, 0) * speed


    def update(self, player, enemy_manager):
        # Update position
        self.rect.center += self.velocity * self.game.delta_time

        # Update animation
        super().update()

        # Check collisions
        if self.target_type == 'player':
            if self.rect.colliderect(player.rect):
                player.health -= self.damage
                return True
        elif self.target_type == 'enemy':
            for enemy in enemy_manager.enemies:
                if self.rect.colliderect(enemy.rect):
                    if enemy.take_damage(self.damage):
                        enemy_manager.remove_enemy(enemy)
                    return True

        # Check max distance
        dx = self.rect.centerx - self.puntoDeIOrigen[0]
        dy = self.rect.centery - self.puntoDeIOrigen[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        return distance > 1000

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)

    def is_off_screen(self):
        return (self.rect.centerx < 0 or self.rect.centerx > self.settings.map_width * self.settings.tile_size or
                self.rect.centery < 0 or self.rect.centery > self.settings.map_height * self.settings.tile_size)
    
    def reset(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name):
        """Reset projectile for reuse from pool"""
        self.settings = settings
        self.animation_manager = animation_manager
        self.animation_name = animation_name
        self.current_animation = animation_manager.get_animation(animation_name)
        self.rect.center = position
        self.target_position = pygame.Vector2(target_position)
        self.velocity = self.calculate_velocity(speed)
        self.damage = damage
        self.target_type = target_type
        self.puntoDeIOrigen = position
        self.current_frame = 0
        self.animation_time = 0