"""
export.py
Exportiert die Bestandsliste als Excel-Datei (.xlsx) oder als CSV-Datei.

Für Excel braucht es das Paket openpyxl:  pip install openpyxl
Ist es nicht installiert, wird automatisch eine CSV-Datei erstellt.
"""

import csv
from datetime import datetime
from pathlib import Path

from lager import bestandsliste

SPALTEN = ["Artikelnummer", "Bezeichnung", "Lagerplatz", "Bestand", "Mindestbestand", "Status"]


def _zeilen():
    """Bereitet die Daten für den Export vor."""
    for a in bestandsliste():
        status = "Nachbestellen" if a["bestand"] < a["mindestbestand"] else "OK"
        yield [a["artikelnummer"], a["bezeichnung"], a["lagerplatz"],
               a["bestand"], a["mindestbestand"], status]


def exportieren(ordner="."):
    """Erstellt die Export-Datei und gibt den Dateinamen zurück."""
    datum = datetime.now().strftime("%Y-%m-%d")
    try:
        return _als_excel(Path(ordner) / f"Bestandsliste {datum}.xlsx")
    except ImportError:
        return _als_csv(Path(ordner) / f"Bestandsliste {datum}.csv")


def _als_excel(pfad):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "Bestand"
    ws.append(SPALTEN)

    # Kopfzeile fett
    for zelle in ws[1]:
        zelle.font = Font(bold=True)

    rot = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    for zeile in _zeilen():
        ws.append(zeile)
        # Artikel unter Mindestbestand rot markieren
        if zeile[-1] == "Nachbestellen":
            for zelle in ws[ws.max_row]:
                zelle.fill = rot

    # Spaltenbreite an den Inhalt anpassen
    for spalte in ws.columns:
        breite = max(len(str(z.value)) for z in spalte) + 2
        ws.column_dimensions[spalte[0].column_letter].width = breite

    wb.save(pfad)
    return pfad


def _als_csv(pfad):
    # Semikolon und utf-8-sig, damit Excel in der Schweiz die Datei richtig öffnet
    with open(pfad, "w", newline="", encoding="utf-8-sig") as f:
        schreiber = csv.writer(f, delimiter=";")
        schreiber.writerow(SPALTEN)
        schreiber.writerows(_zeilen())
    return pfad
