from os import walk

import pygame.image


def import_folder(path):
    surface_list = []

    for _, _, img_files in walk(path):
        for img in img_files:
            image_path = path + "/" + img
            img_surf = pygame.image.load(image_path).convert_alpha()
            surface_list.append(img_surf)

    return surface_list


def import_folder_dict(path):
    surface_dict = {}
    for _, _, img_files in walk(path):
        for img in img_files:
            image_path = path + "/" + img
            img_surf = pygame.image.load(image_path).convert_alpha()
            surface_dict[img.split('.')[0]] = img_surf

    return surface_dict
