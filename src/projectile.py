import pygame
from sprite_object import SpriteObject
import game

class Projectile(SpriteObject):
    def __init__(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name,game):
        image = animation_manager.get_animation(animation_name)[0][0]
        super().__init__(image, position, (16, 16), settings, game)
        self.settings = settings
        self.target_position = pygame.Vector2(target_position)
        self.velocity = self.calculate_velocity(speed)
        self.damage = damage
        self.target_type = target_type  # 'player' o 'enemy'
        self.animation_name = animation_name
        self.animation_manager = animation_manager
        self.frames = self.animation_manager.get_animation(animation_name)
        self.current_frame = 0
        self.time_accumulator = 0
        self.update_frequency = 0.1  # Frecuencia de actualización de la animación
        self.puntoDeIOrigen = position

    def calculate_velocity(self, speed):
        # Obtener el vector dirección desde la posición inicial hasta el objetivo
        direction = pygame.Vector2(
            self.target_position.x - self.rect.centerx,
            self.target_position.y - self.rect.centery
        )
        
        # Normalizar el vector solo si tiene longitud
        if direction.length_squared() > 0:  # Usar length_squared es más eficiente que length()
            direction = direction.normalize()
            return direction * speed
        else:
            # En caso de que el objetivo esté en la misma posición, disparar hacia la derecha
            return pygame.Vector2(1, 0) * speed

    def update(self, player, enemy_manager):
        self.rect.center += self.velocity * self.game.delta_time

        if self.target_type == 'player':
            # Verificar colisión con el jugador
            if self.rect.colliderect(player.rect):
                player.health -= self.damage
                return True  # El proyectil se destruye al impactar
        elif self.target_type == 'enemy':
            # Verificar colisión con enemigos
            for enemy in enemy_manager.enemies:
                if self.rect.colliderect(enemy.rect):
                    if enemy.take_damage(self.damage):
                        enemy_manager.remove_enemy(enemy)
                    return True  # El proyectil se destruye al impactar
        
        # Replace the distance_to check with a manual distance calculation
        dx = self.rect.centerx - self.puntoDeIOrigen[0]
        dy = self.rect.centery - self.puntoDeIOrigen[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance > 1000:
            return True  # Projectile should be destroyed

        # Actualizar animación
        self.time_accumulator += self.game.delta_time
        if self.time_accumulator >= self.update_frequency:
            self.time_accumulator -= self.update_frequency
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame][0]

        return False

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)

    def is_off_screen(self):
        return (self.rect.centerx < 0 or self.rect.centerx > self.settings.map_width * self.settings.tile_size or
                self.rect.centery < 0 or self.rect.centery > self.settings.map_height * self.settings.tile_size)
    
    def reset(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name):
        """Reset projectile for reuse from pool"""
        self.settings = settings
        self.animation_manager = animation_manager
        self.rect.center = position
        self.target_position = pygame.Vector2(target_position)
        self.velocity = self.calculate_velocity(speed)
        self.damage = damage
        self.target_type = target_type
        self.animation_name = animation_name
        self.frames = self.animation_manager.get_animation(animation_name)
        self.current_frame = 0
        self.time_accumulator = 0
        self.update_frequency = 0.1
        self.puntoDeIOrigen = position
        self.image = self.frames[self.current_frame][0]