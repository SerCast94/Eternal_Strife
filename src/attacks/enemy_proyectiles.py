import pygame
from src.entities.sprite_object import SpriteObject

class EnemyProjectile(SpriteObject):
    def __init__(self, settings, animation_manager, position, target_position,game, damage=10, speed=100):
        """
        Constructor de la clase EnemyProjectile que inicializa un proyectil enemigo.
        Parámetros:
        - settings: Configuraciones generales del juego
        - animation_manager: Gestor de animaciones para obtener la imagen del proyectil
        - position: Posición inicial del proyectil (x, y)
        - target_position: Posición objetivo hacia donde se dirige el proyectil
        - game: Referencia al objeto principal del juego
        - damage: Cantidad de daño que inflige el proyectil (por defecto 10)
        - speed: Velocidad de movimiento del proyectil (por defecto 100)
        """
        image = animation_manager.get_animation('enemy_projectile_idle')[0][0]
        super().__init__(image, position, (16, 16), settings)  # Asegúrate de que el tamaño sea correcto
        self.settings = settings
        self.game = game
        self.target_position = pygame.Vector2(target_position)
        self.velocity = self.calculate_velocity(speed)
        self.damage = damage

    def calculate_velocity(self, speed):
        """
        Calcula el vector de velocidad del proyectil enemigo.
        Parámetros:
        - speed: Velocidad escalar del proyectil
        Retorna:
        - Vector normalizado multiplicado por la velocidad que indica la dirección y magnitud del movimiento
        Si la dirección es cero, retorna un vector nulo
        """
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
        """
        Actualiza la posición y estado del proyectil enemigo en cada frame.
        Verifica la colisión con el jugador y aplica el daño correspondiente.
        Parámetros:
        - player: Objeto jugador para detectar colisiones
        Retorna:
        - True si el proyectil colisiona con el jugador y debe ser destruido
        - False si el proyectil debe continuar su trayectoria
        """
        self.rect.center += self.velocity * self.game.delta_time

        # Verificar colisión con el jugador
        if self.rect.colliderect(player.rect):
            player.health -= self.damage
            return True  # El proyectil se destruye al impactar

        return False

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)
        """
        Dibuja el proyectil enemigo en la pantalla considerando la posición de la cámara.
        Parámetros:
        - screen: Superficie de pygame donde dibujar
        - camera_x: Posición X de la cámara
        - camera_y: Posición Y de la cámara
        """

    def is_off_screen(self):
        """
        Verifica si el proyectil enemigo está fuera de los límites del mapa.
        Retorna:
        - True si el proyectil está fuera de los límites del mapa definidos por settings
        - False si el proyectil está dentro de los límites del mapa
        """
        return (self.rect.centerx < 0 or self.rect.centerx > self.settings.map_width * self.settings.tile_size or
                self.rect.centery < 0 or self.rect.centery > self.settings.map_height * self.settings.tile_size)