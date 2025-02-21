import pygame

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, image, position, size, settings,game, scale=1.0):
        """
        Constructor base para todos los objetos sprite del juego.
        Hereda de pygame.sprite.Sprite y configura la representación visual básica.
        
        Parámetros:
        - image: Superficie de pygame que contiene la imagen del sprite
        - position: Tupla (x, y) con la posición inicial del sprite
        - size: Tupla (width, height) con el tamaño del sprite
        - settings: Configuraciones generales del juego
        - game: Referencia al objeto principal del juego
        - scale: Factor de escala para el sprite (por defecto 1.0)
        
        Inicializa:
        - Imagen escalada según el factor de escala
        - Rectángulo de sprite y hitbox para colisiones
        """
        super().__init__()
        self.settings = settings
        self.game = game
        self.image = image
        self.image = pygame.transform.scale(self.image, (int(size[0] * scale), int(size[1] * scale)))
        self.rect = self.image.get_rect(center=position)
        self.hitbox = pygame.Rect(0, 0, size[0], size[1])
        self.hitbox.center = self.rect.center

    def move(self, x, y):
        """
        Actualiza la posición del sprite y su hitbox.
        
        Parámetros:
        - x: Nueva posición en el eje X
        - y: Nueva posición en el eje Y
        
        Mantiene sincronizados el rectángulo del sprite y su hitbox
        """
        self.rect.x = x
        self.rect.y = y
        self.hitbox.center = self.rect.center

    def draw(self, screen, camera_x, camera_y):
        """
        Dibuja el sprite en la pantalla considerando la posición de la cámara y el zoom.
        
        Parámetros:
        - screen: Superficie de pygame donde dibujar
        - camera_x: Posición X de la cámara
        - camera_y: Posición Y de la cámara
        
        Aplica:
        - Escalado según el factor de zoom actual
        - Desplazamiento según la posición de la cámara
        """
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * self.settings.zoom), int(self.rect.height * self.settings.zoom)))
        screen.blit(scaled_image, (self.rect.x * self.settings.zoom - camera_x * self.settings.zoom, self.rect.y * self.settings.zoom - camera_y * self.settings.zoom))