import pygame
from game_variables.game_variables import GameVariables as gv
from game_variables.game_variables import GameScreens


def save_slots_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_5/5.png")
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    pygame.display.set_caption("Save Slots Screen")

    # KI-Anfang
    # KI: Qwen
    # prompt: mach mir die buttons gui fürs save slot screen

    # 1. Texte für die Buttons erstellen
    slot1_text = gv.FONT_MIDDLE.render("Slot 1 - Leer", True, "white")
    slot2_text = gv.FONT_MIDDLE.render("Slot 2 - Leer", True, "white")
    slot3_text = gv.FONT_MIDDLE.render("Slot 3 - Leer", True, "white")
    back_text = gv.FONT_MIDDLE.render("X", True, "white")

    # Löschen-Texte (in Rot, damit es nach "Gefahr/Aktion" aussieht)
    delete1_text = gv.FONT_MIDDLE.render("Löschen", True, (255, 50, 50))
    delete2_text = gv.FONT_MIDDLE.render("Löschen", True, (255, 50, 50))
    delete3_text = gv.FONT_MIDDLE.render("Löschen", True, (255, 50, 50))

    # 2. Rechtecke für die Buttons
    # Slots etwas nach links versetzt, damit rechts Platz für den Löschen-Button ist
    slot1_rect = slot1_text.get_rect(center=(gv.SCREEN_WIDTH // 2 - 100, 200))
    slot2_rect = slot2_text.get_rect(center=(gv.SCREEN_WIDTH // 2 - 100, 300))
    slot3_rect = slot3_text.get_rect(center=(gv.SCREEN_WIDTH // 2 - 100, 400))

    # Löschen-Buttons rechts daneben
    delete1_rect = delete1_text.get_rect(center=(gv.SCREEN_WIDTH // 2 + 150, 200))
    delete2_rect = delete2_text.get_rect(center=(gv.SCREEN_WIDTH // 2 + 150, 300))
    delete3_rect = delete3_text.get_rect(center=(gv.SCREEN_WIDTH // 2 + 150, 400))

    back_rect = back_text.get_rect(center=(gv.SCREEN_WIDTH // 5, 100))


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exit")
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Main Menu!")
                    return GameScreens.MAIN

            # Maus-Klicks abfangen
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Slot-Auswahl -> Weiterleitung zum Play Screen
                if slot1_rect.collidepoint(event.pos):
                    print("Slot 1 ausgewählt -> Starte Spiel!")
                    return GameScreens.PLAY
                if slot2_rect.collidepoint(event.pos):
                    print("Slot 2 ausgewählt -> Starte Spiel!")
                    return GameScreens.PLAY
                if slot3_rect.collidepoint(event.pos):
                    print("Slot 3 ausgewählt -> Starte Spiel!")
                    return GameScreens.PLAY

                # Löschen-Buttons
                if delete1_rect.collidepoint(event.pos):
                    print("Slot 1 gelöscht!")
                    # Hier später deine Speicherstands-Logik einbauen:
                    # z.B. save_data[0].clear() und slot1_text neu rendern
                if delete2_rect.collidepoint(event.pos):
                    print("Slot 2 gelöscht!")
                if delete3_rect.collidepoint(event.pos):
                    print("Slot 3 gelöscht!")

                # Zurück-Button
                if back_rect.collidepoint(event.pos):
                    print("Main Menu!")
                    return GameScreens.MAIN

        screen.blit(Hintergrund, Hintergrund_rect)

        # 4. Dann den Text (die eigentlichen Buttons) darüber zeichnen
        screen.blit(slot1_text, slot1_rect)
        screen.blit(slot2_text, slot2_rect)
        screen.blit(slot3_text, slot3_rect)
        screen.blit(delete1_text, delete1_rect)
        screen.blit(delete2_text, delete2_rect)
        screen.blit(delete3_text, delete3_rect)
        screen.blit(back_text, back_rect)

        # KI ende

        pygame.display.flip()
        clock.tick(gv.FPS)


def play_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_1/4.png")
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    pygame.display.set_caption("Play Screen")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exit")
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Main Menu!")
                    return GameScreens.MAIN

        screen.blit(Hintergrund, Hintergrund_rect)
        pygame.display.flip()
        clock.tick(gv.FPS)


def controls_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    pygame.display.set_caption("Controls Screen")

    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_4/5.png")
    Boot_ctrls = gv.FONT_MIDDLE.render("A/D  für links und rechts bewegen vom Boot", True, "white")
    Köder_ctrls = gv.FONT_MIDDLE.render("SPACE für Köder werfen", True, "white")
    minigame_ctrls = gv.FONT_MIDDLE.render("Beim Angel Minigame SPACE gedrückt halten zum Verfolgen vom Fisch", True,
                                           "white")
    interact_ctrl = gv.FONT_MIDDLE.render("Links Klick für Menü Interaktion", True, "white")
    pause_ctrl = gv.FONT_MIDDLE.render("ESC für Pausenmenü / Exit", True, "white")
    x = gv.FONT_BIG.render("X", True, "white")

    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    Boot_ctrls_rect = Boot_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 150))
    Köder_ctrls_rect = Köder_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 250))
    minigame_ctrls_rect = minigame_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 350))
    interact_ctrl_rect = interact_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 450))
    pause_ctrl_rect = pause_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 550))
    x_rect = x.get_rect(center=(gv.SCREEN_WIDTH // 5, 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exit!")
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Main Menu!")
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

    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    title_text_rect = Logo.get_rect(center=(gv.SCREEN_WIDTH // 1.45, 350))
    starten_text_rect = starten_text.get_rect(center=(gv.SCREEN_WIDTH // 4, 250))
    controls_text_rect = controls_text.get_rect(center=(gv.SCREEN_WIDTH // 4, 350))
    exit_text_rect = exit_text.get_rect(center=(gv.SCREEN_WIDTH // 4, 450))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exit!")
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Exit!")
                    return GameScreens.EXIT
            if event.type == pygame.MOUSEBUTTONDOWN:
                if starten_text_rect.collidepoint(event.pos):
                    print("Start!")
                    return GameScreens.SAVE_SLOTS
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
        elif GameScreens.actual == GameScreens.SAVE_SLOTS:
            GameScreens.actual = save_slots_screen(screen, clock)
        elif GameScreens.actual == GameScreens.EXIT:
            break
    pygame.quit()


if __name__ == '__main__':
    main()