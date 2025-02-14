import pygame
import os
from sprite_object import SpriteObject

class AnimationManager:
    def __init__(self, settings, game):
        self.settings = settings
        self.game = game  # Referencia al juego
        self.animations = self.load_animations(settings.animation_configs)
        self.cache = {}  # Caché para almacenar frames de animación
        self.global_time = 0  # Tiempo global para sincronizar animaciones
        self.paused = False  # Add pause state

    def load_animations(self, config):
        animations = {}
        for name, anim_data in config.items():
            spritesheet = pygame.image.load(anim_data['spritesheet']).convert_alpha()
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

    def update(self):
        if not self.paused:  # Only update time if not paused
            self.global_time += self.game.delta_time

    def get_current_frame(self, animation_name):
        frames = self.get_animation(animation_name)
        if not frames:
            return None
        total_duration = sum(frame[1] for frame in frames)
        current_time = self.global_time % total_duration
        elapsed_time = 0
        for frame, duration in frames:
            elapsed_time += duration
            if elapsed_time >= current_time:
                return frame
        return frames[0][0]  # Default to the first frame if something goes wrong
    
    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

class AnimatedSprite(SpriteObject):
    def __init__(self, animation_manager, animation_name, position, size, settings,game, update_frequency=0.1):
        self.animation_manager = animation_manager
        self.game = game  # Referencia al juego
        self.animation_name = animation_name
        self.frames = self.animation_manager.get_animation(animation_name)
        self.current_frame = 0
        self.time_accumulator = 0
        self.paused = False  # Add pause state
        self.update_frequency = update_frequency  # Frecuencia de actualización de la animación
        super().__init__(self.frames[self.current_frame][0], position, size, settings,self.game)

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
        
    def update(self):
        if self.paused:  # Don't update animation if paused
            return
        self.time_accumulator += self.game.delta_time
        if self.time_accumulator >= self.update_frequency:
            self.time_accumulator -= self.update_frequency
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame][0]
            
    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False