import pygame
import os


class SoundHandler:
    def __init__(self):
        self._music_initialized = False

    def init_music(self):
        if not self._music_initialized:
            try:
                pygame.mixer.init()
                self._music_initialized = True
            except pygame.error as e:
                raise RuntimeError(f"Failed to initialize music: {e}")

    def play_background_music(self, loop: bool = True):
        self.init_music()
        path = os.path.join("assets", "sounds", "background_music.wav")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Music file not found: {path}")
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
        except pygame.error as e:
            raise RuntimeError(f"Failed to play music: {e}")

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            raise RuntimeError(f"Failed to stop music: {e}")

    def cleanup(self):
        if self._music_initialized:
            pygame.mixer.quit()
