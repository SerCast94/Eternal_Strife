import random
import pygame
import sys
import colorsys
from pygame.locals import *
from PIL import Image
import os
from screens.score import show_high_scores
from managers.music_player import MusicPlayer

class Menu:
    def __init__(self, screen,music_player):
        """
        Constructor del menú principal.
        
        Inicializa:
        - Pantalla y estado del juego
        - Control de volumen
        - Animación de fondo (GIF)
        - Imagen del título
        - Sistema de estrellas
        - Botones de interfaz
        - Variables de control de animación
        
        Parámetros:
        - screen: Superficie de pygame donde se dibuja el menú
        - music_player: Gestor de música del juego
        """
        self.screen = screen
        self.start_game = False
        self.debug_mode = False  # Añadir un atributo para el modo de depuración
        self.music_player = music_player

        volume_x = self.screen.get_width() - 120  # 120 = ancho del slider + margen
        volume_y = self.screen.get_height() - 30  # 30 = margen desde abajo
        self.volume_slider = VolumeSlider((volume_x, volume_y))
        self.volume_slider.value = music_player.get_volume()

        # Guardar el volumen original del menú
        self.original_menu_volume = music_player.get_volume()
    
        # Load the GIF frames
        self.frames = []
        gif_path = 'assets/images/menu_background.gif'
        gif = Image.open(gif_path)
        for frame in range(gif.n_frames):
            gif.seek(frame)
            frame_image = gif.convert("RGBA")
            frame_data = frame_image.tobytes()
            frame_surface = pygame.image.fromstring(frame_data, frame_image.size, "RGBA")
            frame_surface = pygame.transform.scale(frame_surface, (300, 300))

            # Calculate the position to center the image
            x_pos = (self.screen.get_width() - 300) // 2  # Ajustar posición x
            y_pos = (self.screen.get_height() - 330) // 2  # Ajustar posición y


            # Append the frame with the calculated position
            self.frames.append((frame_surface, (x_pos, y_pos)))

        # Load the title image
        self.title_image = pygame.image.load('assets/images/titulo.png')
        self.title_image = pygame.transform.scale(self.title_image, (250, 250))  # Adjust size as needed

        # Calculate the position to center the title image
        self.title_x_pos = (self.screen.get_width() - self.title_image.get_width()) // 2  # Centrar la imagen del título
        self.title_y_pos = -50  # Adjust the y position as needed

        # Generate stars
        self.num_stars = 100
        self.stars = []
        for _ in range(self.num_stars):
            x = random.randint(0, self.screen.get_width())
            y = random.randint(0, self.screen.get_height())
            radius = random.randint(1, 3)
            self.stars.append([x, y, radius, random.randint(0, 255)])

        # Create buttons - Modificar posiciones Y
        self.start_button = Button("Jugar", (345, 440), None)
        self.high_scores_button = Button("Puntuaciones", (250, 495), None)
        self.exit_button = Button("Salir", (345, 550), None)
        self.debug_button = Button("Modo Debug", (280, 440), None, is_rainbow=True)  # Activar efecto arcoíris
        
        # Variables de control
        self.showing_debug = False
        self.frame_index = 0
        self.frame_delay = 70
        self.last_frame_time = pygame.time.get_ticks()

        # Variables para controlar el GIF
        self.frame_index = 0
        self.frame_delay = 70  # Tiempo en milisegundos entre frames
        self.last_frame_time = pygame.time.get_ticks()  # Tiempo inicial

        

    def run(self):
        """
        Ejecuta el bucle principal del menú.
        
        Gestiona:
        - Eventos de entrada
        - Actualización de estados
        - Renderizado de elementos
        - Control de música
        - Animaciones de fondo
        
        Retorna:
        - True si se inicia el juego
        - False si se cierra la aplicación
        """
        running = True
        clock = pygame.time.Clock()
        # Restaurar volumen original al inicio del menú
        self.music_player.set_volume(self.original_menu_volume)
        self.volume_slider.value = self.original_menu_volume
        self.volume_slider.update_handle_position()
        self.music_player.change_playlist("menu")
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.music_player.stop()
                    pygame.quit()
                    sys.exit()
                
                # Detectar combinación de teclas para debug
                keys = pygame.key.get_pressed()
                self.showing_debug = keys[pygame.K_LCTRL] and keys[pygame.K_LSHIFT]
                
                # Manejar clicks según el botón visible
                if not self.showing_debug and self.start_button.click(event):
                    self.start_game = True
                    self.debug_mode = False
                    running = False
                elif self.showing_debug and self.debug_button.click(event):
                    self.start_game = True
                    self.debug_mode = True
                    running = False
                    
                if self.high_scores_button.click(event):
                    show_high_scores(self.screen)
                if self.exit_button.click(event):
                    pygame.quit()
                    sys.exit()

            if self.volume_slider.update(events):
                self.music_player.set_volume(self.volume_slider.value)

            # Draw background and animations
            self.screen.fill((0, 0, 0))
            
            # Dibujar estrellas con movimiento
            for star in self.stars:
                star[0] -= 0.1  # Movimiento a la izquierda
                if star[0] < 0:
                    star[0] = self.screen.get_width()
                star[3] = (star[3] + random.randint(-1, 1)) % 256  # Parpadeo
                pygame.draw.circle(self.screen, (star[3], star[3], star[3]), 
                                (int(star[0]), star[1]), star[2])

            # Actualizar y dibujar frame del GIF
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time >= self.frame_delay:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.last_frame_time = current_time

            # Dibujar GIF y título
            frame_surface, pos = self.frames[self.frame_index]
            self.screen.blit(frame_surface, pos)
            self.screen.blit(self.title_image, (self.title_x_pos, self.title_y_pos))

            # Mostrar botones según estado
            if self.showing_debug:
                self.debug_button.show(self.screen)  # Botón con efecto arcoíris
            else:
                self.start_button.show(self.screen)  # Botón normal
            
            # Mostrar botones adicionales
            self.high_scores_button.show(self.screen)
            self.exit_button.show(self.screen)

            self.volume_slider.draw(self.screen)

            self.music_player.update()
            self.music_player.draw(self.screen)


            # Actualizar pantalla
            pygame.display.update()
            clock.tick(60)  # Limitar a 60 FPS

