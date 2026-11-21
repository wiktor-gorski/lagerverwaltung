"""
beispieldaten.py
Füllt die Datenbank mit ein paar Beispielartikeln, damit man das Tool
sofort ausprobieren kann.

Starten mit:  python beispieldaten.py
"""

from datenbank import tabellen_anlegen
import lager
from lager import LagerFehler

ARTIKEL = [
    # Nummer,   Bezeichnung,                    Platz,     Bestand, Minimum
    ("SP-1001", "Spanplatte 19 mm 2800x2070",   "A-01-1",  120,     40),
    ("SP-1002", "Spanplatte 16 mm 2800x2070",   "A-01-2",  25,      40),
    ("MDF-2001", "MDF-Platte 8 mm 2800x2070",   "A-02-1",  60,      20),
    ("KA-3001", "Kantenband Eiche 22 mm",       "B-04-3",  300,     100),
    ("PA-4001", "Palette EUR 1200x800",         "C-00-1",  15,      30),
    ("FO-5001", "Stretchfolie 500 mm",          "B-02-1",  48,      12),
]

if __name__ == "__main__":
    tabellen_anlegen()
    for a in ARTIKEL:
        try:
            lager.artikel_anlegen(*a)
            print(f"Angelegt: {a[0]} {a[1]}")
        except LagerFehler as fehler:
            print(f"Übersprungen: {fehler}")

    # Ein paar Bewegungen, damit das Protokoll nicht leer ist
    lager.warenausgang("SP-1001", 30)
    lager.wareneingang("PA-4001", 10)
    lager.warenausgang("FO-5001", 40)
    print("Beispieldaten fertig.")
