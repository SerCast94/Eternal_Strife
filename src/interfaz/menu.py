import random
import pygame
import sys
from pygame.locals import *
from PIL import Image
import os

# Initialize Pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Menu principal")

# Load the GIF frames
frames = []
gif_path = 'assets/images/menu_background.gif'
gif = Image.open(gif_path)
for frame in range(gif.n_frames):
    gif.seek(frame)
    frame_image = gif.convert("RGBA")
    frame_data = frame_image.tobytes()
    frame_surface = pygame.image.fromstring(frame_data, frame_image.size, "RGBA")
    frame_surface = pygame.transform.scale(frame_surface, (300, 300))

    # Calculate the position to center the image
    x_pos = (SCREEN_WIDTH - 300) // 2
    y_pos = (SCREEN_HEIGHT - 350) // 2

    # Append the frame with the calculated position
    frames.append((frame_surface, (x_pos, y_pos)))
    
# Generate stars
num_stars = 100
stars = []
for _ in range(num_stars):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    radius = random.randint(1, 3)
    stars.append([x, y, radius, random.randint(0, 255)])
    
# Button class
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
        self.text = self.font.render(text, True, WHITE)
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self):
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        return False

# Create buttons
start_button = Button("Iniciar Juego", (260, 440), None)
high_scores_button = Button("Puntuaciones", (250, 495), None)
exit_button = Button("Salir", (345, 550), None)

# Main loop
running = True
frame_index = 0
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if start_button.click(event):
            print("Iniciar Juego")
            # Add code to start the game
        if high_scores_button.click(event):
            print("Puntuaciones")
            # Add code to show high scores
        if exit_button.click(event):
            pygame.quit()
            sys.exit()

    # Draw the background (stars)
    screen.fill(BLACK)
    for star in stars:
        star[3] = (star[3] + random.randint(-5, 5)) % 256
        pygame.draw.circle(screen, (star[3], star[3], star[3]), (star[0], star[1]), star[2])

    # Draw the planet (GIF)
    frame_surface, pos = frames[frame_index]
    screen.blit(frame_surface, pos)
    frame_index = (frame_index + 1) % len(frames)

    # Draw buttons
    start_button.show()
    high_scores_button.show()
    exit_button.show()

    pygame.display.update()
    clock.tick(10)  # Adjust the frame rate as needed