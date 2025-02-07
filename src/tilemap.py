import pygame
import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pattern import Pattern

@dataclass
class TilesetInfo:
    path: str
    tile_size: int
    columns: int
    rows: int

@dataclass
class GenerationRule:
    type: str
    tileset: TilesetInfo
    chance: Optional[float] = None
    pattern: Optional[List[List[Dict[str, any]]]] = None
    position: Optional[Tuple[int, int]] = None
    collidable: Optional[bool] = False
    tiles: Optional[List[Dict[str, any]]] = None  # Lista de tiles y sus pesos

@dataclass
class GenerationStage:
    name: str
    rules: List[GenerationRule]

@dataclass
class Tile:
    surface: pygame.Surface
    x: int
    y: int
    layer: int
    collidable: bool
    is_pattern: bool

class TileMap:
    def __init__(self, settings):
        try:
            print("Inicializando TileMap...")
            self.settings = settings
            self.seed = random.randint(0, 999999)
            self.base_layer = [[None for _ in range(settings.map_width)] for _ in range(settings.map_height)]  # Capa base
            self.medium_layer = []  # Lista de tiles de capas posteriores a la base
            self.pattern_tiles = []  # Lista de tiles de patrones
            self.collidables = set()
            self.stages = self._create_stages()
            self.camera_x = 0
            self.camera_y = 0
            self.player_start_pos = (settings.map_width // 2, settings.map_height // 2)  # Posición inicial del jugador
            self.safe_radius = 5  # Radio seguro alrededor del jugador donde no se generarán colisiones
            self.generated_patterns = []  # Lista para almacenar los patrones generados
            print("TileMap inicializado correctamente")
        except Exception as e:
            print(f"Error inicializando TileMap: {e}")
            raise

    def _create_stages(self) -> List[GenerationStage]:
        try:
            print("Creando etapas de generación de TileMap...")
            stages = []
            for stage_config in self.settings.generation_stages:
                rules = [GenerationRule(
                    type=rule['type'],
                    tileset=TilesetInfo(**rule['tileset']),
                    chance=rule.get('chance'),
                    pattern=rule.get('pattern'),
                    position=rule.get('position'),
                    collidable=rule.get('collidable', False),
                    tiles=rule.get('tiles')
                ) for rule in stage_config['rules']]
                stage = GenerationStage(stage_config['name'], rules)
                stages.append(stage)
            print("Etapas de generación de TileMap creadas correctamente")
            return stages
        except Exception as e:
            print(f"Error creando etapas de generación de TileMap: {e}")
            raise

    def _load_tileset(self, tileset_info: TilesetInfo) -> pygame.Surface:
        try:
            tileset = pygame.image.load(tileset_info.path).convert_alpha()
            return tileset
        except Exception as e:
            print(f"Error cargando tileset: {e}")
            raise

    def _get_tile_from_tileset(self, tileset: pygame.Surface, tile_id: int, tileset_info: TilesetInfo) -> pygame.Surface:
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

    def _choose_tile(self, rule: GenerationRule) -> int:
        if rule.tiles:
            tiles = [tile["tile"] for tile in rule.tiles]
            weights = [tile["weight"] for tile in rule.tiles]
            return random.choices(tiles, weights=weights, k=1)[0]
        else:
            return random.randint(0, rule.tileset.columns * rule.tileset.rows - 1)

    def _is_within_safe_radius(self, x, y):
        player_x, player_y = self.player_start_pos
        distance = ((x - player_x) ** 2 + (y - player_y) ** 2) ** 0.5
        return distance < self.safe_radius

    def generate(self):
        try:
            print("Generando TileMap...")
            random.seed(self.seed)

            for stage in self.stages:
                for rule in stage.rules:
                    if not rule.tileset:
                        print(f"Error: La regla de generación no tiene un tileset definido: {rule}")
                        continue

                    tileset = self._load_tileset(rule.tileset)
                    if rule.type == "random":
                        for y in range(self.settings.map_height):
                            for x in range(self.settings.map_width):
                                if random.random() < rule.chance and not (rule.collidable and self._is_within_safe_radius(x, y)):
                                    tile_id = self._choose_tile(rule)
                                    tile_surface = self._get_tile_from_tileset(tileset, tile_id, rule.tileset)
                                    scaled_tile_surface = pygame.transform.scale(tile_surface, (int(16 * self.settings.zoom), int(16 * self.settings.zoom)))
                                    if stage.name == "base":
                                        self.base_layer[y][x] = scaled_tile_surface
                                    else:
                                        self.medium_layer.append(Tile(scaled_tile_surface, x, y, 1, rule.collidable, False))
                                    if rule.collidable:
                                        self.collidables.add((x, y))
                    elif rule.type == "pattern":
                        if rule.position:
                            self._place_pattern(rule, tileset, rule.position[0], rule.position[1])
                            self.generated_patterns.append((rule, rule.position))
                        elif rule.chance:
                            self._place_random_pattern(rule, tileset)
            print("TileMap generado correctamente")
            self._log_generated_patterns()
        except Exception as e:
            print(f"Error generando TileMap: {e}")
            raise

    def _place_pattern(self, rule, tileset, pos_x, pos_y):
        if not rule.pattern:
            print(f"Error: La regla de generación de patrón no tiene un patrón definido: {rule}")
            return

        pattern_height = len(rule.pattern)
        pattern_width = len(rule.pattern[0])
        for py in range(pattern_height):
            for px in range(pattern_width):
                cell = rule.pattern[py][px]
                if isinstance(cell, dict):
                    tile_id = cell["tile"]
                    collidable = cell["collidable"]
                    x = pos_x + px
                    y = pos_y + py
                    if not (collidable and self._is_within_safe_radius(x, y)):
                        tile_surface = self._get_tile_from_tileset(tileset, tile_id, rule.tileset)
                        scaled_tile_surface = pygame.transform.scale(tile_surface, (int(16 * self.settings.zoom), int(16 * self.settings.zoom)))
                        self.pattern_tiles.append(Tile(scaled_tile_surface, x, y, 1, collidable, True))
                        if collidable:
                            self.collidables.add((x, y))
                elif cell != 0:
                    x = pos_x + px
                    y = pos_y + py
                    tile_surface = self._get_tile_from_tileset(tileset, cell, rule.tileset)
                    scaled_tile_surface = pygame.transform.scale(tile_surface, (int(16 * self.settings.zoom), int(16 * self.settings.zoom)))
                    self.pattern_tiles.append(Tile(scaled_tile_surface, x, y, 1, False, True))

    def _place_random_pattern(self, rule, tileset):
        if not rule.pattern:
            print(f"Error: La regla de generación de patrón aleatorio no tiene un patrón definido: {rule}")
            return

        pattern_height = len(rule.pattern)
        pattern_width = len(rule.pattern[0])
        for _ in range(int(self.settings.map_width * self.settings.map_height * rule.chance)):
            pos_x = random.randint(0, self.settings.map_width - pattern_width)
            pos_y = random.randint(0, self.settings.map_height - pattern_height)
            if not any(self._is_within_safe_radius(pos_x + px, pos_y + py) for py in range(pattern_height) for px in range(pattern_width)):
                self._place_pattern(rule, tileset, pos_x, pos_y)
                self.generated_patterns.append((rule, (pos_x, pos_y)))

    def _log_generated_patterns(self):
        print("Patrones generados:")
        for rule, position in self.generated_patterns:
            print(f"Patrón '{rule.tileset.path}' generado en posición {position}")

    def update_camera(self, player_x: float, player_y: float):
        # Centrar la cámara en el jugador teniendo en cuenta el factor de zoom
        self.camera_x = player_x - (self.settings.screen_width / self.settings.zoom) // 2
        self.camera_y = player_y - (self.settings.screen_height / self.settings.zoom) // 2
        
        # Limitar la cámara a los bordes del mapa
        self.camera_x = max(0, min(self.camera_x, 
            self.settings.map_width * self.settings.tile_size - self.settings.screen_width / self.settings.zoom))
        self.camera_y = max(0, min(self.camera_y,
            self.settings.map_height * self.settings.tile_size - self.settings.screen_height / self.settings.zoom))

    def check_collision(self, rect: pygame.Rect) -> bool:
        tile_x1 = max(0, rect.left // self.settings.tile_size)
        tile_x2 = min(self.settings.map_width - 1, rect.right // self.settings.tile_size)
        tile_y1 = max(0, rect.top // self.settings.tile_size)
        tile_y2 = min(self.settings.map_height - 1, rect.bottom // self.settings.tile_size)

        for y in range(tile_y1, tile_y2 + 1):
            for x in range(tile_x1, tile_x2 + 1):
                if (x, y) in self.collidables:
                    tile_rect = pygame.Rect(
                        x * self.settings.tile_size,
                        y * self.settings.tile_size,
                        self.settings.tile_size,
                        self.settings.tile_size
                    )
                    if rect.colliderect(tile_rect):
                        return True
        return False

    def draw_base_layer(self, screen: pygame.Surface):
        # Calcular qué tiles están en la vista
        start_x = int(self.camera_x) // self.settings.tile_size
        start_y = int(self.camera_y) // self.settings.tile_size
        end_x = start_x + int(self.settings.view_width * self.settings.zoom)
        end_y = start_y + int(self.settings.view_height * self.settings.zoom)

        # Asegurar que no nos salimos de los límites del mapa
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.settings.map_width, end_x)
        end_y = min(self.settings.map_height, end_y)

        # Dibujar capa base
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if self.base_layer[y][x] is not None:
                    screen.blit(
                        self.base_layer[y][x],
                        (x * 16 * self.settings.zoom - int(self.camera_x * self.settings.zoom),
                         y * 16 * self.settings.zoom - int(self.camera_y * self.settings.zoom))
                    )

    def draw_medium_layer(self, screen: pygame.Surface):
        # Calcular qué tiles están en la vista
        start_x = int(self.camera_x) // self.settings.tile_size
        start_y = int(self.camera_y) // self.settings.tile_size
        end_x = start_x + int(self.settings.view_width * self.settings.zoom)
        end_y = start_y + int(self.settings.view_height * self.settings.zoom)

        # Asegurar que no nos salimos de los límites del mapa
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.settings.map_width, end_x)
        end_y = min(self.settings.map_height, end_y)

        # Dibujar capa media
        for tile in self.medium_layer:
            if start_x <= tile.x < end_x and start_y <= tile.y < end_y:
                tile_pos = (tile.x * 16 * self.settings.zoom - int(self.camera_x * self.settings.zoom),
                            tile.y * 16 * self.settings.zoom - int(self.camera_y * self.settings.zoom))
                screen.blit(tile.surface, tile_pos)

    def draw_overlay_layer(self, screen: pygame.Surface, player_rect: pygame.Rect):
        # Calcular qué tiles están en la vista
        start_x = int(self.camera_x) // self.settings.tile_size
        start_y = int(self.camera_y) // self.settings.tile_size
        end_x = start_x + int(self.settings.view_width * self.settings.zoom)
        end_y = start_y + int(self.settings.view_height * self.settings.zoom)

        # Asegurar que no nos salimos de los límites del mapa
        start_x = max(0, start_x)
        start_y = max(0, start_y)
        end_x = min(self.settings.map_width, end_x)
        end_y = min(self.settings.map_height, end_y)

        # Dibujar tiles de patrones con transparencia si el jugador está en la misma posición
        self.pattern_tiles.sort(key=lambda tile: tile.y)
        for tile in self.pattern_tiles:
            if start_x <= tile.x < end_x and start_y <= tile.y < end_y:
                tile_pos = (tile.x * 16 * self.settings.zoom - int(self.camera_x * self.settings.zoom),
                            tile.y * 16 * self.settings.zoom - int(self.camera_y * self.settings.zoom))
                if not tile.collidable:
                    transparent_surface = tile.surface.copy()
                    transparent_surface.set_alpha(128)
                    screen.blit(transparent_surface, tile_pos)
                else:
                    screen.blit(tile.surface, tile_pos)
                    