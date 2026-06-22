import pygame
import random
from game_variables.game_variables import GameVariables as gv
from inventar import FISH_TYPES, RARITY_INFO

# KI-Anfang
# KI: Claude
# prompt: Wie gewichte ich eine Zufallsauswahl in Python nach
#         mehreren Faktoren (Rarity-Gewicht * Upgrade-Multiplikator)?
def pick_random_fish(upgrade_manager):
    """
    @brief Wählt einen Fisch gewichtet nach Rarity UND Köder-Upgrade aus.

    Statt einer gleichverteilten Auswahl (random.choice) wird hier
    random.choices() mit individuellen Gewichten pro Fisch verwendet.
    Jeder Fisch erbt zunächst das Basis-"weight" seiner Rarity aus
    RARITY_INFO. Dieses Basisgewicht wird zusätzlich mit dem
    Köder-Upgrade-Multiplikator der jeweiligen Rarity verrechnet
    (siehe upgrades.py -> get_rarity_weight_multiplier()), sodass
    seltenere Fische mit steigendem Köder-Level häufiger gezogen werden.

    @param upgrade_manager Instanz von UpgradeManager, liefert den
                            aktuellen Köder-Level und die Multiplikatoren.
    @return Name eines zufällig gezogenen Fisches (str), passend
            gewichtet nach Rarity und Upgrade-Stand.
    """
    namen = list(FISH_TYPES.keys())
    gewichte = []
    for name in namen:
        rarity = FISH_TYPES[name]["rarity"]
        basis_gewicht = RARITY_INFO[rarity]["weight"]
        koeder_multiplikator = upgrade_manager.get_rarity_weight_multiplier(rarity)
        gewichte.append(basis_gewicht * koeder_multiplikator)
    return random.choices(namen, weights=gewichte, k=1)[0]
# KI-Ende


