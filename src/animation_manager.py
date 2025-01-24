import pygame
import os

class AnimationManager:
    def __init__(self, settings):
        self.settings = settings
        self.animations = self.load_animations(settings.animation_configs)
        self.cache = {}  # Caché para almacenar frames de animación

    def load_animations(self, config):
        animations = {}
        for name, anim_data in config.items():
            spritesheet = pygame.image.load(os.path.join(self.settings.base_path, anim_data['spritesheet'])).convert_alpha()
            frames = []
            for frame_data in anim_data['frames']:
                frame_index = frame_data['index']
                frame_duration = frame_data['duration']
                frame_x = (frame_index % (spritesheet.get_width() // anim_data['frame_width'])) * anim_data['frame_width']
                frame_y = (frame_index // (spritesheet.get_width() // anim_data['frame_width'])) * anim_data['frame_height']
                frame_image = spritesheet.subsurface(pygame.Rect(frame_x, frame_y, anim_data['frame_width'], anim_data['frame_height']))
                frames.append((frame_image, frame_duration))
            animations[name] = frames
        return animations

    def get_animation(self, name):
        if name in self.cache:
            return self.cache[name]
        animation = self.animations.get(name, [])
        self.cache[name] = animation
        return animation

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, animation_manager, animation_name, position, size, update_frequency=0.1):
        super().__init__()
        self.animation_manager = animation_manager
        self.animation_name = animation_name
        self.frames = self.animation_manager.get_animation(animation_name)
        self.current_frame = 0
        self.image = self.frames[self.current_frame][0]
        self.rect = self.image.get_rect(center=position)
        self.hitbox = pygame.Rect(0, 0, size[0], size[1])
        self.hitbox.center = self.rect.center
        self.time_accumulator = 0
        self.update_frequency = update_frequency  # Frecuencia de actualización de la animación

    def change_animation(self, animation_name):
        if self.animation_name != animation_name:
            self.animation_name = animation_name
            self.frames = self.animation_manager.get_animation(animation_name)
            self.current_frame = 0
            self.time_accumulator = 0
            self.image = self.frames[self.current_frame][0]

    def scale_sprite(self, scale):
        if scale != 1:
            self.frames = [
                (pygame.transform.scale(
                    frame[0], 
                    (int(frame[0].get_width() * scale), 
                     int(frame[0].get_height() * scale))
                ), frame[1])
                for frame in self.frames
            ]
            self.image = self.frames[self.current_frame][0]
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
            self.hitbox.center = self.rect.center
        
    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.hitbox.center = self.rect.center
        
    def update(self, delta_time):
        self.time_accumulator += delta_time
        if self.time_accumulator >= self.update_frequency:
            self.time_accumulator -= self.update_frequency
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame][0]