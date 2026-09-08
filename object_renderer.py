import pygame as pg
from settings import *
from doom_font import DoomFont
from floorcasting import FloorCaster
from utils import resource_path

CEILING_COLOR = (128, 128, 128)

class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.render_surface
        self.wall_textures = self.load_wall_textures()
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', (RENDER_WIDTH, RENDER_HEIGHT))
        self.floor_caster = FloorCaster(game)

        self.digit_size = int(90 * (RENDER_WIDTH / 800))
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))

        self.doom_font = DoomFont(char_size=24)

        try:
            self.heartbar_texture = pg.image.load(resource_path('resources/textures/heartbar.png')).convert_alpha()
            self.heart_size = 30
            self.heartbar_texture = pg.transform.scale(self.heartbar_texture, (self.heart_size, self.heart_size))
        except:
            self.heartbar_texture = None

        self.game_over_image = self.get_texture('resources/textures/game_over.png', (RENDER_WIDTH, RENDER_HEIGHT))
        self.win_image = self.get_texture('resources/textures/win.png', (RENDER_WIDTH, RENDER_HEIGHT))

    def draw(self):
        self.draw_background()
        self.render_game_objects()

    def draw_player_health(self):
        health = str(self.game.player.health)
        x, y = 20, 20
        for i, ch in enumerate(health):
            self.screen.blit(self.digits[ch], (x + i*self.digit_size, y))
        self.screen.blit(self.digits['10'], (x + len(health)*self.digit_size, y))

    def draw_lives(self):
        lives = self.game.player.lives
        x, y = 20, 20 + self.digit_size + 12
        if self.heartbar_texture:
            for i in range(lives):
                self.screen.blit(self.heartbar_texture, (x + i*(self.heart_size+5), y))
        else:
            fallback = pg.Surface((30,30), pg.SRCALPHA)
            pg.draw.circle(fallback, (255,0,0), (10,10), 10)
            pg.draw.circle(fallback, (255,0,0), (20,10), 10)
            pg.draw.polygon(fallback, (255,0,0), [(0,12), (30,12), (15,30)])
            for i in range(lives):
                self.screen.blit(fallback, (x + i*35, y))

    def draw_music_hud(self):
        mp = self.game.music_player
        if not mp or not mp.library or mp.current_idx is None:
            return
        track = mp.current_track_title()
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -"
        clean = ''.join(c for c in track if c in allowed)[:40]
        surf = self.doom_font.render(clean, color=(255,255,255))
        x, y = 20, 20 + self.digit_size + 12 + 45
        self.screen.blit(surf, (x, y))

    def draw_level(self, level):
        label = self.doom_font.render("level", color=(200,200,200), scale=0.8)
        x = 20
        y = 20 + self.digit_size + 12 + 45 + 30
        self.screen.blit(label, (x, y))
        level_str = str(level)
        digit_x = x + label.get_width() + 10
        for ch in level_str:
            if ch in self.digits:
                self.screen.blit(self.digits[ch], (digit_x, y - 4))
                digit_x += self.digit_size

    def draw_win_only(self):
        self.screen.blit(self.win_image, (0,0))

    def draw_blood_overlay(self):
        self.screen.blit(self.blood_screen, (0,0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0,0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0,0))

    def draw_background(self):
        pg.draw.rect(self.screen, CEILING_COLOR, (0, 0, RENDER_WIDTH, HALF_HEIGHT))
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, RENDER_WIDTH, RENDER_HEIGHT - HALF_HEIGHT))
        try:
            self.floor_caster.draw(self.screen)
        except:
            pass

    def render_game_objects(self):
        for depth, img, pos in sorted(self.game.raycasting.objects_to_render, key=lambda x: x[0], reverse=True):
            self.screen.blit(img, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        full_path = resource_path(path)
        try:
            tex = pg.image.load(full_path).convert_alpha()
        except:
            tex = pg.Surface(res, pg.SRCALPHA)
            tex.fill((100,100,100))
        return pg.transform.scale(tex, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
            6: self.get_texture('resources/textures/doom_door.png'),
            9: self.get_texture('resources/textures/doom_elevator_wall.png'),
        }