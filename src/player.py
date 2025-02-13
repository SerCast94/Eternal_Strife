import pygame
from animation_manager import AnimatedSprite
from attacks import FireballAttack
from item import Gem, Tuna

class Player(AnimatedSprite):
    def __init__(self, settings, animation_manager, enemy_manager, game):
        initial_pos = (settings.map_width * settings.tile_size // 2, 
                      settings.map_height * settings.tile_size // 2)
        super().__init__(animation_manager, 'player_idle', initial_pos, settings.player_size, settings,game)
        self.settings = settings
        self.game = game
        self.velocity = pygame.Vector2()
        self.health = settings.player_health
        self.max_health = settings.player_health
        self.score = 0
        self.scoreToLevelUp = 0
        self.is_player = True  # Atributo para identificar al jugador
        self.level = 1
        self.exp_to_next_level = 5
        self.exp_increase_rate = 1.5 
        
        # Movement state
        self.moving = False
        self.direction = pygame.Vector2()
        
        # Current state
        self.state = "idle"
        
        self.animations = {
            "idle": "player_idle",
            "walk_left": "player_walk_left",
            "walk_right": "player_walk_right",
            "walk_up": "player_walk_up",
            "walk_down": "player_walk_down"
        }

        # Inventario de ataques
        self.attacks = []
        self.add_attack(FireballAttack(settings, self, enemy_manager,self.game))

        # Referencia al EnemyManager
        self.enemy_manager = enemy_manager

    def add_attack(self, attack):
        self.attacks.append(attack)
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_w:
                self.velocity.y = -1
                self.change_animation(self.animations["walk_up"])
            elif event.key == pygame.K_s:
                self.velocity.y = 1
                self.change_animation(self.animations["walk_down"])
            elif event.key == pygame.K_a:
                self.velocity.x = -1
                self.change_animation(self.animations["walk_left"])
            elif event.key == pygame.K_d:
                self.velocity.x = 1
                self.change_animation(self.animations["walk_right"])
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s):
                self.velocity.y = 0
            elif event.key in (pygame.K_a, pygame.K_d):
                self.velocity.x = 0
            
            if self.velocity.length() == 0:
                self.change_animation(self.animations["idle"])
                
    def update(self, tilemap):
        if self.game.paused:
            return False
        
        super().update()
        # Update movement
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize()
            
        # Calculate new position    
        new_x = self.rect.x + self.velocity.x * self.settings.player_speed * self.game.delta_time
        new_y = self.rect.y + self.velocity.y * self.settings.player_speed * self.game.delta_time
        
        # Store old position
        old_position = self.rect.topleft
        
        # Try to move
        self.move(new_x, new_y)
        
        # Check collisions and bounds
        if tilemap.check_collision(self.hitbox):
            self.move(old_position[0], old_position[1])
        
        # Keep in bounds    
        new_x = max(0, min(self.rect.x,
            self.settings.map_width * self.settings.tile_size - self.settings.player_size[0]))
        new_y = max(0, min(self.rect.y,
            self.settings.map_height * self.settings.tile_size - self.settings.player_size[1]))
        self.move(new_x, new_y)

        # Actualizar ataques
        for attack in self.attacks:
            attack.update()
            attack.attack()  # Lanzar ataque automáticamente después del cooldown

        # Recoger ítems
        return self.collect_items(self.enemy_manager.items)

    def draw(self, screen, camera_x, camera_y):
        super().draw(screen, camera_x, camera_y)
        for attack in self.attacks:
            attack.draw(screen, camera_x, camera_y)
            
    def level_up(self):
        self.level += 1
        self.exp_to_next_level = int(self.exp_to_next_level * self.exp_increase_rate)
        self.scoreToLevelUp = 0
        return True
            
    def collect_items(self, items):
        level_up = False
        for item in items[:]:
            if self.hitbox.colliderect(item.rect):
                if isinstance(item, Gem):
                    self.scoreToLevelUp += 1
                    self.score += 1
                    # Verificar si subimos de nivel
                    if self.scoreToLevelUp >= self.exp_to_next_level:
                        level_up = self.level_up()
                elif isinstance(item, Tuna):
                    self.health = min(self.max_health, self.health + self.max_health * 0.2)
                items.remove(item)
        return level_up
    


        