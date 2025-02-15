from managers.animation_manager import AnimatedSprite
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
        self.debug_font = pygame.font.Font(None, 20)

        # Cache valores calculados frecuentemente
        self._collision_rect = pygame.Rect(0, 0, self.collision_radius*2, self.collision_radius*2)
        self._last_collision_check = 0
        self._collision_cache = {}
        
    def check_collision_with_enemy(self, other_enemy):
        # Usar distancia al cuadrado para evitar sqrt
        dx = self.rect.centerx - other_enemy.rect.centerx
        dy = self.rect.centery - other_enemy.rect.centery
        dist_squared = dx * dx + dy * dy
        return dist_squared < (self.collision_radius * 2) ** 2

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
        """Dibuja el enemigo y su información de debug si está activado"""
        super().draw(screen, camera_x, camera_y)
        
        # Si el juego está en modo debug, mostrar vida y daño
        if self.game.debug_mode:
            # Crear fuente pequeña para el texto
            
            # Renderizar texto de vida y daño
            health_text = self.debug_font.render(f"HP:{self.health:.0f}", True, (255, 0, 0))
            damage_text = self.debug_font.render(f"DMG:{self.damage:.1f}", True, (255, 165, 0))
            
            # Calcular posiciones ajustadas a la cámara y el zoom
            health_pos = (
                (self.rect.centerx - health_text.get_width()/2) * self.settings.zoom - camera_x * self.settings.zoom,
                (self.rect.top - 20) * self.settings.zoom - camera_y * self.settings.zoom
            )
            damage_pos = (
                (self.rect.centerx - damage_text.get_width()/2) * self.settings.zoom - camera_x * self.settings.zoom,
                (self.rect.top - 5) * self.settings.zoom - camera_y * self.settings.zoom
            )
            
            # Dibujar textos
            screen.blit(health_text, health_pos)
            screen.blit(damage_text, damage_pos)