import pygame as pg
from interactables import Door, Elevator
import copy

# Base map (original)
_ = False
BASE_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,_,_,_,_,_,_,_,_,_,_,_,_,_,_,1],
    [1,_,_,3,3,3,3,_,_,_,2,2,2,_,_,1],
    [1,_,_,_,_,_,4,_,_,_,_,_,2,_,_,1],
    [1,_,_,_,_,_,4,_,_,_,_,_,2,_,_,1],
    [1,_,_,3,3,3,3,_,_,_,_,_,_,_,_,1],
    [1,_,_,_,_,_,_,_,_,_,_,_,_,_,_,1],
    [1,_,_,_,4,_,_,_,4,_,_,_,_,_,_,1],
    [1,1,1,_,6,_,1,1,1,3,_,_,3,1,1,1],
    [1,1,1,1,1,1,1,1,1,3,_,_,3,1,1,1],
    [1,1,1,1,1,1,1,1,1,3,_,_,3,1,1,1],
    [1,1,3,1,1,1,1,1,1,3,_,_,3,1,1,1],
    [1,4,_,_,_,_,_,_,_,_,_,_,_,_,_,1],
    [3,_,_,_,_,_,_,_,_,_,_,_,_,_,_,1],
    [1,_,_,_,_,_,_,_,_,_,_,_,_,_,_,1],
    [1,_,_,2,_,_,_,_,_,3,4,_,4,3,_,1],
    [1,_,_,5,_,_,_,_,_,_,3,_,3,_,_,1],
    [1,_,_,2,_,_,_,_,_,_,_,_,_,_,_,1],
    [1,_,_,_,_,_,_,_,_,_,_,_,_,_,_,1],
    [3,_,_,_,_,_,_,_,_,_,_,_,_,_,_,1],
    [1,4,_,_,_,_,_,_,4,_,_,4,_,_,_,1],
    [1,1,3,3,_,_,3,3,1,3,3,1,3,1,1,1],
    [1,1,1,3,_,_,3,1,1,1,1,1,1,1,1,1],
    [1,3,3,4,_,_,4,3,3,3,3,3,3,3,3,1],
    [3,_,_,_,_,_,_,_,_,_,_,_,_,_,_,3],
    [3,_,_,_,_,_,_,_,_,_,_,_,_,_,_,3],
    [3,_,_,_,_,_,_,_,_,_,_,_,_,_,_,3],
    [3,_,_,_,_,_,_,_,_,_,_,_,_,_,_,3],
    [3,_,9,9,9,9,9,9,_,_,_,_,_,_,_,3],
    [3,_,9,7,7,7,7,9,_,_,_,_,_,_,_,3],
    [3,_,9,7,7,7,7,9,_,_,_,_,_,_,_,3],
    [3,_,9,7,7,7,7,9,_,_,_,_,_,_,_,3],
    [3,_,9,9,6,9,9,9,_,_,_,_,_,_,_,3],
    [3,_,_,_,_,_,_,_,_,_,_,_,_,_,_,3],
    [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
]

def rotate_map(m):
    return [list(row) for row in zip(*m[::-1])]

def flip_map(m):
    return [row[::-1] for row in m]

def generate_maps(base, count=15):
    maps = [base]
    variants = []
    variants.append(base)
    for angle in [1,2,3]:
        m = copy.deepcopy(base)
        for _ in range(angle):
            m = rotate_map(m)
        variants.append(m)
    variants.append(flip_map(base))
    variants.append(flip_map(rotate_map(base)))
    variants.append(flip_map(rotate_map(rotate_map(base))))
    for angle in [1,2,3]:
        m = copy.deepcopy(base)
        for _ in range(angle):
            m = rotate_map(m)
        variants.append(flip_map(m))
    while len(variants) < count:
        variants.append(copy.deepcopy(base))
    return variants[:count]

ALL_MAPS = generate_maps(BASE_MAP, 15)

# Elevator links: (elevator tile pos) -> (destination tile pos)
ELEVATOR_LINKS = {
    (4, 29): (2, 2),
}

class Map:
    def __init__(self, game, level=1):
        self.game = game
        self.level = level
        self.mini_map = ALL_MAPS[(level-1) % len(ALL_MAPS)]
        self.world_map = {}
        self.doors = {}
        self.elevators = {}
        self.elevator_spawn = None  # will be set in get_map()
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.get_map()

    def get_map(self):
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                pos = (i, j)
                if value == 6:
                    self.world_map[pos] = 6
                    self.doors[pos] = Door(pos)
                elif value == 7:
                    # Elevator floor – walkable
                    dest = ELEVATOR_LINKS.get(pos, (i, j))
                    self.elevators[pos] = Elevator(pos, dest)
                    # Store the first elevator tile found as spawn point
                    if self.elevator_spawn is None:
                        self.elevator_spawn = (i + 0.5, j + 0.5)
                elif value == 9:
                    self.world_map[pos] = 9
                elif value:
                    self.world_map[pos] = value

        # Fallback if no elevator tile found (shouldn't happen)
        if self.elevator_spawn is None:
            self.elevator_spawn = (1.5, 1.5)

    def update(self):
        for door in self.doors.values():
            door.update()
        for elevator in self.elevators.values():
            elevator.update(self.game)

    def draw(self):
        for pos in self.world_map:
            pg.draw.rect(self.game.screen, 'darkgray', (pos[0]*100, pos[1]*100, 100, 100), 2)