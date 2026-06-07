# main.py
import pygame
from game_variables.game_variables import GameVariables as gv
from game_variables.game_variables import GameScreens
from save_manager import load_save, delete_save, save_game

# Eigene Spiel-Module importieren
from inventar import Inventory
from angelsystem import FishingSystem


def save_slots_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    """Bildschirm für die Auswahl und das Löschen der 3 Spielstände."""
    pygame.display.set_caption("Save Slots Screen")

    # Hintergrund laden und über ein Rechteck exakt in der Bildschirmmitte zentrieren
    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_5/5.png")
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))

    # "Zurück"-Button (X) oben links vorbereiten
    back_text = gv.FONT_BIG.render("X", True, "white")
    back_rect = back_text.get_rect(center=(gv.SCREEN_WIDTH // 5, 100))

    def refresh_ui():
        """Interne Hilfsfunktion: Schaut auf der Festplatte nach Speicherständen
        und bereitet die Texte für die Anzeige frisch vor."""
        texts, rects = [], []
        del_texts, del_rects = [], []

        for i in range(1, 4):
            y_pos = 100 + i * 100  # Verteilt die Slots sauber untereinander (200, 300, 400)
            save_data = load_save(i)

            # Text bestimmen: Gibt es Daten, zeigen wir Geld & Zeit. Wenn nicht -> "Neu starten"
            if save_data:
                label = f"Slot {i} | Geld: {save_data.get('money', '')}€ | {save_data.get('timestamp', '')}"
            else:
                label = f"Slot {i} - Neu starten"

            # Slot-Button generieren
            t = gv.FONT_MIDDLE.render(label, True, "white")
            r = t.get_rect(center=(gv.SCREEN_WIDTH // 2 - 100, y_pos))
            texts.append(t)
            rects.append(r)

            # "Löschen"-Button generieren
            dt = gv.FONT_MIDDLE.render("Löschen", True, (255, 50, 50))
            dr = dt.get_rect(center=(gv.SCREEN_WIDTH // 2 + 250, y_pos))
            del_texts.append(dt)
            del_rects.append(dr)

        return texts, rects, del_texts, del_rects

    # Benutzeroberfläche das erste Mal generieren
    slot_texts, slot_rects, delete_texts, delete_rects = refresh_ui()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return GameScreens.MAIN

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 1. Prüfen, ob ein Spielstand-Slot angeklickt wurde
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(event.pos):
                        slot_num = i + 1
                        # Falls der Slot leer ist, legen wir direkt eine neue Standard-Datei an
                        if load_save(slot_num) is None:
                            save_game(slot_num, {"money": 0, "player_name": "Fischer"})
                        gv.current_slot = slot_num
                        return GameScreens.PLAY

                # 2. Prüfen, ob ein Löschen-Button angeklickt wurde
                for i, rect in enumerate(delete_rects):
                    if rect.collidepoint(event.pos):
                        slot_num = i + 1
                        delete_save(slot_num)
                        # UI sofort aktualisieren, damit der Slot visuell wieder frei wird
                        slot_texts, slot_rects, delete_texts, delete_rects = refresh_ui()

                # 3. Prüfen, ob der Zurück-Button (X) geklickt wurde
                if back_rect.collidepoint(event.pos):
                    return GameScreens.MAIN

        # --- RENDERING (Zeichnen) ---
        screen.blit(Hintergrund, Hintergrund_rect)
        for i in range(3):
            screen.blit(slot_texts[i], slot_rects[i])
            screen.blit(delete_texts[i], delete_rects[i])
        screen.blit(back_text, back_rect)

        pygame.display.flip()
        clock.tick(gv.FPS)


def play_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    """Das eigentliche Gameplay: Boot fahren, Angeln, Fische verkaufen."""
    pygame.display.set_caption("Play Screen")

    # Instanzen für das Inventar und das Angelsystem erzeugen
    inventory = Inventory()
    fishing_system = FishingSystem(inventory)

    # --- HINTERGRUND-BERECHNUNG (DEINE KORREKTE LOGIK) ---
    # Wir laden das Bild und berechnen den Skalierungsfaktor so, dass das Seitenverhältnis
    # stabil bleibt (max-Funktion sorgt dafür, dass der Bildschirm lückenlos ausgefüllt wird).
    Hintergrund_raw = pygame.image.load("./assets/Hintergründe/Ocean_1/4.png").convert()
    bg_w, bg_h = Hintergrund_raw.get_size()
    scale_factor_bg = max(gv.SCREEN_WIDTH / bg_w, gv.SCREEN_HEIGHT / bg_h)
    new_bg_w = int(bg_w * scale_factor_bg)
    new_bg_h = int(bg_h * scale_factor_bg)
    Hintergrund = pygame.transform.scale(Hintergrund_raw, (new_bg_w, new_bg_h))
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))

    # Kachel-Einstellungen für die Spielwelt am unteren Rand
    TARGET_BLOCK_SIZE = 96
    bloecke_hoch = 1
    sand_bloecke_breite = 3

    # Wasser-Kacheln vorbereiten (Seitenverhältnis des Tiles wahren)
    wasser_tile_raw = pygame.image.load("./assets/Haupt_Fisch_Sachen/3 Objects/Water.png").convert_alpha()
    wasser_scaled_h = TARGET_BLOCK_SIZE
    wasser_scaled_w = int(wasser_tile_raw.get_width() * (wasser_scaled_h / wasser_tile_raw.get_height()))
    wasser_tile = pygame.transform.scale(wasser_tile_raw, (wasser_scaled_w, wasser_scaled_h))

    # Sand-Kacheln vorbereiten
    sand_tile_raw = pygame.image.load("./assets/Sand/new_piskel_5.png").convert()
    sand_tile = pygame.transform.scale(sand_tile_raw, (TARGET_BLOCK_SIZE, TARGET_BLOCK_SIZE))

    # Maße und Positionen für die Kachelflächen berechnen
    bereich_height = bloecke_hoch * TARGET_BLOCK_SIZE
    y_position_am_boden = gv.SCREEN_HEIGHT - bereich_height
    sand_width = sand_bloecke_breite * TARGET_BLOCK_SIZE
    water_width = gv.SCREEN_WIDTH - sand_width

    # Sand-Bodenfläche mit einer Schleife kacheln
    sand_surface = pygame.Surface((sand_width, bereich_height), pygame.SRCALPHA)
    for y in range(0, bereich_height, TARGET_BLOCK_SIZE):
        for x in range(0, sand_width, TARGET_BLOCK_SIZE):
            sand_surface.blit(sand_tile, (x, y))

    # Wasser-Bodenfläche mit einer Schleife kacheln
    water_surface = pygame.Surface((water_width, bereich_height + 2), pygame.SRCALPHA)
    for y in range(0, bereich_height, wasser_scaled_h):
        for x in range(0, water_width + wasser_scaled_w, wasser_scaled_w):
            water_surface.blit(wasser_tile, (x, y))

    # Grafiken für Boot und Fischer laden und skalieren
    SCALE_FACTOR = 2.5
    boot_raw = pygame.image.load("./assets/Haupt_Fisch_Sachen/3 Objects/Boat.png").convert_alpha()
    boot_img = pygame.transform.scale(boot_raw, (int(boot_raw.get_width() * SCALE_FACTOR),
                                                 int(boot_raw.get_height() * SCALE_FACTOR)))

    fischer_sheet = pygame.image.load("./assets/Haupt_Fisch_Sachen/1 Fisherman/Fisherman_walk.png").convert_alpha()
    fischer_ganz_raw = fischer_sheet.subsurface(pygame.Rect(0, 0, 48, 38))
    fischer_img = pygame.transform.scale(fischer_ganz_raw, (int(fischer_ganz_raw.get_width() * SCALE_FACTOR),
                                                            int(fischer_ganz_raw.get_height() * SCALE_FACTOR)))

    # Start-Positionen und Grenzen für die Bootsbewegung festlegen
    boat_y = y_position_am_boden - int(12 * SCALE_FACTOR) - 1
    player_x = sand_width + 20
    player_speed = 5
    max_x = gv.SCREEN_WIDTH - boot_img.get_width()

    # Offsets, damit der Fischer perfekt auf seiner Bank IM Boot hockt
    player_x_offset = int(18 * SCALE_FACTOR)
    player_y_offset = int(-30 * SCALE_FACTOR)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return GameScreens.MAIN

            # Leitet Events (z.B. SPACE-Taste) direkt an das Angelsystem-Modul weiter
            fishing_system.handle_event(event)

        # Kontinuierliche Tastenabfrage (halten der Tasten)
        keys = pygame.key.get_pressed()

        # Das Boot darf nur gesteuert werden, wenn man NICHT im Angel-Minigame ist
        if fishing_system.state != "MINIGAME":
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_x -= player_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_x += player_speed

        # Grenzen prüfen (Boot stoppt am Strand und rechts am Bildschirmrand)
        if player_x < sand_width - 40: player_x = sand_width - 40
        if player_x > max_x: player_x = max_x

        # Wenn der Spieler am Strand steht und 'E' drückt -> Fische verkaufen
        if player_x <= sand_width and keys[pygame.K_e]:
            inventory.sell_all_fish()

        # Angelsystem-Logik updaten
        fishing_system.update()

        # --- RENDERING (SPIELWELT ZEICHNEN) ---
        screen.fill((0, 0, 0))
        screen.blit(Hintergrund, Hintergrund_rect)
        screen.blit(sand_surface, (0, y_position_am_boden))
        screen.blit(water_surface, (sand_width, y_position_am_boden - 1))

        # Erst Fischer (Hintergrund-Ebene), dann Boot (Vordergrund-Ebene), damit er drin sitzt
        screen.blit(fischer_img, (player_x + player_x_offset, boat_y + player_y_offset))
        screen.blit(boot_img, (player_x, boat_y))

        # Das Angel-Minigame (Balken, Fisch) über die Welt zeichnen
        fishing_system.draw(screen)

        # --- BENUTZEROBERFLÄCHE (HUD) ---
        slot = getattr(gv, 'current_slot', 1)
        save_data = load_save(slot) or {"money": 0}

        # Geldanzeige mit deinem definierten Ziel-Format
        money_txt = gv.FONT_MIDDLE.render(f"Geld: {save_data.get('money', 0)}€ / 50.000,--€", True, "white")
        screen.blit(money_txt, (20, 20))

        # Überprüfung der globalen Win-Condition
        if save_data["money"] >= 50000:
            end_txt = gv.FONT_BIG.render("Glückwunsch! Du hast 50.000€ erreicht!", True, "green")
            end_rect = end_txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
            screen.blit(end_txt, end_rect)

        # Aktuelles Fische-Inventar als Textzeile aufbereiten
        inv_list = [f"{count}x {fish}" for fish, count in inventory.content.items()]
        inv_string = ", ".join(inv_list) if inv_list else "Leer"
        inv_txt = gv.FONT_SMALL.render(f"Inventar: {inv_string}", True, (200, 200, 200))
        screen.blit(inv_txt, (20, 55))

        # Shop-Hinweis einblenden, sobald das Boot nah genug am Strand steht
        if player_x <= sand_width:
            shop_txt = gv.FONT_SMALL.render("Drücke 'E' zum Fische verkaufen", True, (255, 255, 100))
            draw_rect = shop_txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 12))
            screen.blit(shop_txt, draw_rect)

        pygame.display.flip()
        clock.tick(gv.FPS)


def controls_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    """Der Steuerungs-Bildschirm mit Erklärungen für den Spieler."""
    pygame.display.set_caption("Controls Screen")

    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_4/5.png")
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))

    # Steuerungstexte rendern
    Boot_ctrls = gv.FONT_MIDDLE.render("A/D  für links und rechts bewegen vom Boot", True, "white")
    Köder_ctrls = gv.FONT_MIDDLE.render("SPACE für Köder werfen", True, "white")
    minigame_ctrls = gv.FONT_MIDDLE.render("Beim Angel Minigame SPACE gedrückt halten zum Verfolgen vom Fisch", True,
                                           "white")
    interact_ctrl = gv.FONT_MIDDLE.render("Links Klick für Menü Interaktion", True, "white")
    pause_ctrl = gv.FONT_MIDDLE.render("ESC für Pausenmenü / Exit", True, "white")
    x = gv.FONT_BIG.render("X", True, "white")

    # Alle Texte auf festen Positionen zentrieren
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return GameScreens.MAIN
            if event.type == pygame.MOUSEBUTTONDOWN and x_rect.collidepoint(event.pos):
                return GameScreens.MAIN

        # Zeichnen
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
    """Das Hauptmenü direkt beim Spielstart."""
    pygame.display.set_caption("Main Screen")

    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_4/5.png")
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))

    Logo = pygame.image.load("./assets/Logo/logo_ohne_hintergrund.png")
    starten_text = gv.FONT_MIDDLE.render("Start", True, "white")
    controls_text = gv.FONT_MIDDLE.render("Controls", True, "white")
    exit_text = gv.FONT_MIDDLE.render("Exit", True, "white")

    # Klickboxen für das Logo und die Buttons definieren
    title_text_rect = Logo.get_rect(center=(gv.SCREEN_WIDTH // 1.45, 350))
    starten_text_rect = starten_text.get_rect(center=(gv.SCREEN_WIDTH // 4, 250))
    controls_text_rect = controls_text.get_rect(center=(gv.SCREEN_WIDTH // 4, 350))
    exit_text_rect = exit_text.get_rect(center=(gv.SCREEN_WIDTH // 4, 450))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return GameScreens.EXIT

            if event.type == pygame.MOUSEBUTTONDOWN:
                if starten_text_rect.collidepoint(event.pos):
                    return GameScreens.SAVE_SLOTS
                if controls_text_rect.collidepoint(event.pos):
                    return GameScreens.CONTROLS
                if exit_text_rect.collidepoint(event.pos):
                    return GameScreens.EXIT

        # Zeichnen
        screen.blit(Hintergrund, Hintergrund_rect)
        screen.blit(Logo, title_text_rect)
        screen.blit(starten_text, starten_text_rect)
        screen.blit(controls_text, controls_text_rect)
        screen.blit(exit_text, exit_text_rect)

        pygame.display.flip()
        clock.tick(gv.FPS)


def main():
    """Der zentrale Programmeinstieg. Verwaltet die Navigation zwischen den Screens."""
    gv.init()
    screen = pygame.display.set_mode((gv.SCREEN_WIDTH, gv.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Diese Endlosschleife schaltet je nach Zustand den passenden Bildschirm aktiv
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