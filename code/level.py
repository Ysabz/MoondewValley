import pygame
from pytmx.util_pygame import load_pygame

from menu import Menu
from overlay import Overlay
from player import Player
from settings import *
from sky import Rain, Sky
from soil import SoilLayer
from sprites import Generic, Water, WildFlower, Tree, Interaction
from transition import Transition
from util import *


# make rain random after reset instead of using input
class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = True
        self.sky = Sky(self.reset)

        # shop
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)

    def setup(self):
        tmx_data = load_pygame('../data/map.tmx')

        # importing items in the map and placing in the game surface
        # house -> need to multiply the position by the tile size
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

        # water ( is animated so we need to import all the frames)
        water_frames = import_folder('../graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites, self.tree_sprites], obj.name,
                 self.all_sprites, self.player_add)

        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # Question why we do not add the items in the collision layer to the collision group while we are importing
        #  them? maybe because they are wrapped in a named layer and not all the items in that layer are collidable
        #  collision tiles (not in the all_sprite group so it is not updated or drawn) also some parts of the map
        #  such as lawns that are not imported but part of the map itself can have collsion through this method
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    (obj.x, obj.y), self.all_sprites, self.all_sprites, self.collision_sprites, self.tree_sprites,
                    self.interaction_sprites, self.soil_layer, self.toggle_shop)

            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

        Generic((0, 0), pygame.image.load('../graphics/world/ground.png').convert_alpha(), self.all_sprites,
                LAYERS['ground'])

    def player_add(self, item):
        self.player.item_inventory[item] += 1

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    # when the sky gets dark enough, it should call the reset to start the new day
    def reset(self):
        # soil
        self.soil_layer.grow_plants()
        self.soil_layer.remove_water()

        # trees (apples regrow) if the tree is not cut down
        for tree in self.tree_sprites.sprites():
            if tree.alive:
                # destroy previous apples
                for apple in tree.apple_sprites.sprites():
                    apple.kill()
                tree.create_fruit()

    def run(self, dt):
        # drawing logic
        keys = pygame.key.get_pressed()
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        # updates
        if self.shop_active:
            self.menu.update()
            self.raining = False
        else:
            self.all_sprites.update(dt)
            # rain control
            if keys[pygame.K_r] and not self.raining:
                self.raining = True

            if keys[pygame.K_s] and self.raining:
                self.raining = False

        self.overlay.display()

        # daytime
        self.sky.display(dt)

        if self.player.sleep:
            self.transition.play()



        if self.raining:
            self.rain.update()
            self.soil_layer.water_all()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # finding the vector from center to players current position
        # this vector is used (in reverse direction (-)) to draw everything else in the map
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        # use the layer to draw sprites in the correct depth order use sort to sort items based on their y position
        # for the behind/front effect -> items with lower y -> behind -> so drawn first
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

                    # # analytics (for test purpose)
                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.dir]
                    #     pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
