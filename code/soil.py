from random import choice

import pygame
from pytmx.util_pygame import load_pygame

from settings import *
from sprites import Generic
from util import import_folder_dict, import_folder


class SoilLayer:
    def __init__(self, all_sprites):
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

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
                self.grid[y][x].append('W')
                water_surf = choice(self.water_surfs)
                Generic(soil_sprite.rect.topleft, water_surf, [self.all_sprites, self.water_sprites],
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
