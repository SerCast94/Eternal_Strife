import pygame

class SpriteObject(pygame.sprite.Sprite):
    # Class-level sprite cache
    _sprite_cache = {}  # Mover esto fuera del __init__
    
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
        screen_x = (self.rect.x - camera_x) * self.settings.zoom
        screen_y = (self.rect.y - camera_y) * self.settings.zoom
        
        if (0 <= screen_x <= self.settings.screen_width and 
            0 <= screen_y <= self.settings.screen_height):
            scaled_image = self.get_cached_sprite(self.image, self.settings.zoom)
            screen.blit(scaled_image, (screen_x, screen_y))

    @classmethod
    def get_cached_sprite(cls, original_surface, scale):
        """Get a cached scaled sprite or create and cache a new one"""
        cache_key = (original_surface, scale)
        if cache_key not in cls._sprite_cache:
            scaled = pygame.transform.scale(
                original_surface, 
                (int(original_surface.get_width() * scale),
                 int(original_surface.get_height() * scale))
            )
            cls._sprite_cache[cache_key] = scaled
        return cls._sprite_cache[cache_key]