from src.managers.animation_manager import AnimatedSprite

class GameObject(AnimatedSprite):
    def __init__(self, animation_manager, animation_name, position, size,game, update_frequency=0.1,):
        """
        Constructor base para todos los objetos del juego que requieren animación.
        Hereda de AnimatedSprite para manejar las animaciones.

        Parámetros:
        - animation_manager: Gestor de animaciones del juego
        - animation_name: Nombre de la animación inicial
        - position: Tupla (x, y) con la posición inicial del objeto
        - size: Tupla (width, height) con el tamaño del objeto
        - game: Referencia al objeto principal del juego
        - update_frequency: Frecuencia de actualización de la animación (por defecto 0.1)

        Inicializa:
        - Sistema de animaciones
        - Rectángulo de colisión
        - Referencias al juego y configuraciones
        """
        super().__init__(animation_manager, animation_name, position, size,game, update_frequency)