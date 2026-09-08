import pygame as pg
import math
from settings import *

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.lives = PLAYER_START_LIVES
        self.dead = False
        self.respawn_timer = 0
        self.riding_elevator = False
        self.rel = 0
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        self.diag_move_corr = 1 / math.sqrt(2)

        self.godmode = False
        self.noclip = False
        self.all_weapons = False
        self.ammo = 50

        self.speed_multiplier = 1

    def recover_health(self):
        if self.godmode:
            self.health = PLAYER_MAX_HEALTH
            return
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        now = pg.time.get_ticks()
        if now - self.time_prev > self.health_recovery_delay:
            self.time_prev = now
            return True

    def die(self):
        if self.godmode:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game.game_over()
        else:
            self.respawn()

    def respawn(self):
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.health = PLAYER_MAX_HEALTH
        self.shot = False
        self.dead = False

    def game_over(self):
        self.dead = True
        self.game.game_over()

    def get_damage(self, damage):
        if self.godmode:
            return
        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        if self.health <= 0:
            self.die()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True

    def movement(self):
        if self.dead or self.riding_elevator:
            return
        if self.noclip:
            sin_a = math.sin(self.angle)
            cos_a = math.cos(self.angle)
            dx, dy = 0, 0
            speed = PLAYER_SPEED * self.game.delta_time * self.speed_multiplier
            speed_sin = speed * sin_a
            speed_cos = speed * cos_a
            keys = pg.key.get_pressed()
            kb = self.game.settings.get_keybind
            if keys[kb("forward")]:
                dx += speed_cos
                dy += speed_sin
            if keys[kb("backward")]:
                dx -= speed_cos
                dy -= speed_sin
            if keys[kb("strafe_left")]:
                dx += speed_sin
                dy -= speed_cos
            if keys[kb("strafe_right")]:
                dx -= speed_sin
                dy += speed_cos
            self.x += dx
            self.y += dy
            self.angle %= math.tau
            return

        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_SPEED * self.game.delta_time * self.speed_multiplier
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        kb = self.game.settings.get_keybind
        num = -1
        if keys[kb("forward")]:
            num += 1
            dx += speed_cos
            dy += speed_sin
        if keys[kb("backward")]:
            num += 1
            dx -= speed_cos
            dy -= speed_sin
        if keys[kb("strafe_left")]:
            num += 1
            dx += speed_sin
            dy -= speed_cos
        if keys[kb("strafe_right")]:
            num += 1
            dx -= speed_sin
            dy += speed_cos

        if num > 0:
            dx *= self.diag_move_corr
            dy *= self.diag_move_corr

        self.check_wall_collision(dx, dy)
        self.angle %= math.tau

    def check_wall(self, x, y):
        tile = (x, y)
        if tile not in self.game.map.world_map:
            return True
        value = self.game.map.world_map[tile]
        if value == 6:
            door = self.game.map.doors.get(tile)
            return door is not None and not door.blocks_movement
        if value == 7:
            return True
        return False

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def try_interact(self):
        from interactables import find_interactable_near
        door = find_interactable_near(self.game, self.game.map.doors)
        if door:
            door.interact()
            return
        tile = self.map_pos
        if tile in self.game.map.elevators:
            elevator = self.game.map.elevators[tile]
            elevator.interact(self.game)

    def mouse_control(self):
        if self.dead or self.riding_elevator:
            return
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        sensitivity = self.game.settings.get('mouse_sensitivity')
        self.angle += self.rel * sensitivity * self.game.delta_time

    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)