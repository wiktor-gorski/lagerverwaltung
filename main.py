"""
main.py
Startpunkt des Programms: zeigt das Menü und nimmt die Eingaben entgegen.

Starten mit:  python main.py
"""

from datenbank import tabellen_anlegen
from export import exportieren
import lager
from lager import LagerFehler


# ---------- Eingaben sicher einlesen ----------

def text_eingabe(frage):
    """Fragt so lange, bis etwas eingegeben wurde."""
    while True:
        wert = input(frage).strip()
        if wert:
            return wert
        print("  Bitte etwas eingeben.")


def zahl_eingabe(frage, minimum=0):
    """Fragt so lange, bis eine gültige ganze Zahl eingegeben wurde."""
    while True:
        wert = input(frage).strip()
        try:
            zahl = int(wert)
        except ValueError:
            print("  Bitte eine ganze Zahl eingeben.")
            continue
        if zahl < minimum:
            print(f"  Die Zahl muss mindestens {minimum} sein.")
            continue
        return zahl


# ---------- Ausgabe als Tabelle ----------

def tabelle_zeigen(zeilen, spalten, titel):
    """Gibt eine einfache Tabelle im Terminal aus."""
    print(f"\n--- {titel} ---")
    if not zeilen:
        print("  (keine Einträge)")
        return
    # Breite jeder Spalte = längster Eintrag
    breiten = [max(len(str(name)), *(len(str(z[schluessel])) for z in zeilen))
               for name, schluessel in spalten]
    kopf = "  ".join(name.ljust(b) for (name, _), b in zip(spalten, breiten))
    print(kopf)
    print("-" * len(kopf))
    for z in zeilen:
        print("  ".join(str(z[schluessel]).ljust(b) for (_, schluessel), b in zip(spalten, breiten)))


# ---------- Die einzelnen Menüpunkte ----------

def menue_artikel_anlegen():
    nummer = text_eingabe("Artikelnummer: ").upper()
    bezeichnung = text_eingabe("Bezeichnung: ")
    platz = text_eingabe("Lagerplatz (z.B. A-03-2): ").upper()
    bestand = zahl_eingabe("Anfangsbestand: ")
    minimum = zahl_eingabe("Mindestbestand: ")
    lager.artikel_anlegen(nummer, bezeichnung, platz, bestand, minimum)
    print(f"Artikel {nummer} angelegt.")


def menue_wareneingang():
    nummer = text_eingabe("Artikelnummer: ").upper()
    menge = zahl_eingabe("Menge Eingang: ", minimum=1)
    lager.wareneingang(nummer, menge)
    print(f"Eingang gebucht: {menge} Stück {nummer}. Neuer Bestand: {lager.artikel_holen(nummer)['bestand']}")


def menue_warenausgang():
    nummer = text_eingabe("Artikelnummer: ").upper()
    menge = zahl_eingabe("Menge Ausgang: ", minimum=1)
    lager.warenausgang(nummer, menge)
    artikel = lager.artikel_holen(nummer)
    print(f"Ausgang gebucht: {menge} Stück {nummer}. Neuer Bestand: {artikel['bestand']}")
    if artikel["bestand"] < artikel["mindestbestand"]:
        print(f"  ACHTUNG: Mindestbestand ({artikel['mindestbestand']}) unterschritten, bitte nachbestellen!")


def menue_bestandsliste():
    tabelle_zeigen(
        lager.bestandsliste(),
        [("Nr.", "artikelnummer"), ("Bezeichnung", "bezeichnung"), ("Platz", "lagerplatz"),
         ("Bestand", "bestand"), ("Min.", "mindestbestand")],
        "Bestandsliste",
    )


def menue_nachbestellen():
    tabelle_zeigen(
        lager.nachbestellen(),
        [("Nr.", "artikelnummer"), ("Bezeichnung", "bezeichnung"), ("Bestand", "bestand"),
         ("Min.", "mindestbestand"), ("Fehlt", "fehlmenge")],
        "Nachbestellen (unter Mindestbestand)",
    )


def menue_protokoll():
    nummer = input("Artikelnummer (leer = alle): ").strip().upper() or None
    tabelle_zeigen(
        lager.bewegungsprotokoll(nummer),
        [("Zeitpunkt", "zeitpunkt"), ("Nr.", "artikelnummer"), ("Bezeichnung", "bezeichnung"),
         ("Art", "art"), ("Menge", "menge")],
        "Bewegungsprotokoll",
    )


def menue_export():
    datei = exportieren()
    print(f"Export erstellt: {datei}")


MENUE = {
    "1": ("Artikel anlegen", menue_artikel_anlegen),
    "2": ("Wareneingang buchen", menue_wareneingang),
    "3": ("Warenausgang buchen", menue_warenausgang),
    "4": ("Bestandsliste anzeigen", menue_bestandsliste),
    "5": ("Nachbestellen (unter Mindestbestand)", menue_nachbestellen),
    "6": ("Bewegungsprotokoll", menue_protokoll),
    "7": ("Export als Excel", menue_export),
}


def main():
    tabellen_anlegen()
    while True:
        print("\n=== Lagerverwaltung Muster Logistik AG ===")
        for taste, (text, _) in MENUE.items():
            print(f"{taste}  {text}")
        print("0  Beenden")
        wahl = input("Auswahl: ").strip()

        if wahl == "0":
            print("Auf Wiedersehen!")
            break
        if wahl not in MENUE:
            print("Ungültige Auswahl.")
            continue

        try:
            MENUE[wahl][1]()          # gewählte Funktion ausführen
        except LagerFehler as fehler:  # bekannte Fehler freundlich anzeigen
            print(f"Fehler: {fehler}")


if __name__ == "__main__":
    main()
