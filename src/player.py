import pygame
from animation_manager import AnimatedSprite

class Player(AnimatedSprite):
    def __init__(self, settings, animation_manager):
        initial_pos = (settings.map_width * settings.tile_size // 2, 
                      settings.map_height * settings.tile_size // 2)
        super().__init__(animation_manager, 'player_idle', initial_pos, settings.player_size)
        self.settings = settings
        self.velocity = pygame.Vector2()
        self.health = settings.player_health
        
        # Movement state
        self.moving = False
        self.direction = pygame.Vector2()
        
        # Current state
        self.state = "idle"
        
        self.animations = {
            "idle": "player_idle",
            "walk_left": "player_walk_left",
            "walk_right": "player_walk_right",
            "walk_up": "player_walk_up",
            "walk_down": "player_walk_down"
        }
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.velocity.y = -1
                self.change_animation(self.animations["walk_up"])
            elif event.key == pygame.K_s:
                self.velocity.y = 1
                self.change_animation(self.animations["walk_down"])
            elif event.key == pygame.K_a:
                self.velocity.x = -1
                self.change_animation(self.animations["walk_left"])
            elif event.key == pygame.K_d:
                self.velocity.x = 1
                self.change_animation(self.animations["walk_right"])
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s):
                self.velocity.y = 0
            elif event.key in (pygame.K_a, pygame.K_d):
                self.velocity.x = 0
            
            if self.velocity.length() == 0:
                self.change_animation(self.animations["idle"])
                
    def update(self, delta_time, tilemap):
        super().update(delta_time)
        
        # Update movement
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize()
            
        # Calculate new position    
        new_x = self.rect.x + self.velocity.x * self.settings.player_speed * delta_time
        new_y = self.rect.y + self.velocity.y * self.settings.player_speed * delta_time
        
        # Store old position
        old_position = self.rect.topleft
        
        # Try to move
        self.move(new_x, new_y)
        
        # Check collisions and bounds
        if tilemap.check_collision(self.hitbox):
            self.move(old_position[0], old_position[1])
        
        # Keep in bounds    
        new_x = max(0, min(self.rect.x,
            self.settings.map_width * self.settings.tile_size - self.settings.player_size[0]))
        new_y = max(0, min(self.rect.y,
            self.settings.map_height * self.settings.tile_size - self.settings.player_size[1]))
        self.move(new_x, new_y)

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))