import pygame
from entities.sprite_object import SpriteObject

class Item(SpriteObject):
    def __init__(self, settings, animation_manager, animation_name, position, size,game):
        """
        Constructor base para todos los ítems del juego.
        Hereda de SpriteObject para las funcionalidades básicas de sprites.
        
        Parámetros:
        - settings: Configuraciones generales del juego
        - animation_manager: Gestor de animaciones
        - animation_name: Nombre de la animación del ítem
        - position: Tupla (x, y) con la posición inicial
        - size: Tupla (width, height) con el tamaño del ítem
        - game: Referencia al objeto principal del juego
        """
        image = animation_manager.get_animation(animation_name)[0][0]
        self.game = game
        super().__init__(image, position, size, settings,game)
        self.settings = settings

class Gem(Item):
    def __init__(self, settings, animation_manager, position,game):
        """
        Constructor para los ítems tipo Gema.
        Hereda de Item y usa la animación 'gem_idle'.
        
        Parámetros:
        - settings: Configuraciones generales del juego
        - animation_manager: Gestor de animaciones
        - position: Tupla (x, y) con la posición inicial
        - game: Referencia al objeto principal del juego
        
        Tamaño fijo: 10x10 píxeles
        Efecto: Otorga puntos y experiencia al jugador
        """
        super().__init__(settings, animation_manager, 'gem_idle', position, (10, 10),game)

class Tuna(Item):
    def __init__(self, settings, animation_manager, position,game):
        """
        Constructor para los ítems tipo Atún.
        Hereda de Item y usa la animación 'tuna_idle'.
        
        Parámetros:
        - settings: Configuraciones generales del juego
        - animation_manager: Gestor de animaciones
        - position: Tupla (x, y) con la posición inicial
        - game: Referencia al objeto principal del juego
        
        Tamaño fijo: 10x10 píxeles
        Efecto: Restaura salud al jugador (20% de la salud máxima)
        """
        super().__init__(settings, animation_manager, 'tuna_idle', position, (10, 10),game)