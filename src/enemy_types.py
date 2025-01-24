from animation_manager import AnimatedSprite
import pygame
from base_enemy import BaseEnemy

class SlimeEnemy(BaseEnemy):
    def __init__(self, settings, position, animation_manager):
        enemy_data = {
            'idle_animation': 'slime_idle',
            'size': settings.enemy_size,
            'speed': settings.enemy_speed,
            'health': 100,
            'damage': 10,
            'scale': settings.enemy_scale,
            'detection_radius': settings.enemy_detection_radius
        }
        super().__init__(settings, position, animation_manager, enemy_data)
        self.avoid_force = pygame.Vector2()

    def update_behavior(self, delta_time, tilemap, player_pos):
        # Comportamiento básico del slime: perseguir al jugador y evitar obstáculos
        to_player = pygame.Vector2(player_pos) - pygame.Vector2(self.rect.center)
        if to_player.length() > 0:
            to_player = to_player.normalize()

        # Detectar obstáculos
        avoid_force = self._detect_obstacles(tilemap)
        
        # Combinar fuerzas
        steering = to_player + avoid_force
        if steering.length() > 0:
            steering = steering.normalize()
            
        # Actualizar posición
        new_x = self.rect.x + steering.x * self.speed * delta_time
        new_y = self.rect.y + steering.y * self.speed * delta_time
        self.move(new_x, new_y)

    def _detect_obstacles(self, tilemap):
        directions = [(1, 0), (1, 1), (0, 1), (-1, 1),
                     (-1, 0), (-1, -1), (0, -1), (1, -1)]
        avoid_force = pygame.Vector2()
        
        for direction in directions:
            ray_dir = pygame.Vector2(direction)
            ray_pos = pygame.Vector2(self.rect.center)
            
            for distance in range(0, self.detection_radius, 8):
                check_pos = ray_pos + ray_dir * distance
                check_rect = pygame.Rect(check_pos.x - 4, check_pos.y - 4, 8, 8)
                
                if tilemap.check_collision(check_rect):
                    avoid_force -= ray_dir * (self.detection_radius - distance)
                    break
                    
        return avoid_force.normalize() * 0.5 if avoid_force.length() > 0 else avoid_force

class RangedEnemy(BaseEnemy):
    def __init__(self, settings, position, animation_manager):
        enemy_data = {
            'idle_animation': 'ranged_idle',
            'size': settings.enemy_size,
            'speed': settings.enemy_speed * 0.7,
            'health': 70,
            'damage': 15,
            'scale': settings.enemy_scale,
            'detection_radius': settings.enemy_detection_radius * 1.5
        }
        super().__init__(settings, position, animation_manager, enemy_data)
        self.attack_range = 200
        self.attack_cooldown = 2.0
        self.time_since_attack = 0

    def update_behavior(self, delta_time, tilemap, player_pos):
        self.time_since_attack += delta_time
        to_player = pygame.Vector2(player_pos) - pygame.Vector2(self.rect.center)
        distance = to_player.length()

        if distance > 0:
            to_player = to_player.normalize()

        if distance > self.attack_range:
            # Acercarse al jugador
            new_x = self.rect.x + to_player.x * self.speed * delta_time
            new_y = self.rect.y + to_player.y * self.speed * delta_time
            self.move(new_x, new_y)
        elif distance < self.attack_range * 0.7:
            # Alejarse del jugador
            new_x = self.rect.x - to_player.x * self.speed * delta_time
            new_y = self.rect.y - to_player.y * self.speed * delta_time
            self.move(new_x, new_y)