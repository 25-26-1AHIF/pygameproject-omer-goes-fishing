# inventar.py
from game_variables.game_variables import GameVariables as gv
from save_manager import save_game, load_save

# Eine Liste aller Fischarten mit ihren Verkaufspreisen und Schwierigkeitsgraden für das Minigame
FISH_TYPES = {
    "Hering": {"price": 15, "difficulty": 1.0},
    "Makrele": {"price": 25, "difficulty": 1.2},
    "Lachs": {"price": 50, "difficulty": 1.6},
    "Thunfisch": {"price": 95, "difficulty": 2.2},
    "Goldfisch": {"price": 200, "difficulty": 2.8}
}


class Inventory:
    def __init__(self):
        # Das Inventar ist am Anfang ein leeres Wörterbuch (Dictionary)
        self.content = {}
        # Sobald das Inventar geladen wird, holen wir die Fische aus dem Spielstand
        self.load_from_save()

    def load_from_save(self):
        """Lädt die gespeicherten Fische aus dem aktuell aktiven Save-Slot."""
        # Welcher Slot ist aktiv? Wenn keiner gesetzt ist, nimm standardmäßig Slot 1
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        # Wenn ein Spielstand existiert und dort bereits Fische drin sind, lade sie
        if spielstand and "inventory" in spielstand:
            self.content = dict(spielstand["inventory"])
        else:
            self.content = {}

    def save_to_disk(self):
        """Sichert das aktuelle Inventar permanent in die Save-Datei."""
        aktiver_slot = getattr(gv, 'current_slot', 1)
        spielstand = load_save(aktiver_slot)

        # Falls die Datei leer war, erstellen wir ein Standard-Objekt
        if spielstand is None:
            spielstand = {"money": 0, "player_name": "Fischer"}

        # Wir fügen unser aktuelles Inventar dem Spielstand hinzu und speichern
        spielstand["inventory"] = self.content
        save_game(aktiver_slot, spielstand)

    def add_fish(self, fisch_name):
        """Fügt einen gefangenen Fisch hinzu und speichert sofort auf der Festplatte."""
        if fisch_name in FISH_TYPES:
            # Erhöhe die Anzahl des Fisches um 1. Falls er noch nicht existiert, starte bei 0 + 1
            self.content[fisch_name] = self.content.get(fisch_name, 0) + 1
            # Sofort auf der Festplatte sichern, damit nichts verloren geht
            self.save_to_disk()

    def sell_all_fish(self):
        """Verkauft alle Fische, schreibt das Geld dem Spielstand gut und leert das Inventar."""
        gesamter_verdienst = 0

        # Berechne den Gesamtwert aller Fische im Inventar
        for fisch_name, anzahl in self.content.items():
            gesamter_verdienst += FISH_TYPES[fisch_name]["price"] * anzahl

        # Wenn wir überhaupt Fische zum Verkaufen haben:
        if gesamter_verdienst > 0:
            aktiver_slot = getattr(gv, 'current_slot', 1)
            spielstand = load_save(aktiver_slot)

            if spielstand is None:
                spielstand = {"money": 0, "player_name": "Fischer"}

            # 1. Geld im Spielstand erhöhen
            spielstand["money"] += gesamter_verdienst
            # 2. Unser lokales Inventar im Spiel leeren
            self.content.clear()
            # 3. Das Inventar auch in der Speicherdatei auf leer setzen
            spielstand["inventory"] = {}

            # Alles final in die Save-Datei schreiben
            save_game(aktiver_slot, spielstand)
            return gesamter_verdienst

        return 0  # Nichts verdient, weil das Inventar leer war