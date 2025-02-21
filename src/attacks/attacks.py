import pygame
from abc import ABC, abstractmethod
from attacks.projectile import Projectile
import core.game as game

class BaseAttack(ABC):
    def __init__(self, settings, owner, game):
        """
        Constructor de la clase base para todos los ataques.
        Parámetros:
        - settings: Configuraciones generales del juego
        - owner: Propietario del ataque (jugador u otro personaje)
        - game: Referencia al objeto principal del juego
        """
        self.settings = settings
        self.game = game
        self.owner = owner
        self.cooldown = 0
        self.last_attack_time = 0

    @abstractmethod
    def update(self):
        """
        Método abstracto para actualizar el estado del ataque.
        Debe ser implementado por las clases hijas.
        """
        pass

    @abstractmethod
    def draw(self, screen, camera_x, camera_y):
        """
        Método abstracto para dibujar el ataque en pantalla.
        Debe ser implementado por las clases hijas.
        Parámetros:
        - screen: Superficie donde dibujar
        - camera_x: Posición X de la cámara
        - camera_y: Posición Y de la cámara
        """
        pass

    def can_attack(self):
        """
        Verifica si el ataque puede ser realizado basado en el tiempo de cooldown.
        Retorna:
        - True si ha pasado suficiente tiempo desde el último ataque
        - False si aún está en cooldown
        """
        return pygame.time.get_ticks() - self.last_attack_time >= self.cooldown

    def attack(self):
        """
        Ejecuta el ataque si está disponible.
        Actualiza el tiempo del último ataque y llama a perform_attack.
        """
        if self.can_attack():
            self.last_attack_time = pygame.time.get_ticks()
            self.perform_attack()

    @abstractmethod
    def perform_attack(self):
        """
        Método abstracto que define la lógica específica del ataque.
        Debe ser implementado por las clases hijas.
        """
        pass

class FireballAttack(BaseAttack):
    def __init__(self, settings, owner, enemy_manager,game):
        """
        Constructor del ataque de bola de fuego.
        Parámetros:
        - settings: Configuraciones generales del juego
        - owner: Propietario del ataque
        - enemy_manager: Gestor de enemigos del juego
        - game: Referencia al objeto principal del juego
        Inicializa el cooldown, daño y radio de detección
        """
        super().__init__(settings, owner, game)
        self.cooldown = 1000  # 1 segundo de cooldown
        self.damage = 20
        self.game = game
        self.projectiles = []
        self.enemy_manager = enemy_manager  # Referencia al EnemyManager
        self.detection_radius = 170
    def update(self):
        """
        Actualiza el estado de todos los proyectiles de bola de fuego.
        Elimina los proyectiles que hayan impactado o estén fuera de rango.
        """
        for projectile in self.projectiles[:]:
            if projectile.update(self.owner, self.enemy_manager):
                self.projectiles.remove(projectile)

    def draw(self, screen, camera_x, camera_y):
        """
        Dibuja todos los proyectiles de bola de fuego activos.
        Parámetros:
        - screen: Superficie donde dibujar
        - camera_x: Posición X de la cámara
        - camera_y: Posición Y de la cámara
        """
        for projectile in self.projectiles:
            projectile.draw(screen, camera_x, camera_y)

    def perform_attack(self):
        """
        Ejecuta el ataque de bola de fuego.
        Busca el enemigo más cercano y crea un proyectil dirigido hacia él.
        """
        closest_enemy = self.find_closest_enemy()
        if closest_enemy:
            start_pos = pygame.Vector2(self.owner.rect.center)
            target_pos = pygame.Vector2(closest_enemy.rect.center)
            
            projectile = Projectile(
                self.settings,
                self.owner.animation_manager,
                start_pos,
                target_pos,
                self.damage,
                300,
                'enemy',
                'fireball_idle',  # Use specific animation for projectile
                self.game
            )
            self.projectiles.append(projectile)

    def find_closest_enemy(self):
        """
        Encuentra el enemigo más cercano dentro del radio de detección.
        Retorna:
        - El enemigo más cercano si existe dentro del radio
        - None si no hay enemigos en rango
        """
        closest_enemy = None
        min_distance = float('inf')
        player_pos = pygame.Vector2(self.owner.rect.center)

        for enemy in self.enemy_manager.enemies:
            enemy_pos = pygame.Vector2(enemy.rect.center)
            distance = player_pos.distance_to(enemy_pos)
            if distance < min_distance and distance <= self.detection_radius:
                min_distance = distance
                closest_enemy = enemy

        return closest_enemy