import pygame

from settings import *
from timer import Timer


class Menu:
    def __init__(self, player, toggle_menu):
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)

        # options
        self.width = 400
        self.space = 10
        self.padding = 8

        # entries
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()

        # movement
        self.index = 0
        self.timer = Timer(200)

    def display_money(self):
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 6)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):
        # create the text surface
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + self.padding * 2
        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

    def input(self):
        # get input
        # if player presses escape close the menu
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if keys[pygame.K_UP] and not self.timer.active:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.options) - 1
            self.timer.activate()

        if keys[pygame.K_DOWN] and not self.timer.active:
            self.index += 1
            if self.index > len(self.options) - 1:
                self.index = 0
            self.timer.activate()

    def show_entry(self, text_surf, amount, top, selected):
        # background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)
        # text
        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        # amount
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        # show a black outline around the selected item
        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)

    # Problem the sky transition should not affect the color of the menu
    def update(self):
        self.input()
        self.display_money()
        amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
        # pygame.draw.rect(self.display_surface, 'red', self.main_rect)
        for index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + index * (text_surf.get_height() + self.padding * 2 + self.space)
            self.show_entry(text_surf, amount_list[index], top, self.index == index)