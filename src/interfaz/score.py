import random
import pygame
import sys
import xml.etree.ElementTree as ET
from pygame.locals import *

# Initialize Pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Generate stars
num_stars = 100
stars = []
for _ in range(num_stars):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    radius = random.randint(1, 3)
    stars.append([x, y, radius, random.randint(0, 255)])

# Function to read scores from XML
def read_scores_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    scores = []
    for score_element in root.findall("score"):
        name = score_element.find("name").text
        time = score_element.find("time").text
        score_value = int(score_element.find("score_value").text)
        enemies_defeated = int(score_element.find("enemies_defeated").text)
        scores.append({
            "name": name,
            "time": time,
            "score": score_value,
            "enemies_defeated": enemies_defeated
        })

    # Sort scores by score_value in descending order
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores

# Button class
class Button:
    def __init__(self, text, pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.Font(font, 40)
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

    def show(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        return False

def show_high_scores(screen):
    # Load scores
    scores = read_scores_xml("assets/score.xml")

    # Create the "Back" button
    back_button = Button("Atrás", (50, 500), None)

    # Main loop
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if back_button.click(event):
                return  # Exit the high scores screen

        # Draw the background (stars)
        screen.fill(BLACK)
        for star in stars:
            star[3] = (star[3] + random.randint(-5, 5)) % 256
            pygame.draw.circle(screen, (star[3], star[3], star[3]), (star[0], star[1]), star[2])

        # Draw the header
        font = pygame.font.Font(None, 74)
        header_text = font.render("Puntuaciones", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(header_text, header_rect)

        # Draw the scores
        font = pygame.font.Font(None, 36)
        y_offset = 150
        for score in scores:
            text = f"Name: {score['name']}, Time: {score['time']}, Score: {score['score']}, Enemies Defeated: {score['enemies_defeated']}"
            text_surface = font.render(text, True, WHITE)
            screen.blit(text_surface, (50, y_offset))
            y_offset += 40

        # Draw the "Back" button
        back_button.show(screen)

        pygame.display.update()
        clock.tick(30)