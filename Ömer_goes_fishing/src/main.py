import pygame
from game_variables.game_variables import GameVariables as gv
from game_variables.game_variables import GameScreens
from save_manager import load_save, delete_save, save_game


def save_slots_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_5/5.png")
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    pygame.display.set_caption("Save Slots Screen")

    back_text = gv.FONT_BIG.render("X", True, "white")
    back_rect = back_text.get_rect(center=(gv.SCREEN_WIDTH // 5, 100))

    # KI-Anfang
    # KI: Qwen
    # 1. prompt: mach mir die buttons gui fürs save slot screen
    # 2. prompt: save files mit allen infos auslesen und in die buttons einfügen

    def refresh_ui():
        """Liest die Save-Dateien aus und rendert die Texte/Rects dynamisch neu."""
        texts, rects = [], []
        del_texts, del_rects = [], []

        for i in range(1, 4):
            y_pos = 100 + i * 100  # 200, 300, 400
            save_data = load_save(i)

            if save_data:
                label = f"Slot {i} | Geld: {save_data.get('money', '')}€ | {save_data.get('timestamp', '')}"
            else:
                label = f"Slot {i} - Neu starten"

            t = gv.FONT_MIDDLE.render(label, True, "white")
            r = t.get_rect(center=(gv.SCREEN_WIDTH // 2 - 100, y_pos))
            texts.append(t)
            rects.append(r)

            dt = gv.FONT_MIDDLE.render("Löschen", True, (255, 50, 50))
            dr = dt.get_rect(center=(gv.SCREEN_WIDTH // 2 + 150, y_pos))
            del_texts.append(dt)
            del_rects.append(dr)

        return texts, rects, del_texts, del_rects

    # Initiales Laden der UI-Elemente
    slot_texts, slot_rects, delete_texts, delete_rects = refresh_ui()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exit")
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Main Menu!")
                    return GameScreens.MAIN

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Slot-Auswahl -> Weiterleitung zum Play Screen
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(event.pos):
                        slot_num = i + 1

                        # Wenn der Slot leer ist, erstellen wir einen neuen Spielstand
                        if load_save(slot_num) is None:
                            save_game(slot_num, {"money": 0, "player_name": "Fischer"})

                        # Wir hängen dynamisch eine Variable an gv, damit der play_screen weiß,
                        # welcher Slot gerade aktiv ist.
                        gv.current_slot = slot_num
                        print(f"Slot {slot_num} ausgewählt -> Starte Spiel!")
                        return GameScreens.PLAY

                # Löschen-Buttons
                for i, rect in enumerate(delete_rects):
                    if rect.collidepoint(event.pos):
                        slot_num = i + 1
                        delete_save(slot_num)
                        # UI aktualisieren, damit "Neu starten" wieder dasteht
                        slot_texts, slot_rects, delete_texts, delete_rects = refresh_ui()
                        print(f"Slot {slot_num} gelöscht!")

                # Zurück-Button
                if back_rect.collidepoint(event.pos):
                    print("Main Menu!")
                    return GameScreens.MAIN

        screen.blit(Hintergrund, Hintergrund_rect)

        # 5. Dann den Text (die eigentlichen Buttons) darüber zeichnen
        for i in range(3):
            screen.blit(slot_texts[i], slot_rects[i])
            screen.blit(delete_texts[i], delete_rects[i])
        screen.blit(back_text, back_rect)

        # KI ende

        pygame.display.flip()
        clock.tick(gv.FPS)


def play_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    pygame.display.set_caption("Play Screen")

    # Wasser laden und optimieren
    wasser_gesamt = pygame.image.load("./assets/Haupt_Fisch_Sachen/3 Objects/Water.png").convert_alpha()

    # Dynamische Größenermittlung des Wasserbildes, um "out of surface area" Crash zu verhindern:
    img_w = wasser_gesamt.get_width()
    img_h = wasser_gesamt.get_height()

    # Wenn das Bild kleiner als 96x48 ist, nutzen wir die Maximalgröße des Bildes, sonst schneiden wir 96x48 aus
    water_tile_w = min(96, img_w)
    water_tile_h = min(48, img_h)
    wasser_tile = wasser_gesamt.subsurface(pygame.Rect(0, 0, water_tile_w, water_tile_h))

    # Sand laden, optimieren und Größe dynamisch auslesen
    sand_tile = pygame.image.load("./assets/Sand/new_piskel_5.png").convert()
    sand_tile_w = sand_tile.get_width()
    sand_tile_h = sand_tile.get_height()

    # Dimensionen für die vertikale Aufteilung festlegen
    sand_bloecke_breite = 3  # Wie viele Kacheln Sand nebeneinander?
    sand_width = sand_bloecke_breite * sand_tile_w  # Nutzt die echte Breite der Kachel
    sand_height = gv.SCREEN_HEIGHT  # Volle Höhe von oben nach unten

    water_width = gv.SCREEN_WIDTH - sand_width  # Der restliche Platz rechts auf dem Bildschirm
    water_height = gv.SCREEN_HEIGHT

    # Sand-Fläche vorrendern (Links)
    sand_surface = pygame.Surface((sand_width, sand_height))
    for y in range(0, sand_height, sand_tile_h):
        for x in range(0, sand_width, sand_tile_w):
            sand_surface.blit(sand_tile, (x, y))

    # Wasser-Fläche vorrendern (Rechter Rest)
    water_surface = pygame.Surface((water_width, water_height))
    for y in range(0, water_height, water_tile_h):
        # "+ water_tile_w" sorgt dafür, dass das Wasser rechts lückenlos kachelt
        for x in range(0, water_width + water_tile_w, water_tile_w):
            water_surface.blit(wasser_tile, (x, y))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exit")
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Main Menu!")
                    return GameScreens.MAIN

        # Screen mit schwarz füllen (als Basis)
        screen.fill((0, 0, 0))

        # Die beiden großen vorbereiteten Flächen nebeneinander zeichnen
        screen.blit(sand_surface, (0, 0))  # Sand startet ganz links bei X=0
        screen.blit(water_surface, (sand_width, 0))  # Wasser startet exakt da, wo der Sand aufhört

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