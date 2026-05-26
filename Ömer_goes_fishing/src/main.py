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

    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_4/5.png")
    Boot_ctrls = gv.FONT_MIDDLE.render("A/D  für links und rechts bewegen vom Boot", True, "white")
    Köder_ctrls = gv.FONT_MIDDLE.render("SPACE für Köder werfen", True, "white")
    minigame_ctrls = gv.FONT_MIDDLE.render("Beim Angel Minigame SPACE gedrückt halten zum Verfolgen vom Fisch", True, "white")
    interact_ctrl = gv.FONT_MIDDLE.render("Links Klick für Menü Interaktion", True, "white")
    pause_ctrl = gv.FONT_MIDDLE.render("ESC für Pausenmenü / Exit", True, "white")
    x = gv.FONT_BIG.render("X", True, "white")

    Hintergrund_rect = Hintergrund.get_rect(center = (gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    Boot_ctrls_rect = Boot_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 150))
    Köder_ctrls_rect = Köder_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 250))
    minigame_ctrls_rect = minigame_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 350))
    interact_ctrl_rect = interact_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 450))
    pause_ctrl_rect = pause_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 550))
    x_rect = x.get_rect(center=(gv.SCREEN_WIDTH // 5, 100))


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.MAIN
            if event.type == pygame.MOUSEBUTTONDOWN:
                if x_rect.collidepoint(event.pos):
                    print("Main Menu!")
                    return GameScreens.MAIN

        screen.blit(Hintergrund, Hintergrund_rect)
        screen.blit(Boot_ctrls, Boot_ctrls_rect)
        screen.blit(Köder_ctrls, Köder_ctrls_rect)
        screen.blit(minigame_ctrls, minigame_ctrls_rect)
        screen.blit(interact_ctrl, interact_ctrl_rect)
        screen.blit(pause_ctrl, pause_ctrl_rect)
        screen.blit(x, x_rect)
        pygame.display.flip()
        clock.tick(gv.FPS)


def main_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> GameScreens:
    pygame.display.set_caption("Main Screen")

    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_4/5.png")
    Logo = pygame.image.load("./assets/Logo/logo_ohne_hintergrund.png")
    starten_text = gv.FONT_MIDDLE.render("Start", True, "white")
    controls_text = gv.FONT_MIDDLE.render("Controls", True, "white")
    exit_text = gv.FONT_MIDDLE.render("Exit", True, "white")

    Hintergrund_rect = Hintergrund.get_rect(center = (gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
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
                if exit_text_rect.collidepoint(event.pos):
                    print("Exit!")
                    return GameScreens.EXIT

        screen.blit(Hintergrund, Hintergrund_rect)
        screen.blit(Logo, title_text_rect)
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
        elif GameScreens.actual == GameScreens.CONTROLS:
            GameScreens.actual = controls_screen(screen, clock)
        elif GameScreens.actual == GameScreens.EXIT:
            break
    pygame.quit()

if __name__ == '__main__':
    main()