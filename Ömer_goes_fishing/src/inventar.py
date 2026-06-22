from game_variables.game_variables import GameVariables as gv
from save_manager import save_game, load_save
from upgrades import UpgradeManager

# ============================================================
# RARITY-SYSTEM
# ============================================================
# Jede Rarity hat eine Farbe (RGB) und ein "weight" (Gewichtung).
# Je HÖHER das weight, desto HÄUFIGER kommt diese Rarity beim
# zufälligen Fang vor. Die Werte sind so gewählt, dass seltenere
# Rarities deutlich unwahrscheinlicher sind (klassische Lootbox-Kurve).
RARITY_INFO = {
    "common":    {"weight": 100, "colour": (160, 160, 160)},  # Grau
    "uncommon":  {"weight": 55,  "colour": (60, 200, 80)},    # Grün
    "rare":      {"weight": 25,  "colour": (60, 130, 230)},   # Blau
    "epic":      {"weight": 10,  "colour": (160, 60, 220)},   # Lila
    "legendary": {"weight": 4,   "colour": (255, 215, 0)},    # Gelb/Gold
    "mythic":    {"weight": 1.5, "colour": (220, 30, 30)},    # Rot
    "divine":    {"weight": 0.4, "colour": (255, 255, 255)},  # Göttliches Weiß (mit Glow im UI)
}

# ============================================================
# FISCHARTEN
# ============================================================
# "difficulty" steuert weiterhin nur das Minigame (wie schnell/unruhig
# sich der Fisch bewegt). "rarity" steuert, wie oft der Fisch überhaupt
# als current_fish ausgewählt wird (siehe angelsystem.py).
# "colour" wird automatisch aus RARITY_INFO übernommen, damit du es
# nicht bei jedem Fisch einzeln pflegen musst.
FISH_TYPES = {
    # --- Common ---
    "Hering":          {"price": 15,   "difficulty": 1.0, "rarity": "common"},
    "Sardine":         {"price": 12,   "difficulty": 0.9, "rarity": "common"},
    "Karpfen":         {"price": 18,   "difficulty": 1.1, "rarity": "common"},

    # --- Uncommon ---
    "Makrele":         {"price": 25,   "difficulty": 1.2, "rarity": "uncommon"},
    "Barsch":          {"price": 28,   "difficulty": 1.3, "rarity": "uncommon"},

    # --- Rare ---
    "Lachs":           {"price": 50,   "difficulty": 1.6, "rarity": "rare"},
    "Zander":          {"price": 55,   "difficulty": 1.7, "rarity": "rare"},

    # --- Epic ---
    "Thunfisch":       {"price": 95,   "difficulty": 2.2, "rarity": "epic"},
    "Schwertfisch":    {"price": 110,  "difficulty": 2.4, "rarity": "epic"},

    # --- Legendary ---
    "Goldfisch":       {"price": 200,  "difficulty": 2.8, "rarity": "legendary"},
    "Coelacanth":      {"price": 240,  "difficulty": 3.0, "rarity": "legendary"},

    # --- Mythic ---
    "Schattenaal":     {"price": 400,  "difficulty": 3.6, "rarity": "mythic"},

    # --- Divine ---
    "Ur-Leviathan":    {"price": 1000, "difficulty": 4.5, "rarity": "divine"},
}

# Farbe automatisch aus der Rarity ziehen, damit FISH_TYPES nicht doppelt
# gepflegt werden muss. Jeder Fisch bekommt also die Farbe seiner Rarity.
for _fisch, _daten in FISH_TYPES.items():
    _daten["colour"] = RARITY_INFO[_daten["rarity"]]["colour"]


# ============================================================
# INVENTAR-LIMIT
# ============================================================
# Basis-Limit ohne Upgrades: insgesamt maximal 10 Fische im Inventar,
# unabhängig davon welche Art (also z.B. 7 Heringe + 3 Lachse = voll).
# Das "Größerer Korb"-Upgrade erhöht dieses Limit um +2 pro Stufe
# (siehe upgrades.py -> get_inventory_bonus()).
BASE_MAX_TOTAL_FISH = 10


class Inventory:
    def __init__(self, upgrade_manager=None):
        # Das Inventar ist am Anfang ein leeres Wörterbuch (Dictionary)
        self.content = {}
        # Der UpgradeManager wird gebraucht, um das aktuelle Inventar-Limit
        # und den Verkaufspreis-Bonus zu berechnen. Falls keiner übergeben
        # wird, erstellen wir einen eigenen (z.B. für einfache Tests).
        self.upgrade_manager = upgrade_manager if upgrade_manager is not None else UpgradeManager()
        # Sobald das Inventar geladen wird, holen wir die Fische aus dem Spielstand
        self.load_from_save()

    @property
    def MAX_TOTAL_FISH(self):
        """
        Aktuelles Inventar-Limit: Basiswert + Bonus durch das
        'Größerer Korb'-Upgrade (siehe upgrades.py).
        """
        return BASE_MAX_TOTAL_FISH + self.upgrade_manager.get_inventory_bonus()

    def load_from_save(self):
        """Lädt die gespeicherten Fische aus dem aktuell aktiven Save-Slot."""
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        if spielstand and "inventory" in spielstand:
            self.content = dict(spielstand["inventory"])
        else:
            self.content = {}

    def save_to_disk(self):
        """Sichert das aktuelle Inventar permanent in die Save-Datei."""
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        if spielstand is None:
            spielstand = {"money": 0, "player_name": "Fischer"}

        spielstand["inventory"] = self.content
        save_game(aktiver_slot, spielstand)

    def total_fish_count(self):
        """Zählt, wie viele Fische insgesamt (über alle Arten) im Inventar sind."""
        return sum(self.content.values())

    def add_fish(self, fisch_name):
        """
        Fügt einen gefangenen Fisch hinzu, sofern das GLOBALE Limit
        (MAX_TOTAL_FISH, über alle Fischarten zusammen) noch nicht
        erreicht ist, und speichert sofort.

        Gibt True zurück, wenn der Fisch ins Inventar passte,
        False, wenn das Inventar insgesamt bereits voll ist.
        """
        if fisch_name not in FISH_TYPES:
            return False

        if self.total_fish_count() >= self.MAX_TOTAL_FISH:
            # Inventar ist insgesamt voll (egal welche Art)
            return False

        self.content[fisch_name] = self.content.get(fisch_name, 0) + 1
        self.save_to_disk()
        return True

    def sell_all_fish(self):
        """Verkauft alle Fische, schreibt das Geld dem Spielstand gut und leert das Inventar.
        Der Verkaufspreis wird mit dem 'Verhandlungsgeschick'-Upgrade-Multiplikator
        hochgerechnet (+8% pro Stufe)."""
        gesamter_verdienst = 0
        preis_multiplikator = self.upgrade_manager.get_price_multiplier()

        for fisch_name, anzahl in self.content.items():
            grundpreis = FISH_TYPES[fisch_name]["price"] * anzahl
            gesamter_verdienst += grundpreis * preis_multiplikator

        gesamter_verdienst = int(round(gesamter_verdienst))

        if gesamter_verdienst > 0:
            aktiver_slot = getattr(gv, 'current_slot', 1)
            spielstand = load_save(aktiver_slot)

            if spielstand is None:
                spielstand = {"money": 0, "player_name": "Fischer"}

            spielstand["money"] += gesamter_verdienst
            self.content.clear()
            spielstand["inventory"] = {}

            save_game(aktiver_slot, spielstand)
            return gesamter_verdienst

        return 0