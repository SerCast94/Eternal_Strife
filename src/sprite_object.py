import pygame

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, image, position, size, settings, scale=1.0):
        super().__init__()
        self.settings = settings
        self.image = image
        self.image = pygame.transform.scale(self.image, (int(size[0] * scale), int(size[1] * scale)))
        self.rect = self.image.get_rect(center=position)
        self.hitbox = pygame.Rect(0, 0, size[0], size[1])
        self.hitbox.center = self.rect.center

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.hitbox.center = self.rect.center

    def draw(self, screen, camera_x, camera_y):
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.width * self.settings.zoom), int(self.rect.height * self.settings.zoom)))
        screen.blit(scaled_image, (self.rect.x * self.settings.zoom - camera_x * self.settings.zoom, self.rect.y * self.settings.zoom - camera_y * self.settings.zoom))