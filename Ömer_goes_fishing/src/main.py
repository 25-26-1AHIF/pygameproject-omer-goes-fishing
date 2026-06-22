import pygame
from game_variables.game_variables import GameVariables as gv
from game_variables.game_variables import GameScreens
from inventar import Inventory
from angelsystem import FishingSystem
from upgrades import UpgradeManager, UPGRADE_DEFS, MAX_LEVEL
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

    upgrade_manager = UpgradeManager()
    inventory = Inventory(upgrade_manager)
    fishing_system = FishingSystem(inventory)

    # Status für das Upgrade-Menü (öffnet sich nur am Sand mit Taste 'U')
    upgrade_menu_open = False
    upgrade_keys = list(UPGRADE_DEFS.keys())  # feste Reihenfolge: inventar, minigame, preis

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


    player_x_offset = int(18 * SCALE_FACTOR)
    player_y_offset = int(-25 * SCALE_FACTOR)

    # --- ANIMATION SETUP ---
    frame_width, frame_height = 48, 48

    # 1. Row/Walk Animation (Fahren)
    fischer_row_sheet = pygame.image.load("./assets/Haupt_Fisch_Sachen/1 Fisherman/Fisherman_row.png").convert_alpha()
    fischer_row_frames = []
    for i in range(4):
        frame = fischer_row_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        fischer_row_frames.append(pygame.transform.scale(frame, (int(frame_width * SCALE_FACTOR), int(frame_height * SCALE_FACTOR))))

    # 2. Idle Animation (Stehen ohne Angeln)
    fischer_idle_sheet = pygame.image.load("./assets/Haupt_Fisch_Sachen/1 Fisherman/Fisherman_idle.png").convert_alpha()
    fischer_idle_frames = []
    for i in range(4):
        frame = fischer_idle_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        fischer_idle_frames.append(pygame.transform.scale(frame, (int(frame_width * SCALE_FACTOR), int(frame_height * SCALE_FACTOR))))

    # 3. Fish Animation (Köder im Wasser / Minigame läuft)
    fischer_fish_sheet = pygame.image.load("./assets/Haupt_Fisch_Sachen/1 Fisherman/Fisherman_fish.png").convert_alpha()
    fischer_fish_frames = []
    for i in range(4):
        frame = fischer_fish_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        fischer_fish_frames.append(pygame.transform.scale(frame, (int(frame_width * SCALE_FACTOR), int(frame_height * SCALE_FACTOR))))

    # 4. Hook Animation (Ergebnis / Einholen)
    fischer_hook_sheet = pygame.image.load("./assets/Haupt_Fisch_Sachen/1 Fisherman/Fisherman_hook.png").convert_alpha()
    fischer_hook_frames = []
    for i in range(6):
        frame = fischer_hook_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        fischer_hook_frames.append(pygame.transform.scale(frame, (int(frame_width * SCALE_FACTOR), int(frame_height * SCALE_FACTOR))))

    current_frame = 0
    animation_counter = 0
    last_state = "IDLE"  # Hilfsvariable, um Zustandswechsel zu tracken

    boat_y = y_position_am_boden - int(12 * SCALE_FACTOR) - 1
    player_x = sand_width + 20
    player_speed = 5
    max_x = gv.SCREEN_WIDTH - boot_img.get_width()
    player_direction = 1  # 1 = rechts, -1 = links

    while True:
        # Bei einem neuen Statuswechsel setzen wir den Frame-Zähler zurück
        if fishing_system.state != last_state:
            current_frame = 0
            animation_counter = 0
            last_state = fishing_system.state

        # 1. Alle Events abarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameScreens.EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if upgrade_menu_open:
                        upgrade_menu_open = False
                    else:
                        return GameScreens.SAVE_SLOTS

                if event.key == pygame.K_u and player_x <= sand_width:
                    # Menü nur am Sand (Shop-Bereich) öffnen/schließen
                    upgrade_menu_open = not upgrade_menu_open

            if event.type == pygame.MOUSEBUTTONDOWN and upgrade_menu_open:
                # Klick auf eine der Upgrade-Zeilen prüfen
                mouse_x, mouse_y = event.pos
                for idx, key in enumerate(upgrade_keys):
                    row_y = 220 + idx * 70
                    row_rect = pygame.Rect(gv.SCREEN_WIDTH // 2 - 250, row_y - 25, 500, 50)
                    if row_rect.collidepoint(mouse_x, mouse_y):
                        save_data_for_buy = load_save(gv.current_slot) or {"money": 0}
                        aktuelles_geld = save_data_for_buy.get("money", 0)
                        # purchase() speichert Geld + Upgrade-Level selbst in einem Zug
                        upgrade_manager.purchase(key, aktuelles_geld)

            current_keys = pygame.key.get_pressed()
            is_moving_now = (current_keys[pygame.K_a] or current_keys[pygame.K_LEFT] or
                             current_keys[pygame.K_d] or current_keys[pygame.K_RIGHT])

            # Während das Upgrade-Menü offen ist, soll nicht gleichzeitig
            # geangelt werden können (sonst überschneiden sich die UIs)
            if not upgrade_menu_open:
                fishing_system.handle_event(event, is_moving_now)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LSHIFT]:
            player_speed = 9
        else:
            player_speed = 5

        moved_this_frame = False

        # Bewegung nur erlauben, wenn die Angel NICHT im Wasser ist UND das Menü zu ist
        if fishing_system.state == "IDLE" and not upgrade_menu_open:
            # 1. Prüfen, ob beide Tasten gleichzeitig gedrückt werden
            if not ((keys[pygame.K_a] or keys[pygame.K_LEFT]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT])):

                # 2. Nur nach links bewegen & animieren, wenn wir NICHT am Sand-Rand stehen
                if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_x > sand_width - 8:
                    player_x -= player_speed
                    player_direction = -1
                    moved_this_frame = True

                # 3. Nur nach rechts bewegen & animieren, wenn wir NICHT am Bildschirm-Rand stehen
                if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_x < max_x:
                    player_x += player_speed
                    player_direction = 1
                    moved_this_frame = True

        # Grenzen einhalten
        if player_x < sand_width - 8:
            player_x = sand_width - 8
        if player_x > max_x:
            player_x = max_x

        if player_x <= sand_width and keys[pygame.K_e] and not upgrade_menu_open:
            inventory.sell_all_fish()

        # --- DYNAMISCHES ANIMATION UPDATE ---
        animation_counter += 1

        both_keys_pressed = (keys[pygame.K_a] or keys[pygame.K_LEFT]) and (keys[pygame.K_d] or keys[pygame.K_RIGHT])

        if fishing_system.state == "IDLE":
            if moved_this_frame:
                if animation_counter >= 9:
                    current_frame = (current_frame + 1) % len(fischer_row_frames)
                    animation_counter = 0
                active_frames = fischer_row_frames
            else:
                if animation_counter >= 12:
                    current_frame = (current_frame + 1) % len(fischer_idle_frames)
                    animation_counter = 0
                active_frames = fischer_idle_frames

        elif fishing_system.state in ("WAITING", "BITE", "MINIGAME"):
            if animation_counter >= 12:
                current_frame = (current_frame + 1) % len(fischer_fish_frames)
                animation_counter = 0
            active_frames = fischer_fish_frames

        elif fishing_system.state == "RESULT":
            if current_frame < len(fischer_hook_frames) - 1:
                if animation_counter >= 8:  # Geschwindigkeit der Bewegung
                    current_frame += 1
                    animation_counter = 0
            active_frames = fischer_hook_frames

        if current_frame >= len(active_frames):
            current_frame = 0

        fishing_system.update()

        screen.fill((0, 0, 0))
        screen.blit(Hintergrund, Hintergrund_rect)

        fishing_hut_scaled = pygame.transform.scale(Fishing_hut_raw, (int(Fishing_hut_raw.get_width() * 2), int(Fishing_hut_raw.get_height() * 2)))
        screen.blit(fishing_hut_scaled, (sand_width - 246, y_position_am_boden + TARGET_BLOCK_SIZE - fishing_hut_scaled.get_height() - 20))

        screen.blit(sand_surface, (0, y_position_am_boden))
        screen.blit(water_surface, (sand_width, y_position_am_boden - 1))

        interaction_line = pygame.Surface((140, 10), pygame.SRCALPHA)
        pygame.draw.rect(interaction_line, (255, 255, 0, 76), interaction_line.get_rect(), 0)
        screen.blit(interaction_line, (sand_width, y_position_am_boden))

        pygame.draw.rect(screen, (255, 255, 100), (0, y_position_am_boden, sand_width, bereich_height), 3)

        # Boot zeichnen
        screen.blit(boot_img, (player_x, boat_y))

        # Fischer rendern
        fischer_display = pygame.transform.flip(active_frames[current_frame], player_direction == -1, False)
        offset_x = int(player_x_offset * 0.1) if player_direction == -1 else player_x_offset
        screen.blit(fischer_display, (player_x + offset_x, boat_y + player_y_offset))

        fishing_system.draw(screen)

        # UI & Texte rendern
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

        # Inventar-Anzeige inkl. Füllstand (z.B. "7/10"), damit man sieht,
        # wie viel Platz noch frei ist, bevor man verkaufen muss.
        gesamt_fische = inventory.total_fish_count()
        max_fische = inventory.MAX_TOTAL_FISH
        inv_list = [f"{count}x {fish}" for fish, count in inventory.content.items()]
        inv_string = ", ".join(inv_list) if inv_list else "Leer"

        # Wenn das Inventar voll ist, Anzeige rot einfärben als zusätzlicher Hinweis
        inv_farbe = (255, 100, 100) if gesamt_fische >= max_fische else (200, 200, 200)
        inv_txt = gv.FONT_SMALL.render(
            f"Inventar ({gesamt_fische}/{max_fische}): {inv_string}", True, inv_farbe
        )
        screen.blit(inv_txt, (20, 55))

        if player_x <= sand_width:
            shop_txt = gv.FONT_SMALL.render("Drücke 'E' zum Verkaufen | 'U' für Upgrades", True, (255, 255, 100))
            draw_rect = shop_txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 16))
            screen.blit(shop_txt, draw_rect)

        # --- UPGRADE-MENÜ ---
        if upgrade_menu_open:
            menu_width, menu_height = 560, 340
            menu_x = gv.SCREEN_WIDTH // 2 - menu_width // 2
            menu_y = 140

            menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            pygame.draw.rect(menu_bg, (20, 20, 30, 230), menu_bg.get_rect(), border_radius=10)
            pygame.draw.rect(menu_bg, (255, 255, 255, 255), menu_bg.get_rect(), 2, border_radius=10)
            screen.blit(menu_bg, (menu_x, menu_y))

            titel_txt = gv.FONT_MIDDLE.render("Upgrades (ESC zum Schließen)", True, "white")
            screen.blit(titel_txt, (menu_x + 20, menu_y + 15))

            save_data_now = load_save(gv.current_slot) or {"money": 0}
            aktuelles_geld = save_data_now.get("money", 0)

            for idx, key in enumerate(upgrade_keys):
                info = UPGRADE_DEFS[key]
                level = upgrade_manager.get_level(key)
                row_y = 220 + idx * 70

                if level >= MAX_LEVEL:
                    preis_text = "MAX"
                    kann_kaufen = False
                else:
                    kosten = upgrade_manager.get_cost(key)
                    preis_text = f"{kosten}€"
                    kann_kaufen = aktuelles_geld >= kosten

                zeilen_farbe = (60, 200, 80) if kann_kaufen else (160, 60, 60)
                row_rect = pygame.Rect(gv.SCREEN_WIDTH // 2 - 250, row_y - 25, 500, 50)
                pygame.draw.rect(screen, zeilen_farbe, row_rect, 2, border_radius=6)

                name_txt = gv.FONT_SMALL.render(f"{info['name']} (Lvl {level})", True, "white")
                screen.blit(name_txt, (row_rect.x + 12, row_rect.y + 6))

                beschr_txt = gv.FONT_SMALL.render(info["beschreibung"], True, (200, 200, 200))
                screen.blit(beschr_txt, (row_rect.x + 12, row_rect.y + 26))

                preis_txt = gv.FONT_MIDDLE.render(preis_text, True, zeilen_farbe)
                preis_rect = preis_txt.get_rect(midright=(row_rect.right - 15, row_rect.centery))
                screen.blit(preis_txt, preis_rect)

        pygame.display.flip()
        clock.tick(gv.FPS)


def controls_screen(screen: pygame.Surface, clock: pygame.time.Clock):
    pygame.display.set_caption("Controls Screen")

    Hintergrund = pygame.image.load("./assets/Hintergründe/Ocean_4/5.png")
    Boot_ctrls = gv.FONT_MIDDLE.render("A/D  für links und rechts bewegen vom Boot", True, "white")
    Köder_ctrls = gv.FONT_MIDDLE.render("SPACE für Köder werfen", True, "white")
    minigame_ctrls = gv.FONT_MIDDLE.render("Beim Angel Minigame SPACE gedrückt halten zum Verfolgen vom Fisch", True,
                                           "white")
    Verkaufen_ctrl = gv.FONT_MIDDLE.render("E zum Verkaufen (nur am Sand möglich)", True, "white")
    Upgrades_menu_ctrl = gv.FONT_MIDDLE.render("U für Upgrade Menü (nur am Sand möglich)", True, "white")
    interaction_ctrl = gv.FONT_MIDDLE.render("Links zum interagieren", True, "white")
    back_ctrl = gv.FONT_MIDDLE.render("ESC für Pausenmenü / Exit", True, "white")
    x = gv.FONT_BIG.render("X", True, "white")

    interaction_rect = interaction_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 150))
    Hintergrund_rect = Hintergrund.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 2))
    Upgrades_menu_rect = Upgrades_menu_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 400))
    Boot_ctrls_rect = Boot_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 200))
    Köder_ctrls_rect = Köder_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 250))
    minigame_ctrls_rect = minigame_ctrls.get_rect(center=(gv.SCREEN_WIDTH // 2, 300))
    interact_ctrl_rect = Verkaufen_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 350))
    back_ctrl_rect = back_ctrl.get_rect(center=(gv.SCREEN_WIDTH // 2, 450))
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
        screen.blit(interaction_ctrl, interaction_rect)
        screen.blit(Boot_ctrls, Boot_ctrls_rect)
        screen.blit(Köder_ctrls, Köder_ctrls_rect)
        screen.blit(minigame_ctrls, minigame_ctrls_rect)
        screen.blit(Verkaufen_ctrl, interact_ctrl_rect)
        screen.blit(back_ctrl, back_ctrl_rect)
        screen.blit(Upgrades_menu_ctrl, Upgrades_menu_rect)
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