import pygame as pg
from settings import RENDER_WIDTH, RENDER_HEIGHT
from doom_font import DoomFont

class Menu:
    def __init__(self, game):
        self.game = game
        self.selected = 0
        self.options = ["NEW GAME", "OPTIONS", "QUIT"]

        self.font = DoomFont(char_size=32)
        self.background = None
        self.title_image = None
        self.arrow_img = None

        self.load_assets()

        if self.game.music_player and self.game.music_player.library:
            if self.game.music_player.current_idx is None:
                self.game.music_player.play(0)

    def load_assets(self):
        try:
            bg = pg.image.load('resources/textures/doom_menu.png').convert_alpha()
            self.background = pg.transform.scale(bg, (RENDER_WIDTH, RENDER_HEIGHT))
        except:
            self.background = None

        try:
            self.title_image = pg.image.load('resources/textures/doom_title.png').convert_alpha()
            max_width = int(RENDER_WIDTH * 0.8)
            if self.title_image.get_width() > max_width:
                scale = max_width / self.title_image.get_width()
                new_size = (max_width, int(self.title_image.get_height() * scale))
                self.title_image = pg.transform.scale(self.title_image, new_size)
        except:
            self.title_image = None

        # Load arrow from textures folder
        try:
            arrow = pg.image.load('resources/textures/doom-nightmare-arrow.png').convert_alpha()
            font_height = 32
            scale = font_height / arrow.get_height()
            new_width = int(arrow.get_width() * scale)
            self.arrow_img = pg.transform.scale(arrow, (new_width, font_height))
        except:
            self.arrow_img = None

    def handle_events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pg.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pg.K_RETURN:
                self.select_option()

    def select_option(self):
        choice = self.options[self.selected]
        if choice == "NEW GAME":
            self.game.start_game()
        elif choice == "OPTIONS":
            print("Options selected")
        elif choice == "QUIT":
            pg.quit()
            import sys
            sys.exit()

    def update(self):
        pass

    def draw(self):
        screen = self.game.render_surface

        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((30, 30, 30))

        overlay = pg.Surface((RENDER_WIDTH, RENDER_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        # Title
        if self.title_image:
            x = (RENDER_WIDTH - self.title_image.get_width()) // 2
            y = 60
            screen.blit(self.title_image, (x, y))
        else:
            title_surf = self.font.render("doomsday", color=(255, 50, 50), scale=2.5)
            x = (RENDER_WIDTH - title_surf.get_width()) // 2
            y = 60
            screen.blit(title_surf, (x, y))

        # Menu options
        start_y = 320
        for i, option in enumerate(self.options):
            text = option.lower()
            color = (255, 200, 50) if i == self.selected else (200, 200, 200)
            surf = self.font.render(text, color=color)
            x = (RENDER_WIDTH - surf.get_width()) // 2
            y = start_y + i * 60

            if i == self.selected and self.arrow_img:
                arrow_x = x - self.arrow_img.get_width() - 20
                arrow_y = y + (surf.get_height() - self.arrow_img.get_height()) // 2
                screen.blit(self.arrow_img, (arrow_x, arrow_y))

            screen.blit(surf, (x, y))

            if i == self.selected:
                line_y = y + surf.get_height() + 4
                pg.draw.line(screen, (255, 200, 50), (x, line_y), (x + surf.get_width(), line_y), 2)

        try:
            small_font = pg.font.SysFont("Arial", 16)
            credit = small_font.render("DOOMSDAY v0.1 | A Retro FPS Experience", True, (150,150,150))
            screen.blit(credit, (20, RENDER_HEIGHT - 30))
        except:
            pass