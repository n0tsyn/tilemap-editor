from src.spritesheet_loader import load_standard

import os
import pygame
import math

class Tile(pygame.sprite.Sprite):
    def __init__(self, position, img):
        pygame.sprite.Sprite.__init__(self)

        self.image = img
        self.data = None
        self.original_image = self.image
        self.original_size = pygame.Vector2(self.original_image.get_size())

        self.rect = self.image.get_bounding_rect()
        self.rect.x, self.rect.y = position
        self.original_rect = self.rect
            
        self.hovering = False
        self.selected = False

        self.hover_size = pygame.Vector2(
            round(self.original_size.x * 1.2),
            round(self.original_size.y * 1.2)
        )

    @property
    def mask(self):
        return pygame.mask.from_surface(self.image)

    def display(self, screen):
        if self.hovering and pygame.Vector2(self.image.get_size()) != self.hover_size:
            self.image = pygame.transform.scale(self.original_image, self.hover_size)

        elif not self.hovering and pygame.Vector2(self.image.get_size() == self.hover_size):
            self.image = pygame.transform.scale(self.original_image, self.original_size)

        if self.selected:
            surface = self.mask.to_surface(
                setcolor=pygame.Color(255, 255 ,255), 
                unsetcolor=pygame.Color(0, 0, 0, 0)
            )
            surface.set_colorkey(pygame.Color(0, 0, 0))

            for i in range(3):
                screen.blit(surface, pygame.Vector2(self.rect.x - i, self.rect.y))
                screen.blit(surface, pygame.Vector2(self.rect.x + i, self.rect.y))

                screen.blit(surface, pygame.Vector2(self.rect.x, self.rect.y - i))
                screen.blit(surface, pygame.Vector2(self.rect.x, self.rect.y + i))

                screen.blit(surface, pygame.Vector2(self.rect.x - i, self.rect.y - i))
                screen.blit(surface, pygame.Vector2(self.rect.x + i, self.rect.y + i))

                screen.blit(surface, pygame.Vector2(self.rect.x - i, self.rect.y + i))
                screen.blit(surface, pygame.Vector2(self.rect.x + i, self.rect.y - i))  
                
        screen.blit(self.image, self.rect)

