import streamlit as st
import pandas as pd
import datetime as dt
import calendar
import json
import os
import uuid

DATEN_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gespeicherte_eingaben.json")
LOGO_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
BANNER_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.png")
DOKUMENTE_ORDNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pinnwand_dokumente")
os.makedirs(DOKUMENTE_ORDNER, exist_ok=True)

st.set_page_config(
    page_title="PatchEasy Prototyp",
    page_icon=LOGO_DATEI if os.path.exists(LOGO_DATEI) else "🧩",
    layout="wide",
)

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATSNAMEN = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]
ELTERNTEIL_1 = "Elternteil 1"
ELTERNTEIL_2 = "Elternteil 2"
VATER_FARBE = "#3D5A80"  # Standardfarbe fuer Elternteil 1 (Name beibehalten, um Aenderungen klein zu halten)
MUTTER_FARBE = "#E07A5F"  # Standardfarbe fuer Elternteil 2
FERIEN_FARBE = "#F2CC8F"


def anzeige(elternteil):
    """Gibt den von der Nutzerin frei waehlbaren Anzeigenamen fuer 'Elternteil 1'/'Elternteil 2'
    zurueck (Standard: der Name selbst). Alles andere (z. B. 'Wechselt woechentlich') wird
    unveraendert durchgereicht - so kann diese Funktion ueberall dort verwendet werden, wo
    Elternteil-Werte gemeinsam mit anderen Optionen angezeigt werden."""
    return st.session_state.get("rollennamen", {}).get(elternteil, elternteil)


def farbe(elternteil):
    """Gibt die von der Nutzerin frei waehlbare Farbe fuer 'Elternteil 1'/'Elternteil 2' zurueck."""
    standard = {ELTERNTEIL_1: VATER_FARBE, ELTERNTEIL_2: MUTTER_FARBE}
    return st.session_state.get("rollenfarben", {}).get(elternteil, standard.get(elternteil, "#888888"))


def euro(betrag):
    """Formatiert einen Betrag im deutschen Format, z. B. 1234.5 -> '1.234,50 €'."""
    return f"{betrag:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def berechne_finanzsaldo(ausgaben, ausgleichszahlungen):
    """Positiver Saldo: Elternteil 2 schuldet Elternteil 1. Negativer Saldo: Elternteil 1 schuldet Elternteil 2."""
    saldo = 0.0
    for a in ausgaben:
        vater_anteil = a["betrag"] * a["anteil_vater_pct"] / 100
        mutter_anteil = a["betrag"] - vater_anteil
        if a["bezahlt_von"] == "Elternteil 1":
            saldo += mutter_anteil
        else:
            saldo -= vater_anteil
    for z in ausgleichszahlungen:
        if z["von"] == "Elternteil 1":
            saldo += z["betrag"]
        else:
            saldo -= z["betrag"]
    return saldo

# Offizielle Schulferien 2026/2027, Quelle: schulferien-deutschland.org (Stand: 08/2026).
# Bei wichtigen Entscheidungen bitte gegen kmk.org pruefen - Angaben ohne Gewaehr.
FERIEN_DATEN = {
    "Baden-Württemberg": [
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 11)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 6, 5)),
        ("Sommerferien 2026", dt.date(2026, 7, 30), dt.date(2026, 9, 12)),
        ("Herbstferien 2026", dt.date(2026, 10, 26), dt.date(2026, 10, 30)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 9)),
        ("Osterferien 2027", dt.date(2027, 3, 30), dt.date(2027, 4, 3)),
        ("Pfingstferien 2027", dt.date(2027, 5, 18), dt.date(2027, 5, 29)),
        ("Sommerferien 2027", dt.date(2027, 7, 29), dt.date(2027, 9, 11)),
        ("Herbstferien 2027", dt.date(2027, 11, 2), dt.date(2027, 11, 6)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 23), dt.date(2028, 1, 8)),
    ],
    "Bayern": [
        ("Winterferien 2026", dt.date(2026, 2, 16), dt.date(2026, 2, 20)),
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 10)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 6, 5)),
        ("Sommerferien 2026", dt.date(2026, 8, 3), dt.date(2026, 9, 14)),
        ("Herbstferien 2026", dt.date(2026, 11, 2), dt.date(2026, 11, 6)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 24), dt.date(2027, 1, 8)),
        ("Winterferien 2027", dt.date(2027, 2, 8), dt.date(2027, 2, 12)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 2)),
        ("Pfingstferien 2027", dt.date(2027, 5, 18), dt.date(2027, 5, 28)),
        ("Sommerferien 2027", dt.date(2027, 8, 2), dt.date(2027, 9, 13)),
        ("Herbstferien 2027", dt.date(2027, 11, 2), dt.date(2027, 11, 5)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 24), dt.date(2028, 1, 7)),
    ],
    "Berlin": [
        ("Winterferien 2026", dt.date(2026, 2, 2), dt.date(2026, 2, 7)),
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 10)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 5, 26)),
        ("Sommerferien 2026", dt.date(2026, 7, 9), dt.date(2026, 8, 22)),
        ("Herbstferien 2026", dt.date(2026, 10, 19), dt.date(2026, 10, 31)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 2)),
        ("Winterferien 2027", dt.date(2027, 2, 1), dt.date(2027, 2, 6)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 2)),
        ("Pfingstferien 2027", dt.date(2027, 5, 18), dt.date(2027, 5, 19)),
        ("Sommerferien 2027", dt.date(2027, 7, 1), dt.date(2027, 8, 14)),
        ("Herbstferien 2027", dt.date(2027, 10, 11), dt.date(2027, 10, 23)),
        ("Weihnachtsferien 2027", dt.date(2027, 12, 22), dt.date(2027, 12, 31)),
    ],
    "Brandenburg": [
        ("Winterferien 2026", dt.date(2026, 2, 2), dt.date(2026, 2, 7)),
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 10)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 5, 26)),
        ("Sommerferien 2026", dt.date(2026, 7, 9), dt.date(2026, 8, 22)),
        ("Herbstferien 2026", dt.date(2026, 10, 19), dt.date(2026, 10, 30)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 2)),
        ("Winterferien 2027", dt.date(2027, 2, 1), dt.date(2027, 2, 6)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 3)),
        ("Pfingstferien 2027", dt.date(2027, 5, 18), dt.date(2027, 5, 18)),
        ("Sommerferien 2027", dt.date(2027, 7, 1), dt.date(2027, 8, 14)),
        ("Herbstferien 2027", dt.date(2027, 10, 11), dt.date(2027, 10, 23)),
        ("Weihnachtsferien 2027", dt.date(2027, 12, 23), dt.date(2027, 12, 31)),
    ],
    "Bremen": [
        ("Winterferien 2026", dt.date(2026, 2, 2), dt.date(2026, 2, 3)),
        ("Osterferien 2026", dt.date(2026, 3, 23), dt.date(2026, 4, 7)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 5, 26)),
        ("Sommerferien 2026", dt.date(2026, 7, 2), dt.date(2026, 8, 12)),
        ("Herbstferien 2026", dt.date(2026, 10, 12), dt.date(2026, 10, 24)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 9)),
        ("Winterferien 2027", dt.date(2027, 2, 1), dt.date(2027, 2, 2)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 3)),
        ("Pfingstferien 2027", dt.date(2027, 5, 18), dt.date(2027, 5, 18)),
        ("Sommerferien 2027", dt.date(2027, 7, 8), dt.date(2027, 8, 18)),
        ("Herbstferien 2027", dt.date(2027, 10, 18), dt.date(2027, 10, 30)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 23), dt.date(2028, 1, 8)),
    ],
    "Hamburg": [
        ("Winterferien 2026", dt.date(2026, 1, 30), dt.date(2026, 1, 30)),
        ("Osterferien 2026", dt.date(2026, 3, 2), dt.date(2026, 3, 13)),
        ("Pfingstferien 2026", dt.date(2026, 5, 11), dt.date(2026, 5, 15)),
        ("Sommerferien 2026", dt.date(2026, 7, 9), dt.date(2026, 8, 19)),
        ("Herbstferien 2026", dt.date(2026, 10, 19), dt.date(2026, 10, 30)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 21), dt.date(2027, 1, 1)),
        ("Winterferien 2027", dt.date(2027, 1, 29), dt.date(2027, 1, 29)),
        ("Osterferien 2027", dt.date(2027, 3, 1), dt.date(2027, 3, 12)),
        ("Pfingstferien 2027", dt.date(2027, 5, 7), dt.date(2027, 5, 15)),
        ("Sommerferien 2027", dt.date(2027, 7, 1), dt.date(2027, 8, 11)),
        ("Herbstferien 2027", dt.date(2027, 10, 11), dt.date(2027, 10, 22)),
        ("Weihnachtsferien 2027", dt.date(2027, 12, 20), dt.date(2027, 12, 31)),
    ],
    "Hessen": [
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 10)),
        ("Sommerferien 2026", dt.date(2026, 6, 29), dt.date(2026, 8, 7)),
        ("Herbstferien 2026", dt.date(2026, 10, 5), dt.date(2026, 10, 17)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 12)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 2)),
        ("Sommerferien 2027", dt.date(2027, 6, 28), dt.date(2027, 8, 6)),
        ("Herbstferien 2027", dt.date(2027, 10, 4), dt.date(2027, 10, 16)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 23), dt.date(2028, 1, 11)),
    ],
    "Mecklenburg-Vorpommern": [
        ("Winterferien 2026", dt.date(2026, 2, 9), dt.date(2026, 2, 20)),
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 8)),
        ("Pfingstferien 2026", dt.date(2026, 5, 22), dt.date(2026, 5, 26)),
        ("Sommerferien 2026", dt.date(2026, 7, 13), dt.date(2026, 8, 22)),
        ("Herbstferien 2026", dt.date(2026, 10, 15), dt.date(2026, 10, 24)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 21), dt.date(2027, 1, 2)),
        ("Winterferien 2027", dt.date(2027, 2, 8), dt.date(2027, 2, 19)),
        ("Osterferien 2027", dt.date(2027, 3, 24), dt.date(2027, 4, 2)),
        ("Pfingstferien 2027", dt.date(2027, 5, 14), dt.date(2027, 5, 18)),
        ("Sommerferien 2027", dt.date(2027, 7, 5), dt.date(2027, 8, 14)),
        ("Herbstferien 2027", dt.date(2027, 10, 14), dt.date(2027, 10, 23)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 22), dt.date(2028, 1, 4)),
    ],
    "Niedersachsen": [
        ("Winterferien 2026", dt.date(2026, 2, 2), dt.date(2026, 2, 3)),
        ("Osterferien 2026", dt.date(2026, 3, 23), dt.date(2026, 4, 7)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 5, 26)),
        ("Sommerferien 2026", dt.date(2026, 7, 2), dt.date(2026, 8, 12)),
        ("Herbstferien 2026", dt.date(2026, 10, 12), dt.date(2026, 10, 24)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 9)),
        ("Winterferien 2027", dt.date(2027, 2, 1), dt.date(2027, 2, 2)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 3)),
        ("Pfingstferien 2027", dt.date(2027, 5, 18), dt.date(2027, 5, 18)),
        ("Sommerferien 2027", dt.date(2027, 7, 8), dt.date(2027, 8, 18)),
        ("Herbstferien 2027", dt.date(2027, 10, 16), dt.date(2027, 10, 30)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 23), dt.date(2028, 1, 8)),
    ],
    "Nordrhein-Westfalen": [
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 11)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 5, 26)),
        ("Sommerferien 2026", dt.date(2026, 7, 20), dt.date(2026, 9, 1)),
        ("Herbstferien 2026", dt.date(2026, 10, 17), dt.date(2026, 10, 31)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 6)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 3)),
        ("Pfingstferien 2027", dt.date(2027, 5, 18), dt.date(2027, 5, 18)),
        ("Sommerferien 2027", dt.date(2027, 7, 19), dt.date(2027, 8, 31)),
        ("Herbstferien 2027", dt.date(2027, 10, 23), dt.date(2027, 11, 6)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 24), dt.date(2028, 1, 8)),
    ],
    "Rheinland-Pfalz": [
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 10)),
        ("Sommerferien 2026", dt.date(2026, 6, 29), dt.date(2026, 8, 7)),
        ("Herbstferien 2026", dt.date(2026, 10, 5), dt.date(2026, 10, 16)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 8)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 2)),
        ("Sommerferien 2027", dt.date(2027, 6, 28), dt.date(2027, 8, 6)),
        ("Herbstferien 2027", dt.date(2027, 10, 4), dt.date(2027, 10, 15)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 23), dt.date(2028, 1, 7)),
    ],
    "Saarland": [
        ("Winterferien 2026", dt.date(2026, 2, 16), dt.date(2026, 2, 20)),
        ("Osterferien 2026", dt.date(2026, 4, 7), dt.date(2026, 4, 17)),
        ("Sommerferien 2026", dt.date(2026, 6, 29), dt.date(2026, 8, 7)),
        ("Herbstferien 2026", dt.date(2026, 10, 5), dt.date(2026, 10, 16)),
        ("Weihnachtsferien 2026", dt.date(2026, 12, 21), dt.date(2026, 12, 31)),
        ("Winterferien 2027", dt.date(2027, 2, 8), dt.date(2027, 2, 12)),
        ("Osterferien 2027", dt.date(2027, 3, 30), dt.date(2027, 4, 9)),
        ("Sommerferien 2027", dt.date(2027, 6, 28), dt.date(2027, 8, 6)),
        ("Herbstferien 2027", dt.date(2027, 10, 4), dt.date(2027, 10, 15)),
        ("Weihnachtsferien 2027", dt.date(2027, 12, 20), dt.date(2027, 12, 31)),
    ],
    "Sachsen": [
        ("Winterferien 2026", dt.date(2026, 2, 9), dt.date(2026, 2, 21)),
        ("Osterferien 2026", dt.date(2026, 4, 3), dt.date(2026, 4, 10)),
        ("Sommerferien 2026", dt.date(2026, 7, 4), dt.date(2026, 8, 14)),
        ("Herbstferien 2026", dt.date(2026, 10, 12), dt.date(2026, 10, 24)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 2)),
        ("Winterferien 2027", dt.date(2027, 2, 8), dt.date(2027, 2, 19)),
        ("Osterferien 2027", dt.date(2027, 3, 26), dt.date(2027, 4, 2)),
        ("Pfingstferien 2027", dt.date(2027, 5, 15), dt.date(2027, 5, 18)),
        ("Sommerferien 2027", dt.date(2027, 7, 10), dt.date(2027, 8, 20)),
        ("Herbstferien 2027", dt.date(2027, 10, 11), dt.date(2027, 10, 23)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 23), dt.date(2028, 1, 1)),
    ],
    "Sachsen-Anhalt": [
        ("Winterferien 2026", dt.date(2026, 1, 31), dt.date(2026, 2, 6)),
        ("Osterferien 2026", dt.date(2026, 3, 30), dt.date(2026, 4, 4)),
        ("Pfingstferien 2026", dt.date(2026, 5, 26), dt.date(2026, 5, 29)),
        ("Sommerferien 2026", dt.date(2026, 7, 4), dt.date(2026, 8, 14)),
        ("Herbstferien 2026", dt.date(2026, 10, 19), dt.date(2026, 10, 30)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 21), dt.date(2027, 1, 2)),
        ("Winterferien 2027", dt.date(2027, 2, 1), dt.date(2027, 2, 6)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 3, 27)),
        ("Pfingstferien 2027", dt.date(2027, 5, 15), dt.date(2027, 5, 22)),
        ("Sommerferien 2027", dt.date(2027, 7, 10), dt.date(2027, 8, 20)),
        ("Herbstferien 2027", dt.date(2027, 10, 18), dt.date(2027, 10, 23)),
        ("Weihnachtsferien 2027", dt.date(2027, 12, 20), dt.date(2027, 12, 31)),
    ],
    "Schleswig-Holstein": [
        ("Winterferien 2026", dt.date(2026, 2, 2), dt.date(2026, 2, 3)),
        ("Osterferien 2026", dt.date(2026, 3, 26), dt.date(2026, 4, 10)),
        ("Pfingstferien 2026", dt.date(2026, 5, 15), dt.date(2026, 5, 15)),
        ("Sommerferien 2026", dt.date(2026, 7, 4), dt.date(2026, 8, 15)),
        ("Herbstferien 2026", dt.date(2026, 10, 12), dt.date(2026, 10, 24)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 21), dt.date(2027, 1, 6)),
        ("Winterferien 2027", dt.date(2027, 2, 1), dt.date(2027, 2, 2)),
        ("Osterferien 2027", dt.date(2027, 3, 30), dt.date(2027, 4, 10)),
        ("Pfingstferien 2027", dt.date(2027, 5, 7), dt.date(2027, 5, 7)),
        ("Sommerferien 2027", dt.date(2027, 7, 3), dt.date(2027, 8, 14)),
        ("Herbstferien 2027", dt.date(2027, 10, 11), dt.date(2027, 10, 23)),
        ("Weihnachtsferien 2027/28", dt.date(2027, 12, 23), dt.date(2028, 1, 8)),
    ],
    "Thüringen": [
        ("Winterferien 2026", dt.date(2026, 2, 16), dt.date(2026, 2, 21)),
        ("Osterferien 2026", dt.date(2026, 4, 7), dt.date(2026, 4, 17)),
        ("Pfingstferien 2026", dt.date(2026, 5, 15), dt.date(2026, 5, 15)),
        ("Sommerferien 2026", dt.date(2026, 7, 4), dt.date(2026, 8, 14)),
        ("Herbstferien 2026", dt.date(2026, 10, 12), dt.date(2026, 10, 24)),
        ("Weihnachtsferien 2026/27", dt.date(2026, 12, 23), dt.date(2027, 1, 2)),
        ("Winterferien 2027", dt.date(2027, 2, 1), dt.date(2027, 2, 6)),
        ("Osterferien 2027", dt.date(2027, 3, 22), dt.date(2027, 4, 3)),
        ("Pfingstferien 2027", dt.date(2027, 5, 7), dt.date(2027, 5, 7)),
        ("Sommerferien 2027", dt.date(2027, 7, 10), dt.date(2027, 8, 20)),
        ("Herbstferien 2027", dt.date(2027, 10, 9), dt.date(2027, 10, 23)),
        ("Weihnachtsferien 2027", dt.date(2027, 12, 23), dt.date(2027, 12, 31)),
    ],
}

