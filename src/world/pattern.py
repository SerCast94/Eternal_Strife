import pygame

class Pattern:
    def __init__(self, tileset, shape):
        self.tileset = tileset
        self.shape = shape

    def apply(self, tilemap, position):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if isinstance(cell, dict):
                    tile_id = cell["tile"]
                    collidable = cell["collidable"]
                    tilemap.set_tile(position[0] + x, position[1] + y, self.tileset, tile_id, collidable)
                elif cell != 0:
                    tilemap.set_tile(position[0] + x, position[1] + y, self.tileset, cell, False)