class Editor():
    def __init__(self, screen_dimensions):
        sidebar = pygame.Surface(pygame.Vector2(screen_dimensions.x / 5, screen_dimensions.y))
        sidebar.fill(pygame.Color(25, 25, 25))
        self.sidebar = sidebar
        self.sidebar_offset = pygame.Vector2()

        topbar = pygame.Surface(pygame.Vector2(screen_dimensions.x - (screen_dimensions.x / 5), screen_dimensions.y / 5))
        topbar.fill(pygame.Color(30, 30, 30))
        self.topbar = topbar
        self.topbar_offset = pygame.Vector2(screen_dimensions.x / 5, 0)

        view = pygame.Surface(pygame.Vector2(screen_dimensions.x - (screen_dimensions.x / 5), screen_dimensions.y - (screen_dimensions.y / 5))).convert_alpha()
        view.fill(pygame.Color(0, 0, 0, 0))
        self.view = view
        self.view_rect = pygame.Rect(
            0,
            0,
            screen_dimensions.x - (screen_dimensions.x / 5), 
            screen_dimensions.y - (screen_dimensions.y / 5)
            )

        self.view_offset = pygame.Vector2(screen_dimensions.x / 5, screen_dimensions.y / 5)
        self.view_scroll_offset = pygame.Vector2()

        self.tile_dict = dict()
        self.tile_page = 0
        self.load_tiles()
        self.tiles = self.tile_dict[list(self.tile_dict.keys())[self.tile_page]]
        self.selected = None
        self.load_tileset()
    
        self.grid = dict()
        self.grid_layer = 0

        self.tile_size = 32
        self.tile_pos = pygame.Vector2()
        self.map_size = pygame.Vector2(200, 200)

        self.load_grid()
        
    def load_tiles(self):
        img_path = os.path.join('imgs')
        json_path = os.path.join('data', 'imgs')

        for sheet in os.listdir(img_path):
            match = None

            name = f'{os.path.splitext(sheet)[0]}.json'
            for root, _, files in os.walk(json_path):
                if name in files:
                    match = os.path.join(root, name) 

            if not match:
                continue
            
            imgs = list()
            tile_imgs, data = load_standard(os.path.join(img_path, sheet), match)
            for i, img in enumerate(tile_imgs):
                new_img = Tile(pygame.Vector2(), pygame.transform.scale2x(img).convert_alpha())
                new_img.data = data[i]

                imgs.append(new_img)

            self.tile_dict[os.path.splitext(sheet)[0]] = imgs

    def load_tileset(self):
        tile_width = self.tiles[0].rect.width
        offset = pygame.Vector2(tile_width / 2, 100)

        x = 0
        for tile in self.tiles:
            dest = pygame.Vector2(x * (tile_width * 1.5), 0) + offset
            if dest.x > self.sidebar.get_width():
                offset.y += tile_width * 2
                x = 0
                
                dest = pygame.Vector2(x * (tile_width * 1.5), 0)  + offset

            tile.rect.x, tile.rect.y = dest
            x += 1

    def load_grid(self):
        if not self.tile_size or not self.map_size:
            return
        
        for y in range(int(self.map_size.y)):
            for x in range(int(self.map_size.x)):
                self.grid[(x * self.tile_size, y * self.tile_size)] = dict()
                for i in range(10):
                    self.grid[(x * self.tile_size, y * self.tile_size)][i] = None

        self.view = pygame.transform.scale(self.view, pygame.Vector2(self.tile_size * self.map_size.x, self.tile_size * self.map_size.y)).convert_alpha()

    def display_grid(self):
        for pos, layers in self.grid.items():
            if pos[0] > self.view_rect.width + self.view_scroll_offset.x or pos[1] > self.view_rect.height + self.view_scroll_offset.y:
                continue
                
            for tile in layers.values():
                if not tile:
                    continue

                tile.display(self.view)

    def check_mouse(self):
        for tile in self.tiles:
            if tile.rect.collidepoint(pygame.mouse.get_pos()) and not tile.selected:
                tile.hovering = True
                continue

            tile.hovering = False

        if pygame.mouse.get_pressed()[0]:
            for tile in self.tiles:
                if not tile.hovering:
                    continue
                
                if tile != self.selected:
                    if self.selected:
                        self.selected.selected = False

                    self.selected = tile
                    tile.selected = True

            if self.view.get_rect().collidepoint(pygame.mouse.get_pos() - self.view_offset) and isinstance(self.selected, Tile):
                new_tile = Tile(pygame.Vector2(self.tile_pos), self.selected.image.copy().convert_alpha())
                new_tile.data = self.selected.data

                self.grid[self.tile_pos][self.grid_layer] = new_tile

    def check_hover(self):
        mouse_grid_position = pygame.mouse.get_pos() - self.view_offset

        if not self.view.get_rect().collidepoint(mouse_grid_position):
            return 

        if not isinstance(self.selected, Tile):
            return

        tile = self.selected.image.copy()
        tile_offset = pygame.Vector2(tile.get_size()) / 2
        grid_pos = dict()

        for pos in self.grid.keys():
            if pos[0] > mouse_grid_position.x or pos[1] > mouse_grid_position.y:
                continue

            rx = abs((pos[0] + tile_offset.x) - mouse_grid_position[0])
            ry = abs((pos[1] + tile_offset.y) - mouse_grid_position[1])

            grid_pos[pos] = math.sqrt(((rx **2) + (ry **2)))

        min_value = min(grid_pos.values())
        for pos, area in grid_pos.items():
            if area == min_value:
                self.tile_pos = pos

        self.view.blit(tile, self.tile_pos)

    def update(self, screen):
        self.sidebar.fill(pygame.Color(25, 25, 25))
        self.topbar.fill(pygame.Color(30, 30, 30))
        self.view.fill(pygame.Color(0, 0, 0, 0))
                
        self.check_mouse()
        self.display_grid()
        self.check_hover()

        for tile in self.tiles:
            tile.display(self.sidebar)

        screen.blit(self.sidebar, pygame.Vector2() + self.sidebar_offset)
        screen.blit(self.topbar, pygame.Vector2() + self.topbar_offset)
        screen.blit(self.view, pygame.Vector2() + self.view_offset)