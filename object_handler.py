from sprite_object import *
from npc import *
from random import choices, randrange
import pygame as pg

class ObjectHandler:
    def __init__(self, game, enemy_count=20, level_num=1):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'
        self.npc_positions = {}
        self.level_num = level_num

        self.win_active = False
        self.win_blood_timer = 0

        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        for r in range(28, 32):
            for c in range(3, 8):
                self.restricted_area.add((c, r))
        for pos in self.game.map.elevators.keys():
            self.restricted_area.add(pos)

        self.enemies = enemy_count
        self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
        self.weights = [70, 20, 10]
        self.spawn_npc()

        self.add_sprite(AnimatedSprite(game))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
        self.add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
        self.add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
        self.add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
        self.add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
        self.add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
        self.add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 5.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(12.5, 7.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 7.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 12.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 20.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(10.5, 20.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 14.5)))
        self.add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 18.5)))
        self.add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
        self.add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
        self.add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

    def spawn_npc(self):
        for i in range(self.enemies):
            npc = choices(self.npc_types, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def check_win(self):
        if not self.win_active and not len(self.npc_positions):
            if self.level_num >= self.game.max_levels:
                self.win_active = True
                self.win_blood_timer = pg.time.get_ticks()
                self.game.object_renderer.draw_blood_overlay()
                self.game.object_renderer.draw_win_only()
                pg.display.flip()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

        if self.win_active:
            if pg.time.get_ticks() - self.win_blood_timer > 3000:  # 3 seconds
                self.win_active = False
                self.game.return_to_menu()

    @property
    def enemies_remaining(self):
        return len([npc for npc in self.npc_list if npc.alive])

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)