class FishingSystem:
    """
    @brief Steuert den gesamten Angel-Ablauf (Werfen, Warten, Biss,
           Minigame, Ergebnis) sowie dessen Darstellung auf dem Bildschirm.
    """

    def __init__(self, inventory):
        """
        @brief Initialisiert das Angelsystem mit Standardwerten.
        @param inventory Inventory-Instanz, über die Fänge gespeichert
                          und Upgrade-Werte abgefragt werden.
        """
        self.inventory = inventory
        self.state = "IDLE"  # IDLE, WAITING, BITE, MINIGAME, RESULT
        self.timer = 0
        self.current_fish = None
        self.result_text = ""
        self.result_colour = "white"

        self.warning_timer = 0
        self.warning_text = ""

        # UI Layout (Rechte Bildschirmseite)
        self.ui_x = gv.SCREEN_WIDTH - 120
        self.ui_y = 150
        self.ui_width, self.ui_height = 35, 300

        # Spieler-Balken Physik
        self.bar_height = 75
        self.player_y = self.ui_height - self.bar_height
        self.player_vel = 0.0
        self.gravity, self.lift = 0.4, -1.0

        # Fisch-Variablen
        self.fish_y = self.ui_height - 20
        self.fish_target_y = self.fish_y
        self.fish_move_timer = 0
        self.progress = 30.0

    def handle_event(self, event, is_moving=False):
        """
        @brief Verarbeitet den Tastendruck für SPACE je nach aktuellem Status.
        @param event Pygame-Event aus der Event-Queue.
        @param is_moving True, falls sich das Boot aktuell bewegt
                          (verhindert das Werfen des Köders).
        """
        if event.type != pygame.KEYDOWN or event.key != pygame.K_SPACE:
            return

        if self.state == "IDLE":
            if is_moving:
                self.warning_timer = 60  # 1 Sekunde bei 60 FPS
                self.warning_text = "Du musst stehen bleiben zum Angeln!"
                return

            if self.inventory.total_fish_count() >= self.inventory.MAX_TOTAL_FISH:
                # Inventar ist voll -> gar nicht erst werfen, keine Zeit verschwenden
                self.warning_timer = 60
                self.warning_text = "Inventar voll! Erst verkaufen."
                return

            self.state = "WAITING"
            self.timer = random.randint(120, 300)  # 2 bis 5 Sekunden bei 60 FPS
            print("Köder geworfen... Warten auf Biss...")

        elif self.state == "WAITING":
            self._set_result("Eingeholt!", (255, 255, 255), 50)

        elif self.state == "BITE":
            self.state = "MINIGAME"
            # Gewichtete Auswahl inkl. Köder-Upgrade statt reinem Zufall
            self.current_fish = pick_random_fish(self.inventory.upgrade_manager)
            self.progress = 30.0
            # Balkenhöhe inkl. Bonus durch das 'Bessere Angel'-Upgrade
            bonus = self.inventory.upgrade_manager.get_minigame_bar_bonus()
            self.bar_height = 75 + bonus
            self.player_y = self.ui_height - self.bar_height
            self.player_vel = 0.0
            self.fish_y = self.fish_target_y = self.ui_height - 30
            print(f"Ein {self.current_fish} ({FISH_TYPES[self.current_fish]['rarity']}) hat angebissen! Minigame startet.")

    def _set_result(self, text, colour=(255, 255, 255), duration=120):
        """
        @brief Hilfsmethode zum Setzen des Status-Ergebnisses.
        @param text Anzuzeigender Ergebnistext.
        @param colour RGB-Farbtupel für den Text.
        @param duration Anzeigedauer in Frames.
        """
        self.state = "RESULT"
        self.result_text = text
        self.result_colour = colour
        self.timer = duration

    def update(self):
        """
        @brief Aktualisiert die Logik des Angelsystems um einen Frame.
               Wechselt je nach Timer/Status zwischen WAITING, BITE,
               MINIGAME und RESULT.
        """
        if self.warning_timer > 0:
            self.warning_timer -= 1

        self.timer -= 1

        if self.state == "WAITING" and self.timer <= 0:
            self.state = "BITE"
            self.timer = 75  # Spieler hat ca. 1.2 Sekunden Zeit

        elif self.state == "BITE" and self.timer <= 0:
            self._set_result("Entkommen!", (255, 50, 50), 90)

        elif self.state == "MINIGAME":
            self._update_minigame()

        elif self.state == "RESULT" and self.timer <= 0:
            self.state = "IDLE"

    def _update_minigame(self):
        """
        @brief Interne Logik für das eigentliche Fang-Minigame:
               Spieler-Balken-Physik, Fisch-Bewegung und Fortschrittsbalken.
        """
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.player_vel += self.lift

        self.player_vel += self.gravity
        self.player_y = max(0, min(self.player_y + self.player_vel, self.ui_height - self.bar_height))

        if self.player_y in (0, self.ui_height - self.bar_height):
            self.player_vel = 0

        self.fish_move_timer -= 1
        if self.fish_move_timer <= 0:
            self.fish_target_y = random.randint(10, self.ui_height - 15)
            self.fish_move_timer = random.randint(30, 60)

        reduktion = self.inventory.upgrade_manager.get_minigame_difficulty_reduction()
        diff = FISH_TYPES[self.current_fish]["difficulty"] * reduktion
        step = 1.8 * diff

        if abs(self.fish_y - self.fish_target_y) <= step:
            self.fish_y = self.fish_target_y
        else:
            self.fish_y += step if self.fish_y < self.fish_target_y else -step

        if self.player_y <= self.fish_y <= self.player_y + self.bar_height:
            self.progress = min(100.0, self.progress + 0.5)
        else:
            self.progress = max(0.0, self.progress - 0.4)

        if self.progress >= 100:
            erfolg = self.inventory.add_fish(self.current_fish)
            fisch_colour = FISH_TYPES[self.current_fish]["colour"]
            if erfolg:
                self._set_result(f"{self.current_fish} gefangen!", fisch_colour)
            else:
                # Gesamtes Inventar ist voll (globales Limit erreicht)
                self._set_result("Inventar voll! Erst verkaufen.", (255, 150, 0))
        elif self.progress <= 0:
            self._set_result("Entkommen!", (255, 50, 50))

    def draw(self, screen):
        """
        @brief Zeichnet alle grafischen Elemente des Angelsystems
               (Warnungen, Status-Texte, Minigame-UI) auf den Bildschirm.
        @param screen Pygame-Surface, auf die gezeichnet wird.
        """

        if self.warning_timer > 0:
            warn_txt = gv.FONT_BIG.render(self.warning_text, True, (255, 75, 75))
            warn_rect = warn_txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 3))
            screen.blit(warn_txt, warn_rect)

        if self.state == "WAITING":
            txt = gv.FONT_MIDDLE.render("Köder im Wasser... Warten...", True, "white")
            draw_rect = txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 7))
            screen.blit(txt, draw_rect)
        elif self.state == "BITE":
            txt = gv.FONT_BIG.render("!! BISS !! DRÜCKE SPACE!", True, (255, 50, 50))
            draw_rect = txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 7))
            screen.blit(txt, draw_rect)
        elif self.state == "RESULT":
            txt = gv.FONT_BIG.render(self.result_text, True, self.result_colour)
            draw_rect = txt.get_rect(center=(gv.SCREEN_WIDTH // 2, gv.SCREEN_HEIGHT // 7))
            screen.blit(txt, draw_rect)

        elif self.state == "MINIGAME":
            pygame.draw.rect(screen, (40, 40, 40), (self.ui_x, self.ui_y, self.ui_width, self.ui_height))
            pygame.draw.rect(screen, "white", (self.ui_x, self.ui_y, self.ui_width, self.ui_height), 2)

            pygame.draw.rect(screen, (50, 220, 50),
                             (self.ui_x + 3, self.ui_y + int(self.player_y), self.ui_width - 6, self.bar_height))

            pygame.draw.circle(screen, (255, 120, 0), (self.ui_x + self.ui_width // 2, self.ui_y + int(self.fish_y)), 8)

            prog_height = int((self.progress / 100.0) * self.ui_height)
            px = self.ui_x + self.ui_width + 8
            pygame.draw.rect(screen, (20, 20, 20), (px, self.ui_y, 12, self.ui_height))
            pygame.draw.rect(screen, (255, 180, 0), (px, self.ui_y + self.ui_height - prog_height, 12, prog_height))
            pygame.draw.rect(screen, "white", (px, self.ui_y, 12, self.ui_height), 1)

            fisch_daten = FISH_TYPES[self.current_fish]
            lbl = gv.FONT_MIDDLE.render(f"Fisch: {self.current_fish}", True, fisch_daten["colour"])
            screen.blit(lbl, (self.ui_x - 120, self.ui_y - 45))

            rarity_lbl = gv.FONT_SMALL.render(f"[{fisch_daten['rarity'].upper()}]", True, fisch_daten["colour"])
            screen.blit(rarity_lbl, (self.ui_x - 115, self.ui_y - 20))