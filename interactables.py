import pygame as pg
import math

DOOR_OPEN_TIME = 5000
INTERACT_RANGE = 1.5

class Door:
    def __init__(self, pos):
        self.pos = pos
        self.state = "closed"
        self.open_timer = 0

    def interact(self):
        if self.state == "closed":
            self.state = "open"
            self.open_timer = pg.time.get_ticks()
        else:
            self.open_timer = pg.time.get_ticks()

    def update(self):
        if self.state == "open":
            if pg.time.get_ticks() - self.open_timer > DOOR_OPEN_TIME:
                self.state = "closed"

    @property
    def blocks_movement(self):
        return self.state == "closed"

    @property
    def blocks_sight(self):
        return self.state == "closed"


class Elevator:
    def __init__(self, pos, destination):
        self.pos = pos
        self.destination = destination
        self.state = "idle"  # kept for compatibility

    def interact(self, game):
        """Player pressed E while standing on this elevator tile."""
        game.start_elevator_ride(self)

    def update(self, game):
        # Elevator ride is now fully managed by Game (timer, teleport)
        pass

    def ride_progress(self):
        # Not used – game handles progress
        return 0.0


def find_interactable_near(game, interactable_dict):
    """Return the nearest Door within range."""
    player = game.player
    best = None
    best_dist = INTERACT_RANGE
    for pos, obj in interactable_dict.items():
        if isinstance(obj, Door):
            tile_cx, tile_cy = pos[0] + 0.5, pos[1] + 0.5
            dist = math.hypot(tile_cx - player.x, tile_cy - player.y)
            if dist < best_dist:
                best_dist = dist
                best = obj
    return best