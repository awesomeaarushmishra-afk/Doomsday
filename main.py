import sys
import os
import pygame as pg
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
from settings_manager import SettingsManager
from options import Options
from minimap import MiniMap
from utils import resource_path

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        pg.mouse.set_visible(False)

        self.window = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        pg.event.set_grab(True)

        self.render_surface = pg.Surface((RENDER_WIDTH, RENDER_HEIGHT))
        self.screen = self.render_surface

        self.settings = SettingsManager()

        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)

        # Music
        try:
            self.music_player = MusicPlayer(folder="music")
            if self.music_player.library:
                self.music_player.play(0)
                self.music_player.set_volume(self.settings.get('music_volume'))
            else:
                print("No music files found.")
        except Exception as e:
            print(f"Music player failed: {e}")
            self.music_player = None

        self.in_game = False
        self.menu = Menu(self)
        self.options = Options(self)
        self.in_options = False
        self.game_over_state = False
        self.game_over_timer = 0

        self.cheat_menu_active = False
        self.cheat_input = ""
        self.cheat_feedback = ""
        self.developer_room_unlocked = False
        self.enemy_friendly_fire = False

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
        self.minimap = MiniMap(self)

        self.current_level = 1
        self.max_levels = 15

        self.speed_active = False
        self.nightmare_active = False

        self.elevator_ride_active = False
        self.elevator_ride_start = 0
        self.elevator_ride_duration = 1200
        self.elevator_destination = None

    def start_game(self):
        self.in_game = True
        self.game_over_state = False
        self.current_level = 1
        self.new_game()
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def new_game(self, enemy_count=None):
        if enemy_count is None:
            enemy_count = BASE_ENEMIES + (self.current_level - 1) * ENEMIES_PER_LEVEL
        self.map = Map(self, level=self.current_level)
        self.player = Player(self)
        self.player.x, self.player.y = self.map.elevator_spawn
        self.player.angle = PLAYER_ANGLE
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self, enemy_count=enemy_count, level_num=self.current_level)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)

    def new_game_at_level(self, level):
        self.current_level = level
        enemy_count = BASE_ENEMIES + (level - 1) * ENEMIES_PER_LEVEL
        self.map = Map(self, level=level)
        self.player = Player(self)
        self.player.x, self.player.y = self.map.elevator_spawn
        self.player.angle = PLAYER_ANGLE
        self.player.health = PLAYER_MAX_HEALTH
        self.player.shot = False
        self.player.dead = False
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self, enemy_count=enemy_count, level_num=level)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)

    def regenerate_level(self):
        if self.current_level >= self.max_levels:
            return
        self.current_level += 1
        self.map = Map(self, level=self.current_level)
        self.player.x, self.player.y = self.map.elevator_spawn
        self.player.angle = PLAYER_ANGLE
        self.player.health = PLAYER_MAX_HEALTH
        self.player.shot = False
        self.player.dead = False

        enemy_count = BASE_ENEMIES + (self.current_level - 1) * ENEMIES_PER_LEVEL
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self, enemy_count=enemy_count, level_num=self.current_level)
        self.weapon = Weapon(self)
        self.pathfinding = PathFinding(self)

    def is_level_cleared(self):
        return self.object_handler is None or self.object_handler.enemies_remaining == 0

    def start_elevator_ride(self, elevator):
        if not self.is_level_cleared():
            self.show_message("Clear all enemies first!")
            return
        if self.player and not self.elevator_ride_active:
            self.elevator_ride_active = True
            self.elevator_ride_start = pg.time.get_ticks()
            self.elevator_destination = elevator.destination
            self.player.riding_elevator = True

    def finish_elevator_ride(self):
        if not self.elevator_ride_active:
            return
        self.elevator_ride_active = False
        self.player.riding_elevator = False
        if self.current_level < self.max_levels:
            self.regenerate_level()
        else:
            if self.elevator_destination:
                self.player.x, self.player.y = self.elevator_destination[0] + 0.5, self.elevator_destination[1] + 0.5
        self.elevator_destination = None

    def cancel_elevator_ride(self):
        if self.elevator_ride_active:
            self.elevator_ride_active = False
            self.player.riding_elevator = False
            self.elevator_destination = None

    def show_message(self, msg):
        self.cheat_feedback = msg
        self.cheat_feedback_timer = pg.time.get_ticks()

    def open_options(self):
        self.in_options = True
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

    def close_options(self):
        self.in_options = False
        if not self.in_game:
            pg.mouse.set_visible(True)
            pg.event.set_grab(False)
        else:
            pg.mouse.set_visible(False)
            pg.event.set_grab(True)

    def apply_settings(self):
        if self.music_player is not None:
            self.music_player.set_volume(self.settings.get('music_volume'))
        if self.raycasting is not None:
            self.raycasting.set_fov(self.settings.get('fov_degrees'))

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
        elif text in ("IDDQD", "GODMODE"):
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
        elif text == "GM":
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
                return "All enemies eliminated!"
            return "No enemies found"
        elif text == "NOENEMY":
            if self.object_handler:
                for npc in self.object_handler.npc_list:
                    npc.health = 0
                    npc.alive = False
                return "All enemies removed!"
            return "No enemies found"
        elif text == "MAINMENU":
            self.return_to_menu()
            return "Returning to main menu..."
        elif text == "MURDERER":
            self.enemy_friendly_fire = not self.enemy_friendly_fire
            if self.object_handler:
                for npc in self.object_handler.npc_list:
                    npc.friendly_fire = self.enemy_friendly_fire
            return f"Enemy friendly fire: {'ON' if self.enemy_friendly_fire else 'OFF'}"
        elif text == "SPEED":
            self.speed_active = not self.speed_active
            self.update_speed()
            return f"Speed boost: {'ON' if self.speed_active else 'OFF'}"
        elif text == "NIGHTMARE":
            self.nightmare_active = not self.nightmare_active
            if self.nightmare_active and self.object_handler:
                from npc import SoldierNPC, CacoDemonNPC, CyberDemonNPC
                import random
                for _ in range(5):
                    npc_class = random.choice([SoldierNPC, CacoDemonNPC, CyberDemonNPC])
                    pos = (random.randint(1, self.map.cols-2), random.randint(1, self.map.rows-2))
                    while pos in self.map.world_map or pos in self.object_handler.restricted_area:
                        pos = (random.randint(1, self.map.cols-2), random.randint(1, self.map.rows-2))
                    self.object_handler.add_npc(npc_class(self.game, pos=(pos[0]+0.5, pos[1]+0.5)))
            return f"Nightmare mode: {'ON' if self.nightmare_active else 'OFF'}"
        elif text == "FINALLEVEL":
            self.new_game_at_level(self.max_levels)
            return f"Jumped to final level ({self.max_levels})! Kill all enemies to win."
        elif text == "HELP":
            return ("Cheats: IDDQD, IDKFA, GM, MAXHEALTH, KILLALL, NOENEMY\n"
                    "MAINMENU, MURDERER, SPEED, NIGHTMARE, FINALLEVEL, I'M DONE")
        else:
            return f"Unknown cheat: {text}"

    def update_speed(self):
        if self.speed_active and self.player:
            self.player.speed_multiplier = 5
        else:
            self.player.speed_multiplier = 1

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
        if self.in_options:
            self.options.update()
            return
        if self.in_developer_room:
            self.developer_room.update()
            return
        if not self.in_game:
            self.menu.update()
            return

        if self.elevator_ride_active:
            if pg.time.get_ticks() - self.elevator_ride_start >= self.elevator_ride_duration:
                self.finish_elevator_ride()

        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        self.map.update()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        if self.game_over_state:
            self.object_renderer.game_over()
        elif self.in_options:
            self.options.draw()
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
            self.object_renderer.draw_level(self.current_level)
            self.minimap.draw()
            if self.elevator_ride_active:
                self.draw_elevator_overlay()
            if not self.is_level_cleared():
                font = pg.font.SysFont("Arial", 20, bold=True)
                msg = font.render("Clear all enemies to use elevator", True, (255, 200, 50))
                self.render_surface.blit(msg, (20, RENDER_HEIGHT - 80))

        # Win screen: blood background + win image on top
        if hasattr(self.object_handler, 'win_active') and self.object_handler.win_active:
            self.object_renderer.draw_blood_overlay()
            self.object_renderer.draw_win_only()

        if self.cheat_menu_active:
            self.draw_cheat_menu()

        scaled = pg.transform.scale(self.render_surface, self.window.get_size())
        self.window.blit(scaled, (0, 0))
        pg.display.flip()

    def draw_elevator_overlay(self):
        screen = self.render_surface
        overlay = pg.Surface((RENDER_WIDTH, RENDER_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        doom_font = self.object_renderer.doom_font
        text = doom_font.render("riding elevator", color=(255, 200, 50), scale=1.3)
        screen.blit(text, ((RENDER_WIDTH - text.get_width()) // 2, HALF_HEIGHT - 40))
        hint = doom_font.render("press ESC to cancel", color=(180,180,180), scale=0.7)
        screen.blit(hint, ((RENDER_WIDTH - hint.get_width()) // 2, HALF_HEIGHT + 30))

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
            lines = self.cheat_feedback.split('\n')
            for i, line in enumerate(lines):
                fb = small_font.render(line, True, (150, 255, 150))
                screen.blit(fb, (input_x, input_y + 50 + i * 28))

        help_text = small_font.render("Press ENTER to activate, ESC to close", True, (180,180,180))
        screen.blit(help_text, (input_x, RENDER_HEIGHT - 60))
        if self.developer_room_unlocked:
            note = small_font.render("Developer Room Unlocked! (Entered automatically)", True, (255,200,50))
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
                if self.in_options:
                    self.options.handle_events(event)
                    continue
                if self.in_developer_room:
                    self.exit_developer_room()
                    continue
                if self.game_over_state:
                    continue
                if self.elevator_ride_active:
                    self.cancel_elevator_ride()
                    continue
                pg.quit()
                sys.exit()

            if event.type == pg.VIDEORESIZE:
                self.window = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)

            if event.type == self.global_event:
                self.global_trigger = True

            if self.in_options:
                self.options.handle_events(event)
                continue

            if self.in_developer_room:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RIGHT:
                        self.developer_room.next_image()
                    elif event.key == pg.K_LEFT:
                        self.developer_room.prev_image()
                continue

            if event.type == pg.KEYDOWN and self.in_game and not self.game_over_state:
                menu_key = self.settings.get_keybind("cheat_menu")
                if event.key == menu_key:
                    self.toggle_cheat_menu()
                    continue

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

            if not self.cheat_menu_active and not self.game_over_state:
                if not self.in_game:
                    self.menu.handle_events(event)
                else:
                    self.player.single_fire_event(event)
                    if event.type == pg.KEYDOWN and event.key == self.settings.get_keybind("interact"):
                        self.player.try_interact()
                    if event.type == pg.KEYDOWN and event.key == self.settings.get_keybind("minimap_toggle"):
                        self.minimap.toggle()

                if self.music_player and event.type == pg.KEYDOWN:
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