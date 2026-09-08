import pygame as pg
from settings import RENDER_WIDTH, RENDER_HEIGHT
from doom_font import DoomFont
from utils import resource_path

SENSITIVITY_MIN, SENSITIVITY_MAX = 0.0001, 0.0010
VOLUME_MIN, VOLUME_MAX = 0.0, 1.0
FOV_MIN, FOV_MAX = 60, 110

REBIND_ACTIONS = [
    ("forward", "MOVE FORWARD"),
    ("backward", "MOVE BACKWARD"),
    ("strafe_left", "STRAFE LEFT"),
    ("strafe_right", "STRAFE RIGHT"),
    ("interact", "INTERACT"),
    ("cheat_menu", "CHEAT MENU"),
    ("minimap_toggle", "TOGGLE MAP"),
]

class Options:
    def __init__(self, game):
        self.game = game
        self.font = DoomFont(char_size=28)
        self.small_font = DoomFont(char_size=18)

        self.rows = ["SENSITIVITY", "MUSIC VOLUME", "FOV", "REBIND KEYS", "RESET TO DEFAULTS", "BACK"]
        self.selected = 0

        self.in_rebind_screen = False
        self.rebind_selected = 0
        self.awaiting_key = False

        self.bg_image = None
        try:
            self.bg_image = pg.image.load(resource_path('resources/textures/options.png')).convert_alpha()
            self.bg_image = pg.transform.scale(self.bg_image, (RENDER_WIDTH, RENDER_HEIGHT))
        except:
            self.bg_image = None

    def _slider_fraction(self, key, lo, hi):
        val = self.game.settings.get(key)
        return max(0.0, min(1.0, (val - lo) / (hi - lo)))

    def _adjust(self, key, lo, hi, step_frac, direction):
        val = self.game.settings.get(key)
        step = (hi - lo) * step_frac
        val = max(lo, min(hi, val + direction * step))
        self.game.settings.set(key, val)
        self.game.apply_settings()

    def handle_events(self, event):
        if self.in_rebind_screen:
            self._handle_rebind_events(event)
            return

        if event.type != pg.KEYDOWN:
            return

        if event.key == pg.K_ESCAPE:
            self.game.settings.save()
            self.game.close_options()
            return

        if event.key == pg.K_UP:
            self.selected = (self.selected - 1) % len(self.rows)
        elif event.key == pg.K_DOWN:
            self.selected = (self.selected + 1) % len(self.rows)
        elif event.key in (pg.K_LEFT, pg.K_RIGHT):
            direction = -1 if event.key == pg.K_LEFT else 1
            row = self.rows[self.selected]
            if row == "SENSITIVITY":
                self._adjust("mouse_sensitivity", SENSITIVITY_MIN, SENSITIVITY_MAX, 0.05, direction)
            elif row == "MUSIC VOLUME":
                self._adjust("music_volume", VOLUME_MIN, VOLUME_MAX, 0.05, direction)
            elif row == "FOV":
                self._adjust("fov_degrees", FOV_MIN, FOV_MAX, 0.05, direction)
        elif event.key == pg.K_RETURN:
            row = self.rows[self.selected]
            if row == "REBIND KEYS":
                self.in_rebind_screen = True
                self.rebind_selected = 0
            elif row == "RESET TO DEFAULTS":
                self.game.settings.reset_to_defaults()
                self.game.apply_settings()
            elif row == "BACK":
                self.game.settings.save()
                self.game.close_options()

    def _handle_rebind_events(self, event):
        if event.type != pg.KEYDOWN:
            return

        if self.awaiting_key:
            if event.key == pg.K_ESCAPE:
                self.awaiting_key = False
                return
            action, _ = REBIND_ACTIONS[self.rebind_selected]
            self.game.settings.set_keybind(action, event.key)
            self.awaiting_key = False
            return

        if event.key == pg.K_ESCAPE:
            self.in_rebind_screen = False
        elif event.key == pg.K_UP:
            self.rebind_selected = (self.rebind_selected - 1) % len(REBIND_ACTIONS)
        elif event.key == pg.K_DOWN:
            self.rebind_selected = (self.rebind_selected + 1) % len(REBIND_ACTIONS)
        elif event.key == pg.K_RETURN:
            self.awaiting_key = True

    def update(self):
        pass

    def draw(self):
        screen = self.game.render_surface
        if self.bg_image:
            screen.blit(self.bg_image, (0,0))
        else:
            screen.fill((20,20,20))

        overlay = pg.Surface((RENDER_WIDTH, RENDER_HEIGHT), pg.SRCALPHA)
        overlay.fill((0,0,0,60))
        screen.blit(overlay, (0,0))

        title_surf = self.font.render("options", color=(255,200,50), scale=1.6)
        screen.blit(title_surf, ((RENDER_WIDTH - title_surf.get_width())//2, 40))

        if self.in_rebind_screen:
            self._draw_rebind_screen(screen)
            return

        start_y = 150
        row_h = 55
        for i, row in enumerate(self.rows):
            color = (255,200,50) if i == self.selected else (200,200,200)
            label = self.small_font.render(row, color=color)
            y = start_y + i*row_h
            screen.blit(label, (80, y))

            if row == "SENSITIVITY":
                self._draw_slider(screen, self._slider_fraction("mouse_sensitivity", SENSITIVITY_MIN, SENSITIVITY_MAX), y, color)
            elif row == "MUSIC VOLUME":
                self._draw_slider(screen, self._slider_fraction("music_volume", VOLUME_MIN, VOLUME_MAX), y, color)
            elif row == "FOV":
                self._draw_slider(screen, self._slider_fraction("fov_degrees", FOV_MIN, FOV_MAX), y, color)
                val_text = self.small_font.render(f"{int(self.game.settings.get('fov_degrees'))} deg", color=color)
                screen.blit(val_text, (RENDER_WIDTH - 480, y))

        hint = self.small_font.render("LEFT/RIGHT: adjust   ENTER: select   ESC: back & save", color=(150,150,150))
        screen.blit(hint, (80, RENDER_HEIGHT - 50))

    def _draw_slider(self, screen, fraction, y, color):
        bar_x, bar_w, bar_h = RENDER_WIDTH - 380, 260, 10
        pg.draw.rect(screen, (80,80,80), (bar_x, y+5, bar_w, bar_h))
        fill_w = int(bar_w * fraction)
        pg.draw.rect(screen, color, (bar_x, y+5, fill_w, bar_h))
        handle_x = bar_x + fill_w
        pg.draw.circle(screen, color, (handle_x, y+5+bar_h//2), 8)

    def _draw_rebind_screen(self, screen):
        sub = self.small_font.render("REBIND KEYS", color=(255,200,50))
        screen.blit(sub, ((RENDER_WIDTH - sub.get_width())//2, 100))

        start_y = 160
        row_h = 45
        for i, (action, label) in enumerate(REBIND_ACTIONS):
            color = (255,200,50) if i == self.rebind_selected else (200,200,200)
            text = self.small_font.render(label, color=color)
            y = start_y + i*row_h
            screen.blit(text, (100, y))

            key_code = self.game.settings.get_keybind(action)
            key_name = pg.key.name(key_code).upper()
            if self.awaiting_key and i == self.rebind_selected:
                key_name = "PRESS A KEY..."
            key_surf = self.small_font.render(key_name, color=color)
            screen.blit(key_surf, (RENDER_WIDTH - 220, y))

        hint = self.small_font.render("ENTER: rebind   ESC: back", color=(150,150,150))
        screen.blit(hint, (100, RENDER_HEIGHT - 50))