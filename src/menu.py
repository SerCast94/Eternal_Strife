import random
import pygame
import sys
from pygame.locals import *
from PIL import Image
import os
from score import show_high_scores

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.start_game = False

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
            x_pos = (self.screen.get_width() - 300) // 2
            y_pos = (self.screen.get_height() - 300) // 2

            # Append the frame with the calculated position
            self.frames.append((frame_surface, (x_pos, y_pos)))

        # Load the title image
        self.title_image = pygame.image.load('assets/images/titulo.png')
        self.title_image = pygame.transform.scale(self.title_image, (400, 250))  # Adjust size as needed

        # Calculate the position to center the title image
        self.title_x_pos = (self.screen.get_width() - 400) // 2
        self.title_y_pos = -50  # Adjust the y position as needed

        # Generate stars
        self.num_stars = 100
        self.stars = []
        for _ in range(self.num_stars):
            x = random.randint(0, self.screen.get_width())
            y = random.randint(0, self.screen.get_height())
            radius = random.randint(1, 3)
            self.stars.append([x, y, radius, random.randint(0, 255)])

        # Create buttons
        self.start_button = Button("Iniciar Juego", (260, 440), None)
        self.high_scores_button = Button("Puntuaciones", (250, 495), None)
        self.exit_button = Button("Salir", (345, 550), None)

        # Variables para controlar el GIF
        self.frame_index = 0
        self.frame_delay = 70  # Tiempo en milisegundos entre frames
        self.last_frame_time = pygame.time.get_ticks()  # Tiempo inicial

    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if self.start_button.click(event):
                    self.start_game = True
                    running = False
                if self.high_scores_button.click(event):
                    show_high_scores(self.screen)  # Call the function to show high scores
                if self.exit_button.click(event):
                    pygame.quit()
                    sys.exit()

            # Draw the background (stars)
            self.screen.fill((0, 0, 0))
            for star in self.stars:
                star[0] -= 0.1  # Cambia el valor 2 por la velocidad deseada
                if star[0] < 0:
                    star[0] = self.screen.get_width()  # Reaparece en el lado derecho
                star[3] = (star[3] + random.randint(-1, 1)) % 256
                pygame.draw.circle(self.screen, (star[3], star[3], star[3]), (star[0], star[1]), star[2])

            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time >= self.frame_delay:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.last_frame_time = current_time

            frame_surface, pos = self.frames[self.frame_index]
            self.screen.blit(frame_surface, pos)
            self.screen.blit(self.title_image, (self.title_x_pos, self.title_y_pos))

            self.start_button.show(self.screen)
            self.high_scores_button.show(self.screen)
            self.exit_button.show(self.screen)

            pygame.display.update()
            clock.tick(60)

class Button:
    def __init__(self, text, pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 40)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg)

    def change_text(self, text, bg="black"):
        self.text = self.font.render(text, True, (255, 255, 255))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        return False