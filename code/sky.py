from random import randint, choice

import pygame

from settings import *
from sprites import Generic
from timer import Timer
from util import import_folder


class Sky:
    def __init__(self, reset):
        self.display_surf = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        self.end_color = [38, 101, 189]
        self.transition_sign = -1
        self.dayTimer = Timer(120, self.reset_sky)
        self.reset = reset

    def display(self, dt):
        for index, value in enumerate(self.end_color):
            if (self.transition_sign == -1 and self.start_color[index] > value) or (
                    self.transition_sign == 1 and self.start_color[index] < value):
                self.start_color[index] += self.transition_sign * 15 * dt
        self.dayTimer.update()
        # check if already night
        if (self.transition_sign == -1 and not self.dayTimer.active and self.start_color[0] <= self.end_color[0] and
            self.start_color[1] <= self.end_color[1] and self.start_color[
                2] <= self.end_color[2]) or (
                self.transition_sign == 1 and not self.dayTimer.active and self.start_color[0] >= self.end_color[0] and
                self.start_color[1] >= self.end_color[1] and self.start_color[2] >= self.end_color[2]):
            self.dayTimer.activate()

        self.full_surf.fill(self.start_color)
        self.display_surf.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def reset_sky(self):
        if self.transition_sign == -1:
            self.start_color = [38, 101, 189]
            self.end_color = [255, 255, 255]
            self.transition_sign = 1
        else:
            self.reset()
            self.start_color = [255, 255, 255]
            self.end_color = [38, 101, 189]
            self.transition_sign = -1


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
