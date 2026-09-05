import pygame as pg
import os
from settings import RENDER_WIDTH, RENDER_HEIGHT

class DeveloperRoom:
    def __init__(self, game):
        self.game = game
        self.images = []
        self.current_index = 0
        self.font = pg.font.SysFont("Arial", 24)
        self.load_images()

    def load_images(self):
        folder = 'resources/textures/developeronly'
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        for f in os.listdir(folder):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                try:
                    img = pg.image.load(os.path.join(folder, f)).convert_alpha()
                    # Scale to fit screen with aspect ratio
                    w, h = img.get_size()
                    scale_w = RENDER_WIDTH / w
                    scale_h = RENDER_HEIGHT / h
                    scale = min(scale_w, scale_h) * 0.9
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    img = pg.transform.smoothscale(img, (new_w, new_h))
                    self.images.append(img)
                except Exception as e:
                    print("Failed to load image:", f, e)
        if not self.images:
            # Fallback: a text surface
            surf = pg.Surface((RENDER_WIDTH, RENDER_HEIGHT), pg.SRCALPHA)
            surf.fill((50, 50, 50))
            txt = self.font.render("No media found. Place images in resources/textures/developeronly/", True, (255,255,255))
            surf.blit(txt, (RENDER_WIDTH//2 - txt.get_width()//2, RENDER_HEIGHT//2))
            self.images.append(surf)

    def update(self):
        pass  # idle

    def draw(self):
        screen = self.game.render_surface
        screen.fill((20, 20, 20))
        if self.images:
            img = self.images[self.current_index]
            x = (RENDER_WIDTH - img.get_width()) // 2
            y = (RENDER_HEIGHT - img.get_height()) // 2
            screen.blit(img, (x, y))
        # Instructions
        instr = self.font.render("ESC to exit | Left/Right to browse", True, (200, 200, 200))
        screen.blit(instr, (20, RENDER_HEIGHT - 40))
        # Index
        idx_text = self.font.render(f"{self.current_index+1}/{len(self.images)}", True, (200, 200, 200))
        screen.blit(idx_text, (RENDER_WIDTH - idx_text.get_width() - 20, RENDER_HEIGHT - 40))

    def next_image(self):
        if self.images:
            self.current_index = (self.current_index + 1) % len(self.images)

    def prev_image(self):
        if self.images:
            self.current_index = (self.current_index - 1) % len(self.images)