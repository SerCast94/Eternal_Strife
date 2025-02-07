import pygame
from sprite_object import SpriteObject

class Projectile(SpriteObject):
    def __init__(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name):
        image = animation_manager.get_animation(animation_name)[0][0]
        super().__init__(image, position, (16, 16), settings)
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

    def calculate_velocity(self, speed):
        direction = self.target_position - pygame.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
        return direction * speed

    def update(self, delta_time, player, enemy_manager):
        self.rect.center += self.velocity * delta_time

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

        # Actualizar animación
        self.time_accumulator += delta_time
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