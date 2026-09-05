import pygame as pg
import sys
from settings import *
from map import Map
from player import Player
from raycasting import RayCasting
from object_renderer import ObjectRenderer
from sprite_object import *
from object_handler import ObjectHandler
from weapon import Weapon
from sound import Sound
from pathfinding import PathFinding
from music_player import MusicPlayer
from menu import Menu
from developer_room import DeveloperRoom

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.mouse.set_visible(False)

        self.window = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        pg.event.set_grab(True)

        self.render_surface = pg.Surface((RENDER_WIDTH, RENDER_HEIGHT))
        self.screen = self.render_surface

        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)

        # Music player
        try:
            self.music_player = MusicPlayer(folder="music")
            if self.music_player.library:
                self.music_player.play(0)
            else:
                print("No music files found.")
        except Exception as e:
            print(f"Music player failed: {e}")
            self.music_player = None

        # Game state
        self.in_game = False
        self.menu = Menu(self)
        self.game_over_state = False
        self.game_over_timer = 0

        # Cheat system
        self.cheat_menu_active = False
        self.cheat_input = ""
        self.cheat_feedback = ""
        self.developer_room_unlocked = False
        self.enemy_friendly_fire = False

        # Developer room
        self.in_developer_room = False
        self.developer_room = None

        self.map = None
        self.player = None
        self.object_renderer = None
        self.raycasting = None
        self.object_handler = None
        self.weapon = None
        self.sound = None
        self.pathfinding = None

    def start_game(self):
        self.in_game = True
        self.game_over_state = False
        self.new_game()
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def game_over(self):
        self.game_over_state = True
        self.game_over_timer = pg.time.get_ticks()
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

    def return_to_menu(self):
        self.game_over_state = False
        self.in_game = False
        self.in_developer_room = False
        if self.developer_room:
            self.developer_room = None
        if self.object_handler:
            self.object_handler.win_active = False
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        if self.player:
            self.player.lives = PLAYER_START_LIVES
            self.player.health = PLAYER_MAX_HEALTH
            self.player.dead = False

    def process_cheat(self, text):
        text = text.strip().upper()
        if text == "I'M DONE":
            self.developer_room_unlocked = True
            self.enter_developer_room()
            return "Developer Room entered! Press ESC to exit."
        elif text == "IDDQD" or text == "GODMODE":
            if self.player:
                self.player.godmode = not self.player.godmode
                return f"Godmode: {'ON' if self.player.godmode else 'OFF'}"
            return "Player not initialized"
        elif text == "IDKFA":
            if self.player:
                self.player.all_weapons = True
                self.player.ammo = 9999
                return "All weapons & ammo!"
            return "Player not initialized"
        elif text == "GM":   # <-- Only GM
            if self.player:
                self.player.noclip = not self.player.noclip
                return f"Noclip: {'ON' if self.player.noclip else 'OFF'}"
            return "Player not initialized"
        elif text == "MAXHEALTH":
            if self.player:
                self.player.health = PLAYER_MAX_HEALTH
                return "Health restored!"
            return "Player not initialized"
        elif text == "KILLALL":
            if self.object_handler:
                for npc in self.object_handler.npc_list:
                    npc.health = 0
                    npc.alive = False
                return "All enemies eliminated! (Win in 30s)"
            return "No enemies found"
        elif text == "MURDERER":
            self.enemy_friendly_fire = not self.enemy_friendly_fire
            if self.object_handler:
                for npc in self.object_handler.npc_list:
                    npc.friendly_fire = self.enemy_friendly_fire
            return f"Enemy friendly fire: {'ON' if self.enemy_friendly_fire else 'OFF'}"
        elif text == "HELP":
            return "Cheats: IDDQD, IDKFA, GM, MAXHEALTH, KILLALL, MURDERER, I'M DONE, HELP"
        else:
            return f"Unknown cheat: {text}"

    def toggle_cheat_menu(self):
        self.cheat_menu_active = not self.cheat_menu_active
        if self.cheat_menu_active:
            self.cheat_input = ""
            self.cheat_feedback = ""
            pg.mouse.set_visible(True)
            pg.event.set_grab(False)
        else:
            pg.mouse.set_visible(False)
            pg.event.set_grab(True)

    def enter_developer_room(self):
        if not self.developer_room_unlocked:
            return
        self.in_developer_room = True
        self.developer_room = DeveloperRoom(self)
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

    def exit_developer_room(self):
        self.in_developer_room = False
        self.developer_room = None
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def update(self):
        if self.game_over_state:
            if pg.time.get_ticks() - self.game_over_timer > 2000:
                self.return_to_menu()
            return
        if self.cheat_menu_active:
            return
        if self.in_developer_room:
            self.developer_room.update()
            return
        if not self.in_game:
            self.menu.update()
            return
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        if self.game_over_state:
            self.render_surface.fill((0, 0, 0))
            doom_font = self.object_renderer.doom_font
            go_text = doom_font.render("game over", color=(255, 50, 50), scale=2.5)
            x1 = (RENDER_WIDTH - go_text.get_width()) // 2
            y1 = RENDER_HEIGHT // 2 - go_text.get_height() - 10
            self.render_surface.blit(go_text, (x1, y1))
            sub_text = doom_font.render("returning to main menu", color=(200, 200, 200), scale=1.2)
            x2 = (RENDER_WIDTH - sub_text.get_width()) // 2
            y2 = RENDER_HEIGHT // 2 + 10
            self.render_surface.blit(sub_text, (x2, y2))
        elif self.in_developer_room:
            self.developer_room.draw()
        elif not self.in_game:
            self.menu.draw()
        else:
            self.render_surface.fill((0, 0, 0))
            self.object_renderer.draw()
            self.weapon.draw()
            self.object_renderer.draw_player_health()
            self.object_renderer.draw_lives()
            self.object_renderer.draw_music_hud()

        if self.cheat_menu_active:
            self.draw_cheat_menu()

        scaled = pg.transform.scale(self.render_surface, self.window.get_size())
        self.window.blit(scaled, (0, 0))
        pg.display.flip()

    def draw_cheat_menu(self):
        screen = self.render_surface
        overlay = pg.Surface((RENDER_WIDTH, RENDER_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        font = pg.font.SysFont("Arial", 28, bold=True)
        small_font = pg.font.SysFont("Arial", 20)
        title = font.render("CHEAT MENU", True, (255, 200, 50))
        screen.blit(title, (RENDER_WIDTH//2 - title.get_width()//2, 60))
        prompt = font.render("> " + self.cheat_input, True, (255, 255, 255))
        input_x = 120
        input_y = 160
        screen.blit(prompt, (input_x, input_y))
        if pg.time.get_ticks() % 1000 < 500:
            cursor_x = input_x + prompt.get_width()
            pg.draw.line(screen, (255, 255, 255), (cursor_x, input_y), (cursor_x, input_y + prompt.get_height()), 2)
        if self.cheat_feedback:
            fb = small_font.render(self.cheat_feedback, True, (150, 255, 150))
            screen.blit(fb, (input_x, input_y + 50))
        help_text = small_font.render("Press ENTER to activate, ESC to close", True, (180, 180, 180))
        screen.blit(help_text, (input_x, RENDER_HEIGHT - 60))
        if self.developer_room_unlocked:
            note = small_font.render("Developer Room Unlocked! (Entered automatically)", True, (255, 200, 50))
            screen.blit(note, (input_x, RENDER_HEIGHT - 100))

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.cheat_menu_active:
                    self.toggle_cheat_menu()
                    continue
                if self.in_developer_room:
                    self.exit_developer_room()
                    continue
                if self.game_over_state:
                    continue
                pg.quit()
                sys.exit()

            if event.type == pg.VIDEORESIZE:
                self.window = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)

            if event.type == self.global_event:
                self.global_trigger = True

            # Developer room browsing
            if self.in_developer_room:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT:
                        self.developer_room.next_image()
                    elif event.key == pg.K_LEFT:
                        self.developer_room.prev_image()
                continue

            # Toggle cheat menu with 'C' (only in game)
            if event.type == pg.KEYDOWN and event.key == pg.K_c and self.in_game and not self.game_over_state:
                self.toggle_cheat_menu()
                continue

            # Handle cheat menu input
            if self.cheat_menu_active and event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.cheat_feedback = self.process_cheat(self.cheat_input)
                    self.cheat_input = ""
                elif event.key == pg.K_BACKSPACE:
                    self.cheat_input = self.cheat_input[:-1]
                elif event.key == pg.K_ESCAPE:
                    self.toggle_cheat_menu()
                else:
                    if event.unicode and event.unicode.isprintable():
                        self.cheat_input += event.unicode
                continue

            # Only pass events to game if cheat menu is not active and not game over
            if not self.cheat_menu_active and not self.game_over_state:
                if not self.in_game:
                    self.menu.handle_events(event)
                else:
                    self.player.single_fire_event(event)

                # Music controls
                if self.music_player is not None and event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT:
                        self.music_player.next()
                    elif event.key == pg.K_LEFT:
                        pass
                    elif event.key == pg.K_UP:
                        self.music_player.set_volume(min(1.0, self.music_player.volume + 0.1))
                    elif event.key == pg.K_DOWN:
                        self.music_player.set_volume(max(0.0, self.music_player.volume - 0.1))
                    elif event.key == pg.K_SPACE and (pg.key.get_mods() & pg.KMOD_CTRL):
                        self.music_player.toggle()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()

if __name__ == '__main__':
    game = Game()
    game.run()