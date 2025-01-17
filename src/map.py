import pygame
import random
import time

def load_tileset(filename, tile_size, tileset_size):
    """
    Carga un tileset y lo divide en tiles individuales.
    """
    tileset_image = pygame.image.load(filename).convert_alpha()
    tiles = []
    for y in range(0, tileset_size, tile_size):
        for x in range(0, tileset_size, tile_size):
            tile = tileset_image.subsurface((x, y, tile_size, tile_size))
            tiles.append(tile)
    return tiles

def generate_layer(width, height, tilesets, generation_probability):
    """
    Genera una capa del mapa con tiles seleccionados aleatoriamente
    de los tilesets proporcionados, pero sólo si pasa una probabilidad de generación por celda.
    """
    # Establecer una semilla aleatoria basada en el tiempo actual
    random.seed(time.time())
    
    layer_data = []
    
    for _ in range(height):
        row = []
        for _ in range(width):
            # Generar un número aleatorio entre 0 y 1
            if random.random() <= generation_probability:
                # Si el número es menor o igual a la probabilidad de generación, seleccionamos un tile
                tileset = random.choice(tilesets)
                tile_idx = random.randint(0, len(tileset) - 1)  # Elegir aleatoriamente un tile
                row.append((tileset, tile_idx))
            else:
                # Si no se genera un tile, se asigna None o algún marcador de "vacío"
                row.append(None)
        layer_data.append(row)
    
    return layer_data

def draw_layers(screen, layers, tile_size, camera_offset, screen_width, screen_height, zoom):
    """
    Dibuja las capas del mapa con un factor de zoom.
    :param screen: Superficie de pygame.
    :param layers: Lista de capas con datos y tilesets.
    :param tile_size: Tamaño base de los tiles.
    :param camera_offset: Desplazamiento de la cámara (x, y).
    :param screen_width: Ancho de la pantalla.
    :param screen_height: Alto de la pantalla.
    :param zoom: Factor de zoom aplicado al mapa.
    """
    scaled_tile_size = int(tile_size * zoom)  # Tamaño de los tiles escalados por el zoom

    # Asegurar que el desplazamiento de la cámara sea entero
    offset_x = int(camera_offset[0])
    offset_y = int(camera_offset[1])

    # Calcular el rango visible (convertir a entero explícitamente)
    start_col = max(0, offset_x // scaled_tile_size)  # Columna inicial
    end_col = min(len(layers[0]['layer_data'][0]), (offset_x + screen_width) // scaled_tile_size + 1)  # Columna final
    start_row = max(0, offset_y // scaled_tile_size)  # Fila inicial
    end_row = min(len(layers[0]['layer_data']), (offset_y + screen_height) // scaled_tile_size + 1)  # Fila final

    # Dibujar solo los tiles visibles
    for layer in layers:
        layer_data = layer['layer_data']
        for row_idx in range(int(start_row), int(end_row)):  # Convertir a entero por seguridad
            for col_idx in range(int(start_col), int(end_col)):  # Convertir a entero por seguridad
                tile = layer_data[int(row_idx)][int(col_idx)]
                if tile is not None:
                    tileset, tile_idx = tile
                    # Escalar el tile según el zoom
                    scaled_tile = pygame.transform.scale(tileset[tile_idx], (scaled_tile_size, scaled_tile_size))
                    # Dibujar el tile escalado
                    screen.blit(
                        scaled_tile,
                        (
                            col_idx * scaled_tile_size - offset_x,
                            row_idx * scaled_tile_size - offset_y,
                        ),
                    )


