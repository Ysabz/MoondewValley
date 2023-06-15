from random import randint, choice

import pygame

from settings import LAYERS
from sprites import Generic
from util import import_folder


class Drop(Generic):
    def __init__(self, surf, pos, moving, groups, z):
        super().__init__(pos, surf, groups, z)
        # general setup
        self.duration = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        # moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.dir_vec = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt):
        # movement
        if self.moving:
            self.pos += self.dir_vec * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        # timer
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.kill()


# TODO set a duration for the whole rain session
class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('../graphics/rain/drops/')
        self.rain_floor = import_folder('../graphics/rain/floor/')
        self.screen_w, self.screen_h = pygame.image.load('../graphics/world/ground.png').get_size()

    def create_floor(self):
        Drop(choice(self.rain_floor), (randint(0, self.screen_w), randint(0, self.screen_h)), False, self.all_sprites,
             LAYERS['rain floor'])

    def create_drops(self):
        Drop(choice(self.rain_drops), (randint(0, self.screen_w), randint(0, self.screen_h)), False, self.all_sprites,
             LAYERS['rain drops'])

    def update(self):
        self.create_floor()
        self.create_drops()
