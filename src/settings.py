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
        self.player_scale = 1  # Factor de escala del sprite del jugador

          
        # Configuración de enemigos
        self.enemy_spawn_rate = 1.0  # Tasa base de spawn de enemigos
        self.enemy_speed = 120
        self.enemy_detection_radius = 50
        self.enemy_avoid_force = 0.5
        self.enemy_size = (16, 16)
        self.enemy_scale = 1
        
        # Configuración de optimización
        self.max_enemies = 1000  # Límite máximo de enemigos
        self.enemy_culling_distance = 800  # Distancia para culling de enemigos
        self.collision_check_frequency = 10  # Frames entre chequeos de colisión
    

        # Configuración del mapa
        self.tile_size = 16  # Asegurarse de que el tamaño de los tiles sea consistente
        self.map_width = 30
        self.map_height = 30
        self.view_width = self.screen_width // self.tile_size + 2
        self.view_height = self.screen_height // self.tile_size + 2

        # Configuración de zoom
        self.zoom = 2  # Factor de zoom inicial

        # Ruta base del proyecto
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Configuración de las capas del mapa
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
                        "path": os.path.join(self.base_path, "assets", "images", "tileset_base.png"),
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
                        "path": os.path.join(self.base_path, "assets", "images", "tileset_horizontalpath.png"),
                        "tile_size": 16,
                        "columns": 8,
                        "rows": 8,
                        "tiles": [13, 14, 15],
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
                        "path": os.path.join(self.base_path, "assets", "images", "tileset_decor.png"),
                        "tile_size": 16,
                        "columns": 8,
                        "rows": 8,
                    }
                ]
            }
        ]

        self.animation_configs = {
            "player_idle": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 0, "duration": 0.1},
                    {"index": 1, "duration": 0.1}
                ]
            },
            "player_walk_left": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 10, "duration": 0.1},
                    {"index": 11, "duration": 0.1}
                ]
            },
            "player_walk_right": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 14, "duration": 0.1},
                    {"index": 15, "duration": 0.1}
                ]
            },
            "player_walk_up": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 6, "duration": 0.1},
                    {"index": 7, "duration": 0.1}
                ]
            },
            "player_walk_down": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 2, "duration": 0.1},
                    {"index": 3, "duration": 0.1}
                ]
            },
            "enemy_idle": {
                "spritesheet": "assets/images/Slime1_Walk_body.png",
                "frame_width": 32,
                "frame_height": 32,
                "frames": [
                    {"index": 0, "duration": 0.1} for i in range(5)
                ]
            },
             "slime_idle": {
                "spritesheet": "assets/images/Slime1_Walk_body.png",
                "frame_width": 32,
                "frame_height": 32,
                "frames": [
                    {"index": i, "duration": 0.1} for i in range(6)
                ]
            },
            "ranged_idle": {
                "spritesheet": "assets/images/Slime3_Walk_body.png",
                "frame_width": 32,
                "frame_height": 32,
                "frames": [
                    {"index": i, "duration": 0.1} for i in range(4)
                ]
            }
        }