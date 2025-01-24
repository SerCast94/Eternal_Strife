import pygame
import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class TilesetInfo:
    path: str
    tile_size: int
    columns: int
    rows: int
    tiles: Optional[List[int]] = None
    weights: Optional[List[float]] = None

    def __post_init__(self):
        if self.tiles is None:
            self.tiles = list(range(self.columns * self.rows))

@dataclass
class LayerConfig:
    name: str
    collidable: bool
    visible: bool
    generation_chance: float
    noise_scale: float
    noise_threshold: float
    z_index: int
    tilesets: List[TilesetInfo]

class TileLayer:
    def __init__(self, config: dict, map_width: int, map_height: int, seed: int):
        try:
            print(f"Inicializando TileLayer: {config['name']}")
            self.config = self._create_config(config)
            self.width = map_width
            self.height = map_height
            self.tiles = [[None for _ in range(map_width)] for _ in range(map_height)]
            self.seed = seed
            self.tilesets = self._load_tilesets()
            print(f"TileLayer {config['name']} inicializado correctamente")
        except Exception as e:
            print(f"Error inicializando TileLayer {config['name']}: {e}")
            raise

    def _create_config(self, config: dict) -> LayerConfig:
        tilesets = [TilesetInfo(**tileset) for tileset in config['tilesets']]
        return LayerConfig(**{**config, 'tilesets': tilesets})

    def _load_tilesets(self) -> List[pygame.Surface]:
        try:
            print("Cargando tilesets...")
            tilesets = [pygame.image.load(tileset.path).convert_alpha() 
                        for tileset in self.config.tilesets]
            for i, tileset in enumerate(tilesets):
                print(f"Tileset {i} cargado: {tileset.get_size()}")
            print("Tilesets cargados correctamente")
            return tilesets
        except Exception as e:
            print(f"Error cargando tilesets: {e}")
            raise

    def generate(self):
        try:
            print("Generando TileLayer...")
            random.seed(self.seed)

            for y in range(self.height):
                for x in range(self.width):
                    if random.random() < self.config.generation_chance:
                        tileset_index = random.randrange(len(self.config.tilesets))
                        tileset_info = self.config.tilesets[tileset_index]
                        
                        tile_id = random.choices(
                            tileset_info.tiles,
                            weights=tileset_info.weights,
                            k=1
                        )[0] if tileset_info.weights else random.choice(tileset_info.tiles)
                        
                        self.tiles[y][x] = (tileset_index, tile_id)
                        print(f"Tile set at ({x}, {y}): {self.tiles[y][x]}")
                if y % 10 == 0:
                    print(f"Progreso: {y}/{self.height}")
            print("TileLayer generado correctamente")
        except Exception as e:
            print(f"Error generando TileLayer: {e}")
            raise

class TileMap:
    def __init__(self, settings):
        try:
            print("Inicializando TileMap...")
            self.settings = settings
            self.seed = random.randint(0, 999999)
            self.layers = self._create_layers()
            self.camera_x = 0
            self.camera_y = 0
            print("TileMap inicializado correctamente")
        except Exception as e:
            print(f"Error inicializando TileMap: {e}")
            raise

    def _create_layers(self) -> List[TileLayer]:
        try:
            print("Creando capas de TileMap...")
            layers = []
            for config in sorted(self.settings.layer_configs, 
                               key=lambda x: x['z_index']):
                print(f"Creando capa: {config['name']}")
                layer = TileLayer(
                    config,
                    self.settings.map_width,
                    self.settings.map_height,
                    self.seed
                )
                layer.generate()
                layers.append(layer)
            print("Capas de TileMap creadas correctamente")
            return layers
        except Exception as e:
            print(f"Error creando capas de TileMap: {e}")
            raise

    def update_camera(self, player_x: float, player_y: float):
        # Centrar la cámara en el jugador teniendo en cuenta el factor de zoom
        self.camera_x = player_x - (self.settings.screen_width / self.settings.zoom) // 2
        self.camera_y = player_y - (self.settings.screen_height / self.settings.zoom) // 2
        
        # Limitar la cámara a los bordes del mapa
        self.camera_x = max(0, min(self.camera_x, 
            self.settings.map_width * self.settings.tile_size - self.settings.screen_width / self.settings.zoom))
        self.camera_y = max(0, min(self.camera_y,
            self.settings.map_height * self.settings.tile_size - self.settings.screen_height / self.settings.zoom))

    def get_tile_from_tileset(self, tileset: pygame.Surface, tile_id: int, 
                             tileset_info: TilesetInfo) -> pygame.Surface:
        tile_x = (tile_id % tileset_info.columns) * tileset_info.tile_size
        tile_y = (tile_id // tileset_info.columns) * tileset_info.tile_size
        
        tile_surface = pygame.Surface(
            (tileset_info.tile_size, tileset_info.tile_size),
            pygame.SRCALPHA
        )
        tile_surface.blit(
            tileset, 
            (0, 0),
            (tile_x, tile_y, tileset_info.tile_size, tileset_info.tile_size)
        )
        return tile_surface

    def check_collision(self, rect: pygame.Rect) -> bool:
        tile_x1 = max(0, rect.left // self.settings.tile_size)
        tile_x2 = min(self.settings.map_width - 1, rect.right // self.settings.tile_size)
        tile_y1 = max(0, rect.top // self.settings.tile_size)
        tile_y2 = min(self.settings.map_height - 1, rect.bottom // self.settings.tile_size)

        for layer in self.layers:
            if layer.config.collidable:
                for y in range(tile_y1, tile_y2 + 1):
                    for x in range(tile_x1, tile_x2 + 1):
                        if layer.tiles[y][x] is not None:
                            tile_rect = pygame.Rect(
                                x * self.settings.tile_size,
                                y * self.settings.tile_size,
                                self.settings.tile_size,
                                self.settings.tile_size
                            )
                            if rect.colliderect(tile_rect):
                                return True
        return False

    def draw(self, screen: pygame.Surface):
        # Calcular qué tiles están en la vista
        start_x = int(self.camera_x) // self.settings.tile_size
        start_y = int(self.camera_y) // self.settings.tile_size
        end_x = start_x + self.settings.view_width
        end_y = start_y + self.settings.view_height

        # Asegurar que no nos salimos de los límites del mapa
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.settings.map_width, end_x)
        end_y = min(self.settings.map_height, end_y)

        for layer in self.layers:
            if layer.config.visible:
                for y in range(start_y, end_y):
                    for x in range(start_x, end_x):
                        if layer.tiles[y][x] is not None:
                            tileset_index, tile_id = layer.tiles[y][x]
                            tileset = layer.tilesets[tileset_index]
                            tileset_info = layer.config.tilesets[tileset_index]
                            
                            tile_surface = self.get_tile_from_tileset(
                                tileset,
                                tile_id,
                                tileset_info
                            )
                            
                            screen.blit(
                                tile_surface,
                                (x * self.settings.tile_size - int(self.camera_x),
                                 y * self.settings.tile_size - int(self.camera_y))
                            )