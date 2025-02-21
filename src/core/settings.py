import os

class Settings:
    def __init__(self):
        # Configuración de pantalla
        self.screen_width = 800
        self.screen_height = 600
        self.FPS = 60

        # Optimización de rendering
        self.enable_vsync = False
        self.max_fps = 120

        self.culling_margin = 64
        self.max_visible_entities = 1000
        self.enable_threading = True
        self.thread_pool_size = 4

        self.max_delta_time = 0.1  # Maximum allowed delta time

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

          # Optimización de enemigos
        self.enemy_culling_distance = 600  # Reducido de 800
        self.collision_check_frequency = 15  # Reducida frecuencia de chequeo
        self.max_active_projectiles = 200

        # Configuración del mapa
        self.tile_size = 16  # Asegurarse de que el tamaño de los tiles sea consistente
        self.map_width = 150
        self.map_height = 150
        self.view_width = self.screen_width // self.tile_size + 2
        self.view_height = self.screen_height // self.tile_size + 2

         # Debug and optimization settings
        self.show_culling = False  # Add this line

        self.view_padding = 100  # Pixels to pad the visible area
        self.culling_enabled = True  # Enable visibility culling

        # Configuración de zoom
        self.zoom = 2  # Factor de zoom inicial

        # Ruta base del proyecto
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))

        # Configuración de las etapas de generación del mapa
        self.generation_stages = [
            {
                "name": "base",
                "rules": [
                    {
                        "type": "random",
                        "tileset": {
                            "path": os.path.join(self.base_path, "assets", "images", "tileset_base.png"),
                            "tile_size": 16,
                            "columns": 8,
                            "rows": 8,
                        },
                        "chance": 1.0,
                    }
                ]
            },
            {
                "name": "decoration",
                "rules": [
                    {
                        "type": "random",
                        "tileset": {
                            "path": os.path.join(self.base_path, "assets", "images", "tileset_decor.png"),
                            "tile_size": 16,
                            "columns": 8,
                            "rows": 8,
                        },
                        "chance": 0.1,
                    }
                ]
            },
            {
        "name": "patterns",
        "rules": [
            {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_props.png"),
                    "tile_size": 16,
                    "columns": 8,
                    "rows": 8,
                },
                "pattern": [
                    [0, 0, {"tile": 1, "collidable": True}, 0, 0],
                    [0, {"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}, 0],
                    [{"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}],
                    [0, {"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}, {"tile": 1, "collidable": True}, 0],
                    [0, 0, {"tile": 1, "collidable": True}, 0, 0]
                ],
                "position": (100, 100),
                "chance": 1.0
            },
            {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_plants.png"),
                    "tile_size": 32,
                    "columns": 16,
                    "rows": 16,
                },
                "pattern": [
                    [{"tile": 25, "collidable": False},{"tile": 26, "collidable": False}, {"tile": 27, "collidable": False}],
                    [{"tile": 41, "collidable": False},{"tile": 42, "collidable": False}, {"tile": 43, "collidable": False}],
                    [{"tile": 57, "collidable": False},{"tile": 58, "collidable": True}, {"tile": 59, "collidable": False}],
                    [0,{"tile": 74, "collidable": True}, 0]
                ],
                "chance": 0.01
            },
            {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_props.png"),
                    "tile_size": 32,
                    "columns": 16,
                    "rows": 16,
                },
                "pattern": [
                    [{"tile": 208, "collidable": True}, {"tile": 209, "collidable": True}],
                    [{"tile": 224, "collidable": True}, {"tile": 225, "collidable": True}]
                ],
                "chance": 0.001  # 1% de probabilidad de aparición
            },
            {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_props.png"),
                    "tile_size": 32,
                    "columns": 16,
                    "rows": 16,
                },
                "pattern": [
                    [{"tile": 189, "collidable": True}, {"tile": 190, "collidable": True}],
                    [{"tile": 205, "collidable": True}, {"tile": 206, "collidable": True}]
                ],
                "chance": 0.001  # 1% spawn chance
            },
             {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_rocas.png"),
                    "tile_size": 32,
                    "columns": 2,
                    "rows": 3,
                },
                "pattern": [
                    [{"tile": 2, "collidable": True}]
                ],
                "chance": 0.001
            },
             {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_rocas.png"),
                    "tile_size": 32,
                    "columns": 2,
                    "rows": 3,
                },
                "pattern": [
                    [{"tile": 3, "collidable": True}]
                ],
                "chance": 0.001
            },
             {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_rocas.png"),
                    "tile_size": 32,
                    "columns": 2,
                    "rows": 3,
                },
                "pattern": [
                    [{"tile": 4, "collidable": True}]
                ],
                "chance": 0.001
            },
             {
                "type": "pattern",
                "tileset": {
                    "path": os.path.join(self.base_path, "assets", "images", "tileset_rocas.png"),
                    "tile_size": 32,
                    "columns": 2,
                    "rows": 3,
                },
                "pattern": [
                    [{"tile": 5, "collidable": True}]
                ],
                "chance": 0.001
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
                    {"index": 0, "duration": 0.3},
                    {"index": 1, "duration": 0.3}
                ]
            },
            "player_walk_left": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 10, "duration": 0.3},
                    {"index": 11, "duration": 0.3}
                ]
            },
            "player_walk_right": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 14, "duration": 0.3},
                    {"index": 15, "duration": 0.3}
                ]
            },
            "player_walk_up": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 6, "duration": 0.3},
                    {"index": 7, "duration": 0.3}
                ]
            },
            "player_walk_down": {
                "spritesheet": "assets/images/spritesheet_player.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 2, "duration": 0.3},
                    {"index": 3, "duration": 0.3}
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
                    {"index": i, "duration": 0.3} for i in range(6)
                ]
            },
            "ranged_idle": {
                "spritesheet": "assets/images/Slime3_Walk_body.png",
                "frame_width": 32,
                "frame_height": 32,
                "frames": [
                    {"index": i, "duration": 0.3} for i in range(4)
                ]
            },
            "gem_idle": {
                "spritesheet": "assets/images/item.png",
                "frame_width": 32,
                "frame_height": 32,
                "frames": [
                    {"index": 0, "duration": 0.3},
                ]
            },
            "tuna_idle": {
                "spritesheet": "assets/images/pescaito.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": 0, "duration": 0.3},
                ]
            },
            "fireball_idle": {
                "spritesheet": "assets/images/player_attack.png",
                "frame_width": 32,
                "frame_height": 32,
                "frames": [
                    {"index": i, "duration": 0.03} for i in range(30)
                ]
            },
            "enemy_projectile_idle": {
                "spritesheet": "assets/images/spritesheet_fireball.png",
                "frame_width": 16,
                "frame_height": 16,
                "frames": [
                    {"index": i, "duration": 0.01} for i in range(4)

                ]
            }
        }