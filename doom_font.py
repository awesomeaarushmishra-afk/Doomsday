import pygame as pg
import os

class DoomFont:
    def __init__(self, folder='resources/textures/alphabets', char_size=32):
        self.folder = folder
        self.char_size = char_size
        self.chars = {}
        self.load_font()

    def load_font(self):
        # Load a-z
        for i in range(26):
            char = chr(ord('a') + i)
            filename = f'doom-nightmare-{char}.png'
            path = os.path.join(self.folder, filename)
            try:
                img = pg.image.load(path).convert_alpha()
                img = self._fit_to_size(img, self.char_size)
                self.chars[char] = img
            except Exception as e:
                print(f"Missing font: {filename}, using fallback.")
                surf = pg.Surface((self.char_size, self.char_size), pg.SRCALPHA)
                pg.draw.rect(surf, (200,200,200), (2,2,self.char_size-4,self.char_size-4), 1)
                self.chars[char] = surf

        # Load dash
        dash_paths = [
            'resources/textures/doom-nightmare--.png',
            'resources/textures/doom-nightmare-dash.png',
            os.path.join(self.folder, 'doom-nightmare--.png'),
            os.path.join(self.folder, 'doom-nightmare-dash.png'),
        ]
        for path in dash_paths:
            if os.path.exists(path):
                try:
                    img = pg.image.load(path).convert_alpha()
                    img = self._fit_to_size(img, self.char_size)
                    self.chars['-'] = img
                    break
                except:
                    pass
        if '-' not in self.chars:
            print("Dash texture not found, using fallback.")
            surf = pg.Surface((self.char_size, self.char_size), pg.SRCALPHA)
            pg.draw.line(surf, (200,200,200), (4, self.char_size//2), (self.char_size-4, self.char_size//2), 2)
            self.chars['-'] = surf

        # Space width
        self.space_width = self.char_size // 2

    def _fit_to_size(self, img, size):
        """Scale and center image within a square surface."""
        w, h = img.get_size()
        if w > h:
            new_w = size
            new_h = int(h * (size / w))
        else:
            new_h = size
            new_w = int(w * (size / h))
        scaled = pg.transform.smoothscale(img, (new_w, new_h))
        surf = pg.Surface((size, size), pg.SRCALPHA)
        x = (size - new_w) // 2
        y = (size - new_h) // 2
        surf.blit(scaled, (x, y))
        return surf

    def render(self, text, color=(255,255,255), scale=1.0):
        text = text.lower()
        # We'll render at base size then scale the whole surface if needed
        char_size = self.char_size

        # Compute total width
        total_width = 0
        char_surfaces = []
        for ch in text:
            if ch == ' ':
                total_width += self.space_width
                char_surfaces.append(None)
            elif ch in self.chars:
                total_width += char_size
                char_surfaces.append(self.chars[ch])
            else:
                # Unsupported character: skip with small gap
                total_width += char_size // 2
                char_surfaces.append(None)

        # Create surface
        text_surf = pg.Surface((total_width, char_size), pg.SRCALPHA)
        x = 0
        for idx, surf in enumerate(char_surfaces):
            if surf is None:
                x += self.space_width if text[idx] == ' ' else char_size // 2
            else:
                text_surf.blit(surf, (x, 0))
                x += char_size

        # Tint if needed
        if color != (255,255,255):
            colored = pg.Surface(text_surf.get_size(), pg.SRCALPHA)
            colored.fill(color)
            text_surf.blit(colored, (0,0), special_flags=pg.BLEND_RGBA_MULT)

        # Scale if needed
        if scale != 1.0:
            new_w = int(text_surf.get_width() * scale)
            new_h = int(text_surf.get_height() * scale)
            text_surf = pg.transform.smoothscale(text_surf, (new_w, new_h))

        return text_surf