import os

class Settings:
    def __init__(self):
        # Configuración de pantalla
        self.screen_width = 800
        self.screen_height = 600
        self.FPS = 60

        # Configuración del jugador
        self.player_speed = 150
        self.player_health = 100
        self.player_size = (16, 16)  # Asegurarse de que el tamaño del jugador sea consistente

        # Configuración de enemigos
        self.enemy_speed = 100
        self.enemy_spawn_rate = 2.0
        self.enemy_size = (16, 16)  # Asegurarse de que el tamaño de los enemigos sea consistente

        # Configuración del mapa
        self.tile_size = 16  # Asegurarse de que el tamaño de los tiles sea consistente
        self.map_width = 100
        self.map_height = 100
        self.view_width = self.screen_width // self.tile_size + 2
        self.view_height = self.screen_height // self.tile_size + 2

        # Configuración de zoom
        self.zoom = 2.0  # Factor de zoom inicial

        # Ruta base del proyecto
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Configuración de las capas del mapa
        # Estructura de la configuración de las capas (layer_configs):
        # Cada capa está representada por un diccionario con los siguientes campos:
        #   - name: Nombre de la capa.
        #   - collidable: Indica si la capa es colisionable (True o False).
        #   - visible: Indica si la capa es visible (True o False).
        #   - generation_chance: Probabilidad de generación de tiles en esta capa (valor entre 0 y 1).
        #   - noise_scale: Escala del ruido para la generación de tiles (valor flotante).
        #   - noise_threshold: Umbral de ruido para la generación de tiles (valor flotante).
        #   - z_index: Índice Z para el orden de renderizado de la capa (valor entero).
        #   - tilesets: Lista de tilesets utilizados en esta capa. Cada tileset es un diccionario con los siguientes campos:
        #   - path: Ruta de la imagen del tileset.
        #   - tile_size: Tamaño de cada tile en píxeles (valor entero). Tener en cuenta la resolucion de los tiles.
        #   - columns: Número de columnas en el tileset (valor entero). Resolucion del tileset dividido por el tamaño de los tiles.
        #   - rows: Número de filas en el tileset (valor entero). Resolucion del tileset dividido por el tamaño de los tiles
        #   - tiles (opcional): Lista de IDs de tiles específicos que se pueden usar. Si no se especifica, se utilizarán todas las tiles del tileset.
        #   - weights (opcional): Pesos para la selección aleatoria de tiles. Debe tener la misma longitud que la lista de tiles.
        self.layer_configs = [
            {
                "name": "background",
                "collidable": False,
                "visible": True,
                "generation_chance": 1.0,
                "noise_scale": 0.1,
                "noise_threshold": 0.0,
                "z_index": 0,
                "tilesets": [
                    {
                        "path": os.path.join(base_path, "assets", "images", "tileset_base.png"),
                        "tile_size": 16,
                        "columns": 8,
                        "rows": 8,
                    }
                ]
            },
            {
                "name": "terrain",
                "collidable": True,
                "visible": True,
                "generation_chance": 0.01,
                "noise_scale": 0.2,
                "noise_threshold": 0.4,
                "z_index": 2,
                "tilesets": [
                    {
                        "path": os.path.join(base_path, "assets", "images", "tileset_horizontalpath.png"),
                        "tile_size": 16,
                        "columns": 8,
                        "rows": 8,
                        "tiles": [13,14,15],
                        "weights": [0.7, 0.2, 0.1]
                    }
                ]
            },
            {
                "name": "decoration",
                "collidable": False,
                "visible": True,
                "generation_chance": 0.3,
                "noise_scale": 0.3,
                "noise_threshold": 0.6,
                "z_index": 1,
                "tilesets": [
                    {
                        "path": os.path.join(base_path, "assets", "images", "tileset_decor.png"),
                        "tile_size": 16,
                        "columns": 8,
                        "rows": 8,
                        "tiles": [0, 1, 2,3,4,5,6,7,8,9]
                    }
                ]
            }
        ]