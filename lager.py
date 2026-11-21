"""
lager.py
Die eigentliche Lager-Logik: Artikel anlegen, Wareneingang, Warenausgang,
Bestandsliste, Nachbestell-Liste und Bewegungsprotokoll.

Diese Datei kennt kein Menü und keine Eingaben. Sie macht nur die Arbeit.
So kann man die Logik später auch mit einer Weboberfläche weiterverwenden.
"""

import sqlite3
from datetime import datetime

from datenbank import verbinden


class LagerFehler(Exception):
    """Eigener Fehlertyp für Probleme im Lager (z.B. zu wenig Bestand)."""


def artikel_anlegen(artikelnummer, bezeichnung, lagerplatz, bestand=0, mindestbestand=0):
    """Legt einen neuen Artikel an. Gibt einen Fehler, wenn die Nummer schon existiert."""
    if bestand < 0 or mindestbestand < 0:
        raise LagerFehler("Bestand und Mindestbestand dürfen nicht negativ sein.")

    try:
        with verbinden() as db:
            db.execute(
                "INSERT INTO artikel VALUES (?, ?, ?, ?, ?)",
                (artikelnummer, bezeichnung, lagerplatz, bestand, mindestbestand),
            )
            # Anfangsbestand auch im Protokoll festhalten
            if bestand > 0:
                _bewegung_speichern(db, artikelnummer, "Eingang", bestand)
    except sqlite3.IntegrityError:
        raise LagerFehler(f"Artikel {artikelnummer} existiert bereits.")


def artikel_holen(artikelnummer):
    """Gibt einen Artikel zurück oder None, wenn es ihn nicht gibt."""
    with verbinden() as db:
        return db.execute(
            "SELECT * FROM artikel WHERE artikelnummer = ?", (artikelnummer,)
        ).fetchone()


def wareneingang(artikelnummer, menge):
    """Erhöht den Bestand eines Artikels und protokolliert die Buchung."""
    _menge_pruefen(menge)
    with verbinden() as db:
        _artikel_muss_existieren(db, artikelnummer)
        db.execute(
            "UPDATE artikel SET bestand = bestand + ? WHERE artikelnummer = ?",
            (menge, artikelnummer),
        )
        _bewegung_speichern(db, artikelnummer, "Eingang", menge)


def warenausgang(artikelnummer, menge):
    """Verringert den Bestand. Bricht ab, wenn nicht genug Ware da ist."""
    _menge_pruefen(menge)
    with verbinden() as db:
        artikel = _artikel_muss_existieren(db, artikelnummer)
        if artikel["bestand"] < menge:
            raise LagerFehler(
                f"Nicht genug Bestand: {artikel['bestand']} Stück vorhanden, "
                f"{menge} Stück angefordert."
            )
        db.execute(
            "UPDATE artikel SET bestand = bestand - ? WHERE artikelnummer = ?",
            (menge, artikelnummer),
        )
        _bewegung_speichern(db, artikelnummer, "Ausgang", menge)


def bestandsliste():
    """Gibt alle Artikel sortiert nach Lagerplatz zurück."""
    with verbinden() as db:
        return db.execute("SELECT * FROM artikel ORDER BY lagerplatz").fetchall()


def nachbestellen():
    """Gibt alle Artikel zurück, deren Bestand unter dem Mindestbestand liegt."""
    with verbinden() as db:
        return db.execute(
            """SELECT *, (mindestbestand - bestand) AS fehlmenge
               FROM artikel
               WHERE bestand < mindestbestand
               ORDER BY fehlmenge DESC"""
        ).fetchall()


def bewegungsprotokoll(artikelnummer=None, anzahl=50):
    """Gibt die letzten Buchungen zurück, optional nur für einen Artikel."""
    with verbinden() as db:
        if artikelnummer:
            return db.execute(
                """SELECT b.*, a.bezeichnung FROM bewegungen b
                   JOIN artikel a USING (artikelnummer)
                   WHERE artikelnummer = ?
                   ORDER BY b.id DESC LIMIT ?""",
                (artikelnummer, anzahl),
            ).fetchall()
        return db.execute(
            """SELECT b.*, a.bezeichnung FROM bewegungen b
               JOIN artikel a USING (artikelnummer)
               ORDER BY b.id DESC LIMIT ?""",
            (anzahl,),
        ).fetchall()


# ---------- Hilfsfunktionen (mit _ am Anfang = nur für diese Datei gedacht) ----------

def _menge_pruefen(menge):
    if menge <= 0:
        raise LagerFehler("Die Menge muss grösser als 0 sein.")


def _artikel_muss_existieren(db, artikelnummer):
    artikel = db.execute(
        "SELECT * FROM artikel WHERE artikelnummer = ?", (artikelnummer,)
    ).fetchone()
    if artikel is None:
        raise LagerFehler(f"Artikel {artikelnummer} gibt es nicht.")
    return artikel


def _bewegung_speichern(db, artikelnummer, art, menge):
    zeitpunkt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO bewegungen (zeitpunkt, artikelnummer, art, menge) VALUES (?, ?, ?, ?)",
        (zeitpunkt, artikelnummer, art, menge),
    )
