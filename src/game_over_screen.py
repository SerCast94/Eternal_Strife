# src/game_over_screen.py

import pygame
import sys
import xml.etree.ElementTree as ET

class GameOverScreen:
    def __init__(self, screen, game_state, score):
        self.screen = screen
        self.game_state = game_state
        self.score = score
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 40)
        self.input_box = pygame.Rect(200, 300, 400, 50)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.active = False
        self.text = ''
        self.done = False

    def run(self):
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.active = not self.active
                    else:
                        self.active = False
                    self.color = self.color_active if self.active else self.color_inactive
                if event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_RETURN:
                            self.save_score(self.text)
                            self.done = True
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode

            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()

    def draw(self):
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, 100))

        enter_name_text = self.font.render("Enter your name:", True, (255, 255, 255))
        self.screen.blit(enter_name_text, (self.screen.get_width() // 2 - enter_name_text.get_width() // 2, 250))

        txt_surface = self.font.render(self.text, True, self.color)
        width = max(400, txt_surface.get_width() + 10)
        self.input_box.w = width
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        pygame.draw.rect(self.screen, self.color, self.input_box, 2)

    def save_score(self, name):
        tree = ET.parse('assets/score.xml')
        root = tree.getroot()

        new_score = ET.Element("score")
        ET.SubElement(new_score, "name").text = name
        ET.SubElement(new_score, "time").text = str(int(self.game_state.game_time))
        ET.SubElement(new_score, "score_value").text = str(self.score)
        ET.SubElement(new_score, "enemies_defeated").text = str(self.score)  # Asumiendo que el score es igual a enemigos derrotados

        root.append(new_score)
        tree.write('assets/score.xml')