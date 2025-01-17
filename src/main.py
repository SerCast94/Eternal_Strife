import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS
from map import load_tileset, generate_layer, draw_layers
from player import Player

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Juego con Capas y Personaje Jugable")

# Cargar tilesets para diferentes capas
tileset_base = load_tileset("assets/images/tileset_base.png", TILE_SIZE, 128)  # Tileset para fondo (ej: césped)
tileset_decor = load_tileset("assets/images/tileset_decor.png", TILE_SIZE, 128)  # Tileset para props (ej: árboles)
tileset_decorHorizontal = load_tileset("assets/images/tileset_horizontalPath.png", TILE_SIZE, 128)  # Tileset para decoraciones
tileset_decorVertical = load_tileset("assets/images/tileset_verticalPath.png", TILE_SIZE, 128)  # Tileset para decoraciones

# Definir la probabilidad de generación por capa
probabilidad_base = 1.0  # 100% (siempre genera un tile)
probabilidad_props = 0.1  # 10% (genera raramente)
probabilidad_decor = 0.1  # 1% (genera algo más raramente)

# Dimensiones del mapa en tiles
map_width = 100
map_height = 100

# Generar capas con probabilidades específicas
base_layer = generate_layer(map_width, map_height, [tileset_base,tileset_base, tileset_decor], probabilidad_base)  # Capa base (fondo)
decor_layer = generate_layer(map_width, map_height, [tileset_decorHorizontal, tileset_decorVertical], probabilidad_decor)  # Capa de decoraciones

# Agrupar capas con sus tilesets y datos
layers = [
    {'tilesets': [tileset_base], 'layer_data': base_layer},
    {'tilesets': [tileset_decorHorizontal, tileset_decorVertical], 'layer_data': decor_layer}
]

# Inicializar al jugador
player_sprite = "assets/images/player.png" 
player = Player(map_width // 2, map_height // 2,.12, player_sprite, TILE_SIZE,2.2)  # Empieza en el centro del mapa.

# Desplazamiento de la cámara
camera_offset = [0, 0]

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(FPS) / 16  # Delta time normalizado

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Manejar entrada del jugador
    keys = pygame.key.get_pressed()
    player.move(keys, dt)

    # Actualizar el desplazamiento de la cámara
    camera_offset[0] = player.x * TILE_SIZE - SCREEN_WIDTH // 2
    camera_offset[1] = player.y * TILE_SIZE - SCREEN_HEIGHT // 2

    # Dibujar el mapa con desplazamiento de cámara
    screen.fill((0, 0, 0))  # Fondo negro
    # for layer in layers:
    #     layer_data = layer['layer_data']
    #     for row_idx, row in enumerate(layer_data):
    #         for col_idx, tile in enumerate(row):
    #             if tile is not None:
    #                 tileset, tile_idx = tile
    #                 screen.blit(
    #                     tileset[tile_idx],
    #                     (
    #                         col_idx * TILE_SIZE - camera_offset[0],
    #                         row_idx * TILE_SIZE - camera_offset[1],
    #                     ),
    #                 )
    
    draw_layers(screen, layers, TILE_SIZE, camera_offset, SCREEN_WIDTH, SCREEN_HEIGHT,1.3)

    # Dibujar al jugador
    player.draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

    pygame.display.flip()

pygame.quit()
