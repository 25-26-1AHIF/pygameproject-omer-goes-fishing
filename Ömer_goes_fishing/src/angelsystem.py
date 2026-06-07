# angelsystem.py
import pygame
import random
from game_variables.game_variables import GameVariables as gv
from inventar import FISH_TYPES


class FishingSystem:
    def __init__(self, inventory):
        self.inventory = inventory
        self.state = "IDLE"  # Zustände: IDLE, WAITING, BITE, MINIGAME, RESULT

        self.timer = 0
        self.current_fish = None
        self.result_text = ""

        # Position & Dimensionen des Stardew Valley UI Fensters (rechts am Bildschirm)
        self.ui_x = gv.SCREEN_WIDTH - 120
        self.ui_y = 150
        self.ui_width = 35
        self.ui_height = 300

        # Physik-Variablen für den grünen Balken (Spieler-Cursor)
        self.bar_height = 75
        self.player_y = self.ui_height - self.bar_height  # Startet ganz unten
        self.player_vel = 0.0
        self.gravity = 0.4
        self.lift = -1.0  # Wie stark SPACE den Balken nach oben drückt

        # Variablen für den Fisch im Minigame
        self.fish_y = self.ui_height - 20
        self.fish_target_y = self.fish_y
        self.fish_move_timer = 0

        # Fortschrittsbalken (0 bis 100)
        self.progress = 30.0

    def handle_event(self, event):
        """Verarbeitet den Tastendruck für SPACE."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.state == "IDLE":
                # Köder werfen und zufällige Wartezeit (2 bis 5 Sekunden bei 60 FPS) bestimmen
                self.state = "WAITING"
                self.timer = random.randint(120, 300)
                print("Köder geworfen... Warten auf Biss...")

            elif self.state == "BITE":
                # Rechtzeitig reagiert! Minigame startet
                self.state = "MINIGAME"
                self.current_fish = random.choice(list(FISH_TYPES.keys()))
                self.progress = 30.0  # Startwert
                self.player_y = self.ui_height - self.bar_height
                self.player_vel = 0.0
                self.fish_y = self.ui_height - 30
                self.fish_target_y = self.fish_y
                print(f"Ein {self.current_fish} hat angebissen! Minigame startet.")

    def update(self):
        """Aktualisiert die Logik des Angelsystems pro Frame."""
        if self.state == "WAITING":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "BITE"
                self.timer = 75  # Spieler hat ca. 1.2 Sekunden Zeit um SPACE zu drücken

        elif self.state == "BITE":
            self.timer -= 1
            if self.timer <= 0:
                # Zu spät reagiert
                self.state = "RESULT"
                self.result_text = "Entkommen!"
                self.timer = 90

        elif self.state == "MINIGAME":
            # 1. Spieler-Balken Physik (Fliegen durch Halten von SPACE)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.player_vel += self.lift

            self.player_vel += self.gravity
            self.player_y += self.player_vel

            # Kollision mit dem oberen/unteren Rand der UI-Box
            if self.player_y < 0:
                self.player_y = 0
                self.player_vel = 0
            if self.player_y > self.ui_height - self.bar_height:
                self.player_y = self.ui_height - self.bar_height
                self.player_vel = 0

            # 2. KI-Fisch-Bewegung (simuliert unruhiges Schwimmen)
            self.fish_move_timer -= 1
            diff = FISH_TYPES[self.current_fish]["difficulty"]

            if self.fish_move_timer <= 0:
                # Wählt alle 0.5 bis 1 Sekunden ein neues zufälliges Höhen-Ziel
                self.fish_target_y = random.randint(10, self.ui_height - 15)
                self.fish_move_timer = random.randint(30, 60)

            # Fisch bewegt sich interpoliert auf sein Ziel zu (beeinflusst von der Schwierigkeit)
            if self.fish_y < self.fish_target_y:
                self.fish_y += 1.8 * diff
            elif self.fish_y > self.fish_target_y:
                self.fish_y -= 1.8 * diff

            # 3. Prüfung: Befindet sich der Fisch im grünen Balken?
            # Wir geben dem Fisch einen imaginären Radius von 10 Pixeln
            if self.player_y <= self.fish_y <= self.player_y + self.bar_height:
                self.progress += 0.5  # Balken steigt
            else:
                self.progress -= 0.4  # Balken sinkt

            # Gewonnen oder Verloren Abfrage
            if self.progress >= 100:
                self.state = "RESULT"
                self.result_text = f"{self.current_fish} gefangen!"
                self.inventory.add_fish(self.current_fish)
                self.timer = 120
            elif self.progress <= 0:
                self.state = "RESULT"
                self.result_text = "Entkommen!"
                self.timer = 120

        elif self.state == "RESULT":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "IDLE"

    def draw(self, screen):
        """Zeigt die grafischen Elemente des Angelsystems auf dem Bildschirm."""
        # Text-Benachrichtigungen über dem Boot / Mitte des Bildschirms
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

        # Das Stardew Valley Minigame-Fenster rendern
        elif self.state == "MINIGAME":
            # 1. Hintergrund-Messbalken (Graue Box)
            pygame.draw.rect(screen, (40, 40, 40), (self.ui_x, self.ui_y, self.ui_width, self.ui_height))
            pygame.draw.rect(screen, "white", (self.ui_x, self.ui_y, self.ui_width, self.ui_height), 2)

            # 2. Grüner Spieler-Balken
            pygame.draw.rect(screen, (50, 220, 50),
                             (self.ui_x + 3, self.ui_y + int(self.player_y), self.ui_width - 6, self.bar_height))

            # 3. Der Fisch (Oranger Kreis)
            pygame.draw.circle(screen, (255, 120, 0), (self.ui_x + self.ui_width // 2, self.ui_y + int(self.fish_y)), 8)

            # 4. Der Fortschrittsbalken direkt rechts daneben (Gelb/Orange)
            prog_height = int((self.progress / 100.0) * self.ui_height)
            pygame.draw.rect(screen, (20, 20, 20), (self.ui_x + self.ui_width + 8, self.ui_y, 12, self.ui_height))
            pygame.draw.rect(screen, (255, 180, 0),
                             (self.ui_x + self.ui_width + 8, self.ui_y + self.ui_height - prog_height, 12, prog_height))
            pygame.draw.rect(screen, "white", (self.ui_x + self.ui_width + 8, self.ui_y, 12, self.ui_height), 1)

            # Infos über den Fisch anzeigen
            lbl = gv.FONT_MIDDLE.render(f"Fisch: {self.current_fish}", True, "white")
            screen.blit(lbl, (self.ui_x - 140, self.ui_y - 30))