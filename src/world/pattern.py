import pygame

class Pattern:
    def __init__(self, tileset, shape):
        """
        Constructor de la clase Pattern.
        
        Parámetros:
        - tileset: Conjunto de tiles a utilizar en el patrón
        - shape: Matriz que define la forma y configuración del patrón
        
        La matriz shape puede contener:
        - Diccionarios con {'tile': id, 'collidable': bool}
        - Números enteros representando IDs de tiles sin colisión
        - Ceros para espacios vacíos
        """
        self.tileset = tileset
        self.shape = shape

    def apply(self, tilemap, position):
        """
        Aplica el patrón sobre el tilemap en una posición específica.
        
        Parámetros:
        - tilemap: Mapa de tiles donde aplicar el patrón
        - position: Tupla (x, y) indicando la posición inicial
        
        Proceso:
        - Recorre la matriz del patrón celda por celda
        - Si la celda es un diccionario, usa sus propiedades
        - Si la celda es un número != 0, coloca el tile sin colisión
        - Ignora las celdas con valor 0
        """
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if isinstance(cell, dict):
                    tile_id = cell["tile"]
                    collidable = cell["collidable"]
                    tilemap.set_tile(position[0] + x, position[1] + y, self.tileset, tile_id, collidable)
                elif cell != 0:
                    tilemap.set_tile(position[0] + x, position[1] + y, self.tileset, cell, False)