import pygame
import random
from game_variables.game_variables import GameVariables as gv
from inventar import FISH_TYPES


class FishingSystem:
    def __init__(self, inventory):
        self.inventory = inventory
        self.state = "IDLE"  # IDLE, WAITING, BITE, MINIGAME, RESULT
        self.timer = 0
        self.current_fish = None
        self.result_text = ""

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

    def handle_event(self, event):
        """Verarbeitet den Tastendruck für SPACE."""
        if event.type != pygame.KEYDOWN or event.key != pygame.K_SPACE:
            return

        if self.state == "IDLE":
            self.state = "WAITING"
            self.timer = random.randint(120, 300)  # 2 bis 5 Sekunden bei 60 FPS
            print("Köder geworfen... Warten auf Biss...")

        elif self.state == "BITE":
            self.state = "MINIGAME"
            self.current_fish = random.choice(list(FISH_TYPES.keys()))
            self.progress = 30.0
            self.player_y = self.ui_height - self.bar_height
            self.player_vel = 0.0
            self.fish_y = self.fish_target_y = self.ui_height - 30
            print(f"Ein {self.current_fish} hat angebissen! Minigame startet.")

    def _set_result(self, text, duration=120):
        """Hilfsmethode zum Setzen des Status-Ergebnisses."""
        self.state = "RESULT"
        self.result_text = text
        self.timer = duration

    def update(self):
        """Aktualisiert die Logik des Angelsystems pro Frame."""
        self.timer -= 1

        if self.state == "WAITING" and self.timer <= 0:
            self.state = "BITE"
            self.timer = 75  # Spieler hat ca. 1.2 Sekunden Zeit

        elif self.state == "BITE" and self.timer <= 0:
            self._set_result("Entkommen!", 90)

        elif self.state == "MINIGAME":
            self._update_minigame()

        elif self.state == "RESULT" and self.timer <= 0:
            self.state = "IDLE"

    def _update_minigame(self):
        """Interne Logik für das eigentliche Minigame."""
        # 1. Spieler-Balken Physik
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.player_vel += self.lift

        self.player_vel += self.gravity
        self.player_y = max(0, min(self.player_y + self.player_vel, self.ui_height - self.bar_height))

        if self.player_y in (0, self.ui_height - self.bar_height):
            self.player_vel = 0  # Am Rand abbremsen

        # 2. KI-Fisch-Bewegung
        self.fish_move_timer -= 1
        if self.fish_move_timer <= 0:
            self.fish_target_y = random.randint(10, self.ui_height - 15)
            self.fish_move_timer = random.randint(30, 60)

        diff = FISH_TYPES[self.current_fish]["difficulty"]
        step = 1.8 * diff

        # Sanftes Heranbewegen an das Ziel ohne Übersteuern
        if abs(self.fish_y - self.fish_target_y) <= step:
            self.fish_y = self.fish_target_y
        else:
            self.fish_y += step if self.fish_y < self.fish_target_y else -step

        # 3. Fortschrittsbalken updaten
        if self.player_y <= self.fish_y <= self.player_y + self.bar_height:
            self.progress = min(100.0, self.progress + 0.5)
        else:
            self.progress = max(0.0, self.progress - 0.4)

        # Gewinn- / Verlust-Abfrage
        if self.progress >= 100:
            self.inventory.add_fish(self.current_fish)
            self._set_result(f"{self.current_fish} gefangen!")
        elif self.progress <= 0:
            self._set_result("Entkommen!")

    def draw(self, screen):
        """Zeigt die grafischen Elemente des Angelsystems auf dem Bildschirm."""
        # Text-Overlays zeichnen
        if self.state == "WAITING":
            txt = gv.FONT_MIDDLE.render("Köder im Wasser... Warten...", True, "white")
            screen.blit(txt, (gv.SCREEN_WIDTH // 2 - 140, 60))
        elif self.state == "BITE":
            txt = gv.FONT_BIG.render("!! BISS !! DRÜCKE SPACE!", True, (255, 50, 50))
            screen.blit(txt, (gv.SCREEN_WIDTH // 2 - 180, 50))
        elif self.state == "RESULT":
            color = (50, 255, 50) if "gefangen" in self.result_text else (255, 50, 50)
            txt = gv.FONT_BIG.render(self.result_text, True, color)
            screen.blit(txt, (gv.SCREEN_WIDTH // 2 - 120, 50))

        elif self.state == "MINIGAME":
            # 1. Hintergrund-Messbalken
            pygame.draw.rect(screen, (40, 40, 40), (self.ui_x, self.ui_y, self.ui_width, self.ui_height))
            pygame.draw.rect(screen, "white", (self.ui_x, self.ui_y, self.ui_width, self.ui_height), 2)

            # 2. Grüner Spieler-Balken
            pygame.draw.rect(screen, (50, 220, 50),
                             (self.ui_x + 3, self.ui_y + int(self.player_y), self.ui_width - 6, self.bar_height))

            # 3. Der Fisch (Oranger Kreis)
            pygame.draw.circle(screen, (255, 120, 0), (self.ui_x + self.ui_width // 2, self.ui_y + int(self.fish_y)), 8)

            # 4. Der Fortschrittsbalken direkt rechts daneben
            prog_height = int((self.progress / 100.0) * self.ui_height)
            px = self.ui_x + self.ui_width + 8
            pygame.draw.rect(screen, (20, 20, 20), (px, self.ui_y, 12, self.ui_height))
            pygame.draw.rect(screen, (255, 180, 0), (px, self.ui_y + self.ui_height - prog_height, 12, prog_height))
            pygame.draw.rect(screen, "white", (px, self.ui_y, 12, self.ui_height), 1)

            # Info-Text
            lbl = gv.FONT_MIDDLE.render(f"Fisch: {self.current_fish}", True, "white")
            screen.blit(lbl, (self.ui_x - 140, self.ui_y - 30))