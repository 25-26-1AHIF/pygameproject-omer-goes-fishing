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

def controls_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    pygame.display.set_caption("Controls Screen")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.MAIN

    screen.fill("blue")
    pygame.display.flip()
    clock.tick(gv.FPS)


def main_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> GameScreens:
    pygame.display.set_caption("Main Screen")

    Logo = pygame.image.load("./assets/Logo/logo_ohne_hintergrund.png")
    starten_text = gv.FONT_MIDDLE.render("Start", True, "white")
    controls_text = gv.FONT_MIDDLE.render("Controls", True, "white")
    exit_text = gv.FONT_MIDDLE.render("Exit", True, "white")

    title_text_rect = Logo.get_rect(center = (gv.SCREEN_WIDTH // 1.45, 350))
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
                    return GameScreens.CONTROLS
                    #Todo Controls Screen
                if exit_text_rect.collidepoint(event.pos):
                    print("Exit!")
                    return GameScreens.EXIT

        screen.fill("white")
        screen.blit(Logo, title_text_rect)
        screen.blit(starten_text, starten_text_rect)
        screen.blit(controls_text, controls_text_rect)
        screen.blit(exit_text, exit_text_rect)
        pygame.draw.rect(surface=screen, rect=starten_text_rect, color="red", width=1)
        pygame.draw.rect(surface=screen, rect=controls_text_rect, color="red", width=1)
        pygame.draw.rect(surface=screen, rect=exit_text_rect, color="red", width=1)
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
        elif GameScreens.actual == GameScreens.CONTROLS:
            GameScreens.actual = controls_screen(screen, clock)
        elif GameScreens.actual == GameScreens.EXIT:
            break
    pygame.quit()

if __name__ == '__main__':
    main()