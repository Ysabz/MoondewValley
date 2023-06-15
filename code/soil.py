from random import choice

import pygame
from pytmx.util_pygame import load_pygame

from settings import *
from sprites import Generic
from util import import_folder_dict, import_folder


class Plant:
    def __init__(self, pos_rect, groups, seed_type, check_watered):
        # seed needs to watered everyday for growth
        # For now, we update the seed everyday
        path = f'../graphics/fruit/{seed_type}/'
        self.pos = pos_rect
        self.frames = import_folder(path)
        self.grow_speed = GROW_SPEED[seed_type]
        self.fully_grown = False
        self.age = 0
        self.check_watered = check_watered
        self.sprite = Generic(pos_rect.center, self.frames[0], groups, LAYERS['ground plant'], True)

    def grow(self):
        # if not fully grown and watered
        if not self.fully_grown and self.check_watered(self.pos):
            # TODO need to call this function before reseting all the watering
            self.age += self.grow_speed
            self.sprite.image = self.frames[int(self.age)]
            self.sprite.rect = self.sprite.image.get_rect(center=self.pos.center)
            if self.age >= len(self.frames):
                self.fully_grown = True
            if int(self.age) > 0:
                self.sprite.z = LAYERS['main']
                self.sprite.hitbox = self.sprite.rect.copy().inflate(-26, -self.sprite.rect.height * 0.4)


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plants = []

        # graphics
        self.soil_surf = pygame.image.load('../graphics/soil/o.png')
        self.soil_surfs = import_folder_dict('../graphics/soil/')
        self.water_surfs = import_folder('../graphics/soil_water/')

        self.create_soil_grid()
        self.create_hit_rects()

        # requirements
        # if the area is farmable
        # if the soil has been watered
        # if the soil has a plant already

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    # For every farmable tile in the soil layer we make a rectangle that the player can hit
    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    soil_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(soil_rect)

    # Question shouldn't we return or break once we find the colliding point?
    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                # convert the rect to a point in grid
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    # indicate soil patch
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

    # Question should it be possible to rewater the same spot?
    # TODO instead of appending a string, check for boolean flags ? create a soil object with those flags
    def water(self, target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if 'W' not in self.grid[y][x]:
                    self.grid[y][x].append('W')
                    water_surf = choice(self.water_surfs)
                    Generic(soil_sprite.rect.topleft, water_surf, [self.all_sprites, self.water_sprites],
                            LAYERS['soil water'])

    def water_all(self):
        # Question why not going through soil_sprites instead of going through the whole grid?
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                # reminder 'X' mean there is a soil patch
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    water_surf = choice(self.water_surfs)
                    Generic((index_col * TILE_SIZE, index_row * TILE_SIZE), water_surf,
                            [self.all_sprites, self.water_sprites],
                            LAYERS['soil water'])

    def remove_water(self):
        # destroy all the water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        # cleanup the grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def plant_seed(self, target_pos, seed_type):
        # check if the target position is a soil patch and it does not contain a seed already
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if 'P' not in self.grid[y][x]:
                    self.plants.append(Plant(soil_sprite.rect, [self.all_sprites, self.collision_sprites], seed_type,
                                             self.check_watered))
                    # mark the soil as containing a plant
                    self.grid[y][x].append('P')

    def grow_plants(self):
        for plant in self.plants:
            plant.grow()

    def check_watered(self, soil_patch_pos):
        x = soil_patch_pos.x // TILE_SIZE
        y = soil_patch_pos.y // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def create_soil_tiles(self):
        # draw from scratch so we can connect patches that are adjacent
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    # tile options
                    # TODO fix the out of bound error?
                    # Fix the tile naming for a more efficient tile finding
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]
                    x = 'X' in self.grid[index_row - 1][index_col - 1] or 'X' in self.grid[index_row - 1][
                        index_col + 1] or 'X' in self.grid[index_row + 1][index_col - 1] or 'X' in \
                        self.grid[index_row + 1][index_col + 1]

                    tile_type = ''

                    if t: tile_type += 't'
                    if b: tile_type += 'b'
                    if l: tile_type += 'l'
                    if r: tile_type += 'r'
                    if not all((t, b, l, r)) and any(
                            (
                                    all((t, b, l)), all((t, b, r)), all((b, l, r)),
                                    all((t, l, r)))) and x: tile_type += 'x'

                    if not any((t, b, l, r)):
                        tile_type = 'o'

                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    Generic((x, y), self.soil_surfs[tile_type], [self.all_sprites, self.soil_sprites],
                            LAYERS['soil'])
