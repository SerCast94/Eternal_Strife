import pygame
from base_enemy import BaseEnemy
from projectile import Projectile

class SlimeEnemy(BaseEnemy):
    def __init__(self, settings, position, animation_manager, enemy_manager,game):
        enemy_data = {
            'idle_animation': 'slime_idle',
            'size': (32, 32),
            'speed': 50,
            'health': 30,
            'damage': 40,
            'scale': 1.0,
            'detection_radius': 100
        }
        super().__init__(settings, position, animation_manager, enemy_data,game)
        self.enemy_manager = enemy_manager

    def update_behavior(self, tilemap, player_pos):
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
            
        # Guardar la posición anterior
        old_position = self.rect.topleft
        
        # Intentar mover
        new_x = self.rect.x + steering.x * self.speed * self.game.delta_time
        new_y = self.rect.y + steering.y * self.speed * self.game.delta_time
        self.move(new_x, new_y)
        
        # Verificar colisiones y límites
        if tilemap.check_collision(self.hitbox):
            self.move(old_position[0], old_position[1])

    def _detect_obstacles(self, tilemap):
        directions = [
            pygame.Vector2(1, 0), pygame.Vector2(1, 1), pygame.Vector2(0, 1), pygame.Vector2(-1, 1),
            pygame.Vector2(-1, 0), pygame.Vector2(-1, -1), pygame.Vector2(0, -1), pygame.Vector2(1, -1)
        ]
        avoid_force = pygame.Vector2()
        
        for direction in directions:
            ray_pos = pygame.Vector2(self.rect.center)
            
            for distance in range(0, self.detection_radius, 8):
                check_pos = ray_pos + direction * distance
                check_rect = pygame.Rect(check_pos.x - 4, check_pos.y - 4, 8, 8)
                
                if tilemap.check_collision(check_rect):
                    avoid_force -= direction * (self.detection_radius - distance) / self.detection_radius
                    break
                    
        return avoid_force.normalize() * self.settings.enemy_avoid_force if avoid_force.length() > 0 else avoid_force

    def _resolve_stuck(self, tilemap):
        # Intentar moverse en una dirección diferente si hay colisión
        directions = [
            pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)
        ]
        for direction in directions:
            new_x = self.rect.x + direction.x * self.speed * 0.1
            new_y = self.rect.y + direction.y * self.speed * 0.1
            self.move(new_x, new_y)
            if not tilemap.check_collision(self.hitbox):
                break

class RangedEnemy(BaseEnemy):
    def __init__(self, settings, position, animation_manager, enemy_manager,game):
        enemy_data = {
            'idle_animation': 'ranged_idle',
            'size': (32, 32),
            'speed': 50,
            'health': 100,
            'damage': 10,
            'scale': 1.0,
            'projectile_speed': 150,
            'detection_radius': 300,  # Radio de detección para disparar
            'escape_radius': 80,     # Radio de escape para huir
            'attack_cooldown': 2.0
        }
        super().__init__(settings, position, animation_manager, enemy_data,game)
        self.enemy_manager = enemy_manager
        self.attack_timer = 0
        self.projectiles = []  # Inicializar el atributo projectiles

    def update_behavior(self, tilemap, player_pos):
        # Comportamiento básico del enemigo a distancia: mantener distancia y atacar al jugador
        to_player = pygame.Vector2(player_pos) - pygame.Vector2(self.rect.center)
        distance_to_player = to_player.length()
        if distance_to_player > 0:
            to_player = to_player.normalize()

        # Mantener distancia del jugador
        if distance_to_player < self.enemy_data['escape_radius']:
            avoid_force = -to_player  # Huir del jugador si está dentro del radio de escape
        else:
            avoid_force = pygame.Vector2()

        # Detectar obstáculos
        avoid_obstacles = self._detect_obstacles(tilemap)
        
        # Combinar fuerzas
        steering = avoid_force + avoid_obstacles
        if steering.length() > 0:
            steering = steering.normalize()
            
        # Guardar la posición anterior
        old_position = self.rect.topleft
        
        # Intentar mover
        new_x = self.rect.x + steering.x * self.speed * self.game.delta_time
        new_y = self.rect.y + steering.y * self.speed * self.game.delta_time
        self.move(new_x, new_y)
        
        # Verificar colisiones y límites
        if tilemap.check_collision(self.hitbox):
            self.move(old_position[0], old_position[1])
            # Intentar moverse en una dirección diferente si hay colisión
            self._resolve_stuck(tilemap)

        # Atacar al jugador si está en rango de detección
        self.attack_timer -= self.game.delta_time
        if self.attack_timer <= 0 and distance_to_player < self.enemy_data['detection_radius']:
            self.attack(player_pos)
            self.attack_timer = self.enemy_data['attack_cooldown']

    def _detect_obstacles(self, tilemap):
        directions = [
            pygame.Vector2(1, 0), pygame.Vector2(1, 1), pygame.Vector2(0, 1), pygame.Vector2(-1, 1),
            pygame.Vector2(-1, 0), pygame.Vector2(-1, -1), pygame.Vector2(0, -1), pygame.Vector2(1, -1)
        ]
        avoid_force = pygame.Vector2()
        
        for direction in directions:
            ray_pos = pygame.Vector2(self.rect.center)
            
            for distance in range(0, self.enemy_data['detection_radius'], 8):
                check_pos = ray_pos + direction * distance
                check_rect = pygame.Rect(check_pos.x - 4, check_pos.y - 4, 8, 8)
                
                if tilemap.check_collision(check_rect):
                    avoid_force -= direction * (self.enemy_data['detection_radius'] - distance) / self.enemy_data['detection_radius']
                    break
                    
        return avoid_force.normalize() * self.settings.enemy_avoid_force if avoid_force.length() > 0 else avoid_force

    def _resolve_stuck(self, tilemap):
        # Intentar moverse en una dirección diferente si hay colisión
        directions = [
            pygame.Vector2(1, 0), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, -1)
        ]
        for direction in directions:
            new_x = self.rect.x + direction.x * self.speed * 0.1
            new_y = self.rect.y + direction.y * self.speed * 0.1
            self.move(new_x, new_y)
            if not tilemap.check_collision(self.hitbox):
                break

    def attack(self, player_pos):
        # Asegurarse de que player_pos sea un Vector2
        target_pos = pygame.Vector2(player_pos)
        start_pos = pygame.Vector2(self.rect.center)
        
        projectile = Projectile(
            self.settings,
            self.animation_manager,
            start_pos,
            target_pos,
            self.enemy_data['damage'],
            self.enemy_data["projectile_speed"],
            'player',
            'enemy_projectile_idle',
            self.game
        )
        
        self.projectiles.append(projectile)
        self.enemy_manager.add_projectile(projectile)