class Button:
    def __init__(self, text, pos, font, bg="black", feedback="", is_rainbow=False):
        """
        Constructor de botón personalizado.
        
        Parámetros:
        - text: Texto a mostrar en el botón
        - pos: Tupla (x, y) con la posición
        - font: Fuente a utilizar (opcional)
        - bg: Color de fondo (por defecto "black")
        - feedback: Texto de retroalimentación
        - is_rainbow: Activa efecto arcoíris (por defecto False)
        """
        self.x, self.y = pos
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 40)
        self.feedback = "text" if feedback == "" else feedback
        self.is_rainbow = is_rainbow
        self.hue = 0
        self.change_text(text, bg)

    def change_text(self, text, bg="black"):
        """
        Actualiza el texto y apariencia del botón.

        Parámetros:
        - text: Nuevo texto a mostrar
        - bg: Color de fondo (por defecto "black")

        Si is_rainbow está activo, aplica color del ciclo arcoíris
        """
        if self.is_rainbow:
            # Convertir HSV a RGB (hue 0-1, saturation 1, value 1)
            rgb = colorsys.hsv_to_rgb(self.hue, 1, 1)
            # Convertir a valores 0-255
            color = tuple(int(x * 255) for x in rgb)
            self.text = self.font.render(text, True, color)
        else:
            self.text = self.font.render(text, True, (255, 255, 255))
        
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))  # Transparente
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def update(self):
        """
        Actualiza el estado del botón.
        Si tiene efecto arcoíris, actualiza el color cíclicamente.
        """
        if self.is_rainbow:
            self.hue = (self.hue + 0.01) % 1.0
            self.change_text("Modo Debug")

    def show(self, screen):
        """
        Dibuja el botón en la pantalla.
        
        Parámetros:
        - screen: Superficie donde dibujar
        
        Actualiza el efecto arcoíris si está activo
        """
        if self.is_rainbow:
            self.update()
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event):
        """
        Verifica si se ha hecho clic en el botón.

        Parámetros:
        - event: Evento de pygame a procesar

        Retorna:
        - True si se hizo clic izquierdo dentro del área del botón
        - False en caso contrario
        """
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    return True
        return False

class VolumeSlider:
    def __init__(self, pos, width=100, height=5):
        """
        Constructor del control deslizante de volumen.

        Parámetros:
        - pos: Tupla (x, y) con la posición
        - width: Ancho del control (por defecto 100)
        - height: Alto del control (por defecto 5)

        Inicializa:
        - Rectángulos de barra y control
        - Colores y estados
        - Valor inicial (0.5)
        """
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.handle_rect = pygame.Rect(pos[0], pos[1] - 5, 10, 15)
        self.color = (100, 100, 100)
        self.handle_color = (200, 200, 200)
        self.active_color = (150, 150, 150)
        self.value = 0.5  # Valor inicial (0.0 a 1.0)
        self.dragging = False
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 20)


        self.update_handle_position()
        
    def update(self, events):
        """
        Actualiza el estado del control según los eventos.
        
        Parámetros:
        - events: Lista de eventos de pygame
        
        Retorna:
        - True si el valor cambió
        - False si no hubo cambios
        """
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.handle_rect.collidepoint(mouse_pos):
                    self.dragging = True
            elif event.type == MOUSEBUTTONUP:
                self.dragging = False
                
        if self.dragging:
            # Actualizar posición del control
            new_x = min(max(mouse_pos[0], self.rect.left), self.rect.right - self.handle_rect.width)
            self.handle_rect.x = new_x
            # Calcular valor (0.0 a 1.0)
            self.value = (new_x - self.rect.left) / (self.rect.width - self.handle_rect.width)
            return True
            
        return False
    
    def update_handle_position(self):
        """
        Actualiza la posición visual del control
        según el valor actual (0.0 a 1.0)
        """
        new_x = self.rect.left + (self.rect.width - self.handle_rect.width) * self.value
        self.handle_rect.x = new_x

    def draw(self, screen):
        """
        Dibuja el control deslizante completo.
        
        Parámetros:
        - screen: Superficie donde dibujar
        
        Elementos:
        - Barra de fondo
        - Control deslizante
        - Texto con porcentaje y símbolo musical
        """
        # Dibujar barra
        pygame.draw.rect(screen, self.color, self.rect)
        # Dibujar control
        pygame.draw.rect(screen, self.handle_color if not self.dragging else self.active_color, self.handle_rect)
        # Dibujar ícono y valor - ahora a la izquierda del slider
        volume_text = self.font.render(f"Volumen: ♪ {int(self.value * 100)}%", True, (255, 255, 255))
        text_pos = (self.rect.left - volume_text.get_width() - 10, self.rect.top - 7)
        screen.blit(volume_text, text_pos)