import random
import pygame
import sys
import colorsys
from pygame.locals import *
from PIL import Image
import os
from score import show_high_scores
from music_player import MusicPlayer

class Menu:
    def __init__(self, screen,music_player):
        self.screen = screen
        self.start_game = False
        self.debug_mode = False  # Añadir un atributo para el modo de depuración
        self.music_player = music_player
    
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
        running = True
        clock = pygame.time.Clock()
        self.music_player.change_playlist("menu")
        while running:
            for event in pygame.event.get():
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

            self.music_player.update()
            self.music_player.draw(self.screen)


            # Actualizar pantalla
            pygame.display.update()
            clock.tick(60)  # Limitar a 60 FPS

class Button:
    def __init__(self, text, pos, font, bg="black", feedback="", is_rainbow=False):
        self.x, self.y = pos
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 40)
        self.feedback = "text" if feedback == "" else feedback
        self.is_rainbow = is_rainbow
        self.hue = 0
        self.change_text(text, bg)

    def change_text(self, text, bg="black"):
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
        if self.is_rainbow:
            self.hue = (self.hue + 0.01) % 1.0
            self.change_text("Modo Debug")

    def show(self, screen):
        if self.is_rainbow:
            self.update()
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event):
        """Comprueba si se ha hecho clic en el botón"""
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(mouse_pos):
                    return True
        return False