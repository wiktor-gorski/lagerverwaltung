"""
datenbank.py
Verbindung zur SQLite-Datenbank und Anlegen der Tabellen.

SQLite ist eine Datenbank, die in einer einzigen Datei gespeichert wird
(hier: lager.db). Sie ist in Python schon eingebaut, man muss nichts installieren.
"""

import sqlite3
from pathlib import Path

# Die Datenbank-Datei liegt im gleichen Ordner wie dieses Skript
DB_PFAD = Path(__file__).parent / "lager.db"


def verbinden():
    """Öffnet eine Verbindung zur Datenbank und gibt sie zurück."""
    verbindung = sqlite3.connect(DB_PFAD)
    # Damit kann man Spalten mit Namen ansprechen, z.B. zeile["bestand"]
    verbindung.row_factory = sqlite3.Row
    # Fremdschlüssel einschalten (SQLite macht das nicht automatisch)
    verbindung.execute("PRAGMA foreign_keys = ON")
    return verbindung


def tabellen_anlegen():
    """Legt die Tabellen an, falls sie noch nicht existieren."""
    with verbinden() as db:
        # Tabelle 1: alle Artikel im Lager
        db.execute("""
            CREATE TABLE IF NOT EXISTS artikel (
                artikelnummer   TEXT PRIMARY KEY,
                bezeichnung     TEXT NOT NULL,
                lagerplatz      TEXT NOT NULL,
                bestand         INTEGER NOT NULL DEFAULT 0 CHECK (bestand >= 0),
                mindestbestand  INTEGER NOT NULL DEFAULT 0 CHECK (mindestbestand >= 0)
            )
        """)

        # Tabelle 2: jede Buchung (Eingang oder Ausgang) wird hier protokolliert
        db.execute("""
            CREATE TABLE IF NOT EXISTS bewegungen (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                zeitpunkt       TEXT NOT NULL,
                artikelnummer   TEXT NOT NULL REFERENCES artikel(artikelnummer),
                art             TEXT NOT NULL CHECK (art IN ('Eingang', 'Ausgang')),
                menge           INTEGER NOT NULL CHECK (menge > 0)
            )
        """)
