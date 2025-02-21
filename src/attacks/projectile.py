import pygame
from entities.sprite_object import SpriteObject
import core.game as game
from managers.animation_manager import AnimatedSprite

class Projectile(AnimatedSprite):
    def __init__(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name, game):
        size = (32, 32) if target_type == 'enemy' else (16, 16)
        
        """
        Constructor de la clase Projectile que inicializa un proyectil en el juego.
        Parámetros:
        - settings: Configuraciones generales del juego
        - animation_manager: Gestor de animaciones del juego
        - position: Posición inicial del proyectil (x, y)
        - target_position: Posición objetivo hacia donde se dirige el proyectil
        - damage: Cantidad de daño que inflige el proyectil
        - speed: Velocidad de movimiento del proyectil
        - target_type: Tipo de objetivo ('enemy' o 'player')
        - animation_name: Nombre de la animación a utilizar
        - game: Referencia al objeto principal del juego
        """

        super().__init__(
            animation_manager,
            animation_name,
            position,
            size,
            settings,
            game,
            0.05  
        )
        
        self.target_position = pygame.Vector2(target_position)
        self.velocity = self.calculate_velocity(speed)
        self.damage = damage
        self.target_type = target_type
        self.puntoDeIOrigen = position
        

    def calculate_velocity(self, speed):
        """
        Calcula el vector de velocidad del proyectil basado en su velocidad y dirección.
        Parámetros:
        - speed: Velocidad escalar del proyectil
        Retorna:
        - Vector normalizado multiplicado por la velocidad que indica la dirección y magnitud del movimiento
        """
        direction = pygame.Vector2(
            self.target_position.x - self.rect.centerx,
            self.target_position.y - self.rect.centery
        )
        
        if direction.length_squared() > 0:
            direction = direction.normalize()
            return direction * speed
        return pygame.Vector2(1, 0) * speed


    def update(self, player, enemy_manager):
        """
        Actualiza la posición y estado del proyectil en cada frame.
        Gestiona las colisiones con jugadores o enemigos y aplica el daño correspondiente.
        Parámetros:
        - player: Objeto jugador para detectar colisiones
        - enemy_manager: Gestor de enemigos para detectar colisiones con enemigos
        Retorna:
        - True si el proyectil debe ser destruido (por colisión o distancia máxima)
        """
        self.rect.center += self.velocity * self.game.delta_time

        super().update()

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

        dx = self.rect.centerx - self.puntoDeIOrigen[0]
        dy = self.rect.centery - self.puntoDeIOrigen[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        return distance > 1000

    def draw(self, screen, camera_x, camera_y):
        """
        Dibuja el proyectil en la pantalla considerando la posición de la cámara.
        Parámetros:
        - screen: Superficie de pygame donde dibujar
        - camera_x: Posición X de la cámara
        - camera_y: Posición Y de la cámara
        """
        super().draw(screen, camera_x, camera_y)

    def is_off_screen(self):
        """
        Verifica si el proyectil está fuera de los límites del mapa.
        Retorna:
        - True si el proyectil está fuera de los límites del mapa
        """
        return (self.rect.centerx < 0 or self.rect.centerx > self.settings.map_width * self.settings.tile_size or
                self.rect.centery < 0 or self.rect.centery > self.settings.map_height * self.settings.tile_size)
    
    def reset(self, settings, animation_manager, position, target_position, damage, speed, target_type, animation_name):
        """
        Reinicia el estado del proyectil para su reutilización desde el pool de proyectiles.
        Parámetros:
        - settings: Nuevas configuraciones
        - animation_manager: Gestor de animaciones
        - position: Nueva posición inicial
        - target_position: Nueva posición objetivo
        - damage: Nuevo valor de daño
        - speed: Nueva velocidad
        - target_type: Nuevo tipo de objetivo
        - animation_name: Nuevo nombre de animación
        """
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