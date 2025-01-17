import pygame

class Player:
    def __init__(self, settings):
        self.settings = settings
        self.position = pygame.Vector2(
            settings.map_width * settings.tile_size // 2,
            settings.map_height * settings.tile_size // 2
        )
        self.velocity = pygame.Vector2()
        self.health = settings.player_health
        self.rect = pygame.Rect(
            self.position.x,
            self.position.y,
            settings.player_size[0],
            settings.player_size[1]
        )

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.velocity.y = -1
            elif event.key == pygame.K_s:
                self.velocity.y = 1
            elif event.key == pygame.K_a:
                self.velocity.x = -1
            elif event.key == pygame.K_d:
                self.velocity.x = 1
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s):
                self.velocity.y = 0
            elif event.key in (pygame.K_a, pygame.K_d):
                self.velocity.x = 0

    def update(self, delta_time, tilemap):
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize()

        # Guardar posición anterior
        old_position = self.position.copy()

        # Actualizar posición
        self.position += self.velocity * self.settings.player_speed * delta_time
        self.rect.x = self.position.x
        self.rect.y = self.position.y

        # Comprobar colisiones
        if tilemap.check_collision(self.rect):
            self.position = old_position
            self.rect.x = self.position.x
            self.rect.y = self.position.y

        # Mantener al jugador dentro de los límites del mapa
        self.position.x = max(0, min(self.position.x,
            self.settings.map_width * self.settings.tile_size - self.settings.player_size[0]))
        self.position.y = max(0, min(self.position.y,
            self.settings.map_height * self.settings.tile_size - self.settings.player_size[1]))

    def draw(self, screen, camera_x, camera_y):
        pygame.draw.rect(screen, (0, 255, 0),
            pygame.Rect(
                self.position.x - camera_x,
                self.position.y - camera_y,
                self.settings.player_size[0],
                self.settings.player_size[1]
            )
        )