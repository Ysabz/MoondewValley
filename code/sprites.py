from random import randint, choice

import pygame

from settings import *
from timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        # we don't want to shrink too much in horizontal but in vertical we want a higher shrink otherwise the
        # character is unable to go behind object (e.g sunflower)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


# water is animated
class Water(Generic):
    def __init__(self, pos, frames, groups):
        # animation setup
        self.frames = frames
        self.frame_index = 0

        # sprite setup
        super().__init__(pos, surf=self.frames[self.frame_index], groups=groups, z=LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        # white surface (using masks)
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)

        # tree attributes
        self.health = 5
        self.alive = True
        stump_path = f'../graphics/stumps/{"small" if name == "Small" else "large"}.png'
        self.stump_surf = pygame.image.load(stump_path).convert_alpha()
        self.invul_timer = Timer(200)

        # apples
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

    def damage(self):
        self.health -= 1
        # remove apple when the tree is hit
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(random_apple.rect.topleft, random_apple.image, self.groups()[0], LAYERS['fruit'])
            random_apple.kill()

    def check_health(self):
        if self.health <= 0:
            self.alive = False
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                # TODO this needs a cleaner way to get the all_sprites group
                Generic((x, y), self.apple_surf, [self.apple_sprites, self.groups()[0]], LAYERS['fruit'])

    def update(self, dt):
        if self.alive:
            self.check_health()
