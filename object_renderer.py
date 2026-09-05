import pygame as pg
from settings import *
from doom_font import DoomFont

class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.render_surface
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (RENDER_WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', (RENDER_WIDTH, RENDER_HEIGHT))

        # Health digit textures
        self.digit_size = int(90 * (RENDER_WIDTH / 800))
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))

        # Doom font for music & game over (used by main)
        self.doom_font = DoomFont(char_size=24)

        # Heartbar texture
        try:
            self.heartbar_texture = pg.image.load('resources/textures/heartbar.png').convert_alpha()
            self.heart_size = 30
            self.heartbar_texture = pg.transform.scale(self.heartbar_texture, (self.heart_size, self.heart_size))
        except Exception as e:
            print(f"Heartbar texture not found: {e}")
            self.heartbar_texture = None

        self.game_over_image = self.get_texture('resources/textures/game_over.png', (RENDER_WIDTH, RENDER_HEIGHT))
        self.win_image = self.get_texture('resources/textures/win.png', (RENDER_WIDTH, RENDER_HEIGHT))

    def draw(self):
        self.draw_background()
        self.render_game_objects()

    def draw_player_health(self):
        health = str(self.game.player.health)
        x = 20
        y = 20
        for i, char in enumerate(health):
            if char in self.digits:
                self.screen.blit(self.digits[char], (x + i * self.digit_size, y))
        self.screen.blit(self.digits['10'], (x + len(health) * self.digit_size, y))

    def draw_lives(self):
        lives = self.game.player.lives
        if lives < 0:
            lives = 0
        x = 20
        y = 20 + self.digit_size + 12

        if self.heartbar_texture:
            for i in range(lives):
                self.screen.blit(self.heartbar_texture, (x + i * (self.heart_size + 5), y))
        else:
            # Fallback heart shape
            fallback = pg.Surface((30, 30), pg.SRCALPHA)
            pg.draw.circle(fallback, (255, 0, 0), (10, 10), 10)
            pg.draw.circle(fallback, (255, 0, 0), (20, 10), 10)
            pg.draw.polygon(fallback, (255, 0, 0), [(0, 12), (30, 12), (15, 30)])
            for i in range(lives):
                self.screen.blit(fallback, (x + i * 35, y))

    def draw_music_hud(self):
        if not hasattr(self.game, 'music_player') or self.game.music_player is None:
            return
        mp = self.game.music_player
        if not (mp.library and mp.current_idx is not None):
            return

        track = mp.current_track_title()
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -"
        clean = ''.join(c for c in track if c in allowed)
        clean = clean[:40]
        surf = self.doom_font.render(clean, color=(255, 255, 255))
        x = 20
        y = 20 + self.digit_size + 12 + 45
        self.screen.blit(surf, (x, y))

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % RENDER_WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + RENDER_WIDTH, 0))
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, RENDER_WIDTH, RENDER_HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
        }