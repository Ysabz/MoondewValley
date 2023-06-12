import pygame

from settings import *
from timer import Timer
from util import *


# TODO what if player detecting collision, items detect collision so we don't need to loop through them to find which one was hit by player
# Question why player is not inheriting the Generic?
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites):
        super().__init__(group)
        self.import_assets()
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.status = '_idle'
        self.dir = 'down'
        self.frame_index = 0

        # general attributes
        self.image = self.animations[self.dir + self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # movement attributes
        self.dir_vec = pygame.math.Vector2()
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

        # interaction
        self.tree_sprites = tree_sprites

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.dir]

    def use_seed(self):
        print("seed used1")

    def use_tool(self):
        if self.tools[self.tool_index] == 'hoe':
            pass
        elif self.tools[self.tool_index] == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        elif self.tools[self.tool_index] == 'water':
            pass

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
        if self.frame_index >= len(self.animations[self.dir + self.status]):
            self.frame_index = 0
        self.image = self.animations[self.dir + self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.timers['tool_use'].active:
            # vertical movement
            if keys[pygame.K_UP]:
                self.dir_vec.y = -1
                self.dir = 'up'
                self.status = ''
            elif keys[pygame.K_DOWN]:
                self.dir_vec.y = 1
                self.dir = 'down'
                self.status = ''

            else:
                self.dir_vec.y = 0

            # horizontal movement
            if keys[pygame.K_LEFT]:
                self.dir_vec.x = -1
                self.dir = 'left'
                self.status = ''
            elif keys[pygame.K_RIGHT]:
                self.dir_vec.x = 1
                self.dir = 'right'
                self.status = ''

            else:
                self.dir_vec.x = 0

            # Tool use
            if keys[pygame.K_SPACE]:
                # timer for tool use
                self.timers['tool_use'].activate()
                self.dir_vec = pygame.math.Vector2()
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
                self.dir_vec = pygame.math.Vector2()
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
                        if self.dir_vec.x > 0:  # moving to right
                            self.hitbox.right = sprite.hitbox.left
                        if self.dir_vec.x < 0:  # moving to left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    else:
                        if self.dir_vec.y > 0:  # moving  down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.dir_vec.y < 0:  # moving  up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        if self.dir_vec.magnitude() > 0:
            self.dir_vec = self.dir_vec.normalize()
        # horizontal movement
        self.pos.x += dt * self.speed * self.dir_vec.x
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')
        # vertical movement
        self.pos.y += dt * self.speed * self.dir_vec.y
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def get_status(self):
        # if player is not moving it should be idle
        # TODO use enum for action
        if self.timers['tool_use'].active:
            self.status = "_" + self.tools[self.tool_index]
        elif self.dir_vec.magnitude() == 0:
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
        self.get_target_pos()
