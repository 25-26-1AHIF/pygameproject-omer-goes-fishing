import pygame
from game_variables.game_variables import GameVariables as gv
from game_variables.game_variables import GameScreens
from inventar import Inventory
from angelsystem import FishingSystem
from save_manager import load_save, delete_save, save_game


def save_slots_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_5/5.png")
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    pygame.display.set_caption("Save Slots Screen")

    back_text = gv.FONT_BIG.render("X", True, "white")
    back_rect = back_text.get_rect(center=(gv.SCREEN_WIDTH // 5, 100))

    # Listen für die Buttons erstellen
    slot_texts = []
    slot_rects = []
    delete_texts = []
    delete_rects = []

    # Die drei Speicher-Slots laden
    for i in range(1, 4):
        y_pos = 100 + i * 100
        save_data = load_save(i)

        if save_data:
            label = f"Slot {i} | Geld: {save_data.get('money', '')}€ | {save_data.get('timestamp', '')}"
        else:
            label = f"Slot {i} - Neu starten"

        t = gv.FONT_MIDDLE.render(label, True, "white")
        r = t.get_rect(center=(gv.SCREEN_WIDTH // 2 - 100, y_pos))
        slot_texts.append(t)
        slot_rects.append(r)

        dt = gv.FONT_MIDDLE.render("Löschen", True, (255, 50, 50))
        dr = dt.get_rect(center=(gv.SCREEN_WIDTH // 2 + 250, y_pos))
        delete_texts.append(dt)
        delete_rects.append(dr)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.MAIN

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Klick auf einen Slot überprüfen
                for i in range(len(slot_rects)):
                    rect = slot_rects[i]
                    if rect.collidepoint(event.pos):
                        slot_num = i + 1
                        if load_save(slot_num) is None:
                            save_game(slot_num, {"money": 0, "player_name": "Fischer"})
                        gv.current_slot = slot_num
                        return GameScreens.PLAY

                # Klick auf Löschen-Button überprüfen
                for i in range(len(delete_rects)):
                    rect = delete_rects[i]
                    if rect.collidepoint(event.pos):
                        slot_num = i + 1
                        delete_save(slot_num)

                        # Listen leeren und neu aufbauen
                        slot_texts = []
                        slot_rects = []
                        delete_texts = []
                        delete_rects = []
                        for j in range(1, 4):
                            y_pos = 100 + j * 100
                            save_data = load_save(j)
                            if save_data:
                                label = f"Slot {j} | Geld: {save_data.get('money', '')}€ | {save_data.get('timestamp', '')}"
                            else:
                                label = f"Slot {j} - Neu starten"

                            t = gv.FONT_MIDDLE.render(label, True, "white")
                            r = t.get_rect(center=(gv.SCREEN_WIDTH // 2 - 100, y_pos))
                            slot_texts.append(t)
                            slot_rects.append(r)

                            dt = gv.FONT_MIDDLE.render("Löschen", True, (255, 50, 50))
                            dr = dt.get_rect(center=(gv.SCREEN_WIDTH // 2 + 250, y_pos))
                            delete_texts.append(dt)
                            delete_rects.append(dr)

                if back_rect.collidepoint(event.pos):
                    return GameScreens.MAIN

        screen.blit(Hintergrund, Hintergrund_rect)

        for i in range(3):
            screen.blit(slot_texts[i], slot_rects[i])
            screen.blit(delete_texts[i], delete_rects[i])
        screen.blit(back_text, back_rect)

        pygame.display.flip()
        clock.tick(gv.FPS)


def play_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    pygame.display.set_caption("Play Screen")

    inventory = Inventory()
    fishing_system = FishingSystem(inventory)

    # Hintergrundbild laden und anpassen
    # Größe des Hintergrunds ermitteln
    Fishing_hut_raw = pygame.image.load("./assets/Haupt_Fisch_Sachen/3 Objects/Fishing_hut.png").convert()
    Hintergrund_raw = pygame.image.load("./assets/Hintergründe/Ocean_1/4.png").convert()
    bg_w, bg_h = Hintergrund_raw.get_size()
    scale_factor_bg = max(gv.SCREEN_WIDTH / bg_w, gv.SCREEN_HEIGHT / bg_h)
    new_bg_w = int(bg_w * scale_factor_bg)
    new_bg_h = int(bg_h * scale_factor_bg)
    Hintergrund = pygame.transform.scale(Hintergrund_raw, (new_bg_w, new_bg_h))
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))

    TARGET_BLOCK_SIZE = 96
    bloecke_hoch = 1
    sand_bloecke_breite = 3

    wasser_tile_raw = pygame.image.load("./assets/Haupt_Fisch_Sachen/3 Objects/Water.png").convert_alpha()
    water_tile_w = wasser_tile_raw.get_width()
    water_tile_h = wasser_tile_raw.get_height()
    wasser_scaled_h = TARGET_BLOCK_SIZE
    wasser_scaled_w = int(water_tile_w * (wasser_scaled_h / water_tile_h))
    wasser_tile = pygame.transform.scale(wasser_tile_raw, (wasser_scaled_w, wasser_scaled_h))

    sand_tile_raw = pygame.image.load("./assets/Sand/new_piskel_5.png").convert()
    sand_tile = pygame.transform.scale(sand_tile_raw, (TARGET_BLOCK_SIZE, TARGET_BLOCK_SIZE))

    bereich_height = bloecke_hoch * TARGET_BLOCK_SIZE
    y_position_am_boden = gv.SCREEN_HEIGHT - bereich_height
    sand_width = sand_bloecke_breite * TARGET_BLOCK_SIZE
    water_width = gv.SCREEN_WIDTH - sand_width

    sand_surface = pygame.Surface((sand_width, bereich_height), pygame.SRCALPHA)
    for y in range(0, bereich_height, TARGET_BLOCK_SIZE):
        for x in range(0, sand_width, TARGET_BLOCK_SIZE):
            sand_surface.blit(sand_tile, (x, y))

    water_surface = pygame.Surface((water_width, bereich_height + 2), pygame.SRCALPHA)
    for y in range(0, bereich_height, wasser_scaled_h):
        for x in range(0, water_width + wasser_scaled_w, wasser_scaled_w):
            water_surface.blit(wasser_tile, (x, y))

    SCALE_FACTOR = 2.5
    boot_raw = pygame.image.load("./assets/Haupt_Fisch_Sachen/3 Objects/Boat.png").convert_alpha()
    boot_w = int(boot_raw.get_width() * SCALE_FACTOR)
    boot_h = int(boot_raw.get_height() * SCALE_FACTOR)
    boot_img = pygame.transform.scale(boot_raw, (boot_w, boot_h))

    fischer_sheet = pygame.image.load("./assets/Haupt_Fisch_Sachen/1 Fisherman/Fisherman_walk.png").convert_alpha()
    fischer_ganz_raw = fischer_sheet.subsurface(pygame.Rect(0, 0, 48, 48))
    fischer_w = int(fischer_ganz_raw.get_width() * SCALE_FACTOR)
    fischer_h = int(fischer_ganz_raw.get_height() * SCALE_FACTOR)
    fischer_img = pygame.transform.scale(fischer_ganz_raw, (fischer_w, fischer_h))

    player_x_offset = int(18 * SCALE_FACTOR)
    player_y_offset = int(-25 * SCALE_FACTOR)

    # Animation Setup für Row-Animation
    fischer_row_sheet = pygame.image.load("./assets/Haupt_Fisch_Sachen/1 Fisherman/Fisherman_row.png").convert_alpha()
    fischer_frames = []
    frame_width = 48
    frame_height = 48
    for i in range(4):  # 4 Frames
        frame = fischer_row_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        frame_scaled = pygame.transform.scale(frame, (fischer_w, fischer_h))
        fischer_frames.append(frame_scaled)

    current_frame = 0
    animation_counter = 0

    boat_y = y_position_am_boden - int(12 * SCALE_FACTOR) - 1
    player_x = sand_width + 20
    player_speed = 5
    max_x = gv.SCREEN_WIDTH - boot_img.get_width()
    player_direction = 1  # 1 = rechts, -1 = links


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.MAIN

            fishing_system.handle_event(event)

        keys = pygame.key.get_pressed()

        # Geschwindigkeit erhöhen, wenn Shift gedrückt ist
        # Normale Geschwindigkeit, wenn Shift nicht gedrückt ist
        if keys[pygame.K_LSHIFT]:
            player_speed = 9
        else:
            player_speed = 5

        if fishing_system.state != "MINIGAME":
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_x -= player_speed
                player_direction = -1  # Nach links schauen
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_x += player_speed
                player_direction = 1  # Nach rechts schauen

        if player_x < sand_width - 8:
            player_x = sand_width - 8
        if player_x > max_x:
            player_x = max_x

        if player_x <= sand_width and keys[pygame.K_e]:
            inventory.sell_all_fish()

        # Animation Update
        if fishing_system.state != "MINIGAME":
            if keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                animation_counter += 1
                if animation_counter >= 9: # Schnelligkeit
                    current_frame = (current_frame + 1) % len(fischer_frames)
                    animation_counter = 0
            else:
                current_frame = 0  # Idle frame

        fishing_system.update()

        screen.fill((0, 0, 0))
        screen.blit(Hintergrund, Hintergrund_rect)

        # Fishing Hut im Hintergrund zeichnen (HINTER Sand und Wasser)
        fishing_hut_scaled = pygame.transform.scale(Fishing_hut_raw, (int(Fishing_hut_raw.get_width() * 2), int(Fishing_hut_raw.get_height() * 2)))
        screen.blit(fishing_hut_scaled, (sand_width - 246, y_position_am_boden + TARGET_BLOCK_SIZE - fishing_hut_scaled.get_height() - 20))

        screen.blit(sand_surface, (0, y_position_am_boden))
        screen.blit(water_surface, (sand_width, y_position_am_boden - 1))

        # Gelbe Interaktionslinie beim Boot-Spawn (dünne Linie, 70% transparent)
        interaction_line = pygame.Surface((140, 10), pygame.SRCALPHA)
        pygame.draw.rect(interaction_line, (255, 255, 0, 76), interaction_line.get_rect(), 0)
        screen.blit(interaction_line, (sand_width, y_position_am_boden))

        # Fischer und Boot VOR dem Fishing Hut zeichnen
        pygame.draw.rect(screen, (255, 255, 100), (0, y_position_am_boden, sand_width, bereich_height), 3)

        screen.blit(boot_img, (player_x, boat_y))

        # Fischer mit Flip je nach Richtung zeichnen
        fischer_display = pygame.transform.flip(fischer_frames[current_frame], player_direction == -1, False)
        # Offset anpassen je nach Richtung - weniger heftig nach rechts
        offset_x = int(player_x_offset * 0.1) if player_direction == -1 else player_x_offset
        screen.blit(fischer_display, (player_x + offset_x, boat_y + player_y_offset))

        fishing_system.draw(screen)

        # Aktuellen Speicherstand auslesen
        slot = gv.current_slot
        save_data = load_save(slot)
        if save_data is None:
            save_data = {"money": 0}

        money_txt = gv.FONT_MIDDLE.render(f"Geld: {save_data.get('money', 0)}€ / 50.000,--€", True, "white")
        screen.blit(money_txt, (20, 20))

        if save_data["money"] >= 50000:
            end_txt = gv.FONT_BIG.render("Glückwunsch! Du hast 50.000€ erreicht!", True, "green")
            end_rect = end_txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
            screen.blit(end_txt, end_rect)

        inv_list = [f"{count}x {fish}" for fish, count in inventory.content.items()]
        inv_string = ", ".join(inv_list) if inv_list else "Leer"
        inv_txt = gv.FONT_SMALL.render(f"Inventar: {inv_string}", True, (200, 200, 200))
        screen.blit(inv_txt, (20, 55))

        if player_x <= sand_width:
            shop_txt = gv.FONT_SMALL.render("Drücke 'E' zum Fische verkaufen", True, (255, 255, 100))
            draw_rect = shop_txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 12))
            screen.blit(shop_txt, draw_rect)

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
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.MAIN
            if event.type == pygame.MOUSEBUTTONDOWN:
                if x_rect.collidepoint(event.pos):
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
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return GameScreens.EXIT
            if event.type == pygame.MOUSEBUTTONDOWN:
                if starten_text_rect.collidepoint(event.pos):
                    return GameScreens.SAVE_SLOTS
                if controls_text_rect.collidepoint(event.pos):
                    return GameScreens.CONTROLS
                if exit_text_rect.collidepoint(event.pos):
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

    # Hauptschleife für den Wechsel der Bildschirme
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