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
        "cost_multiplier": 1.5,  # Jede Stufe kostet das 1.6-fache der vorigen
    },
    "minigame": {
        "name": "Bessere Angel",
        "beschreibung": "Größerer Fangbalken & ruhigerer Fisch pro Stufe",
        "base_cost": 150,
        "cost_multiplier": 1.5,
    },
    "preis": {
        "name": "Verhandlungsgeschick",
        "beschreibung": "+50% Verkaufspreis für alle Fische pro Stufe",
        "base_cost": 200,
        "cost_multiplier": 1.5,
    },
    "koeder": {
        "name": "Besserer Köder",
        "beschreibung": "Höhere Chance auf seltenere Fische pro Stufe",
        "base_cost": 180,
        "cost_multiplier": 1.5,
    },
}

# Wie viele Stufen ein Upgrade maximal haben darf (Sicherheitsgrenze,
# damit nichts ins Absurde wächst). Kann später erhöht werden.
MAX_LEVEL = 20


class UpgradeManager:
    def __init__(self):
        # levels speichert pro Upgrade-Typ die aktuelle Stufe (0 = noch nicht gekauft)
        self.levels = {key: 0 for key in UPGRADE_DEFS}
        self.load_from_save()

    def load_from_save(self):
        """Lädt die gespeicherten Upgrade-Stufen aus dem aktuell aktiven Save-Slot."""
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        if spielstand and "upgrades" in spielstand:
            gespeichert = spielstand["upgrades"]
            for key in UPGRADE_DEFS:
                self.levels[key] = gespeichert.get(key, 0)
        else:
            self.levels = {key: 0 for key in UPGRADE_DEFS}

    def save_to_disk(self):
        """Sichert die aktuellen Upgrade-Stufen permanent in die Save-Datei."""
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        if spielstand is None:
            spielstand = {"money": 0, "player_name": "Fischer"}

        spielstand["upgrades"] = self.levels
        save_game(aktiver_slot, spielstand)

    def get_level(self, upgrade_key):
        """Aktuelle Stufe eines Upgrades (0 = noch keine Stufe gekauft)."""
        return self.levels.get(upgrade_key, 0)

    def get_cost(self, upgrade_key):
        """
        Berechnet die Kosten für die NÄCHSTE Stufe eines Upgrades.
        Formel: base_cost * (cost_multiplier ^ aktuelle_stufe)
        Dadurch wird jede weitere Stufe teurer.
        """
        info = UPGRADE_DEFS[upgrade_key]
        aktuelle_stufe = self.get_level(upgrade_key)
        kosten = info["base_cost"] * (info["cost_multiplier"] ** aktuelle_stufe)
        return int(round(kosten))

    def can_afford(self, upgrade_key, money):
        if self.get_level(upgrade_key) >= MAX_LEVEL:
            return False
        return money >= self.get_cost(upgrade_key)

    def purchase(self, upgrade_key, money):
        """
        Versucht, ein Upgrade um eine Stufe zu erhöhen.

        Bei Erfolg: erhöht die Stufe, zieht die Kosten vom übergebenen
        'money' ab und speichert GELD + UPGRADES in EINEM einzigen
        Schreibvorgang (load -> ändern -> save), damit sich Käufer
        aus main_screen.py und dieser Save-Aufruf nicht gegenseitig
        überschreiben.

        Gibt (erfolg: bool, neuer_geldbetrag: int) zurück.
        Bei Misserfolg (zu wenig Geld oder Max-Level erreicht): (False, money) unverändert.
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
        """+2 Inventarplätze pro Stufe des 'inventar'-Upgrades."""
        return self.get_level("inventar") * 2

    def get_price_multiplier(self):
        """Verkaufspreis-Multiplikator, z.B. 2 bei Stufe 2 (+50% pro Stufe)."""
        return 1.0 + (self.get_level("preis") * 0.5)

    def get_minigame_bar_bonus(self):
        """Zusätzliche Höhe (Pixel) für den Spieler-Balken im Minigame, pro Stufe."""
        return self.get_level("minigame") * 4

    def get_minigame_difficulty_reduction(self):
        """
        Reduziert effektiv die 'difficulty' jedes Fisches im Minigame.
        Gibt einen Faktor zwischen 0 und 1 zurück, mit dem die
        ursprüngliche difficulty multipliziert wird (kleiner = leichter).
        Pro Stufe -5%, aber nie unter 50% der Originalschwierigkeit.
        """
        reduktion = self.get_level("minigame") * 0.05
        return max(0.5, 1.0 - reduktion)

    def get_rarity_weight_multiplier(self, rarity):
        """
        Gibt den Gewichtungs-Multiplikator für eine bestimmte Rarity zurück,
        abhängig von der aktuellen Stufe des 'Köder'-Upgrades.

        Idee: "common" bleibt unverändert (Multiplikator 1.0), aber je
        seltener die Rarity, desto stärker wird ihr Gewicht pro Stufe
        angehoben. Dadurch verschiebt sich die Gesamtverteilung Schritt
        für Schritt zugunsten selterener Fische, ohne dass Common komplett
        verschwindet.

        Reihenfolge der Seltenheits-Ränge (0 = am häufigsten):
        common=0, uncommon=1, rare=2, epic=3, legendary=4, mythic=5, divine=6
        Jeder Rang bekommt pro Stufe +12% Gewicht relativ zu seinem Rang.
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
        # +12% pro Stufe, skaliert mit dem Seltenheits-Rang
        # (common: Rang 0 -> immer Multiplikator 1.0, bleibt unverändert)
        return 1.0 + (stufe * 0.12 * rang)