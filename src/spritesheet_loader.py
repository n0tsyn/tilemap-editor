import pygame
import json

def load_standard(pngpath, jsonpath):
    sheet, data = None, None
    imgs = list()
            
    sheet = pygame.image.load(pngpath).convert_alpha()
    data = json.load(open(jsonpath))

    width = data['spritesize']['width']
    height = data['spritesize']['height']

    for i in range(int(data['sheetsize']['height'] / height)):
        y = height * i

        for i2 in range(int(data['sheetsize']['width'] / width)):
            x = width * i2

            img = pygame.Surface((width, height)).convert_alpha()
            img.set_colorkey(pygame.Color((0, 0, 0)))
            img.blit(sheet, pygame.Vector2(0, 0), (x, y, width, height))

            imgs.append(img)

    return imgs