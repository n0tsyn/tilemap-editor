def main(screen, clock, editor):
    quit = False
    
    while not quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
        
        screen.fill(pygame.Color(0, 0, 0))

        editor.update(screen)
        pygame.display.update()

        clock.tick(30)

if __name__ == '__main__':
    import pygame
    import sys

    from src.editor import Editor

    SCREEN_DIMENSIONS = pygame.Vector2(1280, 720)

    pygame.mixer.init()
    pygame.init()

    pygame.display.set_caption('tilemap_editor')

    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
    main(screen, pygame.time.Clock(), Editor(SCREEN_DIMENSIONS))
    
    pygame.quit()
    sys.exit()
