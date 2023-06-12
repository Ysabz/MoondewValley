import pygame

from settings import *
from timer import Timer
from util import *


# Question why player is not inheriting the Generic?
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites):
        super().__init__(group)
        self.import_assets()
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.status = '_idle'
        self.action = 'down'
        self.frame_index = 0

        # general attributes
        self.image = self.animations[self.action + self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # movement attributes
        self.dir = pygame.math.Vector2()
        # we use a different attribute for position because rect only store integer which does not work with delta time
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # collision
        self.collision_sprites = collision_sprites
        self.hitbox = self.rect.copy().inflate((-126, -70))

        # timers
        self.timers = {
            'tool_use': Timer(350, self.use_tool),
            'tool_switch': Timer(250),
            'seed_use': Timer(350, self.use_seed),
            'seed_switch': Timer(250)
        }

        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def use_seed(self):
        print("seed used1")

    def use_tool(self):
        print(self.status + "3")

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
                           'up_hoe': [], 'down_hoe': [], 'left_hoe': [], 'right_hoe': [],
                           'up_axe': [], 'down_axe': [], 'left_axe': [], 'right_axe': [],
                           'up_water': [], 'down_water': [], 'left_water': [], 'right_water': [], }
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.action + self.status]):
            self.frame_index = 0
        self.image = self.animations[self.action + self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.timers['tool_use'].active:
            # vertical movement
            if keys[pygame.K_UP]:
                self.dir.y = -1
                self.action = 'up'
                self.status = ''
            elif keys[pygame.K_DOWN]:
                self.dir.y = 1
                self.action = 'down'
                self.status = ''

            else:
                self.dir.y = 0

            # horizontal movement
            if keys[pygame.K_LEFT]:
                self.dir.x = -1
                self.action = 'left'
                self.status = ''
            elif keys[pygame.K_RIGHT]:
                self.dir.x = 1
                self.action = 'right'
                self.status = ''

            else:
                self.dir.x = 0

            # Tool use
            if keys[pygame.K_SPACE]:
                # timer for tool use
                self.timers['tool_use'].activate()
                self.dir = pygame.math.Vector2()
                self.frame_index = 0

            # Change tool
            if keys[pygame.K_q] and not self.timers['tool_switch'].active:
                self.timers['tool_switch'].activate()
                self.tool_index += 1
                if self.tool_index >= len(self.tools):
                    self.tool_index = 0

            # seed use
            if keys[pygame.K_LCTRL]:
                self.timers['seed_use'].activate()
                self.dir = pygame.math.Vector2()
                self.frame_index = 0
                print('use seed')

            # change seed
            if keys[pygame.K_e] and not self.timers['seed_switch'].active:
                self.timers['seed_switch'].activate()
                self.seed_index += 1
                if self.seed_index >= len(self.seeds):
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]
                print(self.selected_seed)

    def collision(self, dir):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if dir == 'horizontal':
                        if self.dir.x > 0:  # moving to right
                            self.hitbox.right = sprite.hitbox.left
                        if self.dir.x < 0:  # moving to left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    else:
                        if self.dir.y > 0:  # moving  down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.dir.y < 0:  # moving  up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        if self.dir.magnitude() > 0:
            self.dir = self.dir.normalize()
        # horizontal movement
        self.pos.x += dt * self.speed * self.dir.x
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        # vertical movement
        self.pos.y += dt * self.speed * self.dir.y
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def get_status(self):
        # if player is not moving it should be idle
        # TODO use enum for action
        if self.timers['tool_use'].active:
            self.status = "_" + self.tools[self.tool_index]
        elif self.dir.magnitude() == 0:
            self.status = '_idle'

    def update_timer(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.get_status()
        self.update_timer()
