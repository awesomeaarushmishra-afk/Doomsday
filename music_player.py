import os
import random
import pygame as pg
from utils import resource_path

class MusicPlayer:
    def __init__(self, folder="music"):
        self.folder = resource_path(folder)
        self.library = self.scan_folder()
        self.current_idx = 0 if self.library else None
        self.playing = False
        self.volume = 0.7
        self.shuffle = False
        self.repeat = False

        if self.library:
            if not pg.mixer.get_init():
                pg.mixer.init()
            pg.mixer.music.set_volume(self.volume)

    def scan_folder(self):
        tracks = []
        if not os.path.exists(self.folder):
            os.makedirs(self.folder, exist_ok=True)
            return tracks
        for f in os.listdir(self.folder):
            if f.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                path = os.path.join(self.folder, f)
                title = os.path.splitext(f)[0]
                tracks.append({"title": title, "file": path})
        return tracks

    def play(self, idx=None):
        if idx is None:
            idx = self.current_idx or 0
        if not self.library or idx >= len(self.library):
            return
        self.current_idx = idx
        try:
            if not pg.mixer.get_init():
                pg.mixer.init()
            pg.mixer.music.load(self.library[idx]["file"])
            pg.mixer.music.play(-1 if self.repeat else 0)
            self.playing = True
        except Exception as e:
            print("Music play error:", e)

    def toggle(self):
        if self.playing:
            pg.mixer.music.pause()
            self.playing = False
        else:
            pg.mixer.music.unpause()
            self.playing = True

    def next(self):
        if not self.library:
            return
        if self.shuffle:
            self.current_idx = random.randint(0, len(self.library)-1)
        else:
            self.current_idx = (self.current_idx + 1) % len(self.library)
        self.play(self.current_idx)

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        pg.mixer.music.set_volume(self.volume)

    def current_track_title(self):
        if self.current_idx is not None and self.library:
            return self.library[self.current_idx].get("title", "Unknown")
        return "No music"