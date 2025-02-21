# src/music_player.py

import pygame
import os
import random

class MusicPlayer:
    
    def __init__(self, screen):
        """
        Constructor del reproductor de música.
        Inicializa:
        - Sistema de audio de pygame
        - Listas de reproducción (menú, juego, otros)
        - Estados de reproducción
        - Sistema de visualización de canciones
        - Configuración de volumen
        """
        pygame.mixer.init()
        
        self.screen = screen
        self.current_song = None
        self.previous_state = None  # Añadir variable para guardar estado anterior
        self.music_folder = "assets/sounds/music"
        self.show_song_timer = 0
        self.show_song_duration = 3000  # Duración en milisegundos (3 segundos)

        
        # Diccionario para almacenar las listas de reproducción
        self.playlists = {
            "menu": [],
            "game": [],
            "others": []
        }
        
        # Estado de cada playlist
        self.playlist_states = {
            "menu": {"last_song": None, "position": 0},
            "game": {"last_song": None, "position": 0},
            "others": {"last_song": None, "position": 0}
        }
        
        self.current_playlist = "menu"
        self.load_songs()
        self.font = pygame.font.Font("assets/fonts/EldringBold.ttf", 20)
        pygame.mixer.music.set_volume(0.5)


    def save_current_state(self):
        """
        Guarda el estado actual de la playlist.
        Almacena:
        - Canción actual
        - Posición de reproducción en segundos
        Solo guarda si hay música reproduciéndose.
        """
        if pygame.mixer.music.get_busy():
            self.playlist_states[self.current_playlist].update({
                "last_song": self.current_song,
                "position": pygame.mixer.music.get_pos() / 1000.0  # Convertir a segundos
            })

    def play_once(self, sound_name, reset_state=True):
        """
        Reproduce un sonido de la lista 'others' una sola vez.
        Parámetros:
        - sound_name: Nombre del sonido a reproducir
        - reset_state: Si debe restaurar el estado anterior al terminar
        Guarda el estado actual antes de reproducir.
        """
        try:
            # Buscar el sonido en la lista others
            sound_file = None
            for file in self.playlists["others"]:
                if sound_name in file:
                    sound_file = file
                    break
            
            if sound_file:
                # Guardar estado actual en la variable de clase
                self.previous_state = {
                    "song": self.current_song,
                    "playlist": self.current_playlist,
                    "position": pygame.mixer.music.get_pos() / 1000.0 if pygame.mixer.music.get_busy() else 0
                }
                
                # Reproducir el sonido
                pygame.mixer.music.load(os.path.join(self.music_folder, sound_file))
                pygame.mixer.music.play()
                
                if reset_state:
                    self.restore_previous_state()
                    
        except Exception as e:
            print(f"Error reproduciendo sonido {sound_name}: {e}")

    def restore_previous_state(self):
        """
        Restaura el estado anterior guardado.
        Recupera:
        - Canción anterior
        - Posición de reproducción
        - Playlist actual
        """
        if self.previous_state and self.previous_state["song"]:
            pygame.mixer.music.load(os.path.join(self.music_folder, self.previous_state["song"]))
            pygame.mixer.music.play(start=self.previous_state["position"])
            self.current_song = self.previous_state["song"]
            self.current_playlist = self.previous_state["playlist"]


    def restore_state(self, playlist_type):
        """
        Restaura el estado guardado de una playlist específica.
        Parámetros:
        - playlist_type: Tipo de playlist a restaurar
        Si no hay estado guardado, reproduce una canción aleatoria.
        """
        state = self.playlist_states[playlist_type]
        if state["last_song"]:
            self.current_song = state["last_song"]
            pygame.mixer.music.load(os.path.join(self.music_folder, self.current_song))
            pygame.mixer.music.play(start=state["position"])
        else:
            self.play_random(playlist_type)

    def change_playlist(self, playlist_type):
        """
        Cambia a una lista de reproducción específica.
        Parámetros:
        - playlist_type: Tipo de playlist a cambiar
        Guarda el estado actual antes de cambiar.
        """
        if playlist_type in self.playlists and self.current_playlist != playlist_type:
            # Guardar estado actual
            self.save_current_state()
            
            # Detener reproducción actual
            self.stop()
            
            # Cambiar playlist
            self.current_playlist = playlist_type
            print(f"Cambiando a lista de reproducción: {playlist_type}")
            # Restaurar estado de la nueva playlist
            self.restore_state(playlist_type)
            self.show_song_timer = pygame.time.get_ticks()  # Reiniciar temporizador



    def play_random(self, playlist_type=None):
        """
        Reproduce una canción aleatoria de la lista especificada.
        Parámetros:
        - playlist_type: Tipo de playlist opcional
        Evita repetir la última canción si hay más disponibles.
        """
        if playlist_type:
            self.current_playlist = playlist_type
            
        current_songs = self.playlists[self.current_playlist]
        if not current_songs:
            return
            
        # Evitar repetir la misma canción si hay más de una
        available_songs = [song for song in current_songs 
                         if song != self.playlist_states[self.current_playlist]["last_song"]]
        if not available_songs and current_songs:
            available_songs = current_songs
            
        self.current_song = random.choice(available_songs)
        self.playlist_states[self.current_playlist]["last_song"] = self.current_song
        self.playlist_states[self.current_playlist]["position"] = 0
        
        pygame.mixer.music.load(os.path.join(self.music_folder, self.current_song))
        pygame.mixer.music.play()
        self.show_song_timer = pygame.time.get_ticks()  # Reiniciar temporizador


    def load_songs(self):
        """
        Carga y clasifica las canciones en sus respectivas listas.
        Clasifica según sufijos:
        - _menu: Para menú
        - _game: Para juego
        - otros: Sin sufijo específico
        """
        try:
            for file in os.listdir(self.music_folder):
                if not file.endswith(('.mp3', '.wav', '.ogg')):
                    continue
                # Clasificar la canción según su sufijo
                if "_menu." in file:
                    self.playlists["menu"].append(file)
                elif "_game." in file:
                    self.playlists["game"].append(file)
                else:
                    # Si no tiene sufijo, añadirla a la lista del juego
                    self.playlists["others"].append(file)
                    
        except Exception as e:
            print(f"Error cargando música: {e}")

    def update(self):
        """
        Verifica si la canción terminó y reproduce la siguiente.
        Se ejecuta en cada frame del juego.
        """
        if not pygame.mixer.music.get_busy():
            self.play_random()

    def draw(self, screen):
        """
        Dibuja el nombre de la canción actual con efecto de fundido.
        Características:
        - Muestra el título durante 3 segundos
        - Aplica efecto de fundido el último segundo
        - Ajusta el texto a un ancho máximo
        - Muestra símbolo musical (♫)
        """
        current_time = pygame.time.get_ticks()
        if not self.current_song:
            return
            
        # Calcular opacidad basada en el tiempo
        elapsed_time = current_time - self.show_song_timer
        if elapsed_time > self.show_song_duration:
            return
            
        # Calcular alpha (opacidad)
        # Mantener opacidad completa durante 2 segundos, luego fundir durante 1 segundo
        fade_duration = 1000  # 1 segundo de fundido
        if elapsed_time < (self.show_song_duration - fade_duration):
            alpha = 255
        else:
            fade_progress = (self.show_song_duration - elapsed_time) / fade_duration
            alpha = max(0, min(255, int(255 * fade_progress)))
        
        # Configuración
        MAX_WIDTH = 200
        LINE_SPACING = 25
        MARGIN_RIGHT = 10
        MARGIN_TOP = 10
        
        # Remover extensión y etiquetas
        song_name = os.path.splitext(self.current_song)[0]
        song_name = song_name.replace("_menu", "").replace("_game", "")
        words = song_name.split()
        lines = []
        current_line = "♫ "
        
        # Dividir el texto en líneas
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.font.render(test_line, True, (255, 255, 255))
            
            if test_surface.get_width() > MAX_WIDTH:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        
        # Añadir la última línea
        if current_line:
            lines.append(current_line)
        
        # Dibujar cada línea con transparencia
        for i, line in enumerate(lines):
            # Renderizar texto en una superficie temporal
            text = self.font.render(line, True, (255, 255, 255))
            
            # Crear superficie con canal alpha
            text_alpha = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            text_alpha.fill((255, 255, 255, alpha))
            
            # Aplicar alpha al texto
            text.blit(text_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Posicionar y dibujar
            text_rect = text.get_rect(
                topright=(self.screen.get_width() - MARGIN_RIGHT, 
                        MARGIN_TOP + i * LINE_SPACING)
            )
            screen.blit(text, text_rect)


    def set_volume(self, volume):
        """
        Ajusta el volumen de reproducción.
        Parámetros:
        - volume: Valor entre 0.0 y 1.0
        """
        pygame.mixer.music.set_volume(volume)

    def stop(self):
        """
        Detiene la reproducción de música actual.
        """
        pygame.mixer.music.stop()

    def pause(self):
        """
        Pausa la reproducción de música actual.
        """
        pygame.mixer.music.pause()

    def unpause(self):
        """
        Reanuda la reproducción de música pausada.
        """
        pygame.mixer.music.unpause()
    
    def get_volume(self):
        """
        Obtiene el volumen actual de reproducción.
        Retorna:
        - Valor entre 0.0 y 1.0
        """
        return pygame.mixer.music.get_volume()