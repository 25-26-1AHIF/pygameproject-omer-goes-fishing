import pygame
from game_variables.game_variables import GameVariables as gv
from game_variables.game_variables import GameScreens

def play_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    pygame.display.set_caption("Play Screen")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.MAIN

        screen.fill("black")
        pygame.display.flip()
        clock.tick(gv.FPS)

def main_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> GameScreens:
    pygame.display.set_caption("Main Screen")

    titel_text = gv.FONT_BIG.render("Ömer goes fishing", True, "white")
    starten_text = gv.FONT_MIDDLE.render("Start", True, "white")
    controls_text = gv.FONT_MIDDLE.render("Controls", True, "white")
    exit_text = gv.FONT_MIDDLE.render("Exit", True, "white")

    title_text_rect = titel_text.get_rect(center = (gv.SCREEN_WIDTH // 1.2, 100))
    starten_text_rect = starten_text.get_rect(center = (gv.SCREEN_WIDTH // 4, 250))
    controls_text_rect = controls_text.get_rect(center = (gv.SCREEN_WIDTH // 4, 350))
    exit_text_rect = exit_text.get_rect(center = (gv.SCREEN_WIDTH // 4, 450))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.EXIT
            if event.type == pygame.MOUSEBUTTONDOWN:
                if starten_text_rect.collidepoint(event.pos):
                    print("Start!")
                    return GameScreens.PLAY
                if controls_text_rect.collidepoint(event.pos):
                    print("Controls!")
                    #Todo Controls Screen
                if exit_text_rect.collidepoint(event.pos):
                    print("Exit!")
                    return GameScreens.EXIT
        screen.fill("black")
        screen.blit(titel_text, title_text_rect)
        screen.blit(starten_text, starten_text_rect)
        screen.blit(controls_text, controls_text_rect)
        screen.blit(exit_text, exit_text_rect)


        pygame.display.flip()
        clock.tick(gv.FPS)

def main():
    gv.init()
    screen = pygame.display.set_mode((gv.SCREEN_WIDTH, gv.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    while True:
        if GameScreens.actual == GameScreens.MAIN:
            GameScreens.actual = main_screen(screen, clock)
        elif GameScreens.actual == GameScreens.PLAY:
            GameScreens.actual = play_screen(screen, clock)
        elif GameScreens.actual == GameScreens.EXIT:
            break
    pygame.quit()

if __name__ == '__main__':
    main()