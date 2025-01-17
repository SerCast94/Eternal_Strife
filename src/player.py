import pygame

class Player:

    def __init__(self, x, y,speed, sprite_path, base_size, scale=1.0):
        """
        Inicializa al jugador.
        :param x: Posición X inicial (en tiles).
        :param y: Posición Y inicial (en tiles).
        :param sprite_path: Ruta al sprite del jugador.
        :param base_size: Tamaño base del sprite.
        :param scale: Factor de escala para el jugador.
        """
        self.x = x
        self.y = y
        self.base_size = base_size
        self.scale = scale
        self.speed = speed

        # Cargar y escalar el sprite
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        self.update_sprite()

    def update_sprite(self):
        """Actualiza el tamaño del sprite según el factor de escala."""
        self.scaled_size = int(self.base_size * self.scale)
        self.sprite = pygame.transform.scale(self.sprite, (self.scaled_size, self.scaled_size))

    def draw(self, screen, screen_width, screen_height):
        """
        Dibuja al jugador en el centro de la pantalla.
        :param screen: Superficie de pygame.
        :param screen_width: Ancho de la pantalla.
        :param screen_height: Alto de la pantalla.
        """
        player_x = (screen_width // 2) - (self.scaled_size // 2)
        player_y = (screen_height // 2) - (self.scaled_size // 2)
        screen.blit(self.sprite, (player_x, player_y))

    def move(self, keys, dt):
        """
        Mueve al jugador según la entrada del usuario.
        :param keys: Teclas presionadas.
        :param dt: Delta tiempo para movimiento suave.
        """
        currenty = self.y
        currentx = self.x
        if keys[pygame.K_w]:  # Arriba
            currenty -= self.speed * dt
        if keys[pygame.K_s]:  # Abajo
            currenty += self.speed * dt
        if keys[pygame.K_a]:  # Izquierda
            currentx -= self.speed * dt
        if keys[pygame.K_d]:  # Derecha
            currentx += self.speed * dt
        
        self.y = currenty
        self.x = currentx
