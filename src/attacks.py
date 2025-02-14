import pygame
from abc import ABC, abstractmethod
from projectile import Projectile
import game

class BaseAttack(ABC):
    def __init__(self, settings, owner, game):
        self.settings = settings
        self.game = game
        self.owner = owner
        self.cooldown = 0
        self.last_attack_time = 0

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, screen, camera_x, camera_y):
        pass

    def can_attack(self):
        return pygame.time.get_ticks() - self.last_attack_time >= self.cooldown

    def attack(self):
        if self.can_attack():
            self.last_attack_time = pygame.time.get_ticks()
            self.perform_attack()

    @abstractmethod
    def perform_attack(self):
        pass

class FireballAttack(BaseAttack):
    def __init__(self, settings, owner, enemy_manager,game):
        super().__init__(settings, owner, game)
        self.cooldown = 1000  # 1 segundo de cooldown
        self.damage = 20
        self.game = game
        self.projectiles = []
        self.enemy_manager = enemy_manager  # Referencia al EnemyManager
        self.detection_radius = 170

    def update(self):
        for projectile in self.projectiles[:]:
            if projectile.update(self.owner, self.enemy_manager):
                self.projectiles.remove(projectile)

    def draw(self, screen, camera_x, camera_y):
        for projectile in self.projectiles:
            projectile.draw(screen, camera_x, camera_y)

    def perform_attack(self):
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
                'fireball_idle',
                self.game
            )
            self.projectiles.append(projectile)

    def find_closest_enemy(self):
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