FEIERTAGE_DATEN = {
    "Baden-Württemberg": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Heilige Drei Könige", dt.date(2026, 1, 6)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Fronleichnam", dt.date(2026, 6, 4)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Allerheiligen", dt.date(2026, 11, 1)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Heilige Drei Könige", dt.date(2027, 1, 6)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Fronleichnam", dt.date(2027, 5, 27)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Allerheiligen", dt.date(2027, 11, 1)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Bayern": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Heilige Drei Könige", dt.date(2026, 1, 6)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Fronleichnam", dt.date(2026, 6, 4)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Allerheiligen", dt.date(2026, 11, 1)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Heilige Drei Könige", dt.date(2027, 1, 6)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Fronleichnam", dt.date(2027, 5, 27)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Allerheiligen", dt.date(2027, 11, 1)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Berlin": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Internationaler Frauentag", dt.date(2026, 3, 8)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Internationaler Frauentag", dt.date(2027, 3, 8)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Brandenburg": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostersonntag", dt.date(2026, 4, 5)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstsonntag", dt.date(2026, 5, 24)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostersonntag", dt.date(2027, 3, 28)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstsonntag", dt.date(2027, 5, 16)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Bremen": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Hamburg": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Hessen": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Fronleichnam", dt.date(2026, 6, 4)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Fronleichnam", dt.date(2027, 5, 27)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Mecklenburg-Vorpommern": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Internationaler Frauentag", dt.date(2026, 3, 8)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Internationaler Frauentag", dt.date(2027, 3, 8)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Niedersachsen": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Nordrhein-Westfalen": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Fronleichnam", dt.date(2026, 6, 4)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Allerheiligen", dt.date(2026, 11, 1)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Fronleichnam", dt.date(2027, 5, 27)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Allerheiligen", dt.date(2027, 11, 1)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Rheinland-Pfalz": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Fronleichnam", dt.date(2026, 6, 4)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Allerheiligen", dt.date(2026, 11, 1)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Fronleichnam", dt.date(2027, 5, 27)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Allerheiligen", dt.date(2027, 11, 1)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Saarland": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Fronleichnam", dt.date(2026, 6, 4)),
        ("Mariä Himmelfahrt", dt.date(2026, 8, 15)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Allerheiligen", dt.date(2026, 11, 1)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Fronleichnam", dt.date(2027, 5, 27)),
        ("Mariä Himmelfahrt", dt.date(2027, 8, 15)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Allerheiligen", dt.date(2027, 11, 1)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Sachsen": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("Buß- und Bettag", dt.date(2026, 11, 18)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("Buß- und Bettag", dt.date(2027, 11, 17)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Sachsen-Anhalt": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Heilige Drei Könige", dt.date(2026, 1, 6)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Heilige Drei Könige", dt.date(2027, 1, 6)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Schleswig-Holstein": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
    "Thüringen": [
        ("Neujahr", dt.date(2026, 1, 1)),
        ("Karfreitag", dt.date(2026, 4, 3)),
        ("Ostermontag", dt.date(2026, 4, 6)),
        ("Tag der Arbeit", dt.date(2026, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2026, 5, 14)),
        ("Pfingstmontag", dt.date(2026, 5, 25)),
        ("Weltkindertag", dt.date(2026, 9, 20)),
        ("Tag der Deutschen Einheit", dt.date(2026, 10, 3)),
        ("Reformationstag", dt.date(2026, 10, 31)),
        ("1. Weihnachtstag", dt.date(2026, 12, 25)),
        ("2. Weihnachtstag", dt.date(2026, 12, 26)),
        ("Neujahr", dt.date(2027, 1, 1)),
        ("Karfreitag", dt.date(2027, 3, 26)),
        ("Ostermontag", dt.date(2027, 3, 29)),
        ("Tag der Arbeit", dt.date(2027, 5, 1)),
        ("Christi Himmelfahrt", dt.date(2027, 5, 6)),
        ("Pfingstmontag", dt.date(2027, 5, 17)),
        ("Weltkindertag", dt.date(2027, 9, 20)),
        ("Tag der Deutschen Einheit", dt.date(2027, 10, 3)),
        ("Reformationstag", dt.date(2027, 10, 31)),
        ("1. Weihnachtstag", dt.date(2027, 12, 25)),
        ("2. Weihnachtstag", dt.date(2027, 12, 26)),
    ],
}

# ---------- Session State (Rollennamen/-farben muessen vor dem Header feststehen) ----------
st.session_state.setdefault("rollennamen", {ELTERNTEIL_1: ELTERNTEIL_1, ELTERNTEIL_2: ELTERNTEIL_2})
st.session_state.setdefault("rollenfarben", {ELTERNTEIL_1: VATER_FARBE, ELTERNTEIL_2: MUTTER_FARBE})

# ---------- Globales Design-System ----------
# Die Grundfarben/Schrift kommen aus .streamlit/config.toml (native Streamlit-Themes,
# faerbt auch native Widgets wie Radio/Slider/Checkbox/Multiselect zuverlaessig ein).
# Hier nur die Feinheiten, die ueber Theme-Optionen nicht erreichbar sind.
st.markdown(
    f"""
    <style>
    :root {{
        --pe-purple: #534AB7;
        --pe-purple-dark: #3F3890;
        --pe-teal: #0F5C66;
        --pe-card: #FFFFFF;
        --pe-border: #D9D4EC;
        --pe-ink-soft: #6E6A80;
        --pe-radius-md: 14px;
        --pe-shadow: 0 4px 16px rgba(83,74,183,0.08), 0 1px 3px rgba(44,42,61,0.05);
    }}

    /* Aktiver Menuepunkt oben: Markenfarbe statt neutralem Grau, damit sofort klar ist,
       wo man sich befindet. */
    a[data-testid="stTopNavLink"][aria-current="page"] {{
        background: var(--pe-purple) !important;
        box-shadow: 0 3px 10px rgba(83,74,183,0.30) !important;
    }}
    a[data-testid="stTopNavLink"][aria-current="page"] [data-testid="stIconMaterial"],
    a[data-testid="stTopNavLink"][aria-current="page"] [data-testid="stMarkdownContainer"] p {{
        color: #ffffff !important;
    }}
    a[data-testid="stTopNavLink"]:not([aria-current="page"]):hover {{
        background: rgba(83,74,183,0.08) !important;
    }}

    /* Kennzahlen (st.metric) als dezente Karten statt frei schwebender Zahlen. */
    div[data-testid="stMetric"] {{
        background: var(--pe-card);
        border: 1px solid var(--pe-border);
        border-radius: var(--pe-radius-md);
        padding: 0.9rem 1.1rem 0.75rem 1.1rem;
        box-shadow: var(--pe-shadow);
    }}
    div[data-testid="stMetricLabel"] p {{ color: var(--pe-ink-soft) !important; }}

    /* Karten-Look fuer Container mit einem Key, der mit "pe_card_" beginnt - wiederverwendbar
       auf allen Seiten (z. B. Finanzen-Zeilen), Substring-Selektor wie beim Pinnwand-Board. */
    div[class*="st-key-pe_card_"] {{
        background: var(--pe-card) !important;
        border: 1px solid var(--pe-border) !important;
        border-radius: var(--pe-radius-md) !important;
        box-shadow: 0 1px 4px rgba(44,42,61,0.05) !important;
        padding: 0.65rem 1rem !important;
        margin-bottom: 0.55rem !important;
    }}

    /* Wunsch-/Verzicht-Buttons im Tages-Dialog: Farbe des jeweiligen Elternteils statt
       neutralem Lila - macht auf einen Blick klar, wer gemeint ist. */
    .st-key-tag_panel_wv button, .st-key-tag_panel_vv button {{
        border-color: {farbe(ELTERNTEIL_1)} !important;
        color: {farbe(ELTERNTEIL_1)} !important;
    }}
    .st-key-tag_panel_wv button:hover, .st-key-tag_panel_vv button:hover {{
        background: {farbe(ELTERNTEIL_1)} !important;
        color: #fff !important;
    }}
    .st-key-tag_panel_wm button, .st-key-tag_panel_vm button {{
        border-color: {farbe(ELTERNTEIL_2)} !important;
        color: {farbe(ELTERNTEIL_2)} !important;
    }}
    .st-key-tag_panel_wm button:hover, .st-key-tag_panel_vm button:hover {{
        background: {farbe(ELTERNTEIL_2)} !important;
        color: #fff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if os.path.exists(BANNER_DATEI):
    st.image(BANNER_DATEI, width=340)
else:
    st.markdown(
        """
        <div style="font-size:2.1rem;font-weight:800;letter-spacing:-0.03em;line-height:1.15;">
          PatchEasy
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown(
    f"""
    <div style="font-size:0.95rem;font-weight:600;color:var(--pe-ink-soft);margin-top:2px;margin-bottom:14px;
                display:flex;align-items:center;flex-wrap:wrap;gap:0.4rem;">
      <span>Funktionsprototyp</span>
      <span style="display:inline-block;padding:2px 11px;border-radius:999px;
                   background:{farbe(ELTERNTEIL_1)};color:white;font-size:0.72rem;font-weight:700;
                   box-shadow:0 2px 5px rgba(0,0,0,0.12);">{anzeige(ELTERNTEIL_1)}</span>
      <span style="display:inline-block;padding:2px 11px;border-radius:999px;
                   background:{farbe(ELTERNTEIL_2)};color:white;font-size:0.72rem;font-weight:700;
                   box-shadow:0 2px 5px rgba(0,0,0,0.12);">{anzeige(ELTERNTEIL_2)}</span>
    </div>
    """,
    unsafe_allow_html=True,
)
for key in ["wunsch_vater", "verzicht_vater", "wunsch_mutter", "verzicht_mutter"]:
    st.session_state.setdefault(key, [])
st.session_state.setdefault("ferien", [])  # list of dicts: name, start, end
st.session_state.setdefault("feiertage", [])  # list of dicts: name, datum (informativ, ohne Einfluss auf die Zuordnung)
st.session_state.setdefault("feste_wochentage", {})  # {Wochentagsname: "Elternteil 1"/"Elternteil 2"}
st.session_state.setdefault("wechselmodell", "block")  # "block" oder "wochenplan"
st.session_state.setdefault(
    "wochenplan",
    {tag: "Wechselt wöchentlich" for tag in WOCHENTAGE},
)  # {Wochentagsname: "Elternteil 1"/"Elternteil 2"/"Wechselt wöchentlich"}
st.session_state.setdefault("wechsel_start_parent", "Elternteil 1")
st.session_state.setdefault("wechselzeit", dt.time(18, 0))
st.session_state.setdefault("wechselzeit_ausnahmen", {})  # {datetime.date: datetime.time} - abweichende Uebergabezeit an einzelnen Tagen
st.session_state.setdefault("kinder", ["Kind 1"])  # Namen der Kinder, fuer die Ausgaben erfasst werden koennen
st.session_state.setdefault("ausgaben", [])  # [{"id","datum","beschreibung","betrag","bezahlt_von","anteil_vater_pct","kind"}]
st.session_state.setdefault("ausgleichszahlungen", [])  # [{"id","datum","von","betrag"}] - direkte Ausgleichszahlungen zwischen den Eltern
st.session_state.setdefault("dokumente", [])  # [{"id","titel","dateiname","original_name","hochgeladen_am"}]
st.session_state.setdefault("notfallkontakte", [])  # [{"id","name","rolle","telefon","notiz"}]
st.session_state.setdefault("uebergabe_checkliste", [])  # [{"id","text","erledigt"}] - was beim naechsten Wechsel mit soll
st.session_state.setdefault("pw_doku_form_key", 0)  # zaehlt hoch, um Titel-Feld + file_uploader nach dem Speichern zurueckzusetzen
st.session_state.setdefault("nk_form_key", 0)  # zaehlt hoch, um das Kontaktformular nach dem Speichern zurueckzusetzen
st.session_state.setdefault("checkliste_form_key", 0)  # zaehlt hoch, um das Eingabefeld nach dem Hinzufuegen zurueckzusetzen
st.session_state.setdefault("checkliste_reset_key", 0)  # zaehlt hoch, um alle Haekchen ueber "Zuruecksetzen" zu leeren


def lade_gespeicherte_daten():
    """Laedt beim allerersten Aufruf pro Prozess gespeicherte Eingaben aus der JSON-Datei
    in den session_state, BEVOR die Widgets erzeugt werden. Ueberschreibt spaetere
    Live-Aenderungen der Nutzerin nicht (nur einmal pro Prozessstart aktiv)."""
    if st.session_state.get("_daten_geladen"):
        return
    st.session_state["_daten_geladen"] = True
    if not os.path.exists(DATEN_DATEI):
        return
    try:
        with open(DATEN_DATEI, "r", encoding="utf-8") as f:
            daten = json.load(f)
    except Exception:
        return

    def _migriere_elternteil(wert):
        """Bildet Werte ab, die noch von vor der Umbenennung 'Vater'/'Mutter' zu
        'Elternteil 1'/'Elternteil 2' stammen, auf die neuen Bezeichner ab - damit
        bereits gespeicherte Daten (auch bei bestehenden Beta-Testerinnen) nicht
        stillschweigend auf einen Standardwert zurueckfallen."""
        return {"Vater": ELTERNTEIL_1, "Mutter": ELTERNTEIL_2}.get(wert, wert)

    if "rollennamen" in daten and isinstance(daten["rollennamen"], dict):
        _rn = st.session_state["rollennamen"].copy()
        for _k in (ELTERNTEIL_1, ELTERNTEIL_2):
            if isinstance(daten["rollennamen"].get(_k), str) and daten["rollennamen"][_k].strip():
                _rn[_k] = daten["rollennamen"][_k]
        st.session_state["rollennamen"] = _rn
    if "rollenfarben" in daten and isinstance(daten["rollenfarben"], dict):
        _rf = st.session_state["rollenfarben"].copy()
        for _k in (ELTERNTEIL_1, ELTERNTEIL_2):
            if isinstance(daten["rollenfarben"].get(_k), str) and daten["rollenfarben"][_k].startswith("#"):
                _rf[_k] = daten["rollenfarben"][_k]
        st.session_state["rollenfarben"] = _rf

    if "start_date" in daten:
        st.session_state["start_date_input"] = dt.date.fromisoformat(daten["start_date"])
    if "end_date" in daten:
        st.session_state["end_date_input"] = dt.date.fromisoformat(daten["end_date"])
    if "ziel_vater_pct" in daten:
        st.session_state["ziel_vater_slider"] = daten["ziel_vater_pct"]
        # Zusaetzlich in einem eigenen, nicht an ein Widget gebundenen Key merken: Streamlit
        # verwirft den Wert eines Widget-Keys, wenn das Widget (hier: der Zielverteilung-
        # Slider) in einem Skriptdurchlauf nicht gezeichnet wird - z. B. weil gerade der
        # Wochenplan-Modus aktiv ist. Ohne diesen Schatten-Key wuerde ein Moduswechsel den
        # zuletzt eingestellten Blockweise-Zielwert sonst stillschweigend zuruecksetzen.
        st.session_state["ziel_vater_persistent"] = daten["ziel_vater_pct"]
    if "wechseltag" in daten and daten["wechseltag"] in WOCHENTAGE:
        st.session_state["wechseltag_auswahl"] = daten["wechseltag"]
        st.session_state["wechseltag_persistent"] = daten["wechseltag"]
    for key in ["wunsch_vater", "verzicht_vater", "wunsch_mutter", "verzicht_mutter"]:
        if key in daten:
            eintraege = []
            for x in daten[key]:
                if isinstance(x, dict):
                    eintraege.append({"datum": dt.date.fromisoformat(x["datum"]), "notiz": x.get("notiz", "")})
                else:
                    # Altes Format (nur Datum ohne Notiz) - abwaertskompatibel einlesen
                    eintraege.append({"datum": dt.date.fromisoformat(x), "notiz": ""})
            st.session_state[key] = eintraege
    if "ferien" in daten:
        st.session_state["ferien"] = [
            {
                "name": f["name"],
                "start": dt.date.fromisoformat(f["start"]),
                "end": dt.date.fromisoformat(f["end"]),
                "regel": f.get("regel", "rotation"),
                "erste_haelfte": _migriere_elternteil(f.get("erste_haelfte", ELTERNTEIL_1)),
                "ferien_wechseltag": f.get("ferien_wechseltag", WOCHENTAGE[2]),
            }
            for f in daten["ferien"]
        ]
    if "feiertage" in daten:
        st.session_state["feiertage"] = [
            {"name": f["name"], "datum": dt.date.fromisoformat(f["datum"])}
            for f in daten["feiertage"]
        ]
    if "feste_wochentage" in daten:
        fw = {
            k: _migriere_elternteil(v) for k, v in daten["feste_wochentage"].items()
            if k in WOCHENTAGE and _migriere_elternteil(v) in (ELTERNTEIL_1, ELTERNTEIL_2)
        }
        st.session_state["feste_wochentage"] = fw
        # Widget-Keys VOR der Erzeugung der Selectboxen setzen, damit sie den gespeicherten Wert uebernehmen
        for tag in WOCHENTAGE:
            if tag in fw:
                st.session_state[f"fw_{tag}"] = fw[tag]
    if "wechselmodell" in daten and daten["wechselmodell"] in ("block", "wochenplan"):
        st.session_state["wechselmodell"] = daten["wechselmodell"]
        st.session_state["wechselmodell_auswahl"] = (
            "Wochenplan (fester Rhythmus pro Wochentag)" if daten["wechselmodell"] == "wochenplan"
            else "Blockweise (Zielverteilung + Wechseltag)"
        )
    if "wochenplan" in daten:
        wp = {}
        for k, v in daten["wochenplan"].items():
            if k not in WOCHENTAGE:
                continue
            _v = v if v == "Wechselt wöchentlich" else _migriere_elternteil(v)
            if _v in (ELTERNTEIL_1, ELTERNTEIL_2, "Wechselt wöchentlich"):
                wp[k] = _v
        st.session_state["wochenplan"] = {**st.session_state["wochenplan"], **wp}
        for tag in WOCHENTAGE:
            if tag in wp:
                st.session_state[f"wp_{tag}"] = wp[tag]
    if "wechsel_start_parent" in daten and _migriere_elternteil(daten["wechsel_start_parent"]) in (ELTERNTEIL_1, ELTERNTEIL_2):
        _wsp = _migriere_elternteil(daten["wechsel_start_parent"])
        st.session_state["wechsel_start_parent"] = _wsp
        st.session_state["wechsel_start_parent_auswahl"] = _wsp
    if "wechselzeit" in daten:
        try:
            _wz = dt.time.fromisoformat(daten["wechselzeit"])
            st.session_state["wechselzeit"] = _wz
            st.session_state["wechselzeit_auswahl"] = _wz
        except Exception:
            pass
    if "wechselzeit_ausnahmen" in daten:
        _wza = {}
        for _iso, _zeit in daten["wechselzeit_ausnahmen"].items():
            try:
                _wza[dt.date.fromisoformat(_iso)] = dt.time.fromisoformat(_zeit)
            except Exception:
                continue
        st.session_state["wechselzeit_ausnahmen"] = _wza
    if "kinder" in daten:
        _kinder_geladen = [k for k in daten["kinder"] if isinstance(k, str) and k.strip()]
        if _kinder_geladen:
            st.session_state["kinder"] = _kinder_geladen
    if "ausgaben" in daten:
        st.session_state["ausgaben"] = [
            {
                "id": a.get("id") or uuid.uuid4().hex[:8],
                "datum": dt.date.fromisoformat(a["datum"]),
                "beschreibung": a.get("beschreibung", ""),
                "betrag": float(a.get("betrag", 0)),
                "bezahlt_von": _migriere_elternteil(a.get("bezahlt_von")) if _migriere_elternteil(a.get("bezahlt_von")) in (ELTERNTEIL_1, ELTERNTEIL_2) else ELTERNTEIL_1,
                "anteil_vater_pct": float(a.get("anteil_vater_pct", 50)),
                # Abwaertskompatibel: alte Eintraege ohne "kind" (aus einer Version vor der
                # Mehrkind-Unterstuetzung) gelten automatisch fuer alle aktuell erfassten Kinder.
                "kind": a["kind"] if a.get("kind") else list(st.session_state["kinder"]),
            }
            for a in daten["ausgaben"]
        ]
    if "ausgleichszahlungen" in daten:
        st.session_state["ausgleichszahlungen"] = [
            {
                "id": z.get("id") or uuid.uuid4().hex[:8],
                "datum": dt.date.fromisoformat(z["datum"]),
                "von": _migriere_elternteil(z.get("von")) if _migriere_elternteil(z.get("von")) in (ELTERNTEIL_1, ELTERNTEIL_2) else ELTERNTEIL_1,
                "betrag": float(z.get("betrag", 0)),
            }
            for z in daten["ausgleichszahlungen"]
        ]
    if "dokumente" in daten:
        st.session_state["dokumente"] = [
            {
                "id": d.get("id") or uuid.uuid4().hex[:8],
                "titel": d.get("titel", "Dokument"),
                "dateiname": d.get("dateiname", ""),
                "original_name": d.get("original_name", ""),
                "hochgeladen_am": d.get("hochgeladen_am", ""),
            }
            for d in daten["dokumente"]
        ]
    if "notfallkontakte" in daten:
        st.session_state["notfallkontakte"] = [
            {
                "id": k.get("id") or uuid.uuid4().hex[:8],
                "name": k.get("name", ""),
                "rolle": k.get("rolle", ""),
                "telefon": k.get("telefon", ""),
                "notiz": k.get("notiz", ""),
            }
            for k in daten["notfallkontakte"]
        ]
    if "uebergabe_checkliste" in daten:
        st.session_state["uebergabe_checkliste"] = [
            {
                "id": p.get("id") or uuid.uuid4().hex[:8],
                "text": p.get("text", ""),
                "erledigt": bool(p.get("erledigt", False)),
            }
            for p in daten["uebergabe_checkliste"]
        ]


def speichere_daten():
    """Liest alle zu speichernden Werte direkt aus dem session_state (statt aus
    Funktionsparametern), damit die Funktion unabhaengig davon aufgerufen werden kann,
    ob gerade die Kalender- oder die Finanzen-Seite aktiv ist (bei st.navigation()
    werden Widgets einer Seite nur gezeichnet, wenn diese Seite aktiv ist)."""
    _start_date = st.session_state.get("start_date_persistent", dt.date.today())
    _end_date = st.session_state.get("end_date_persistent", dt.date.today() + dt.timedelta(days=120))
    _wechselzeit = st.session_state.get("wechselzeit", dt.time(18, 0))
    _ziel_vater_pct = st.session_state.get("ziel_vater_persistent", 60)
    _wechseltag_label = st.session_state.get("wechseltag_persistent", WOCHENTAGE[2])
    daten = {
        "rollennamen": st.session_state["rollennamen"],
        "rollenfarben": st.session_state["rollenfarben"],
        "start_date": _start_date.isoformat(),
        "end_date": _end_date.isoformat(),
        "ziel_vater_pct": _ziel_vater_pct,
        "wechseltag": _wechseltag_label,
        "wunsch_vater": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["wunsch_vater"]],
        "verzicht_vater": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["verzicht_vater"]],
        "wunsch_mutter": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["wunsch_mutter"]],
        "verzicht_mutter": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["verzicht_mutter"]],
        "ferien": [
            {
                "name": f["name"], "start": f["start"].isoformat(), "end": f["end"].isoformat(),
                "regel": f.get("regel", "rotation"), "erste_haelfte": f.get("erste_haelfte", ELTERNTEIL_1),
                "ferien_wechseltag": f.get("ferien_wechseltag", _wechseltag_label),
            }
            for f in st.session_state["ferien"]
        ],
        "feiertage": [
            {"name": f["name"], "datum": f["datum"].isoformat()}
            for f in st.session_state["feiertage"]
        ],
        "feste_wochentage": st.session_state["feste_wochentage"],
        "wechselmodell": st.session_state["wechselmodell"],
        "wochenplan": st.session_state["wochenplan"],
        "wechsel_start_parent": st.session_state["wechsel_start_parent"],
        "wechselzeit": _wechselzeit.isoformat(),
        "wechselzeit_ausnahmen": {
            d.isoformat(): z.isoformat() for d, z in st.session_state["wechselzeit_ausnahmen"].items()
        },
        "kinder": st.session_state["kinder"],
        "ausgaben": [
            {
                "id": a["id"], "datum": a["datum"].isoformat(), "beschreibung": a["beschreibung"],
                "betrag": a["betrag"], "bezahlt_von": a["bezahlt_von"], "anteil_vater_pct": a["anteil_vater_pct"],
                "kind": a.get("kind", []),
            }
            for a in st.session_state["ausgaben"]
        ],
        "ausgleichszahlungen": [
            {"id": z["id"], "datum": z["datum"].isoformat(), "von": z["von"], "betrag": z["betrag"]}
            for z in st.session_state["ausgleichszahlungen"]
        ],
        "dokumente": st.session_state["dokumente"],
        "notfallkontakte": st.session_state["notfallkontakte"],
        "uebergabe_checkliste": st.session_state["uebergabe_checkliste"],
    }
    try:
        with open(DATEN_DATEI, "w", encoding="utf-8") as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)
    except Exception:
        pass




