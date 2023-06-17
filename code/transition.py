import pygame

from settings import *


class Transition:
    def __init__(self, reset, player, sky):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.reset = reset
        self.player = player
        self.active = False

        # overlay image
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.sky = sky
        self.speed = -200
        self.color = (0, 0, 0)

    def play(self, dt):
        # set the start color once and then start the transition to black and white
        if not self.active:
            self.color = self.sky.start_color.copy()
            self.active = True
        for index, item in enumerate(self.color):
            self.color[index] += self.speed * dt
            # get dark and then light
            if self.color[index] >= 0:
                if self.color[index] >= 255:
                    self.color[index] = 255
            else:
                self.color[index] = 0

        # check if sky is white
        if self.color[0] == 255 and self.color[1] == 255 and self.color[2] == 255:
            self.speed *= -1
            self.player.sleep = False
            self.active = False
            self.sky.start_color = self.color.copy()

        # check if the sky is black
        elif self.color[0] == 0 and self.color[1] == 0 and self.color[2] == 0:
            self.speed *= -1
            self.reset()

        self.image.fill((self.color[0], self.color[1], self.color[2]))

        self.display_surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
