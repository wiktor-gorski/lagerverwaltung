"""
test_lager.py
Automatische Tests: prüfen, ob die Lager-Logik richtig funktioniert.

Starten mit:  python -m unittest test_lager.py
"""

import tempfile
import unittest
from pathlib import Path

import datenbank
import lager
from lager import LagerFehler


class LagerTest(unittest.TestCase):

    def setUp(self):
        """Vor jedem Test: eine leere Test-Datenbank in einem temporären Ordner."""
        self.ordner = tempfile.TemporaryDirectory()
        datenbank.DB_PFAD = Path(self.ordner.name) / "test.db"
        datenbank.tabellen_anlegen()
        lager.artikel_anlegen("T-1", "Testartikel", "A-01-1", bestand=10, mindestbestand=5)

    def tearDown(self):
        self.ordner.cleanup()

    def test_wareneingang_erhoeht_bestand(self):
        lager.wareneingang("T-1", 5)
        self.assertEqual(lager.artikel_holen("T-1")["bestand"], 15)

    def test_warenausgang_verringert_bestand(self):
        lager.warenausgang("T-1", 4)
        self.assertEqual(lager.artikel_holen("T-1")["bestand"], 6)

    def test_zu_wenig_bestand_gibt_fehler(self):
        with self.assertRaises(LagerFehler):
            lager.warenausgang("T-1", 11)
        # Bestand darf sich nicht verändert haben
        self.assertEqual(lager.artikel_holen("T-1")["bestand"], 10)

    def test_doppelte_artikelnummer_gibt_fehler(self):
        with self.assertRaises(LagerFehler):
            lager.artikel_anlegen("T-1", "Nochmal", "A-01-2")

    def test_unbekannter_artikel_gibt_fehler(self):
        with self.assertRaises(LagerFehler):
            lager.wareneingang("GIBTSNICHT", 1)

    def test_menge_null_gibt_fehler(self):
        with self.assertRaises(LagerFehler):
            lager.wareneingang("T-1", 0)

    def test_nachbestellen_zeigt_artikel_unter_minimum(self):
        self.assertEqual(len(lager.nachbestellen()), 0)
        lager.warenausgang("T-1", 7)   # Bestand jetzt 3, Minimum 5
        liste = lager.nachbestellen()
        self.assertEqual(len(liste), 1)
        self.assertEqual(liste[0]["fehlmenge"], 2)

    def test_jede_buchung_wird_protokolliert(self):
        lager.wareneingang("T-1", 2)
        lager.warenausgang("T-1", 1)
        # Anfangsbestand + Eingang + Ausgang = 3 Einträge
        self.assertEqual(len(lager.bewegungsprotokoll("T-1")), 3)


if __name__ == "__main__":
    unittest.main()
