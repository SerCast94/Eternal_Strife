from animation_manager import AnimatedSprite

class GameObject(AnimatedSprite):
    def __init__(self, animation_manager, animation_name, position, size,game, update_frequency=0.1,):
        super().__init__(animation_manager, animation_name, position, size,game, update_frequency)