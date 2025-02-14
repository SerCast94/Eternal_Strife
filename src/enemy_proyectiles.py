import pygame
from sprite_object import SpriteObject

class EnemyProjectile(SpriteObject):
    def __init__(self, settings, animation_manager, position, target_position,game, damage=10, speed=100):
        image = animation_manager.get_animation('enemy_projectile_idle')[0][0]
        super().__init__(image, position, (16, 16), settings)  # Asegúrate de que el tamaño sea correcto
        self.settings = settings
        self.game = game
        self.target_position = pygame.Vector2(target_position)
        self.velocity = self.calculate_velocity(speed)
        self.damage = damage

    def calculate_velocity(self, speed):
        # Convertir las posiciones a vectores si no lo están ya
        start_pos = pygame.Vector2(self.rect.center)
        target_pos = pygame.Vector2(self.target_position)
        
        # Calcular el vector dirección
        direction = target_pos - start_pos
        
        # Normalizar solo si la dirección no es cero
        if direction.length() > 0:
            direction = direction.normalize()
            return direction * speed
        return pygame.Vector2(0, 0)

    def update(self, player):
        self.rect.center += self.velocity * self.game.delta_time

        # Verificar colisión con el jugador
        if self.rect.colliderect(player.rect):
            player.health -= self.damage
            return True  # El proyectil se destruye al impactar

        return False

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)

    def is_off_screen(self):
        return (self.rect.centerx < 0 or self.rect.centerx > self.settings.map_width * self.settings.tile_size or
                self.rect.centery < 0 or self.rect.centery > self.settings.map_height * self.settings.tile_size)