lade_gespeicherte_daten()


def add_eintrag(key, date_value, notiz):
    for e in st.session_state[key]:
        if e["datum"] == date_value:
            e["notiz"] = notiz
            st.session_state[key].sort(key=lambda x: x["datum"])
            return
    st.session_state[key].append({"datum": date_value, "notiz": notiz})
    st.session_state[key].sort(key=lambda x: x["datum"])


def date_list_widget(label, key):
    with st.sidebar.expander(label, expanded=False):
        d = st.date_input("Datum", key=f"pick_{key}")
        notiz = st.text_input(
            "Notiz (optional)", key=f"notiz_{key}",
            placeholder="z. B. Familienfeier, Geburtstag …",
        )
        if st.button("➕ Hinzufügen", key=f"add_{key}", type="primary"):
            add_eintrag(key, d, notiz)
            st.rerun()
        for existing in list(st.session_state[key]):
            r1, r2 = st.columns([4, 1])
            text = f"{existing['datum'].strftime('%d.%m.%Y')} ({WOCHENTAGE[existing['datum'].weekday()][:2]})"
            if existing.get("notiz"):
                text += f"  \n*{existing['notiz']}*"
            r1.write(text)
            if r2.button("✕", key=f"rm_{key}_{existing['datum'].isoformat()}"):
                st.session_state[key] = [e for e in st.session_state[key] if e["datum"] != existing["datum"]]
                st.rerun()



# ---------- Algorithmus ----------

def ferien_periode_fuer(d, ferien_liste):
    for f in ferien_liste:
        if f["start"] <= d <= f["end"]:
            return f
    return None


