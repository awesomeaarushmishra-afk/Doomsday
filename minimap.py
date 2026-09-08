import pygame as pg
import math
from settings import RENDER_WIDTH, RENDER_HEIGHT

MINIMAP_TILE_SIZE = 10
MINIMAP_MARGIN = 20
MINIMAP_MAX_WIDTH = 320
MINIMAP_MAX_HEIGHT = 320

COLOR_WALL = (90, 90, 90)
COLOR_DOOR_CLOSED = (150, 100, 40)
COLOR_DOOR_OPEN = (220, 180, 90)
COLOR_ELEVATOR = (80, 160, 220)
COLOR_BG = (15, 15, 15)
COLOR_PLAYER = (255, 60, 60)
COLOR_BORDER = (200, 200, 200)


class MiniMap:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.small_font = pg.font.SysFont("Arial", 14)

    def toggle(self):
        self.visible = not self.visible

    def draw(self):
        if not self.visible or self.game.map is None:
            return

        game_map = self.game.map
        cols, rows = game_map.cols, game_map.rows

        tile_size = min(MINIMAP_TILE_SIZE,
                         MINIMAP_MAX_WIDTH // max(cols, 1),
                         MINIMAP_MAX_HEIGHT // max(rows, 1))
        tile_size = max(2, tile_size)

        map_w = cols * tile_size
        map_h = rows * tile_size

        panel = pg.Surface((map_w + 4, map_h + 4), pg.SRCALPHA)
        panel.fill((*COLOR_BG, 210))

        # Draw walls (skip doors/elevators)
        for pos, value in game_map.world_map.items():
            if value in (6, 7):
                continue
            x, y = pos
            rect = (2 + x * tile_size, 2 + y * tile_size, tile_size, tile_size)
            pg.draw.rect(panel, COLOR_WALL, rect)

        # Draw doors (using state)
        for pos, door in game_map.doors.items():
            x, y = pos
            rect = (2 + x * tile_size, 2 + y * tile_size, tile_size, tile_size)
            color = COLOR_DOOR_OPEN if door.state == "open" else COLOR_DOOR_CLOSED
            pg.draw.rect(panel, color, rect)

        # Draw elevators (floor tiles)
        for pos in game_map.elevators:
            x, y = pos
            rect = (2 + x * tile_size, 2 + y * tile_size, tile_size, tile_size)
            pg.draw.rect(panel, COLOR_ELEVATOR, rect)

        # Player position + facing direction
        player = self.game.player
        if player:
            px = 2 + player.x * tile_size
            py = 2 + player.y * tile_size
            pg.draw.circle(panel, COLOR_PLAYER, (int(px), int(py)), max(3, tile_size // 2))
            facing_len = tile_size * 1.5
            fx = px + math.cos(player.angle) * facing_len
            fy = py + math.sin(player.angle) * facing_len
            pg.draw.line(panel, COLOR_PLAYER, (px, py), (fx, fy), 2)

        pg.draw.rect(panel, COLOR_BORDER, panel.get_rect(), 2)

        screen = self.game.render_surface
        panel_x = RENDER_WIDTH - panel.get_width() - MINIMAP_MARGIN
        panel_y = MINIMAP_MARGIN
        screen.blit(panel, (panel_x, panel_y))

        self._draw_legend(screen, panel_x, panel_y + panel.get_height() + 8)

    def _draw_legend(self, screen, x, y):
        entries = [
            (COLOR_DOOR_CLOSED, "Door"),
            (COLOR_ELEVATOR, "Elevator"),
        ]
        row_h = 18
        for i, (color, label) in enumerate(entries):
            row_y = y + i * row_h
            pg.draw.rect(screen, color, (x, row_y, 12, 12))
            text = self.small_font.render(label, True, (220, 220, 220))
            screen.blit(text, (x + 18, row_y - 2))