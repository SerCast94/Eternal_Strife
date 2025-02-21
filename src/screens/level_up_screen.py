import colorsys
import pygame
import random
import math

class LevelUpScreen:
    def __init__(self, screen, player, settings, game):
        """
        Constructor de la pantalla de subida de nivel.

        Parámetros:
        - screen: Superficie principal de pygame
        - player: Objeto jugador
        - settings: Configuraciones del juego
        - game: Referencia al juego principal

        Inicializa:
        - Superficie y dimensiones del popup
        - Fuentes y textos
        - Sistema de estrellas y partículas
        - Opciones de mejora disponibles
        """

        self.screen = screen
        self.game = game
        self.player = player
        self.settings = settings
        self.popup_width = 600
        self.popup_height = 400
        self.popup_surface = pygame.Surface((self.popup_width, self.popup_height))
        self.popup_rect = self.popup_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        
        # Configurar fuentes con codificación UTF-8
        pygame.font.init()
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 32)
        self.small_font = pygame.font.Font("assets/fonts/EldringBold.ttf", 24)
        self.done = False
        self.button_width = 450
        
        # Generar estrellas normales
        self.stars = []
        self.particles = []  # Para las partículas de explosión
        for _ in range(30):  # Reducido el número de estrellas
            self.stars.append({
                'x': random.randint(0, self.popup_width),
                'y': random.randint(0, self.popup_height),
                'radius': random.randint(2, 4),
                'explosion_timer': random.randint(50, 200),  # Tiempo hasta explosión
                'brightness': random.randint(150, 255)  # Brillo aleatorio
            })
        
        self.options = [
            {"text": "Vida maxima (+20)", "effect": self.increase_max_health},
            {"text": "Cadencia de disparo (+10%)", "effect": self.increase_fire_rate},
            {"text": "Damage (+15%)", "effect": self.increase_damage},
            {"text": "Recuperar vida (20%)", "effect": self.heal}
        ]
        
    def create_explosion(self, x, y):
        """
        Crea una explosión de partículas en una posición específica.
        
        Parámetros:
        - x: Posición X del centro de la explosión
        - y: Posición Y del centro de la explosión
        
        Genera 8-12 partículas con:
        - Dirección aleatoria
        - Velocidad variable
        - Color cambiante (HSV)
        - Tiempo de vida limitado
        """
        num_particles = random.randint(8, 12)
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            speed = random.uniform(0.5, 2)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'radius': random.randint(1, 2),
                'lifetime': random.randint(20, 40),
                'hue': random.random(),
                'speed': random.uniform(0.01, 0.03)
            })

    def increase_max_health(self):
        """
        Aumenta la vida máxima del jugador en 20 puntos.
        Ajusta la vida actual si supera el nuevo máximo.
        """
        self.player.max_health += 20
        self.player.health = min(self.player.health, self.player.max_health)

    def increase_fire_rate(self):
        """
        Mejora la cadencia de disparo reduciendo el cooldown un 10%.
        Aplica a todos los ataques del jugador.
        """
        for attack in self.player.attacks:
            attack.cooldown *= 0.9  # Reduce cooldown by 10%

    def increase_damage(self):
        """
        Aumenta el daño de los ataques un 15%.
        Aplica a todos los ataques del jugador.
        """
        for attack in self.player.attacks:
            attack.damage *= 1.15  # Increase damage by 15%

    def heal(self):
        """
        Cura al jugador un 20% de su vida máxima.
        No supera el límite de vida máxima.
        """
        heal_amount = self.player.max_health * 0.2
        self.player.health = min(self.player.health + heal_amount, self.player.max_health)

    def draw_stats(self):
        """
        Dibuja las estadísticas actuales del jugador:
        - Nivel actual
        - Vida (actual/máxima)
        - Daño base
        - Cadencia de disparo (ataques/segundo)
        """
        stats_text = [
            f"Nivel actual: {self.player.level}",
            f"Vida: {self.player.health:.0f}/{self.player.max_health}",
            f"Damage: {self.player.attacks[0].damage:.1f}",
            f"Cadencia: {1000/self.player.attacks[0].cooldown:.2f}/s"
        ]
        
        y = 60
        for text in stats_text:
            surface = self.small_font.render(text, True, (255, 255, 255))
            self.popup_surface.blit(surface, (74, y))
            y += 30

    def handle_event(self, event):
        """
        Maneja los eventos de la pantalla de level up.
        
        Parámetros:
        - event: Evento de pygame a procesar
        
        Retorna:
        - True si se seleccionó una mejora
        - False si no hubo interacción
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            relative_pos = (mouse_pos[0] - self.popup_rect.x, 
                        mouse_pos[1] - self.popup_rect.y)
            button_x = (self.popup_width - self.button_width) // 2
            for i, option in enumerate(self.options):
                button_rect = pygame.Rect(button_x, 180 + i * 50, self.button_width, 35)  # Match the new positions
                if button_rect.collidepoint(relative_pos):
                    option["effect"]()
                    self.done = True
                    return True
        return False

    def draw(self):
        """
        Renderiza la pantalla completa de level up.
        
        Elementos:
        - Fondo negro con estrellas animadas
        - Explosiones y partículas
        - Borde del popup
        - Título y estadísticas
        - Botones de opciones de mejora
        """
        """Dibuja la pantalla de level up"""
        # Dibujar fondo negro
        self.popup_surface.fill((0, 0, 0))
        
        # Actualizar y dibujar estrellas
        new_stars = []
        for star in self.stars:
            # Dibujar estrella normal (blanca)
            color = (star['brightness'], star['brightness'], star['brightness'])
            pygame.draw.circle(self.popup_surface, color, 
                            (int(star['x']), int(star['y'])), 
                            star['radius'])
            
            # Mover estrella y actualizar timer
            star['x'] -= 0.2
            star['explosion_timer'] -= 1
            
            # Comprobar si debe explotar
            if star['explosion_timer'] <= 0:
                self.create_explosion(star['x'], star['y'])
                # Crear nueva estrella en posición aleatoria en vez de al borde
                new_stars.append({
                    'x': random.randint(0, self.popup_width),
                    'y': random.randint(0, self.popup_height),
                    'radius': random.randint(2, 4),
                    'explosion_timer': random.randint(50, 200),
                    'brightness': random.randint(150, 255)
                })
                continue
            
            # Mantener la estrella si está dentro de la pantalla
            if star['x'] >= 0:
                new_stars.append(star)
            else:
                # Si sale de la pantalla, crear nueva estrella en posición aleatoria
                new_stars.append({
                    'x': random.randint(0, self.popup_width),
                    'y': random.randint(0, self.popup_height),
                    'radius': random.randint(2, 4),
                    'explosion_timer': random.randint(50, 200),
                    'brightness': random.randint(150, 255)
                })
        
        # Actualizar lista de estrellas
        self.stars = new_stars

        # Actualizar y dibujar partículas de explosión
        new_particles = []
        for particle in self.particles:
            # Actualizar color
            particle['hue'] = (particle['hue'] + particle['speed']) % 1.0
            rgb = colorsys.hsv_to_rgb(particle['hue'], 1, 1)
            color = tuple(int(x * 255) for x in rgb)
            
            # Dibujar partícula
            pygame.draw.circle(self.popup_surface, color,
                            (int(particle['x']), int(particle['y'])),
                            particle['radius'])
            
            # Actualizar posición
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            
            # Mantener partícula si sigue viva y dentro de la pantalla
            if (particle['lifetime'] > 0 and 
                0 <= particle['x'] <= self.popup_width and 
                0 <= particle['y'] <= self.popup_height):
                new_particles.append(particle)
        
        # Actualizar lista de partículas
        self.particles = new_particles

        # Dibujar borde del popup
        pygame.draw.rect(self.popup_surface, (255, 255, 255), 
                        self.popup_surface.get_rect(), 2)

        # Dibujar título
        title = self.font.render("¡Subiste de nivel!", True, (255, 255, 255))
        self.popup_surface.blit(title, (self.popup_width//2 - title.get_width()//2, 20))

        # Dibujar estadísticas
        self.draw_stats()

        # Dibujar opciones
        button_x = (self.popup_width - self.button_width) // 2
        for i, option in enumerate(self.options):
            button_rect = pygame.Rect(button_x, 180 + i * 50, self.button_width, 35)  # Changed Y position and spacing
            pygame.draw.rect(self.popup_surface, (50, 50, 50), button_rect)
            pygame.draw.rect(self.popup_surface, (255, 255, 255), button_rect, 1)
            text = self.small_font.render(option["text"], True, (255, 255, 255))
            self.popup_surface.blit(text, (button_rect.centerx - text.get_width()//2, 
                                        button_rect.centery - text.get_height()//2))


        # Dibujar popup en la pantalla
        self.screen.blit(self.popup_surface, self.popup_rect)

    def run(self):
        """
        Ejecuta el bucle principal de la pantalla de level up.
        
        Funcionalidad:
        - Procesa eventos
        - Pausa el juego principal
        - Actualiza la visualización
        - Espera selección de mejora
        
        Se usa principalmente para pruebas independientes.
        """
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                self.handle_event(event)
            self.game.delta_time = 0
            self.game.paused = True
            self.draw()
            pygame.display.flip()