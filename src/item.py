import pygame
from sprite_object import SpriteObject

class Item(SpriteObject):
    def __init__(self, settings, animation_manager, animation_name, position, size):
        image = animation_manager.get_animation(animation_name)[0][0]
        super().__init__(image, position, size, settings)
        self.settings = settings

class Gem(Item):
    def __init__(self, settings, animation_manager, position):
        super().__init__(settings, animation_manager, 'gem_idle', position, (10, 10))

class Tuna(Item):
    def __init__(self, settings, animation_manager, position):
        super().__init__(settings, animation_manager, 'tuna_idle', position, (10, 10))