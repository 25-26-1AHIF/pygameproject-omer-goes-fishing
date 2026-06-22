from game_variables.game_variables import GameVariables as gv
from save_manager import save_game, load_save

# ============================================================
# UPGRADE-SYSTEM
# ============================================================
# Es gibt 4 Upgrade-Typen. Jedes kann unendlich oft gekauft werden,
# wird aber mit jeder Stufe teurer (Preis steigt exponentiell).
#
# - "inventar"  : erhöht MAX_TOTAL_FISH um +2 pro Stufe (10 -> 12 -> 14 ...)
# - "minigame"  : macht das Angel-Minigame leichter
#                 (größerer Spieler-Balken, langsamerer Fisch)
# - "preis"     : erhöht den Verkaufspreis aller Fische (Prozent-Bonus)
# - "koeder"    : verschiebt die Rarity-Gewichtung zugunsten selterener Fische

UPGRADE_DEFS = {
    "inventar": {
        "name": "Größerer Korb",
        "beschreibung": "+2 maximale Fische im Inventar pro Stufe",
        "base_cost": 100,
        "cost_multiplier": 1.2,  # Jede Stufe kostet das 1.2-fache der vorigen
    },
    "minigame": {
        "name": "Bessere Angel",
        "beschreibung": "Größerer Fangbalken & ruhigerer Fisch pro Stufe",
        "base_cost": 150,
        "cost_multiplier": 1.2,
    },
    "preis": {
        "name": "Verhandlungsgeschick",
        "beschreibung": "+50% Verkaufspreis für alle Fische pro Stufe",
        "base_cost": 200,
        "cost_multiplier": 1.2,
    },
    "koeder": {
        "name": "Besserer Köder",
        "beschreibung": "Höhere Chance auf seltenere Fische pro Stufe",
        "base_cost": 150,
        "cost_multiplier": 1.2,
    },
}

# Wie viele Stufen ein Upgrade maximal haben darf (Sicherheitsgrenze,
# damit nichts ins Absurde wächst). Kann später erhöht werden.
MAX_LEVEL = 20


