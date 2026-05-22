import pygame
from game_variables.game_variables import GameVariables as gv
from game_variables.game_variables import GameScreens

def main_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    pygame.display.set_caption("Main Screen")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.EXIT

        screen.fill("black")
        pygame.display.flip()
        clock.tick(gv.FPS)

def main():
    gv.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    while True:
        if GameScreens.actual == GameScreens.MAIN:
            GameScreens.actual = main_screen(screen, clock)
        elif GameScreens.actual == GameScreens.EXIT:
            break

    pygame.quit()

if __name__ == '__main__':
    main()