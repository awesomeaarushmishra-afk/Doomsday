import pygame as pg
import math
from settings import *

class RayCasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.objects_to_render = []
        self.textures = self.game.object_renderer.wall_textures

        self.fov = FOV
        self.half_fov = HALF_FOV
        self.num_rays = NUM_RAYS
        self.half_num_rays = HALF_NUM_RAYS
        self.delta_angle = DELTA_ANGLE
        self.screen_dist = SCREEN_DIST
        self.scale = SCALE
        self.max_depth = MAX_DEPTH

        fov_setting = self.game.settings.get('fov_degrees') if hasattr(self.game, 'settings') else None
        self.set_fov(fov_setting)

    def set_fov(self, fov_degrees):
        if fov_degrees is None:
            return
        self.fov = math.radians(fov_degrees)
        self.half_fov = self.fov / 2
        self.num_rays = NUM_RAYS
        self.half_num_rays = self.num_rays // 2
        self.delta_angle = self.fov / self.num_rays
        self.screen_dist = HALF_WIDTH / math.tan(self.half_fov)
        self.scale = RENDER_WIDTH // self.num_rays

    def is_blocking(self, tile, offset):
        value = self.game.map.world_map.get(tile)
        if value is None:
            return False
        if value == 6:
            door = self.game.map.doors.get(tile)
            if door is None:
                return True
            return door.blocks_sight
        return True

    def get_objects_to_render(self):
        self.objects_to_render = []
        scale = self.scale
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values

            if proj_height < HEIGHT:
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - scale), 0, scale, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (scale, proj_height))
                wall_pos = (ray * scale, HALF_HEIGHT - proj_height // 2)
            else:
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - scale), HALF_TEXTURE_SIZE - texture_height // 2,
                    scale, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (scale, HEIGHT))
                wall_pos = (ray * scale, 0)

            self.objects_to_render.append((depth, wall_column, wall_pos))

    def ray_cast(self):
        self.ray_casting_result = []
        texture_vert, texture_hor = 1, 1
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.game.player.angle - self.half_fov + 0.0001
        for ray in range(self.num_rays):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # horizontals
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(self.max_depth):
                tile_hor = int(x_hor), int(y_hor)
                test_offset = x_hor % 1
                if tile_hor in self.game.map.world_map and self.is_blocking(tile_hor, test_offset):
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # verticals
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(self.max_depth):
                tile_vert = int(x_vert), int(y_vert)
                test_offset = y_vert % 1
                if tile_vert in self.game.map.world_map and self.is_blocking(tile_vert, test_offset):
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            depth *= math.cos(self.game.player.angle - ray_angle)

            proj_height = self.screen_dist / (depth + 0.0001)
            self.ray_casting_result.append((depth, proj_height, texture, offset))

            ray_angle += self.delta_angle

    def update(self):
        self.ray_cast()
        self.get_objects_to_render()