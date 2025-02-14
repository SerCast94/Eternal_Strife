import pygame
import sys
import xml.etree.ElementTree as ET
import random


class GameOverScreen:
    def __init__(self, screen, game_state, score, level,game):
        self.screen = screen
        self.game = game
        self.game_state = game_state
        self.score = score
        self.level = level  # Añadir nivel del personaje
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 40)
        self.input_box = pygame.Rect(200, 300, 400, 50)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('red')
        self.color = self.color_inactive
        self.active = False
        self.text = ''
        self.done = False

        # Generate stars
        self.num_stars = 100
        self.stars = []
        for _ in range(self.num_stars):
            x = random.randint(0, self.screen.get_width())
            y = random.randint(0, self.screen.get_height())
            radius = random.randint(1, 3)
            self.stars.append([x, y, radius, random.randint(0, 255)])

        # Create "Enviar Puntuación" button
        self.button_font = pygame.font.Font("assets/fonts/EldringBold.ttf", 40)
        self.button_text = self.button_font.render("Enviar", True, (255, 255, 255))
        self.button_rect = self.button_text.get_rect(center=(self.screen.get_width() // 2, 500))


    def run(self):
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_box.collidepoint(event.pos):
                        self.active = not self.active
                    else:
                        self.active = False
                    self.color = self.color_active if self.active else self.color_inactive
                    if self.button_rect.collidepoint(event.pos):
                        self.save_score(self.text)
                        self.done = True
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
        for star in self.stars:
                star[0] -= 0.008  # Cambia el valor 2 por la velocidad deseada
                if star[0] < 0:
                    star[0] = self.screen.get_width()  # Reaparece en el lado derecho
                star[3] = (star[3] + random.randint(-1, 1)) % 256
                pygame.draw.circle(self.screen, (star[3], star[3], star[3]), (star[0], star[1]), star[2])
            
        # Render "Has muerto" text with a larger font
        game_over_font = pygame.font.Font('assets/fonts/eldringbold.ttf', 74)  # Cambiar tamaño de fuente según sea necesario
        game_over_text = game_over_font.render("Has muerto", True, (255, 0, 0))
        self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, 100))

        # Render "Introduce tu nombre:" text
        enter_name_text = self.font.render("Introduce tu nombre:", True, (255, 255, 255))
        self.screen.blit(enter_name_text, (self.screen.get_width() // 2 - enter_name_text.get_width() // 2, 250))

        # Adjust input box width to match "Introduce tu nombre:" text width
        txt_surface = self.font.render(self.text, True, (255, 255, 255))  # Cambiar color del texto a blanco
        width = enter_name_text.get_width() + 10
        self.input_box.w = width
        self.input_box.h = 60  # Ajustar la altura del cuadro de texto
        self.input_box.x = (self.screen.get_width() - width) // 2  # Centrar el cuadro de texto
        self.input_box.y = 350  
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_box)  # Fondo negro
        # Center the text inside the input box
        txt_x = self.input_box.x + (self.input_box.w - txt_surface.get_width()) // 2
        txt_y = self.input_box.y + (self.input_box.h - txt_surface.get_height()) // 2
        self.screen.blit(txt_surface, (txt_x, txt_y))
        pygame.draw.rect(self.screen, self.color, self.input_box, 2)  # Cambiar color del borde según el estado

         # Draw "Enviar Puntuación" button
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_rect)  # Fondo negro para el botón
        self.screen.blit(self.button_text, self.button_rect)

    def save_score(self, name):
        tree = ET.parse('assets/score.xml')
        root = tree.getroot()

        new_score = ET.Element("score")
        ET.SubElement(new_score, "name").text = name
        minutes = int(self.game.game_time // 60)
        seconds = int(self.game.game_time % 60)
        formatted_time = f"{minutes:02}:{seconds:02}"
        ET.SubElement(new_score, "time").text = formatted_time
        ET.SubElement(new_score, "score_value").text = str(self.score)
        ET.SubElement(new_score, "level").text = str(self.level)  # Añadir nivel del personaje

        root.append(new_score)
        tree.write('assets/score.xml')