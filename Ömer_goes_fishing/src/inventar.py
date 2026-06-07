# inventar.py
from game_variables.game_variables import GameVariables as gv
from save_manager import save_game, load_save

# Definition aller Fischarten mit Verkaufspreis und Schwierigkeit
FISH_TYPES = {
    "Hering": {"price": 15, "difficulty": 1.0},
    "Makrele": {"price": 25, "difficulty": 1.2},
    "Lachs": {"price": 50, "difficulty": 1.6},
    "Thunfisch": {"price": 95, "difficulty": 2.2},
    "Goldfisch": {"price": 200, "difficulty": 2.8}
}


class Inventory:
    def __init__(self):
        self.content = {}
        # Beim Erstellen des Inventars sofort die Fische aus dem aktiven Save-Slot laden
        self.load_from_save()

    def load_from_save(self):
        """Lädt das gespeicherte Inventar aus dem aktiven Save-Slot."""
        slot = getattr(gv, 'current_slot', 1)
        save_data = load_save(slot)

        if save_data and "inventory" in save_data:
            # Erstellt eine echte Kopie des gespeicherten Inventar-Wörterbuchs
            self.content = dict(save_data["inventory"])
        else:
            self.content = {}

    def save_to_disk(self):
        """Speichert den aktuellen Zustand des Inventars in die Save-Datei."""
        slot = getattr(gv, 'current_slot', 1)
        save_data = load_save(slot)

        if save_data is None:
            save_data = {"money": 0, "player_name": "Fischer"}

        # Das Inventar-Diktat im Spielstand aktualisieren
        save_data["inventory"] = self.content
        save_game(slot, save_data)

    def add_fish(self, fish_name):
        """Fügt einen Fisch zum Inventar hinzu und speichert sofort."""
        if fish_name in FISH_TYPES:
            self.content[fish_name] = self.content.get(fish_name, 0) + 1

            # Direkt auf der Festplatte sichern!
            self.save_to_disk()
            print(f"Inventar: {fish_name} wurde hinzugefügt und dauerhaft gespeichert!")

    def sell_all_fish(self):
        """Verkauft alle Fische, leert das Inventar und speichert das Geld + leeres Inventar."""
        total_earnings = 0
        for fish_name, count in self.content.items():
            total_earnings += FISH_TYPES[fish_name]["price"] * count

        if total_earnings > 0:
            slot = getattr(gv, 'current_slot', 1)
            save_data = load_save(slot)

            if save_data is None:
                save_data = {"money": 0, "player_name": "Fischer"}

            # 1. Geld gutschreiben
            save_data["money"] += total_earnings

            # 2. Lokales Inventar leeren
            self.content.clear()

            # 3. Inventar in der Save-Datei leeren
            save_data["inventory"] = {}

            # Alles zusammen final speichern
            save_game(slot, save_data)

            print(f"Erfolgreich verkauft! +{total_earnings}€ verdient. Save-Datei aktualisiert.")
            return total_earnings
        return 0