class UpgradeManager:
    """
    @brief Verwaltet sämtliche Upgrade-Stufen (Inventar, Minigame,
           Verkaufspreis, Köder), deren Kosten sowie das Laden/Speichern
           dieser Stufen im aktiven Save-Slot.
    """

    def __init__(self):
        """
        @brief Initialisiert alle Upgrade-Stufen mit 0 und lädt
               anschließend den gespeicherten Stand (falls vorhanden).
        """
        # levels speichert pro Upgrade-Typ die aktuelle Stufe (0 = noch nicht gekauft)
        self.levels = {key: 0 for key in UPGRADE_DEFS}
        self.load_from_save()

    def load_from_save(self):
        """
        @brief Lädt die gespeicherten Upgrade-Stufen aus dem aktuell
               aktiven Save-Slot. Fehlt ein Eintrag, bleibt die Stufe 0.
        """
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        if spielstand and "upgrades" in spielstand:
            gespeichert = spielstand["upgrades"]
            for key in UPGRADE_DEFS:
                self.levels[key] = gespeichert.get(key, 0)
        else:
            self.levels = {key: 0 for key in UPGRADE_DEFS}

    def save_to_disk(self):
        """
        @brief Sichert die aktuellen Upgrade-Stufen permanent in die
               Save-Datei des aktiven Slots.
        """
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        if spielstand is None:
            spielstand = {"money": 0, "player_name": "Fischer"}

        spielstand["upgrades"] = self.levels
        save_game(aktiver_slot, spielstand)

    def get_level(self, upgrade_key):
        """
        @brief Liefert die aktuelle Stufe eines Upgrades.
        @param upgrade_key Schlüssel aus UPGRADE_DEFS (z.B. "inventar").
        @return Aktuelle Stufe (int), 0 falls noch keine Stufe gekauft.
        """
        return self.levels.get(upgrade_key, 0)

    def get_cost(self, upgrade_key):
        """
        @brief Berechnet die Kosten für die NÄCHSTE Stufe eines Upgrades.

        Formel: base_cost * (cost_multiplier ^ aktuelle_stufe)
        Dadurch wird jede weitere Stufe teurer.

        @param upgrade_key Schlüssel aus UPGRADE_DEFS.
        @return Kosten der nächsten Stufe in Euro (int, gerundet).
        """
        info = UPGRADE_DEFS[upgrade_key]
        aktuelle_stufe = self.get_level(upgrade_key)
        kosten = info["base_cost"] * (info["cost_multiplier"] ** aktuelle_stufe)
        return int(round(kosten))

    def can_afford(self, upgrade_key, money):
        """
        @brief Prüft, ob genug Geld für die nächste Stufe vorhanden ist
               und das Max-Level noch nicht erreicht wurde.
        @param upgrade_key Schlüssel aus UPGRADE_DEFS.
        @param money Aktuell verfügbares Geld.
        @return True, falls das Upgrade gekauft werden könnte.
        """
        if self.get_level(upgrade_key) >= MAX_LEVEL:
            return False
        return money >= self.get_cost(upgrade_key)

    def purchase(self, upgrade_key, money):
        """
        @brief Versucht, ein Upgrade um eine Stufe zu erhöhen.

        Bei Erfolg: erhöht die Stufe, zieht die Kosten vom übergebenen
        'money' ab und speichert GELD + UPGRADES in EINEM einzigen
        Schreibvorgang (load -> ändern -> save), damit sich Käufe
        aus main_screen.py und dieser Save-Aufruf nicht gegenseitig
        überschreiben.

        @param upgrade_key Schlüssel aus UPGRADE_DEFS.
        @param money Aktuell verfügbares Geld vor dem Kauf.
        @return Tupel (erfolg: bool, neuer_geldbetrag: int).
                Bei Misserfolg (zu wenig Geld oder Max-Level erreicht)
                wird (False, money) unverändert zurückgegeben.
        """
        if self.get_level(upgrade_key) >= MAX_LEVEL:
            return False, money

        kosten = self.get_cost(upgrade_key)
        if money < kosten:
            return False, money

        self.levels[upgrade_key] += 1
        verbleibendes_geld = money - kosten

        # Geld UND Upgrades in einem Zug speichern (atomar bzgl. dieser Operation)
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)
        if spielstand is None:
            spielstand = {"money": 0, "player_name": "Fischer"}

        spielstand["money"] = verbleibendes_geld
        spielstand["upgrades"] = self.levels
        save_game(aktiver_slot, spielstand)

        return True, verbleibendes_geld

    # ------------------------------------------------------------
    # Effektive Werte, die andere Module (inventar.py, angelsystem.py)
    # abfragen, um die tatsächliche Spiel-Auswirkung zu bestimmen.
    # ------------------------------------------------------------

    def get_inventory_bonus(self):
        """
        @brief Berechnet den zusätzlichen Inventarplatz durch das
               'Größerer Korb'-Upgrade.
        @return +2 Inventarplätze pro Stufe (int).
        """
        return self.get_level("inventar") * 2

    def get_price_multiplier(self):
        """
        @brief Berechnet den Verkaufspreis-Multiplikator durch das
               'Verhandlungsgeschick'-Upgrade.
        @return Multiplikator (float), z.B. 2.0 bei Stufe 2 (+50% pro Stufe).
        """
        return 1.0 + (self.get_level("preis") * 0.5)

    def get_minigame_bar_bonus(self):
        """
        @brief Berechnet die zusätzliche Balkenhöhe im Minigame durch
               das 'Bessere Angel'-Upgrade.
        @return Zusätzliche Höhe in Pixel (int), +4px pro Stufe.
        """
        return self.get_level("minigame") * 4

    def get_minigame_difficulty_reduction(self):
        """
        @brief Reduziert effektiv die 'difficulty' jedes Fisches im
               Minigame durch das 'Bessere Angel'-Upgrade.

        Gibt einen Faktor zwischen 0 und 1 zurück, mit dem die
        ursprüngliche difficulty multipliziert wird (kleiner = leichter).
        Pro Stufe -5%, aber nie unter 50% der Originalschwierigkeit.

        @return Reduktionsfaktor (float) im Bereich [0.5, 1.0].
        """
        reduktion = self.get_level("minigame") * 0.05
        return max(0.5, 1.0 - reduktion)

    # KI-Anfang
    # KI: Claude
    # prompt: Wie kann ich bei einer gewichteten Zufallsauswahl seltenere
    #         Kategorien durch ein Upgrade gezielt häufiger machen, ohne
    #         die häufigste Kategorie (common) zu verändern?
    def get_rarity_weight_multiplier(self, rarity):
        """
        @brief Liefert den Gewichtungs-Multiplikator für eine bestimmte
               Rarity, abhängig von der aktuellen Stufe des
               'Köder'-Upgrades.

        Idee: "common" bleibt unverändert (Multiplikator 1.0), aber je
        seltener die Rarity, desto stärker wird ihr Gewicht pro Stufe
        angehoben. Dadurch verschiebt sich die Gesamtverteilung Schritt
        für Schritt zugunsten seltenerer Fische, ohne dass Common komplett
        verschwindet.

        Reihenfolge der Seltenheits-Ränge (0 = am häufigsten):
        common=0, uncommon=1, rare=2, epic=3, legendary=4, mythic=5, divine=6
        Jeder Rang bekommt pro Stufe +25% Gewicht relativ zu seinem Rang.

        @param rarity Rarity-Schlüssel (z.B. "common", "legendary", ...).
        @return Multiplikator (float) >= 1.0, mit dem das Basisgewicht
                der Rarity in pick_random_fish() verrechnet wird.
        """
        seltenheits_rang = {
            "common": 0,
            "uncommon": 1,
            "rare": 2,
            "epic": 3,
            "legendary": 4,
            "mythic": 5,
            "divine": 6,
        }
        stufe = self.get_level("koeder")
        rang = seltenheits_rang.get(rarity, 0)
        # +25% pro Stufe, skaliert mit dem Seltenheits-Rang
        # (common: Rang 0 -> immer Multiplikator 1.0, bleibt unverändert)
        return 1.0 + (stufe * 0.25 * rang)
    # KI-Ende