def ferien_regel_parent(periode, d):
    """Gibt den durch die Ferien-Regel festgelegten Elternteil zurueck, oder None,
    wenn die normale Rotation weiterlaufen soll (Regel "rotation" oder keine Ferienzeit)."""
    if periode is None:
        return None
    regel = periode.get("regel", "rotation")
    if regel == "vater":
        return "Elternteil 1"
    if regel == "mutter":
        return "Elternteil 2"
    if regel == "haelftig":
        laenge = (periode["end"] - periode["start"]).days + 1
        erste_haelfte_tage = -(-laenge // 2)  # aufrunden
        grenze = periode["start"] + dt.timedelta(days=erste_haelfte_tage - 1)
        erste = periode.get("erste_haelfte", "Elternteil 1")
        zweite = "Elternteil 2" if erste == "Elternteil 1" else "Elternteil 1"
        return erste if d <= grenze else zweite
    return None


def wochenplan_parent(d, start, wochenplan, wechsel_start_parent):
    """Elternteil laut Wochenplan-Modell: an festen Tagen immer derselbe Elternteil,
    an "wechselt woechentlich"-Tagen alterniert es im 7-Tage-Rhythmus ab dem Startdatum."""
    eintrag = wochenplan.get(WOCHENTAGE[d.weekday()], "Wechselt wöchentlich")
    if eintrag in ("Elternteil 1", "Elternteil 2"):
        return eintrag
    wochen_index = (d - start).days // 7
    if wochen_index % 2 == 0:
        return wechsel_start_parent
    return "Elternteil 2" if wechsel_start_parent == "Elternteil 1" else "Elternteil 1"


def berechne_plan(start, end, wechseltag_idx, ziel_vater_pct,
                   wunsch_vater, verzicht_vater, wunsch_mutter, verzicht_mutter, ferien_liste,
                   feste_wochentage=None, feiertage_lookup=None,
                   modus="block", wochenplan=None, wechsel_start_parent="Elternteil 1", wechselzeit=None,
                   wechselzeit_ausnahmen=None):
    feste_wochentage = feste_wochentage or {}
    feiertage_lookup = feiertage_lookup or {}
    wochenplan = wochenplan or {}
    wechselzeit_ausnahmen = wechselzeit_ausnahmen or {}
    ziel_vater_frac = ziel_vater_pct / 100
    ziel_mutter_frac = 1 - ziel_vater_frac
    wechselzeit_str = wechselzeit.strftime("%H:%M") if wechselzeit else None

    tage = []
    vater_tage = 0
    mutter_tage = 0
    aktueller_block_owner = "Elternteil 1" if ziel_vater_pct >= (100 - ziel_vater_pct) else "Elternteil 2"
    # Vorheriger Tag wird verglichen, um echte Wechsel (Uebergabe von einem Elternteil
    # zum anderen) zu erkennen - unabhaengig davon, durch welche Regel (Wunschtag,
    # Ferienregel, Wochenplan, regulaerer Rhythmus, ...) der Tageseigentuemer bestimmt wurde.
    voriger_parent = None

    d = start
    while d <= end:
        ferien_periode = ferien_periode_fuer(d, ferien_liste)

        # In Ferien mit eigenem Wechseltag gilt fuer den Block-Rhythmus dieser statt des
        # normalen Wechseltags - der Ausgleichs-Algorithmus selbst bleibt derselbe.
        aktueller_wechseltag_idx = wechseltag_idx
        if ferien_periode and ferien_periode.get("regel") == "eigener_wechseltag":
            ferien_wechseltag_label = ferien_periode.get("ferien_wechseltag", WOCHENTAGE[wechseltag_idx])
            if ferien_wechseltag_label in WOCHENTAGE:
                aktueller_wechseltag_idx = WOCHENTAGE.index(ferien_wechseltag_label)

        # Am Wechseltag: Owner fuer den neuen Block per Ausgleichs-Logik bestimmen
        if d.weekday() == aktueller_wechseltag_idx:
            gesamt_bisher = vater_tage + mutter_tage
            if gesamt_bisher == 0:
                aktueller_block_owner = "Elternteil 1" if ziel_vater_frac >= ziel_mutter_frac else "Elternteil 2"
            else:
                defizit_vater = ziel_vater_frac * gesamt_bisher - vater_tage
                defizit_mutter = ziel_mutter_frac * gesamt_bisher - mutter_tage
                aktueller_block_owner = "Elternteil 1" if defizit_vater >= defizit_mutter else "Elternteil 2"

        will_vater = d in wunsch_vater
        will_mutter = d in wunsch_mutter
        nicht_vater = d in verzicht_vater
        nicht_mutter = d in verzicht_mutter

        konflikt = None
        notiz = None
        if will_vater and will_mutter:
            parent = aktueller_block_owner
            konflikt = "Beide wollten das Kind an diesem Tag sicher dabei haben."
            grund = "Konflikt (Wunsch/Wunsch)"
        elif nicht_vater and nicht_mutter:
            parent = aktueller_block_owner
            konflikt = "Beide wollten das Kind an diesem Tag bewusst nicht dabei haben."
            grund = "Konflikt (Verzicht/Verzicht)"
        elif will_vater:
            parent = "Elternteil 1"
            grund = f"Wunschtag {anzeige('Elternteil 1')}"
            notiz = wunsch_vater.get(d) or None
        elif will_mutter:
            parent = "Elternteil 2"
            grund = f"Wunschtag {anzeige('Elternteil 2')}"
            notiz = wunsch_mutter.get(d) or None
        elif nicht_vater:
            parent = "Elternteil 2"
            grund = f"Verzichtstag {anzeige('Elternteil 1')}"
            notiz = verzicht_vater.get(d) or None
        elif nicht_mutter:
            parent = "Elternteil 1"
            grund = f"Verzichtstag {anzeige('Elternteil 2')}"
            notiz = verzicht_mutter.get(d) or None
        elif ferien_regel_parent(ferien_periode, d) is not None:
            parent = ferien_regel_parent(ferien_periode, d)
            grund = f"Ferienregel ({ferien_periode['name']})"
        elif modus == "block" and WOCHENTAGE[d.weekday()] in feste_wochentage:
            parent = feste_wochentage[WOCHENTAGE[d.weekday()]]
            grund = f"Feste Wochentagsregel ({WOCHENTAGE[d.weekday()]} immer {anzeige(parent)})"
        elif modus == "wochenplan":
            parent = wochenplan_parent(d, start, wochenplan, wechsel_start_parent)
            wp_eintrag = wochenplan.get(WOCHENTAGE[d.weekday()], "Wechselt wöchentlich")
            if wp_eintrag == "Wechselt wöchentlich":
                grund = f"Wochenplan ({WOCHENTAGE[d.weekday()]} wechselt wöchentlich)"
            else:
                grund = f"Wochenplan ({WOCHENTAGE[d.weekday()]} immer {anzeige(wp_eintrag)})"
        else:
            parent = aktueller_block_owner
            grund = "regulär (Wechselrhythmus)"

        if parent == "Elternteil 1":
            vater_tage += 1
        else:
            mutter_tage += 1

        ist_wechsel = voriger_parent is not None and parent != voriger_parent
        tag_voriger_elternteil = voriger_parent
        voriger_parent = parent

        tag_wechselzeit = None
        tag_wechselzeit_individuell = False
        if ist_wechsel:
            if d in wechselzeit_ausnahmen:
                tag_wechselzeit = wechselzeit_ausnahmen[d].strftime("%H:%M")
                tag_wechselzeit_individuell = True
            else:
                tag_wechselzeit = wechselzeit_str

        tage.append({
            "datum": d,
            "wochentag": WOCHENTAGE[d.weekday()],
            "elternteil": parent,
            "grund": grund,
            "notiz": notiz,
            "konflikt": konflikt,
            "ferien": ferien_periode["name"] if ferien_periode else None,
            "feiertag": ", ".join(feiertage_lookup[d]) if d in feiertage_lookup else None,
            "wechsel": ist_wechsel,
            "voriger_elternteil": tag_voriger_elternteil,
            "wechselzeit": tag_wechselzeit,
            "wechselzeit_individuell": tag_wechselzeit_individuell,
        })
        d += dt.timedelta(days=1)

    return pd.DataFrame(tage)



def seite_kalender():
    st.sidebar.header("Zeitraum & Grundregeln")
    # Re-Seed-Guard: Streamlit verwirft den Wert eines Widget-Keys, wenn das Widget in
    # einem Skriptdurchlauf nicht gezeichnet wird - z. B. weil gerade die Finanzen-Seite
    # aktiv war. Ohne diesen Schatten-Key wuerde ein Seitenwechsel den zuletzt gewaehlten
    # Zeitraum sonst stillschweigend auf die Default-Werte zuruecksetzen.
    if "start_date_input" not in st.session_state and "start_date_persistent" in st.session_state:
        st.session_state["start_date_input"] = st.session_state["start_date_persistent"]
    if "end_date_input" not in st.session_state and "end_date_persistent" in st.session_state:
        st.session_state["end_date_input"] = st.session_state["end_date_persistent"]
    start_date = st.sidebar.date_input("Start", dt.date.today(), key="start_date_input")
    end_date = st.sidebar.date_input("Ende", dt.date.today() + dt.timedelta(days=120), key="end_date_input")
    st.session_state["start_date_persistent"] = start_date
    st.session_state["end_date_persistent"] = end_date

    st.sidebar.write("Wechselmodell")
    _wm_optionen = ["Blockweise (Zielverteilung + Wechseltag)", "Wochenplan (fester Rhythmus pro Wochentag)"]
    _wm_index = 1 if st.session_state["wechselmodell"] == "wochenplan" else 0
    _wm_auswahl = st.sidebar.radio(
        "Wechselmodell", _wm_optionen, index=_wm_index,
        key="wechselmodell_auswahl", label_visibility="collapsed",
    )
    _wm_neu = "wochenplan" if _wm_auswahl == _wm_optionen[1] else "block"
    if _wm_neu != st.session_state["wechselmodell"]:
        st.session_state["wechselmodell"] = _wm_neu
        st.rerun()

    # Gleicher Re-Seed-Guard wie oben bei start_date/end_date.
    if "wechselzeit_auswahl" not in st.session_state and "wechselzeit" in st.session_state:
        st.session_state["wechselzeit_auswahl"] = st.session_state["wechselzeit"]
    wechselzeit = st.sidebar.time_input(
        "Wechselzeit (Übergabe-Uhrzeit)", dt.time(18, 0), key="wechselzeit_auswahl", step=900,
    )
    st.session_state["wechselzeit"] = wechselzeit
    st.sidebar.caption(
        f"Die Übergabe an einem Wechseltag findet um {wechselzeit.strftime('%H:%M')} Uhr statt "
        "(nicht um Mitternacht) – wird im Kalender bei jedem Wechsel angezeigt."
    )

    if st.session_state["wechselmodell"] == "block":
        st.sidebar.caption(
            "Ihr gebt eine Zielquote vor (z. B. 60/40) – die App verteilt die Tage am "
            "Wechseltag so, dass sich diese Quote über den Zeitraum einpendelt. Passend, "
            "wenn abwechselnd mehrtägige oder wöchentliche Blöcke geplant sind."
        )
        # Streamlit wirft den Wert eines Widget-Keys weg, wenn das Widget in einem Durchlauf
        # nicht gezeichnet wird (z. B. waehrend der Wochenplan-Modus aktiv war) - hier aus dem
        # Schatten-Key wiederherstellen, aber nur falls der Widget-Key gerade fehlt, damit eine
        # laufende Nutzer-Interaktion (Drag am Slider) nie ueberschrieben wird.
        if "ziel_vater_slider" not in st.session_state and "ziel_vater_persistent" in st.session_state:
            st.session_state["ziel_vater_slider"] = st.session_state["ziel_vater_persistent"]
        if "wechseltag_auswahl" not in st.session_state and "wechseltag_persistent" in st.session_state:
            st.session_state["wechseltag_auswahl"] = st.session_state["wechseltag_persistent"]

        st.sidebar.write("Zielverteilung")
        _ziel_vorschau = st.session_state.get("ziel_vater_slider", 60)
        st.sidebar.markdown(
            f"""
            <div style="display:flex;border-radius:6px;overflow:hidden;height:28px;
                        font-size:13px;color:white;font-weight:600;margin-bottom:2px;">
              <div style="width:{_ziel_vorschau}%;background:{farbe(ELTERNTEIL_1)};
                          display:flex;align-items:center;justify-content:center;">
                {anzeige(ELTERNTEIL_1) + " " + str(_ziel_vorschau) + "%" if _ziel_vorschau >= 12 else ""}
              </div>
              <div style="width:{100 - _ziel_vorschau}%;background:{farbe(ELTERNTEIL_2)};
                          display:flex;align-items:center;justify-content:center;">
                {anzeige(ELTERNTEIL_2) + " " + str(100 - _ziel_vorschau) + "%" if (100 - _ziel_vorschau) >= 12 else ""}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ziel_vater_pct = st.sidebar.slider(
            "Zielverteilung", 0, 100, 60, format="%d%%", label_visibility="collapsed",
            key="ziel_vater_slider",
        )
        ziel_mutter_pct = 100 - ziel_vater_pct
        st.session_state["ziel_vater_persistent"] = ziel_vater_pct

        wechseltag_label = st.sidebar.selectbox("Wechseltag", WOCHENTAGE, index=2, key="wechseltag_auswahl")
        wechseltag_idx = WOCHENTAGE.index(wechseltag_label)
        st.session_state["wechseltag_persistent"] = wechseltag_label
    else:
        st.sidebar.caption(
            f"Ihr legt direkt fest, wer an welchem Wochentag dran ist – z. B. Mo–Mi immer "
            f"{anzeige(ELTERNTEIL_1)}, Do–Fr immer {anzeige(ELTERNTEIL_2)}. Tage, die wöchentlich wechseln (z. B. ein "
            "alternierendes Wochenende, oder eine komplette Wechselwoche), markiert ihr "
            "als „Wechselt wöchentlich”."
        )
        _wp_optionen = [ELTERNTEIL_1, ELTERNTEIL_2, "Wechselt wöchentlich"]
        for _tag in WOCHENTAGE:
            _wp_gespeichert = st.session_state["wochenplan"].get(_tag, "Wechselt wöchentlich")
            _wp_index = _wp_optionen.index(_wp_gespeichert) if _wp_gespeichert in _wp_optionen else 2
            _wp_auswahl = st.sidebar.selectbox(
                _tag, _wp_optionen, index=_wp_index, key=f"wp_{_tag}", format_func=anzeige,
            )
            if _wp_auswahl != _wp_gespeichert:
                st.session_state["wochenplan"][_tag] = _wp_auswahl
                st.rerun()

        if any(v == "Wechselt wöchentlich" for v in st.session_state["wochenplan"].values()):
            _wsp_index = 0 if st.session_state["wechsel_start_parent"] == "Elternteil 1" else 1
            _wsp_auswahl = st.sidebar.radio(
                "Wer hat die wechselnden Tage ab dem Startdatum zuerst?", [ELTERNTEIL_1, ELTERNTEIL_2],
                index=_wsp_index, key="wechsel_start_parent_auswahl", horizontal=True, format_func=anzeige,
            )
            if _wsp_auswahl != st.session_state["wechsel_start_parent"]:
                st.session_state["wechsel_start_parent"] = _wsp_auswahl
                st.rerun()

        # Platzhalter-Werte, damit speichere_daten() und die Ferien-Regel-UI (die einen
        # "normalen" Wechseltag als Vorschlagswert nutzt) unveraendert weiterlaufen koennen.
        _wp_schaetzung = [
            100 if v == "Elternteil 1" else 0 if v == "Elternteil 2" else 50
            for v in (st.session_state["wochenplan"].get(t, "Wechselt wöchentlich") for t in WOCHENTAGE)
        ]
        ziel_vater_pct = round(sum(_wp_schaetzung) / 7)
        ziel_mutter_pct = 100 - ziel_vater_pct
        wechseltag_label = WOCHENTAGE[2]
        wechseltag_idx = 2
        st.sidebar.caption(
            f"→ ergibt rechnerisch ca. {anzeige(ELTERNTEIL_1)} {ziel_vater_pct}% / "
            f"{anzeige(ELTERNTEIL_2)} {ziel_mutter_pct}% im Durchschnitt."
        )

    speichere_daten()
    with st.sidebar.expander("💾 Gespeicherte Eingaben"):
        st.caption("Alle Eingaben werden automatisch lokal gespeichert und beim nächsten Start wieder geladen.")
        if st.button("🗑️ Alle Eingaben zurücksetzen"):
            for key in ["wunsch_vater", "verzicht_vater", "wunsch_mutter", "verzicht_mutter"]:
                st.session_state[key] = []
            st.session_state["ferien"] = []
            st.session_state["feiertage"] = []
            st.session_state["feste_wochentage"] = {}
            st.session_state["wechselmodell"] = "block"
            st.session_state["wochenplan"] = {tag: "Wechselt wöchentlich" for tag in WOCHENTAGE}
            st.session_state["wechsel_start_parent"] = "Elternteil 1"
            st.session_state["wechselzeit"] = dt.time(18, 0)
            st.session_state["wechselzeit_ausnahmen"] = {}
            st.session_state["kinder"] = ["Kind 1"]
            st.session_state["ausgaben"] = []
            st.session_state["ausgleichszahlungen"] = []
            if os.path.exists(DATEN_DATEI):
                os.remove(DATEN_DATEI)
            st.rerun()

    st.sidebar.header("Feste Wunsch-/Verzichtstage")
    date_list_widget(f"{anzeige(ELTERNTEIL_1)} – Kind(er) sicher dabei", "wunsch_vater")
    date_list_widget(f"{anzeige(ELTERNTEIL_1)} – bewusst nicht dabei", "verzicht_vater")
    date_list_widget(f"{anzeige(ELTERNTEIL_2)} – Kind(er) sicher dabei", "wunsch_mutter")
    date_list_widget(f"{anzeige(ELTERNTEIL_2)} – bewusst nicht dabei", "verzicht_mutter")

    if st.session_state["wechselmodell"] == "block":
        st.sidebar.header("Feste Wochentage")
        with st.sidebar.expander("📌 Wiederkehrende Wochentags-Regel", expanded=False):
            st.caption(
                f"Bestimmte Wochentage sind unabhängig vom Wechselrhythmus immer bei einem "
                f"Elternteil (z. B. jeden Mittwoch bei {anzeige(ELTERNTEIL_1)}). Feste Wunsch-/Verzichtstage und "
                "Ferienregeln haben trotzdem immer Vorrang vor dieser Regel. Im Wochenplan-Modell "
                "legt ihr das direkt beim Wechselmodell weiter oben fest."
            )
            _fw_optionen = ["Wechselrhythmus", ELTERNTEIL_1, ELTERNTEIL_2]
            _fw_label = lambda v: v if v == "Wechselrhythmus" else f"Immer {anzeige(v)}"
            for _tag in WOCHENTAGE:
                _fw_gespeichert = st.session_state["feste_wochentage"].get(_tag)
                _fw_index = 0
                if _fw_gespeichert == "Elternteil 1":
                    _fw_index = 1
                elif _fw_gespeichert == "Elternteil 2":
                    _fw_index = 2
                _fw_auswahl = st.selectbox(
                    _tag, _fw_optionen, index=_fw_index, key=f"fw_{_tag}", format_func=_fw_label,
                )
                _fw_neu = _fw_auswahl if _fw_auswahl in (ELTERNTEIL_1, ELTERNTEIL_2) else None
                if _fw_neu != _fw_gespeichert:
                    if _fw_neu is None:
                        st.session_state["feste_wochentage"].pop(_tag, None)
                    else:
                        st.session_state["feste_wochentage"][_tag] = _fw_neu
                    # Sofort speichern statt erst bei der naechsten Interaktion (speichere_daten()
                    # laeuft weiter oben im Skript, also vor dieser Aenderung) - ohne den Rerun wuerde
                    # die Wahl beim naechsten Programmstart sonst verloren gehen.
                    st.rerun()

    st.sidebar.header("Ferienzeiten & Feiertage")
    with st.sidebar.expander("Offizielle Ferien & Feiertage automatisch laden", expanded=False):
        bundesland = st.selectbox(
            "Bundesland", list(FERIEN_DATEN.keys()), key="bundesland_auswahl", index=None,
            placeholder="Bundesland wählen …",
        )
        st.caption(
            "Schulferien-Quelle: schulferien-deutschland.org, Stand 08/2026. "
            "Feiertage: bundesweite plus landesspezifische gesetzliche Feiertage 2026/2027 "
            "(regionale Sonderfälle wie Fronleichnam nur in Teilen Sachsens/Thüringens oder "
            "Mariä Himmelfahrt nur in kath. geprägten bayerischen Gemeinden sind hier nicht "
            "berücksichtigt). Bei wichtigen Entscheidungen bitte offiziell gegenprüfen."
        )
        bc1, bc2 = st.columns(2)
        if bc1.button("📥 Ferien laden", disabled=bundesland is None, width="stretch", type="primary"):
            vorhandene = {(f["name"], f["start"], f["end"]) for f in st.session_state["ferien"]}
            neu = 0
            for name, s, e in FERIEN_DATEN[bundesland]:
                eintrag_name = f"{name} ({bundesland})"
                if (eintrag_name, s, e) not in vorhandene:
                    st.session_state["ferien"].append({"name": eintrag_name, "start": s, "end": e})
                    neu += 1
            st.success(f"{neu} Ferienzeiten hinzugefügt.")
            st.rerun()
        if bc2.button("📥 Feiertage laden", disabled=bundesland is None, width="stretch", type="primary"):
            vorhandene_ft = {(f["name"], f["datum"]) for f in st.session_state["feiertage"]}
            neu_ft = 0
            for name, d in FEIERTAGE_DATEN[bundesland]:
                eintrag_name = f"{name} ({bundesland})"
                if (eintrag_name, d) not in vorhandene_ft:
                    st.session_state["feiertage"].append({"name": eintrag_name, "datum": d})
                    neu_ft += 1
            st.success(f"{neu_ft} Feiertage hinzugefügt.")
            st.rerun()

    REGEL_OPTIONEN = {
        "rotation": "Wie sonst (normale Rotation läuft weiter)",
        "eigener_wechseltag": "Rotation läuft weiter, aber mit anderem Wechseltag",
        "vater": f"Komplett bei {anzeige(ELTERNTEIL_1)}",
        "mutter": f"Komplett bei {anzeige(ELTERNTEIL_2)}",
        "haelftig": "Hälftig teilen (wochenweise, erste/zweite Hälfte)",
    }

    with st.sidebar.expander("Ferien hinzufügen", expanded=False):
        f_name = st.text_input("Name", placeholder="z. B. Sommerferien", key="f_name")
        f_start = st.date_input("Von", key="f_start")
        f_end = st.date_input("Bis", key="f_end")
        if f_start <= f_end:
            dauer = (f_end - f_start).days + 1
            if dauer > 40:
                st.warning(f"⚠️ Das sind {dauer} Tage – Von/Bis wirklich richtig eingestellt?")
            else:
                st.caption(f"→ {dauer} Tag(e)")
        f_regel = st.selectbox(
            "Regel für diese Ferienzeit", list(REGEL_OPTIONEN.keys()),
            format_func=lambda k: REGEL_OPTIONEN[k], key="f_regel",
            help="Feste Wunsch-/Verzichtstage gelten trotzdem immer zuerst, egal welche Regel hier gewählt ist.",
        )
        f_erste_haelfte = "Elternteil 1"
        if f_regel == "haelftig":
            f_erste_haelfte = st.radio(
                "Wer hat die erste Hälfte?", [ELTERNTEIL_1, ELTERNTEIL_2], key="f_erste_haelfte",
                horizontal=True, format_func=anzeige,
            )
        f_ferien_wechseltag = wechseltag_label
        if f_regel == "eigener_wechseltag":
            f_ferien_wechseltag = st.selectbox(
                "Wechseltag während dieser Ferienzeit", WOCHENTAGE, key="f_ferien_wechseltag",
            )
        if st.button("➕ Ferien hinzufügen", type="primary"):
            if f_name and f_start <= f_end:
                st.session_state["ferien"].append({
                    "name": f_name, "start": f_start, "end": f_end,
                    "regel": f_regel, "erste_haelfte": f_erste_haelfte,
                    "ferien_wechseltag": f_ferien_wechseltag,
                })
                st.rerun()
            else:
                st.warning("Bitte Name angeben und Start ≤ Ende.")

    with st.sidebar.expander(f"📋 Alle Ferienzeiten & Regeln ({len(st.session_state['ferien'])})", expanded=False):
        st.caption("Gilt für alle Ferien – auch automatisch geladene. Feste Wunsch-/Verzichtstage haben trotzdem immer Vorrang.")
        if not st.session_state["ferien"]:
            st.write("Noch keine Ferienzeiten erfasst.")
        for i, f in enumerate(st.session_state["ferien"]):
            eintrag_id = f"{i}_{f['name']}_{f['start'].isoformat()}"
            st.markdown(f"**{f['name']}**  \n{f['start'].strftime('%d.%m.')} – {f['end'].strftime('%d.%m.%Y')}")
            regel_keys = list(REGEL_OPTIONEN.keys())
            aktuelle_regel = f.get("regel", "rotation")
            neue_regel = st.selectbox(
                "Regel", regel_keys, format_func=lambda k: REGEL_OPTIONEN[k],
                index=regel_keys.index(aktuelle_regel) if aktuelle_regel in regel_keys else 0,
                key=f"regel_{eintrag_id}", label_visibility="collapsed",
            )
            if neue_regel != aktuelle_regel:
                st.session_state["ferien"][i]["regel"] = neue_regel
                st.rerun()
            if neue_regel == "haelftig":
                aktuelle_erste = f.get("erste_haelfte", "Elternteil 1")
                neue_erste = st.radio(
                    "Wer hat die erste Hälfte?", [ELTERNTEIL_1, ELTERNTEIL_2], horizontal=True,
                    index=[ELTERNTEIL_1, ELTERNTEIL_2].index(aktuelle_erste),
                    key=f"erste_{eintrag_id}", format_func=anzeige,
                )
                if neue_erste != aktuelle_erste:
                    st.session_state["ferien"][i]["erste_haelfte"] = neue_erste
                    st.rerun()
            if neue_regel == "eigener_wechseltag":
                aktueller_ferien_wechseltag = f.get("ferien_wechseltag", wechseltag_label)
                if aktueller_ferien_wechseltag not in WOCHENTAGE:
                    aktueller_ferien_wechseltag = wechseltag_label
                neuer_ferien_wechseltag = st.selectbox(
                    "Wechseltag während dieser Ferienzeit", WOCHENTAGE,
                    index=WOCHENTAGE.index(aktueller_ferien_wechseltag),
                    key=f"ferienwechsel_{eintrag_id}",
                )
                if neuer_ferien_wechseltag != aktueller_ferien_wechseltag:
                    st.session_state["ferien"][i]["ferien_wechseltag"] = neuer_ferien_wechseltag
                    st.rerun()
            if st.button("✕ Entfernen", key=f"rm_ferien_{eintrag_id}"):
                st.session_state["ferien"].pop(i)
                st.rerun()
            st.divider()

    with st.sidebar.expander("Feiertag hinzufügen", expanded=False):
        st.caption("Rein informativ – wird im Kalender markiert, beeinflusst aber nicht, bei wem das Kind ist.")
        ft_name = st.text_input("Name", placeholder="z. B. Weihnachten", key="ft_name")
        ft_datum = st.date_input("Datum", key="ft_datum")
        if st.button("➕ Feiertag hinzufügen", type="primary"):
            if ft_name:
                st.session_state["feiertage"].append({"name": ft_name, "datum": ft_datum})
                st.rerun()
            else:
                st.warning("Bitte einen Namen angeben.")

    with st.sidebar.expander(f"🎉 Alle Feiertage ({len(st.session_state['feiertage'])})", expanded=False):
        st.caption("Rein informativ – auch automatisch geladene Feiertage. Ohne Einfluss auf die Zuordnung.")
        if not st.session_state["feiertage"]:
            st.write("Noch keine Feiertage erfasst.")
        for i, f in enumerate(sorted(st.session_state["feiertage"], key=lambda x: x["datum"])):
            eintrag_id = f"{i}_{f['name']}_{f['datum'].isoformat()}"
            r1, r2 = st.columns([4, 1])
            r1.write(f"**{f['name']}**  \n{f['datum'].strftime('%d.%m.%Y')} ({WOCHENTAGE[f['datum'].weekday()][:2]})")
            if r2.button("✕", key=f"rm_feiertag_{eintrag_id}"):
                st.session_state["feiertage"] = [
                    e for e in st.session_state["feiertage"]
                    if not (e["name"] == f["name"] and e["datum"] == f["datum"])
                ]
                st.rerun()

    if start_date > end_date:
        st.error("Das Start-Datum muss vor dem End-Datum liegen.")
        st.stop()

    _feiertage_lookup = {}
    for _f in st.session_state["feiertage"]:
        _feiertage_lookup.setdefault(_f["datum"], []).append(_f["name"])

    df = berechne_plan(
        start_date, end_date, wechseltag_idx, ziel_vater_pct,
        {e["datum"]: e.get("notiz", "") for e in st.session_state["wunsch_vater"]},
        {e["datum"]: e.get("notiz", "") for e in st.session_state["verzicht_vater"]},
        {e["datum"]: e.get("notiz", "") for e in st.session_state["wunsch_mutter"]},
        {e["datum"]: e.get("notiz", "") for e in st.session_state["verzicht_mutter"]},
        st.session_state["ferien"],
        st.session_state["feste_wochentage"],
        _feiertage_lookup,
        st.session_state["wechselmodell"],
        st.session_state["wochenplan"],
        st.session_state["wechsel_start_parent"],
        wechselzeit=wechselzeit,
        wechselzeit_ausnahmen=st.session_state["wechselzeit_ausnahmen"],
    )

    st.caption(
        "Mockup zum Testen der Idee mit echten Daten – kein fertiges Produkt. "
        "Feste Wunsch-/Verzichtstage haben Vorrang, alle übrigen Tage werden am Wechseltag so "
        "verteilt, dass sich die Zielquote über den Zeitraum einpendelt."
    )
    st.info(
        "Vereinfachung in dieser Version: eine gemeinsame Rotation für alle Kinder. "
        "Unterschiedliche Zeiten je Kind wären ein möglicher nächster Schritt.",
        icon=":material/info:",
    )

    # ---------- Auswertung ----------
    gesamt = len(df)
    vater_n = int((df["elternteil"] == "Elternteil 1").sum())
    mutter_n = int((df["elternteil"] == "Elternteil 2").sum())

    st.subheader("Auswertung")
    st.markdown(
        """
        <style>
        div[data-testid="stMetricValue"] { font-size: 1.6rem; }
        div[data-testid="stMetricLabel"] { font-size: 0.85rem; }
        div[data-testid="stMetricDelta"] { font-size: 0.8rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tage gesamt", gesamt)
    if st.session_state["wechselmodell"] == "wochenplan":
        c2.metric(anzeige(ELTERNTEIL_1), f"{vater_n} Tage", f"{vater_n/gesamt*100:.0f}% (ergibt sich aus Wochenplan)")
        c3.metric(anzeige(ELTERNTEIL_2), f"{mutter_n} Tage", f"{mutter_n/gesamt*100:.0f}% (ergibt sich aus Wochenplan)")
    else:
        c2.metric(anzeige(ELTERNTEIL_1), f"{vater_n} Tage", f"{vater_n/gesamt*100:.0f}% (Ziel {ziel_vater_pct}%)")
        c3.metric(anzeige(ELTERNTEIL_2), f"{mutter_n} Tage", f"{mutter_n/gesamt*100:.0f}% (Ziel {ziel_mutter_pct}%)")

    ferien_df = df[df["ferien"].notna()]
    if len(ferien_df) > 0:
        fv = int((ferien_df["elternteil"] == "Elternteil 1").sum())
        fm = int((ferien_df["elternteil"] == "Elternteil 2").sum())
        c4.metric("Ferientage", f"{len(ferien_df)} Tage", f"{anzeige(ELTERNTEIL_1)} {fv} / {anzeige(ELTERNTEIL_2)} {fm}")
        with st.expander("Ferien im Detail"):
            for name in ferien_df["ferien"].unique():
                sub = ferien_df[ferien_df["ferien"] == name]
                fv_n = int((sub["elternteil"] == "Elternteil 1").sum())
                fm_n = int((sub["elternteil"] == "Elternteil 2").sum())
                st.write(f"**{name}**: {len(sub)} Tage – {anzeige(ELTERNTEIL_1)} {fv_n}, {anzeige(ELTERNTEIL_2)} {fm_n}")
    else:
        c4.metric("Ferientage", "keine erfasst")

    feiertage_df = df[df["feiertag"].notna()]
    if len(feiertage_df) > 0:
        with st.expander(f"🎉 Feiertage im Zeitraum ({len(feiertage_df)})"):
            st.caption("Rein informativ – zeigt zur Orientierung, bei wem das Kind an diesem Feiertag laut Plan ist.")
            for _, row in feiertage_df.sort_values("datum").iterrows():
                st.write(f"**{row['feiertag']}** – {row['datum'].strftime('%d.%m.%Y')} ({row['wochentag'][:2]}), bei {anzeige(row['elternteil'])}")

    konflikte = df[df["konflikt"].notna()]
    if len(konflikte) > 0:
        st.warning(f"⚠️ {len(konflikte)} Tag(e) mit widersprüchlichen Angaben – bitte manuell klären.")
        with st.expander("Konflikte anzeigen"):
            st.dataframe(konflikte[["datum", "wochentag", "konflikt"]], hide_index=True, use_container_width=True)

    st.divider()

    # ---------- Kalenderansicht ----------
    st.subheader("Kalender")


    _chip_basis = (
        "display:inline-flex; align-items:center; gap:6px; padding:5px 12px; "
        "border-radius:999px; background:#FFFFFF; border:1px solid var(--pe-border); "
        "font-size:0.86rem; font-weight:500; color:#2B2A3D; box-shadow:0 1px 3px rgba(44,42,61,0.04);"
    )
    _legende_swatch = "display:inline-block; width:10px; height:10px; border-radius:50%; flex-shrink:0;"
    legende = f"""
    <div style="display:flex; gap:8px; margin-bottom:12px; align-items:center; flex-wrap:wrap;">
      <div style="{_chip_basis}"><span style="{_legende_swatch}background:{farbe(ELTERNTEIL_1)};"></span>{anzeige(ELTERNTEIL_1)}</div>
      <div style="{_chip_basis}"><span style="{_legende_swatch}background:{farbe(ELTERNTEIL_2)};"></span>{anzeige(ELTERNTEIL_2)}</div>
      <div style="{_chip_basis}">🏖️ Ferien</div>
      <div style="{_chip_basis}">🎉 Feiertag</div>
      <div style="{_chip_basis}">🎯 Wunschtag</div>
      <div style="{_chip_basis}">🚫 Verzichtstag</div>
      <div style="{_chip_basis}">⚠️ Konflikt</div>
      <div style="{_chip_basis}">
        <span style="display:inline-block; width:18px; height:12px; border-radius:4px; flex-shrink:0;
                     background:linear-gradient(90deg, {farbe(ELTERNTEIL_1)} 50%, {farbe(ELTERNTEIL_2)} 50%);"></span>
        Wechsel (Übergabe {wechselzeit.strftime('%H:%M')} Uhr, an einzelnen Tagen abweichend möglich)
      </div>
    </div>
    """
    st.markdown(legende, unsafe_allow_html=True)
    st.caption("Klicke auf einen Tag im Kalender – ein Fenster zum Ändern der Zuordnung oder zum Setzen von Wunsch-/Verzichtstagen öffnet sich.")

    st.session_state.setdefault("ausgewaehlter_tag", None)


    def _tag_setzen(key, tag, notiz):
        for k in ["wunsch_vater", "verzicht_vater", "wunsch_mutter", "verzicht_mutter"]:
            st.session_state[k] = [e for e in st.session_state[k] if e["datum"] != tag]
        add_eintrag(key, tag, notiz)
        st.rerun()


    def _tag_zuruecksetzen(tag):
        for k in ["wunsch_vater", "verzicht_vater", "wunsch_mutter", "verzicht_mutter"]:
            st.session_state[k] = [e for e in st.session_state[k] if e["datum"] != tag]
        st.rerun()


    @st.dialog("Tag bearbeiten", width="medium")
    def tag_dialog(df):
        tag = st.session_state.get("ausgewaehlter_tag")
        treffer = df[df["datum"] == tag]
        if treffer.empty:
            st.session_state["ausgewaehlter_tag"] = None
            return
        info = treffer.iloc[0]
        st.markdown(
            f"**{WOCHENTAGE[tag.weekday()]}, {tag.strftime('%d.%m.%Y')}** – aktuell **{info['elternteil']}** "
            f"({info['grund']}{': ' + info['notiz'] if isinstance(info['notiz'], str) and info['notiz'] else ''})"
        )
        if isinstance(info["ferien"], str):
            st.caption(f"🏖️ Ferien: {info['ferien']}")
        if isinstance(info["feiertag"], str):
            st.caption(f"🎉 Feiertag: {info['feiertag']}")
        if info.get("wechsel"):
            _wz_marker = "⏰" if info.get("wechselzeit_individuell") else "🔁"
            _wz_hinweis = " (abweichende Zeit nur an diesem Tag)" if info.get("wechselzeit_individuell") else ""
            st.caption(f"{_wz_marker} Wechseltag – Übergabe ab {info.get('wechselzeit') or wechselzeit.strftime('%H:%M')} Uhr{_wz_hinweis}")
            _wz_aktuell = st.session_state["wechselzeit_ausnahmen"].get(tag, wechselzeit)
            _wz_neu = st.time_input(
                "Übergabezeit an diesem Tag", value=_wz_aktuell, key="tag_panel_wechselzeit", step=900,
            )
            wzc1, wzc2 = st.columns(2)
            if wzc1.button("⏰ Nur für diesen Tag übernehmen", key="tag_panel_wz_setzen", width="stretch"):
                st.session_state["wechselzeit_ausnahmen"][tag] = _wz_neu
                st.rerun()
            if info.get("wechselzeit_individuell"):
                if wzc2.button("↩️ Standardzeit verwenden", key="tag_panel_wz_reset", width="stretch"):
                    st.session_state["wechselzeit_ausnahmen"].pop(tag, None)
                    st.rerun()
        if isinstance(info["konflikt"], str):
            st.warning(f"⚠️ {info['konflikt']}")
        notiz_eingabe = st.text_input(
            "Notiz (optional, gilt für Wunsch/Verzicht)", key="tag_panel_notiz",
            placeholder="z. B. Familienfeier, Geburtstag …",
        )
        b1, b2 = st.columns(2)
        if b1.button(f"🎯 {anzeige(ELTERNTEIL_1)} will", key="tag_panel_wv", width="stretch"):
            _tag_setzen("wunsch_vater", tag, notiz_eingabe)
        if b2.button(f"🎯 {anzeige(ELTERNTEIL_2)} will", key="tag_panel_wm", width="stretch"):
            _tag_setzen("wunsch_mutter", tag, notiz_eingabe)
        b3, b4 = st.columns(2)
        if b3.button(f"🚫 {anzeige(ELTERNTEIL_1)} verzichtet", key="tag_panel_vv", width="stretch"):
            _tag_setzen("verzicht_vater", tag, notiz_eingabe)
        if b4.button(f"🚫 {anzeige(ELTERNTEIL_2)} verzichtet", key="tag_panel_vm", width="stretch"):
            _tag_setzen("verzicht_mutter", tag, notiz_eingabe)
        if st.button("↩️ Automatisch (Wechselrhythmus entscheidet)", key="tag_panel_reset", width="stretch",
                     help="Entfernt Wunsch/Verzicht an diesem Tag - die normale Rotation entscheidet wieder."):
            _tag_zuruecksetzen(tag)
        st.divider()
        if st.button("Schließen", key="tag_panel_close", width="stretch"):
            st.session_state["ausgewaehlter_tag"] = None
            st.rerun()


    if st.session_state.get("ausgewaehlter_tag") is not None:
        tag_dialog(df)


    st.markdown(
        """
        <style>
        div[class*="st-key-kalender_bereich"] {
            background: var(--pe-card);
            border: 1px solid var(--pe-border);
            border-radius: var(--pe-radius-md);
            box-shadow: var(--pe-shadow);
            padding: 1.1rem 1.2rem 1.3rem 1.2rem;
        }
        .st-key-kalender_bereich div[data-testid="stElementContainer"] { margin-bottom:3px !important; }
        .st-key-kalender_bereich button {
            padding:0.3rem 0.1rem !important;
            min-height:2.15rem !important;
            transition:filter 0.1s ease;
        }
        .st-key-kalender_bereich button:hover { filter:brightness(1.12); cursor:pointer; }
        </style>
        """,
        unsafe_allow_html=True,
    )


    def render_monat_interaktiv(jahr, monat, df, css_regeln):
        cal = calendar.Calendar(firstweekday=0)  # Montag
        wochen = cal.monthdayscalendar(jahr, monat)
        df_lookup = df.set_index("datum").to_dict("index")
        ausgewaehlt = st.session_state.get("ausgewaehlter_tag")

        st.markdown(f"**{MONATSNAMEN[monat - 1]} {jahr}**")
        kopf_cols = st.columns(7, gap=None)
        for i, t in enumerate(WOCHENTAGE):
            kopf_cols[i].markdown(
                f"<div style='text-align:center;font-size:12px;color:#888;'>{t[:2]}</div>",
                unsafe_allow_html=True,
            )

        for woche in wochen:
            cols = st.columns(7, gap=None)
            for i, tag in enumerate(woche):
                if tag == 0:
                    cols[i].write("")
                    continue
                d = dt.date(jahr, monat, tag)
                info = df_lookup.get(d)
                if info is None:
                    cols[i].write("")
                    continue

                marker_str = ""
                if isinstance(info["konflikt"], str):
                    marker_str += "⚠️"
                elif str(info["grund"]).startswith("Wunschtag"):
                    marker_str += "🎯"
                elif str(info["grund"]).startswith("Verzichtstag"):
                    marker_str += "🚫"
                if isinstance(info["ferien"], str):
                    marker_str += "🏖️"
                if isinstance(info["feiertag"], str):
                    marker_str += "🎉"
                label = f"{tag} {marker_str}".rstrip()

                tooltip_teile = [f"{WOCHENTAGE[d.weekday()]}, {d.strftime('%d.%m.%Y')} – {anzeige(info['elternteil'])}"]
                if info["grund"] != "regulär (Wechselrhythmus)":
                    zeile = info["grund"]
                    if isinstance(info["notiz"], str) and info["notiz"]:
                        zeile += f": {info['notiz']}"
                    tooltip_teile.append(zeile)
                if isinstance(info["ferien"], str):
                    tooltip_teile.append(f"Ferien: {info['ferien']}")
                if isinstance(info["feiertag"], str):
                    tooltip_teile.append(f"Feiertag: {info['feiertag']}")
                if info.get("wechsel"):
                    _tt_marker = "⏰" if info.get("wechselzeit_individuell") else "🔁"
                    _tt_hinweis = " (abweichende Zeit)" if info.get("wechselzeit_individuell") else ""
                    tooltip_teile.append(f"{_tt_marker} Wechsel – Übergabe ab {info.get('wechselzeit')} Uhr{_tt_hinweis}")
                if isinstance(info["konflikt"], str):
                    tooltip_teile.append(f"⚠️ {info['konflikt']}")
                tooltip = " | ".join(tooltip_teile)

                # Nachbartage in derselben Wochenzeile, für den durchlaufenden Balken:
                # gleiche Farbe wie der Nachbar -> Ecke dort nicht abrunden, sonst schon.
                d_links = dt.date(jahr, monat, woche[i - 1]) if i > 0 and woche[i - 1] != 0 else None
                d_rechts = dt.date(jahr, monat, woche[i + 1]) if i < 6 and woche[i + 1] != 0 else None
                info_links = df_lookup.get(d_links) if d_links else None
                info_rechts = df_lookup.get(d_rechts) if d_rechts else None
                radius_links = "0px" if info_links and info_links["elternteil"] == info["elternteil"] else "10px"
                radius_rechts = "0px" if info_rechts and info_rechts["elternteil"] == info["elternteil"] else "10px"

                _tagesfarbe = farbe(ELTERNTEIL_1) if info["elternteil"] == "Elternteil 1" else farbe(ELTERNTEIL_2)
                # An einem Wechseltag zeigt die Zelle beide Farben (statt eines Icons): links die
                # Farbe des Elternteils, der das Kind bis zur Uebergabezeit noch hat, rechts die
                # Farbe des Elternteils, der ab der Uebergabezeit uebernimmt - intuitiver als ein
                # Symbol, die genaue Uhrzeit steht weiterhin im Tooltip/Popup.
                if info.get("wechsel") and isinstance(info.get("voriger_elternteil"), str):
                    _farbe_vorher = farbe(ELTERNTEIL_1) if info["voriger_elternteil"] == "Elternteil 1" else farbe(ELTERNTEIL_2)
                    hintergrund = f"linear-gradient(90deg, {_farbe_vorher} 50%, {_tagesfarbe} 50%)"
                else:
                    hintergrund = _tagesfarbe
                iso = d.isoformat()
                schatten = f"inset 0 -4px 0 0 {FERIEN_FARBE}" if isinstance(info["ferien"], str) else "none"
                umriss = "outline:3px solid #1b1b1b !important; outline-offset:-3px;" if ausgewaehlt == d else ""
                css_regeln.append(f"""
                .st-key-tagbtn_{iso} button {{
                    background:{hintergrund} !important;
                    color:white !important;
                    border:none !important;
                    border-radius:{radius_links} {radius_rechts} {radius_rechts} {radius_links} !important;
                    box-shadow:{schatten} !important;
                    font-weight:600 !important;
                    {umriss}
                }}""")

                if cols[i].button(label, key=f"tagbtn_{iso}", help=tooltip, width="stretch"):
                    st.session_state["ausgewaehlter_tag"] = d
                    st.rerun()
        st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)


    # Monate im Zeitraum ermitteln
    monate = []
    cur = dt.date(start_date.year, start_date.month, 1)
    end_marker = dt.date(end_date.year, end_date.month, 1)
    while cur <= end_marker:
        monate.append((cur.year, cur.month))
        if cur.month == 12:
            cur = dt.date(cur.year + 1, 1, 1)
        else:
            cur = dt.date(cur.year, cur.month + 1, 1)

    with st.container(key="kalender_bereich"):
        _css_regeln = []
        for jahr, monat in monate:
            render_monat_interaktiv(jahr, monat, df, _css_regeln)
        st.markdown(f"<style>{''.join(_css_regeln)}</style>", unsafe_allow_html=True)

    st.divider()
    with st.expander("Rohdaten (alle Tage)"):
        st.dataframe(df, hide_index=True, use_container_width=True)


def seite_finanzen():
    st.subheader(":material/account_balance_wallet: Finanzen")
    st.caption(
        "Gemeinsame Ausgaben fürs Kind eintragen und sehen, wer wem noch was schuldet – "
        "unabhängig vom Betreuungskalender."
    )

    _ausgaben = st.session_state["ausgaben"]
    _ausgleiche = st.session_state["ausgleichszahlungen"]
    _saldo = berechne_finanzsaldo(_ausgaben, _ausgleiche)

    if abs(_saldo) < 0.005:
        st.success("Ausgeglichen – aktuell schuldet niemand etwas.", icon=":material/check_circle:")
    elif _saldo > 0:
        st.warning(f"{anzeige(ELTERNTEIL_2)} schuldet {anzeige(ELTERNTEIL_1)}: **{euro(_saldo)}**", icon=":material/balance:")
    else:
        st.warning(f"{anzeige(ELTERNTEIL_1)} schuldet {anzeige(ELTERNTEIL_2)}: **{euro(abs(_saldo))}**", icon=":material/balance:")

    _gesamt_ausgaben = sum(a["betrag"] for a in _ausgaben)
    _vater_anteil_gesamt = sum(a["betrag"] * a["anteil_vater_pct"] / 100 for a in _ausgaben)
    _mutter_anteil_gesamt = _gesamt_ausgaben - _vater_anteil_gesamt
    _fc1, _fc2, _fc3 = st.columns(3)
    _fc1.metric("Gesamtausgaben", euro(_gesamt_ausgaben))
    _fc2.metric(f"Anteil {anzeige(ELTERNTEIL_1)}", euro(_vater_anteil_gesamt))
    _fc3.metric(f"Anteil {anzeige(ELTERNTEIL_2)}", euro(_mutter_anteil_gesamt))

    st.divider()

    with st.expander(":material/family_restroom: Kinder verwalten", expanded=False):
        st.caption(
            "Namen der Kinder, für die Ausgaben erfasst werden können – hilfreich, wenn es "
            "mehrere gibt und ihr später sehen wollt, wofür wie viel ausgegeben wurde."
        )
        _kind_neu_col1, _kind_neu_col2 = st.columns([4, 1])
        _kind_name_neu = _kind_neu_col1.text_input(
            "Name hinzufügen", key="kind_name_neu", placeholder="z. B. Mia",
            label_visibility="collapsed",
        )
        if _kind_neu_col2.button(":material/add: Hinzufügen", key="kind_hinzufuegen", type="primary"):
            _name = _kind_name_neu.strip()
            if not _name:
                st.warning("Bitte einen Namen eingeben.")
            elif _name in st.session_state["kinder"]:
                st.warning("Dieses Kind gibt es schon.")
            else:
                st.session_state["kinder"].append(_name)
                # Das Ausgabe-Formular unten ist ein Expander - sein Inhalt (inkl. der
                # "fa_kind"-Mehrfachauswahl) wird bei JEDEM Durchlauf ausgefuehrt, auch wenn er
                # eingeklappt ist. Der Widget-Key wird also schon beim allerersten Laden belegt.
                # Damit ein neu hinzugefuegtes Kind in der Auswahl auch wirklich mit vorausgewaehlt
                # ist, den Key hier direkt auf die neue vollstaendige Liste setzen (statt ihn nur
                # zu loeschen - das reicht bei diesem Widget-Typ nicht zuverlaessig aus).
                st.session_state["fa_kind"] = list(st.session_state["kinder"])
                st.rerun()
        if not st.session_state["kinder"]:
            st.caption("Noch keine Kinder erfasst – neue Ausgaben gelten dann automatisch für „Kind”.")
        for _k in list(st.session_state["kinder"]):
            _kr1, _kr2 = st.columns([4, 1])
            _kr1.write(_k)
            if _kr2.button(":material/delete:", key=f"rm_kind_{_k}"):
                st.session_state["kinder"] = [x for x in st.session_state["kinder"] if x != _k]
                st.session_state["fa_kind"] = [
                    x for x in st.session_state.get("fa_kind", []) if x != _k
                ]
                st.rerun()

    _kinder_optionen = st.session_state["kinder"] or ["Kind"]

    with st.expander(":material/add_shopping_cart: Ausgabe hinzufügen", expanded=False):
        _fa_datum = st.date_input("Datum", dt.date.today(), key="fa_datum")
        _fa_beschreibung = st.text_input(
            "Beschreibung", key="fa_beschreibung",
            placeholder="z. B. Winterjacke, Nachhilfe, Kita-Beitrag …",
        )
        _fa_betrag = st.number_input(
            "Betrag (€)", min_value=0.0, step=1.0, format="%.2f", key="fa_betrag",
        )
        _fa_kind = st.multiselect(
            "Für welche(s) Kind(er)?", _kinder_optionen, default=list(_kinder_optionen), key="fa_kind",
            help="Bei einer Ausgabe für mehrere oder alle Kinder einfach mehrere auswählen.",
        )
        _fa_bezahlt_von = st.radio(
            "Bezahlt von", [ELTERNTEIL_1, ELTERNTEIL_2], key="fa_bezahlt_von", horizontal=True, format_func=anzeige,
        )
        _fa_anteil_vater = st.slider(
            f"Anteil {anzeige(ELTERNTEIL_1)} an dieser Ausgabe", 0, 100, 50, format="%d%%", key="fa_anteil_vater",
        )
        st.caption(
            f"→ {anzeige(ELTERNTEIL_1)} trägt {euro(_fa_betrag * _fa_anteil_vater / 100)}, "
            f"{anzeige(ELTERNTEIL_2)} trägt {euro(_fa_betrag * (100 - _fa_anteil_vater) / 100)}."
        )
        if st.button(":material/add: Ausgabe speichern", key="fa_speichern", type="primary"):
            if _fa_beschreibung.strip() and _fa_betrag > 0:
                st.session_state["ausgaben"].append({
                    "id": uuid.uuid4().hex[:8],
                    "datum": _fa_datum,
                    "beschreibung": _fa_beschreibung.strip(),
                    "betrag": _fa_betrag,
                    "bezahlt_von": _fa_bezahlt_von,
                    "anteil_vater_pct": _fa_anteil_vater,
                    "kind": _fa_kind if _fa_kind else _kinder_optionen,
                })
                st.rerun()
            else:
                st.warning("Bitte eine Beschreibung und einen Betrag größer als 0 eingeben.")

    st.markdown("#### Ausgaben")
    if not _ausgaben:
        st.caption("Noch keine Ausgaben erfasst.")
    else:
        _alle_vorkommenden_kinder = sorted({
            k for a in _ausgaben for k in (a.get("kind") or ["Kind"])
        })
        if len(_alle_vorkommenden_kinder) > 1:
            _filter_kinder = st.multiselect(
                "Nach Kind filtern", _alle_vorkommenden_kinder, default=list(_alle_vorkommenden_kinder),
                key="fa_filter_kind",
            )
        else:
            _filter_kinder = _alle_vorkommenden_kinder
        _ausgaben_gefiltert = [
            a for a in _ausgaben if set(a.get("kind") or ["Kind"]) & set(_filter_kinder)
        ]
        if not _ausgaben_gefiltert:
            st.caption("Keine Ausgaben für diese Auswahl.")
        for _a in sorted(_ausgaben_gefiltert, key=lambda x: x["datum"], reverse=True):
            with st.container(key=f"pe_card_ausgabe_{_a['id']}"):
                _c1, _c2, _c3, _c4, _c5, _c6 = st.columns([1.1, 2.2, 1.0, 2.1, 1.6, 0.5])
                _c1.caption(_a["datum"].strftime("%d.%m.%Y"))
                _c2.markdown(f"**{_a['beschreibung']}**")
                _c3.markdown(
                    f"<span style='color:{farbe(_a['bezahlt_von'])};font-weight:700;'>{euro(_a['betrag'])}</span>",
                    unsafe_allow_html=True,
                )
                _c4.caption(
                    f"bezahlt von {anzeige(_a['bezahlt_von'])} · {anzeige(ELTERNTEIL_1)} {_a['anteil_vater_pct']:.0f}% / "
                    f"{anzeige(ELTERNTEIL_2)} {100 - _a['anteil_vater_pct']:.0f}%"
                )
                _c5.caption(", ".join(_a.get("kind") or ["Kind"]))
                if _c6.button(":material/delete:", key=f"del_ausgabe_{_a['id']}"):
                    st.session_state["ausgaben"] = [
                        x for x in st.session_state["ausgaben"] if x["id"] != _a["id"]
                    ]
                    st.rerun()

    st.divider()

    with st.expander(":material/payments: Ausgleichszahlung eintragen", expanded=False):
        st.caption("Wenn jemand direkt Geld überwiesen hat, um den Saldo auszugleichen.")
        _fz_datum = st.date_input("Datum", dt.date.today(), key="fz_datum")
        _fz_von = st.radio("Wer hat gezahlt", [ELTERNTEIL_1, ELTERNTEIL_2], key="fz_von", horizontal=True, format_func=anzeige)
        _fz_betrag = st.number_input(
            "Betrag (€)", min_value=0.0, step=1.0, format="%.2f", key="fz_betrag",
        )
        if st.button(":material/add: Ausgleichszahlung speichern", key="fz_speichern", type="primary"):
            if _fz_betrag > 0:
                st.session_state["ausgleichszahlungen"].append({
                    "id": uuid.uuid4().hex[:8],
                    "datum": _fz_datum,
                    "von": _fz_von,
                    "betrag": _fz_betrag,
                })
                st.rerun()
            else:
                st.warning("Bitte einen Betrag größer als 0 eingeben.")

    if _ausgleiche:
        st.markdown("#### Ausgleichszahlungen")
        for _z in sorted(_ausgleiche, key=lambda x: x["datum"], reverse=True):
            with st.container(key=f"pe_card_ausgleich_{_z['id']}"):
                _c1, _c2, _c3, _c4 = st.columns([1.2, 2, 3, 0.6])
                _c1.caption(_z["datum"].strftime("%d.%m.%Y"))
                _c2.markdown(
                    f"<span style='color:{farbe(_z['von'])};font-weight:700;'>{euro(_z['betrag'])}</span>",
                    unsafe_allow_html=True,
                )
                _c3.write(f"{anzeige(_z['von'])} hat gezahlt")
                if _c4.button(":material/delete:", key=f"del_ausgleich_{_z['id']}"):
                    st.session_state["ausgleichszahlungen"] = [
                        x for x in st.session_state["ausgleichszahlungen"] if x["id"] != _z["id"]
                    ]
                    st.rerun()

    speichere_daten()


_PINNWAND_SVG_PIN = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M12 2.5C8.55 2.5 5.75 5.3 5.75 8.75c0 4.75 6.25 12.25 6.25 12.25s6.25-7.5 6.25-12.25'
    'C18.25 5.3 15.45 2.5 12 2.5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>'
    '<circle cx="12" cy="8.75" r="2.4" stroke="currentColor" stroke-width="1.6"/></svg>'
)
_PINNWAND_SVG_PHONE = (
    '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M6.6 10.8c1.4 2.8 3.8 5.2 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20'
    'c0 .6-.4 1-1 1C10.4 21 3 13.6 3 4c0-.6.4-1 1-1h3.4c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .8-.2 1L6.6 10.8z"'
    ' stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/></svg>'
)
_PINNWAND_SVG_BILD = (
    '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="3" y="4" width="18" height="16" rx="2.5" stroke="currentColor" stroke-width="1.6"/>'
    '<circle cx="8.5" cy="9.5" r="1.4" stroke="currentColor" stroke-width="1.6"/>'
    '<path d="M21 15.5l-5-5a1.5 1.5 0 0 0-2.1 0L4 20" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
_PINNWAND_SVG_CHECK = (
    '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="4" y="3.5" width="16" height="18" rx="2.3" stroke="currentColor" stroke-width="1.6"/>'
    '<path d="M9 2.5h6a1 1 0 0 1 1 1v1.2a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1z" '
    'stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>'
    '<path d="M8 12.3l2.3 2.3L16 9" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
    'stroke-linejoin="round"/></svg>'
)


def _pinnwand_karten_stil(karten_id: str, praefix: str):
    """Gibt der Karte mit dem Key f'{praefix}{karten_id}' einen duennen, farbigen
    Akzentstreifen oben - dezente Wiedererkennung statt aufwendiger Kork-Optik."""
    _wert = int(karten_id, 16)
    _pin_farben = ["#534AB7", "#0F5C66", "#C97B4A", "#4A7A6B", "#8859A3"]
    _akzent_farbe = _pin_farben[_wert % len(_pin_farben)]
    st.markdown(
        f"""
        <style>
        .st-key-{praefix}{karten_id} {{ border-top: 4px solid {_akzent_farbe} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def seite_pinnwand():
    st.subheader(":material/push_pin: Pinnwand")
    st.caption(
        "Der gemeinsame Ablageort für alles, was beide Elternteile griffbereit haben sollten – "
        "Fotos von Dokumenten wie Stundenplan oder Packliste, und die wichtigsten Notfallkontakte."
    )

    _kontakte = st.session_state["notfallkontakte"]
    _dokumente = st.session_state["dokumente"]
    _checkliste = st.session_state["uebergabe_checkliste"]

    # ---------- Optik: dezente Mint-Flaeche statt fotorealistischer Korkwand ----------
    st.markdown(
        """
        <style>
        div[class*="st-key-pinnwand_board"] {
            background: #DCEFEC !important;
            border: 1px solid #C4E0DC !important;
            border-radius: var(--pe-radius-md) !important;
            box-shadow: var(--pe-shadow) !important;
            padding: 1.4rem 1.4rem 1.6rem 1.4rem !important;
        }
        .pinnwand-titel, .pinnwand-subtitel {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--pe-teal);
            letter-spacing: -0.01em;
        }
        .pinnwand-titel {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .pinnwand-subtitel {
            font-size: 0.92rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--pe-ink-soft);
            margin: 0.3rem 0 0.9rem 0;
        }
        .pinnwand-titel svg, .pinnwand-subtitel svg {
            flex-shrink: 0;
            opacity: 0.9;
        }
        .pinnwand-leer {
            color: var(--pe-ink-soft);
            font-size: 0.95rem;
        }
        div[class*="st-key-karte_"] {
            background: var(--pe-card) !important;
            border: 1px solid var(--pe-border) !important;
            border-radius: var(--pe-radius-md) !important;
            box-shadow: 0 1px 4px rgba(44,42,61,0.05) !important;
            margin: 0 8px 14px 8px !important;
            padding: 16px 16px 14px 16px !important;
        }
        div[class*="st-key-karte_"] img {
            border-radius: 8px;
        }
        .karten-titel {
            font-weight: 700;
            font-size: 1.05rem;
            color: #2B2A3D;
            line-height: 1.25;
        }
        .karten-rolle {
            color: var(--pe-ink-soft);
            font-size: 0.86rem;
            margin-bottom: 0.35rem;
        }
        div[class*="st-key-karte_check"] label p {
            font-size: 0.96rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=False, key="pinnwand_board"):
        st.markdown(
            f'<div class="pinnwand-titel">{_PINNWAND_SVG_PIN}<span>Angepinnt</span></div>',
            unsafe_allow_html=True,
        )

        if not _kontakte and not _dokumente and not _checkliste:
            st.markdown(
                '<div class="pinnwand-leer">Noch nichts an der Pinnwand. Weiter unten kannst du '
                "eine Übergabe-Checkliste anlegen, Notfallkontakte eintragen und Dokumente "
                "hochladen.</div>",
                unsafe_allow_html=True,
            )
        else:
            if _checkliste:
                st.markdown(
                    f'<div class="pinnwand-subtitel">{_PINNWAND_SVG_CHECK}'
                    "<span>Übergabe-Checkliste</span></div>",
                    unsafe_allow_html=True,
                )
                _pinnwand_karten_stil("a1b2c3d4", "karte_checkliste_")
                with st.container(border=True, key="karte_checkliste_a1b2c3d4"):
                    st.caption("Was beim nächsten Wechsel mit soll:")
                    _reset_suffix = st.session_state["checkliste_reset_key"]
                    for _p in _checkliste:
                        _pc1, _pc2 = st.columns([6, 1])
                        with _pc1:
                            _haken = st.checkbox(
                                _p["text"], value=_p["erledigt"],
                                key=f"chk_{_p['id']}_{_reset_suffix}",
                            )
                            if _haken != _p["erledigt"]:
                                _p["erledigt"] = _haken
                                speichere_daten()
                        with _pc2:
                            if st.button(":material/delete:", key=f"del_check_{_p['id']}"):
                                st.session_state["uebergabe_checkliste"] = [
                                    x for x in st.session_state["uebergabe_checkliste"] if x["id"] != _p["id"]
                                ]
                                speichere_daten()
                                st.rerun()
                    if any(p["erledigt"] for p in _checkliste):
                        if st.button(":material/refresh: Für nächstes Mal zurücksetzen", key="checkliste_reset"):
                            for _p in st.session_state["uebergabe_checkliste"]:
                                _p["erledigt"] = False
                            st.session_state["checkliste_reset_key"] += 1
                            speichere_daten()
                            st.rerun()

            if _checkliste and (_kontakte or _dokumente):
                st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

            if _kontakte:
                st.markdown(
                    f'<div class="pinnwand-subtitel">{_PINNWAND_SVG_PHONE}<span>Notfallkontakte</span></div>',
                    unsafe_allow_html=True,
                )
                _kspalten = st.columns(3)
                for _i, _k in enumerate(_kontakte):
                    _pinnwand_karten_stil(_k["id"], "karte_kontakt_")
                    with _kspalten[_i % 3]:
                        with st.container(border=True, key=f"karte_kontakt_{_k['id']}"):
                            st.markdown(f'<div class="karten-titel">{_k["name"]}</div>', unsafe_allow_html=True)
                            if _k["rolle"]:
                                st.markdown(f'<div class="karten-rolle">{_k["rolle"]}</div>', unsafe_allow_html=True)
                            if _k["telefon"]:
                                st.write(f":material/call: {_k['telefon']}")
                            if _k.get("notiz"):
                                st.caption(_k["notiz"])
                            if st.button(":material/delete: Entfernen", key=f"del_kontakt_{_k['id']}", width="stretch"):
                                st.session_state["notfallkontakte"] = [
                                    x for x in st.session_state["notfallkontakte"] if x["id"] != _k["id"]
                                ]
                                speichere_daten()
                                st.rerun()

            if _kontakte and _dokumente:
                st.markdown("<div style='height: 0.4rem'></div>", unsafe_allow_html=True)

            if _dokumente:
                st.markdown(
                    f'<div class="pinnwand-subtitel">{_PINNWAND_SVG_BILD}<span>Dokumente</span></div>',
                    unsafe_allow_html=True,
                )
                _spalten = st.columns(3)
                _sortiert = sorted(_dokumente, key=lambda x: x.get("hochgeladen_am", ""), reverse=True)
                for _i, _d in enumerate(_sortiert):
                    _pfad = os.path.join(DOKUMENTE_ORDNER, _d["dateiname"])
                    _ist_bild = _d["dateiname"].lower().endswith((".png", ".jpg", ".jpeg"))
                    _pinnwand_karten_stil(_d["id"], "karte_doku_")
                    with _spalten[_i % 3]:
                        with st.container(border=True, key=f"karte_doku_{_d['id']}"):
                            if os.path.exists(_pfad) and _ist_bild:
                                st.image(_pfad, width="stretch")
                            elif os.path.exists(_pfad):
                                st.markdown(":material/description: **PDF**")
                            else:
                                st.caption(
                                    ":material/warning: Datei fehlt (nach einem Neustart der App gehen "
                                    "hochgeladene Dateien verloren – bitte erneut hochladen)."
                                )
                            st.markdown(f'<div class="karten-titel">{_d["titel"]}</div>', unsafe_allow_html=True)
                            if _d.get("hochgeladen_am"):
                                st.caption(_d["hochgeladen_am"])
                            if os.path.exists(_pfad):
                                with open(_pfad, "rb") as _f:
                                    st.download_button(
                                        ":material/download: Herunterladen", _f.read(),
                                        file_name=_d.get("original_name") or _d["dateiname"],
                                        key=f"dl_doku_{_d['id']}", width="stretch",
                                    )
                            if st.button(":material/delete: Entfernen", key=f"del_doku_{_d['id']}", width="stretch"):
                                if os.path.exists(_pfad):
                                    try:
                                        os.remove(_pfad)
                                    except Exception:
                                        pass
                                st.session_state["dokumente"] = [
                                    x for x in st.session_state["dokumente"] if x["id"] != _d["id"]
                                ]
                                speichere_daten()
                                st.rerun()

    st.divider()

    # ---------- Neuer Eintrag ----------
    st.markdown("#### :material/add_circle: Neuer Eintrag")
    _neu_c0, _neu_c1, _neu_c2 = st.columns(3)

    with _neu_c0:
        with st.expander(":material/checklist: Checklisten-Punkt hinzufügen", expanded=False):
            st.caption(
                "Dinge, die bei jedem Wechsel mit umziehen sollen – z. B. Sportzeug, "
                "Medikamente, Kuscheltier, Ladekabel."
            )
            _chk_suffix = st.session_state["checkliste_form_key"]
            _chk_text = st.text_input(
                "Was soll mit?", key=f"chk_text_{_chk_suffix}", placeholder="z. B. Sportzeug",
            )
            if st.button(":material/add: Zur Liste hinzufügen", key="checkliste_speichern", type="primary"):
                if _chk_text.strip():
                    st.session_state["uebergabe_checkliste"].append({
                        "id": uuid.uuid4().hex[:8],
                        "text": _chk_text.strip(),
                        "erledigt": False,
                    })
                    st.session_state["checkliste_form_key"] += 1
                    speichere_daten()
                    st.rerun()
                else:
                    st.warning("Bitte einen Text eingeben.")

    with _neu_c1:
        with st.expander(":material/person_add: Notfallkontakt hinzufügen", expanded=False):
            st.caption(
                "Telefonnummern, die im Notfall schnell griffbereit sein sollten – z. B. "
                "Großeltern, Kinderarzt, Schule oder Kita."
            )
            _nk_suffix = st.session_state["nk_form_key"]
            _nk_name = st.text_input(
                "Name", key=f"nk_name_{_nk_suffix}", placeholder="z. B. Oma Erika",
            )
            _nk_rolle = st.text_input(
                "Rolle / Bezug", key=f"nk_rolle_{_nk_suffix}",
                placeholder="z. B. Großmutter, Kinderarzt, Schule",
            )
            _nk_telefon = st.text_input(
                "Telefonnummer", key=f"nk_telefon_{_nk_suffix}", placeholder="z. B. 0170 1234567",
            )
            _nk_notiz = st.text_input(
                "Notiz (optional)", key=f"nk_notiz_{_nk_suffix}", placeholder="z. B. nur werktags erreichbar",
            )
            if st.button(":material/add: Kontakt speichern", key="nk_speichern", type="primary"):
                if _nk_name.strip() and _nk_telefon.strip():
                    st.session_state["notfallkontakte"].append({
                        "id": uuid.uuid4().hex[:8],
                        "name": _nk_name.strip(),
                        "rolle": _nk_rolle.strip(),
                        "telefon": _nk_telefon.strip(),
                        "notiz": _nk_notiz.strip(),
                    })
                    st.session_state["nk_form_key"] += 1
                    speichere_daten()
                    st.rerun()
                else:
                    st.warning("Bitte mindestens Name und Telefonnummer angeben.")

    with _neu_c2:
        with st.expander(":material/upload_file: Dokument hochladen", expanded=False):
            st.caption(
                "Fotos oder PDFs von wichtigen Dokumenten – z. B. Stundenplan, Packliste für die "
                "Klassenfahrt, eine Seite aus dem Impfausweis."
            )
            _pw_suffix = st.session_state["pw_doku_form_key"]
            _pw_titel = st.text_input(
                "Titel", key=f"pw_doku_titel_{_pw_suffix}", placeholder="z. B. Stundenplan Mia",
            )
            _pw_datei = st.file_uploader(
                "Foto oder PDF", type=["png", "jpg", "jpeg", "pdf"],
                key=f"pw_doku_datei_{_pw_suffix}",
            )
            if st.button(":material/add: Hinzufügen", key="pw_doku_speichern", type="primary"):
                if _pw_datei is not None and _pw_titel.strip():
                    _ext = os.path.splitext(_pw_datei.name)[1].lower()
                    _neuer_dateiname = f"{uuid.uuid4().hex[:10]}{_ext}"
                    _pfad = os.path.join(DOKUMENTE_ORDNER, _neuer_dateiname)
                    with open(_pfad, "wb") as f:
                        f.write(_pw_datei.getbuffer())
                    st.session_state["dokumente"].append({
                        "id": uuid.uuid4().hex[:8],
                        "titel": _pw_titel.strip(),
                        "dateiname": _neuer_dateiname,
                        "original_name": _pw_datei.name,
                        "hochgeladen_am": dt.date.today().isoformat(),
                    })
                    st.session_state["pw_doku_form_key"] += 1
                    speichere_daten()
                    st.rerun()
                else:
                    st.warning("Bitte einen Titel eingeben und eine Datei auswählen.")

    speichere_daten()


def seite_einstellungen():
    st.subheader(":material/tune: Grundeinstellungen")
    st.caption(
        "Grundlegende Angaben für PatchEasy: Wie sollen die Elternteile in der App heißen "
        "und welche Farbe soll wer im Kalender bekommen? Wird automatisch gespeichert."
    )

    st.markdown("#### Elternteile")
    st.caption(
        "Standardmäßig „Elternteil 1” und „Elternteil 2” – hier könnt ihr stattdessen eure "
        "eigenen Namen oder Kürzel eintragen. Die Namen werden überall in der App verwendet."
    )

    _rn = st.session_state["rollennamen"]
    _rf = st.session_state["rollenfarben"]

    st.markdown(
        f"""
        <style>
        div[class*="st-key-pe_card_einst_1"], div[class*="st-key-pe_card_einst_2"] {{
            background: var(--pe-card);
            border: 1px solid var(--pe-border);
            border-radius: var(--pe-radius-md);
            box-shadow: var(--pe-shadow);
            padding: 1.1rem 1.2rem 1.3rem 1.2rem;
        }}
        div[class*="st-key-pe_card_einst_1"] {{ border-top: 5px solid {farbe(ELTERNTEIL_1)} !important; }}
        div[class*="st-key-pe_card_einst_2"] {{ border-top: 5px solid {farbe(ELTERNTEIL_2)} !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    _e1, _e2 = st.columns(2)
    with _e1:
        with st.container(key="pe_card_einst_1"):
            st.markdown(f"**{anzeige(ELTERNTEIL_1)}**")
            _neuer_name_1 = st.text_input(
                "Anzeigename", value=_rn.get(ELTERNTEIL_1, ELTERNTEIL_1), key="einst_name_1",
            )
            _neue_farbe_1 = st.color_picker(
                "Farbe", value=_rf.get(ELTERNTEIL_1, VATER_FARBE), key="einst_farbe_1",
            )
    with _e2:
        with st.container(key="pe_card_einst_2"):
            st.markdown(f"**{anzeige(ELTERNTEIL_2)}**")
            _neuer_name_2 = st.text_input(
                "Anzeigename", value=_rn.get(ELTERNTEIL_2, ELTERNTEIL_2), key="einst_name_2",
            )
            _neue_farbe_2 = st.color_picker(
                "Farbe", value=_rf.get(ELTERNTEIL_2, MUTTER_FARBE), key="einst_farbe_2",
            )

    _name_1_final = _neuer_name_1.strip() or ELTERNTEIL_1
    _name_2_final = _neuer_name_2.strip() or ELTERNTEIL_2
    _geaendert = False
    if _rn.get(ELTERNTEIL_1) != _name_1_final or _rn.get(ELTERNTEIL_2) != _name_2_final:
        st.session_state["rollennamen"] = {ELTERNTEIL_1: _name_1_final, ELTERNTEIL_2: _name_2_final}
        _geaendert = True
    if _rf.get(ELTERNTEIL_1) != _neue_farbe_1 or _rf.get(ELTERNTEIL_2) != _neue_farbe_2:
        st.session_state["rollenfarben"] = {ELTERNTEIL_1: _neue_farbe_1, ELTERNTEIL_2: _neue_farbe_2}
        _geaendert = True
    if _geaendert:
        speichere_daten()
        st.rerun()

    if _name_1_final.strip().lower() == _name_2_final.strip().lower():
        st.warning(
            "Beide Elternteile haben denselben Namen – zur besseren Unterscheidung empfiehlt "
            "sich ein unterschiedlicher Name.",
            icon=":material/warning:",
        )

    if st.button(":material/restart_alt: Auf Standardnamen & -farben zurücksetzen", key="einst_reset"):
        st.session_state["rollennamen"] = {ELTERNTEIL_1: ELTERNTEIL_1, ELTERNTEIL_2: ELTERNTEIL_2}
        st.session_state["rollenfarben"] = {ELTERNTEIL_1: VATER_FARBE, ELTERNTEIL_2: MUTTER_FARBE}
        for _k in ("einst_name_1", "einst_name_2", "einst_farbe_1", "einst_farbe_2"):
            st.session_state.pop(_k, None)
        speichere_daten()
        st.rerun()

    st.divider()
    st.caption(
        "Weitere Grundeinstellungen – Zeitraum, Wechselrhythmus, Kinder und mehr – findet ihr "
        "auf der Kalender- bzw. Finanzen-Seite."
    )


pg = st.navigation(
    [
        st.Page(seite_kalender, title="Kalender", icon=":material/calendar_month:", default=True),
        st.Page(seite_finanzen, title="Finanzen", icon=":material/account_balance_wallet:"),
        st.Page(seite_pinnwand, title="Pinnwand", icon=":material/push_pin:"),
        st.Page(seite_einstellungen, title="Einstellungen", icon=":material/tune:"),
    ],
    position="top",
)
pg.run()
