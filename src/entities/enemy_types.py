import pygame
from entities.base_enemy import BaseEnemy
from attacks.projectile import Projectile

class SlimeEnemy(BaseEnemy):
    def __init__(self, settings, position, animation_manager, enemy_manager,game):
        """
        Constructor del enemigo tipo Slime.
        Parámetros:
        - settings: Configuraciones generales del juego
        - position: Posición inicial del enemigo
        - animation_manager: Gestor de animaciones
        - enemy_manager: Gestor de enemigos
        - game: Referencia al objeto principal del juego
        Inicializa las características específicas del Slime:
        - Animación idle
        - Tamaño: 32x32
        - Velocidad: 55
        - Salud: 10
        - Daño: 40
        - Escala: 1.0
        - Radio de detección: 100
        """
        enemy_data = {
            'idle_animation': 'slime_idle',
            'size': (32, 32),
            'speed': 55,
            'health': 10,
            'damage': 40,
            'scale': 1.0,
            'detection_radius': 100
        }
        super().__init__(settings, position, animation_manager, enemy_data,game)
        self.enemy_manager = enemy_manager

    def update_behavior(self, tilemap, player_pos):
        """
        Actualiza el comportamiento del Slime en cada frame.
        Parámetros:
        - tilemap: Mapa de tiles para verificar colisiones
        - player_pos: Posición actual del jugador
        Comportamiento:
        - Persigue al jugador
        - Evita obstáculos
        - Actualiza posición considerando colisiones
        """
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
        """
        Detecta obstáculos alrededor del Slime usando raycast.
        Parámetros:
        - tilemap: Mapa de tiles para verificar colisiones
        Retorna:
        - Vector de fuerza normalizado para evitar obstáculos
        """
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
        """
        Intenta resolver situaciones donde el Slime queda atascado.
        Parámetros:
        - tilemap: Mapa de tiles para verificar colisiones
        Prueba diferentes direcciones hasta encontrar una válida.
        """
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
        """
        Constructor del enemigo a distancia.
        Parámetros:
        - settings: Configuraciones generales del juego
        - position: Posición inicial del enemigo
        - animation_manager: Gestor de animaciones
        - enemy_manager: Gestor de enemigos
        - game: Referencia al objeto principal del juego
        Inicializa características específicas:
        - Animación idle
        - Tamaño: 32x32
        - Velocidad: 50
        - Salud: 30
        - Daño: 10
        - Velocidad de proyectil: 150
        - Radio de detección: 300
        - Radio de escape: 80
        - Cooldown de ataque: 2.0 segundos
        """
        enemy_data = {
            'idle_animation': 'ranged_idle',
            'size': (32, 32),
            'speed': 50,
            'health': 30,
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
        """
        Actualiza el comportamiento del enemigo a distancia.
        Parámetros:
        - tilemap: Mapa de tiles para verificar colisiones
        - player_pos: Posición actual del jugador
        Comportamiento:
        - Mantiene distancia del jugador
        - Evita obstáculos
        - Ataca cuando el jugador está en rango
        - Gestiona cooldown de ataque
        """
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
        """
        Detecta obstáculos alrededor del enemigo usando técnica de raycast.
        Parámetros:
        - tilemap: Mapa de tiles para verificar colisiones

        Funcionamiento:
        - Emite rayos en 8 direcciones diferentes (N, NE, E, SE, S, SO, O, NO)
        - Para cada rayo, verifica colisiones a intervalos de 8 píxeles
        - Si detecta una colisión, genera una fuerza de evasión inversamente proporcional a la distancia
        - La fuerza es más fuerte cuanto más cerca esté el obstáculo

        Retorna:
        - Vector2 normalizado que representa la fuerza de evasión de obstáculos
        - Si no hay obstáculos, retorna un vector nulo
        """
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
        """
        Intenta desatascar al enemigo cuando queda bloqueado por colisiones.
        Parámetros:
        - tilemap: Mapa de tiles para verificar colisiones

        Funcionamiento:
        - Prueba movimientos en 4 direcciones cardinales (derecha, izquierda, arriba, abajo)
        - Para cada dirección, intenta un pequeño movimiento (10% de la velocidad normal)
        - Se detiene en la primera dirección que no resulte en colisión
        - Si ninguna dirección funciona, el enemigo permanecerá en su posición actual
        """
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
        """
        Realiza un ataque a distancia hacia el jugador.
        Parámetros:
        - player_pos: Posición del jugador objetivo
        Crea y añade un nuevo proyectil al gestor de enemigos.
        """
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
