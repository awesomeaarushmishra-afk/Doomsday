from sprite_object import *
from random import randint, random
import math
from player import Player

class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False
        self.friendly_fire = False

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self):
        target = self.get_target()
        if not target:
            return

        next_pos = self.game.pathfinding.get_path(self.map_pos, (int(target.x), int(target.y)))
        if not next_pos:
            return
        next_x, next_y = next_pos

        if not self.friendly_fire:
            if next_pos in self.game.object_handler.npc_positions:
                return

        angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed
        self.check_wall_collision(dx, dy)

    def get_target(self):
        if self.friendly_fire:
            nearest = None
            min_dist = float('inf')
            for npc in self.game.object_handler.npc_list:
                if npc is self or not npc.alive:
                    continue
                dist = math.hypot(npc.x - self.x, npc.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    nearest = npc
            return nearest
        else:
            return self.game.player

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                target = self.get_target()
                if target:
                    if isinstance(target, Player):
                        target.get_damage(self.attack_damage)
                    else:
                        target.health -= self.attack_damage
                        if target.health < 1:
                            target.alive = False
                            self.game.sound.npc_death.play()

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        # Fixed: player can always hit, regardless of ray_cast_value
        if self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def run_logic(self):
        if self.alive:
            target = self.get_target()
            if target:
                self.ray_cast_value = self.ray_cast_to_target(target)
            else:
                self.ray_cast_value = False

            self.check_hit_in_npc()

            if self.pain:
                self.animate_pain()

            elif self.ray_cast_value:
                self.player_search_trigger = True
                dist_to_target = math.hypot(self.x - target.x, self.y - target.y) if target else float('inf')
                if dist_to_target < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()

            elif self.player_search_trigger:
                self.animate(self.walk_images)
                self.movement()

            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    def ray_cast_to_target(self, target):
        if not target:
            return False

        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 0.5:
            return True

        steps = int(dist * 2)
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = self.x + dx * t
            y = self.y + dy * t
            if (int(x), int(y)) in self.game.map.world_map:
                return False
        return True

    @property
    def map_pos(self):
        return int(self.x), int(self.y)


class SoldierNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)

class CacoDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/caco_demon/0.png', pos=(10.5, 6.5),
                 scale=0.7, shift=0.27, animation_time=250):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 1.0
        self.health = 150
        self.attack_damage = 25
        self.speed = 0.05
        self.accuracy = 0.35

class CyberDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/cyber_demon/0.png', pos=(11.5, 6.0),
                 scale=1.0, shift=0.04, animation_time=210):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 6
        self.health = 350
        self.attack_damage = 15
        self.speed = 0.055
        self.accuracy = 0.25