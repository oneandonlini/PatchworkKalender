import streamlit as st
import pandas as pd
import datetime as dt
import calendar
import json
import os

DATEN_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gespeicherte_eingaben.json")
LOGO_DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

st.set_page_config(
    page_title="Patchwork-Kalender Prototyp",
    page_icon=LOGO_DATEI if os.path.exists(LOGO_DATEI) else "🧩",
    layout="wide",
)

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATSNAMEN = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]
VATER_FARBE = "#3D5A80"
MUTTER_FARBE = "#E07A5F"
FERIEN_FARBE = "#F2CC8F"

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

st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:2px;">
      <div style="width:44px;height:44px;border-radius:12px;flex-shrink:0;
                  background:linear-gradient(135deg, {VATER_FARBE} 50%, {MUTTER_FARBE} 50%);"></div>
      <div>
        <div style="font-size:2.1rem;font-weight:800;letter-spacing:-0.03em;line-height:1.15;">
          Patchwork-Kalender
        </div>
        <div style="font-size:0.95rem;font-weight:500;opacity:0.6;">
          Funktionsprototyp
          <span style="display:inline-block;margin-left:8px;padding:1px 9px;border-radius:999px;
                       background:{VATER_FARBE};color:white;font-size:0.7rem;font-weight:700;
                       vertical-align:middle;">Vater</span>
          <span style="display:inline-block;margin-left:4px;padding:1px 9px;border-radius:999px;
                       background:{MUTTER_FARBE};color:white;font-size:0.7rem;font-weight:700;
                       vertical-align:middle;">Mutter</span>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "Mockup zum Testen der Idee mit echten Daten – kein fertiges Produkt. "
    "Feste Wunsch-/Verzichtstage haben Vorrang, alle übrigen Tage werden am Wechseltag so "
    "verteilt, dass sich die Zielquote über den Zeitraum einpendelt."
)
st.info(
    "Vereinfachung in dieser Version: eine gemeinsame Rotation für alle Kinder. "
    "Unterschiedliche Zeiten je Kind wären ein möglicher nächster Schritt.",
    icon="ℹ️",
)

# ---------- Session State ----------
for key in ["wunsch_vater", "verzicht_vater", "wunsch_mutter", "verzicht_mutter"]:
    st.session_state.setdefault(key, [])
st.session_state.setdefault("ferien", [])  # list of dicts: name, start, end
st.session_state.setdefault("feiertage", [])  # list of dicts: name, datum (informativ, ohne Einfluss auf die Zuordnung)
st.session_state.setdefault("feste_wochentage", {})  # {Wochentagsname: "Vater"/"Mutter"}
st.session_state.setdefault("wechselmodell", "block")  # "block" oder "wochenplan"
st.session_state.setdefault(
    "wochenplan",
    {tag: "Wechselt wöchentlich" for tag in WOCHENTAGE},
)  # {Wochentagsname: "Vater"/"Mutter"/"Wechselt wöchentlich"}
st.session_state.setdefault("wechsel_start_parent", "Vater")
st.session_state.setdefault("wechselzeit", dt.time(18, 0))
st.session_state.setdefault("wechselzeit_ausnahmen", {})  # {datetime.date: datetime.time} - abweichende Uebergabezeit an einzelnen Tagen


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
                "erste_haelfte": f.get("erste_haelfte", "Vater"),
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
        fw = {k: v for k, v in daten["feste_wochentage"].items() if k in WOCHENTAGE and v in ("Vater", "Mutter")}
        st.session_state["feste_wochentage"] = fw
        # Widget-Keys VOR der Erzeugung der Selectboxen setzen, damit sie den gespeicherten Wert uebernehmen
        for tag in WOCHENTAGE:
            if tag in fw:
                st.session_state[f"fw_{tag}"] = "Immer Vater" if fw[tag] == "Vater" else "Immer Mutter"
    if "wechselmodell" in daten and daten["wechselmodell"] in ("block", "wochenplan"):
        st.session_state["wechselmodell"] = daten["wechselmodell"]
        st.session_state["wechselmodell_auswahl"] = (
            "Wochenplan (fester Rhythmus pro Wochentag)" if daten["wechselmodell"] == "wochenplan"
            else "Blockweise (Zielverteilung + Wechseltag)"
        )
    if "wochenplan" in daten:
        wp = {
            k: v for k, v in daten["wochenplan"].items()
            if k in WOCHENTAGE and v in ("Vater", "Mutter", "Wechselt wöchentlich")
        }
        st.session_state["wochenplan"] = {**st.session_state["wochenplan"], **wp}
        for tag in WOCHENTAGE:
            if tag in wp:
                st.session_state[f"wp_{tag}"] = wp[tag]
    if "wechsel_start_parent" in daten and daten["wechsel_start_parent"] in ("Vater", "Mutter"):
        st.session_state["wechsel_start_parent"] = daten["wechsel_start_parent"]
        st.session_state["wechsel_start_parent_auswahl"] = daten["wechsel_start_parent"]
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


def speichere_daten(start_date, end_date, ziel_vater_pct, wechseltag_label, wechselzeit):
    daten = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        # Im Wochenplan-Modus ist ziel_vater_pct nur eine rechnerische Schaetzung, kein
        # echter Nutzer-Eingabewert - den Schatten-Key nutzen, damit ein Moduswechsel den
        # zuletzt eingestellten Blockweise-Zielwert nicht ueberschreibt (siehe Kommentar
        # bei lade_gespeicherte_daten).
        "ziel_vater_pct": st.session_state.get("ziel_vater_persistent", ziel_vater_pct),
        # Gleicher Grund wie bei ziel_vater_pct: im Wochenplan-Modus ist wechseltag_label
        # nur ein Platzhalter, kein echter Eingabewert.
        "wechseltag": st.session_state.get("wechseltag_persistent", wechseltag_label),
        "wunsch_vater": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["wunsch_vater"]],
        "verzicht_vater": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["verzicht_vater"]],
        "wunsch_mutter": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["wunsch_mutter"]],
        "verzicht_mutter": [{"datum": e["datum"].isoformat(), "notiz": e.get("notiz", "")} for e in st.session_state["verzicht_mutter"]],
        "ferien": [
            {
                "name": f["name"], "start": f["start"].isoformat(), "end": f["end"].isoformat(),
                "regel": f.get("regel", "rotation"), "erste_haelfte": f.get("erste_haelfte", "Vater"),
                "ferien_wechseltag": f.get("ferien_wechseltag", wechseltag_label),
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
        "wechselzeit": wechselzeit.isoformat(),
        "wechselzeit_ausnahmen": {
            d.isoformat(): z.isoformat() for d, z in st.session_state["wechselzeit_ausnahmen"].items()
        },
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
        if st.button("➕ Hinzufügen", key=f"add_{key}"):
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


st.sidebar.header("Zeitraum & Grundregeln")
start_date = st.sidebar.date_input("Start", dt.date.today(), key="start_date_input")
end_date = st.sidebar.date_input("Ende", dt.date.today() + dt.timedelta(days=120), key="end_date_input")

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
          <div style="width:{_ziel_vorschau}%;background:{VATER_FARBE};
                      display:flex;align-items:center;justify-content:center;">
            {"Vater " + str(_ziel_vorschau) + "%" if _ziel_vorschau >= 12 else ""}
          </div>
          <div style="width:{100 - _ziel_vorschau}%;background:{MUTTER_FARBE};
                      display:flex;align-items:center;justify-content:center;">
            {"Mutter " + str(100 - _ziel_vorschau) + "%" if (100 - _ziel_vorschau) >= 12 else ""}
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
        "Ihr legt direkt fest, wer an welchem Wochentag dran ist – z. B. Mo–Mi immer "
        "Vater, Do–Fr immer Mutter. Tage, die wöchentlich wechseln (z. B. ein "
        "alternierendes Wochenende, oder eine komplette Wechselwoche), markiert ihr "
        "als „Wechselt wöchentlich”."
    )
    _wp_optionen = ["Vater", "Mutter", "Wechselt wöchentlich"]
    for _tag in WOCHENTAGE:
        _wp_gespeichert = st.session_state["wochenplan"].get(_tag, "Wechselt wöchentlich")
        _wp_index = _wp_optionen.index(_wp_gespeichert) if _wp_gespeichert in _wp_optionen else 2
        _wp_auswahl = st.sidebar.selectbox(_tag, _wp_optionen, index=_wp_index, key=f"wp_{_tag}")
        if _wp_auswahl != _wp_gespeichert:
            st.session_state["wochenplan"][_tag] = _wp_auswahl
            st.rerun()

    if any(v == "Wechselt wöchentlich" for v in st.session_state["wochenplan"].values()):
        _wsp_index = 0 if st.session_state["wechsel_start_parent"] == "Vater" else 1
        _wsp_auswahl = st.sidebar.radio(
            "Wer hat die wechselnden Tage ab dem Startdatum zuerst?", ["Vater", "Mutter"],
            index=_wsp_index, key="wechsel_start_parent_auswahl", horizontal=True,
        )
        if _wsp_auswahl != st.session_state["wechsel_start_parent"]:
            st.session_state["wechsel_start_parent"] = _wsp_auswahl
            st.rerun()

    # Platzhalter-Werte, damit speichere_daten() und die Ferien-Regel-UI (die einen
    # "normalen" Wechseltag als Vorschlagswert nutzt) unveraendert weiterlaufen koennen.
    _wp_schaetzung = [
        100 if v == "Vater" else 0 if v == "Mutter" else 50
        for v in (st.session_state["wochenplan"].get(t, "Wechselt wöchentlich") for t in WOCHENTAGE)
    ]
    ziel_vater_pct = round(sum(_wp_schaetzung) / 7)
    ziel_mutter_pct = 100 - ziel_vater_pct
    wechseltag_label = WOCHENTAGE[2]
    wechseltag_idx = 2
    st.sidebar.caption(f"→ ergibt rechnerisch ca. Vater {ziel_vater_pct}% / Mutter {ziel_mutter_pct}% im Durchschnitt.")

speichere_daten(start_date, end_date, ziel_vater_pct, wechseltag_label, wechselzeit)
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
        st.session_state["wechsel_start_parent"] = "Vater"
        st.session_state["wechselzeit"] = dt.time(18, 0)
        st.session_state["wechselzeit_ausnahmen"] = {}
        if os.path.exists(DATEN_DATEI):
            os.remove(DATEN_DATEI)
        st.rerun()

st.sidebar.header("Feste Wunsch-/Verzichtstage")
date_list_widget("Vater – Kind(er) sicher dabei", "wunsch_vater")
date_list_widget("Vater – bewusst nicht dabei", "verzicht_vater")
date_list_widget("Mutter – Kind(er) sicher dabei", "wunsch_mutter")
date_list_widget("Mutter – bewusst nicht dabei", "verzicht_mutter")

if st.session_state["wechselmodell"] == "block":
    st.sidebar.header("Feste Wochentage")
    with st.sidebar.expander("📌 Wiederkehrende Wochentags-Regel", expanded=False):
        st.caption(
            "Bestimmte Wochentage sind unabhängig vom Wechselrhythmus immer bei einem "
            "Elternteil (z. B. jeden Mittwoch bei Vater). Feste Wunsch-/Verzichtstage und "
            "Ferienregeln haben trotzdem immer Vorrang vor dieser Regel. Im Wochenplan-Modell "
            "legt ihr das direkt beim Wechselmodell weiter oben fest."
        )
        _fw_optionen = ["Wechselrhythmus", "Immer Vater", "Immer Mutter"]
        for _tag in WOCHENTAGE:
            _fw_gespeichert = st.session_state["feste_wochentage"].get(_tag)
            _fw_index = 0
            if _fw_gespeichert == "Vater":
                _fw_index = 1
            elif _fw_gespeichert == "Mutter":
                _fw_index = 2
            _fw_auswahl = st.selectbox(_tag, _fw_optionen, index=_fw_index, key=f"fw_{_tag}")
            _fw_neu = {"Immer Vater": "Vater", "Immer Mutter": "Mutter"}.get(_fw_auswahl)
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
    if bc1.button("📥 Ferien laden", disabled=bundesland is None, width="stretch"):
        vorhandene = {(f["name"], f["start"], f["end"]) for f in st.session_state["ferien"]}
        neu = 0
        for name, s, e in FERIEN_DATEN[bundesland]:
            eintrag_name = f"{name} ({bundesland})"
            if (eintrag_name, s, e) not in vorhandene:
                st.session_state["ferien"].append({"name": eintrag_name, "start": s, "end": e})
                neu += 1
        st.success(f"{neu} Ferienzeiten hinzugefügt.")
        st.rerun()
    if bc2.button("📥 Feiertage laden", disabled=bundesland is None, width="stretch"):
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
    "vater": "Komplett bei Vater",
    "mutter": "Komplett bei Mutter",
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
    f_erste_haelfte = "Vater"
    if f_regel == "haelftig":
        f_erste_haelfte = st.radio("Wer hat die erste Hälfte?", ["Vater", "Mutter"], key="f_erste_haelfte", horizontal=True)
    f_ferien_wechseltag = wechseltag_label
    if f_regel == "eigener_wechseltag":
        f_ferien_wechseltag = st.selectbox(
            "Wechseltag während dieser Ferienzeit", WOCHENTAGE, key="f_ferien_wechseltag",
        )
    if st.button("➕ Ferien hinzufügen"):
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
            aktuelle_erste = f.get("erste_haelfte", "Vater")
            neue_erste = st.radio(
                "Wer hat die erste Hälfte?", ["Vater", "Mutter"], horizontal=True,
                index=["Vater", "Mutter"].index(aktuelle_erste),
                key=f"erste_{eintrag_id}",
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
    if st.button("➕ Feiertag hinzufügen"):
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
        return "Vater"
    if regel == "mutter":
        return "Mutter"
    if regel == "haelftig":
        laenge = (periode["end"] - periode["start"]).days + 1
        erste_haelfte_tage = -(-laenge // 2)  # aufrunden
        grenze = periode["start"] + dt.timedelta(days=erste_haelfte_tage - 1)
        erste = periode.get("erste_haelfte", "Vater")
        zweite = "Mutter" if erste == "Vater" else "Vater"
        return erste if d <= grenze else zweite
    return None


def wochenplan_parent(d, start, wochenplan, wechsel_start_parent):
    """Elternteil laut Wochenplan-Modell: an festen Tagen immer derselbe Elternteil,
    an "wechselt woechentlich"-Tagen alterniert es im 7-Tage-Rhythmus ab dem Startdatum."""
    eintrag = wochenplan.get(WOCHENTAGE[d.weekday()], "Wechselt wöchentlich")
    if eintrag in ("Vater", "Mutter"):
        return eintrag
    wochen_index = (d - start).days // 7
    if wochen_index % 2 == 0:
        return wechsel_start_parent
    return "Mutter" if wechsel_start_parent == "Vater" else "Vater"


def berechne_plan(start, end, wechseltag_idx, ziel_vater_pct,
                   wunsch_vater, verzicht_vater, wunsch_mutter, verzicht_mutter, ferien_liste,
                   feste_wochentage=None, feiertage_lookup=None,
                   modus="block", wochenplan=None, wechsel_start_parent="Vater", wechselzeit=None,
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
    aktueller_block_owner = "Vater" if ziel_vater_pct >= (100 - ziel_vater_pct) else "Mutter"
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
                aktueller_block_owner = "Vater" if ziel_vater_frac >= ziel_mutter_frac else "Mutter"
            else:
                defizit_vater = ziel_vater_frac * gesamt_bisher - vater_tage
                defizit_mutter = ziel_mutter_frac * gesamt_bisher - mutter_tage
                aktueller_block_owner = "Vater" if defizit_vater >= defizit_mutter else "Mutter"

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
            parent = "Vater"
            grund = "Wunschtag Vater"
            notiz = wunsch_vater.get(d) or None
        elif will_mutter:
            parent = "Mutter"
            grund = "Wunschtag Mutter"
            notiz = wunsch_mutter.get(d) or None
        elif nicht_vater:
            parent = "Mutter"
            grund = "Verzichtstag Vater"
            notiz = verzicht_vater.get(d) or None
        elif nicht_mutter:
            parent = "Vater"
            grund = "Verzichtstag Mutter"
            notiz = verzicht_mutter.get(d) or None
        elif ferien_regel_parent(ferien_periode, d) is not None:
            parent = ferien_regel_parent(ferien_periode, d)
            grund = f"Ferienregel ({ferien_periode['name']})"
        elif modus == "block" and WOCHENTAGE[d.weekday()] in feste_wochentage:
            parent = feste_wochentage[WOCHENTAGE[d.weekday()]]
            grund = f"Feste Wochentagsregel ({WOCHENTAGE[d.weekday()]} immer {parent})"
        elif modus == "wochenplan":
            parent = wochenplan_parent(d, start, wochenplan, wechsel_start_parent)
            wp_eintrag = wochenplan.get(WOCHENTAGE[d.weekday()], "Wechselt wöchentlich")
            if wp_eintrag == "Wechselt wöchentlich":
                grund = f"Wochenplan ({WOCHENTAGE[d.weekday()]} wechselt wöchentlich)"
            else:
                grund = f"Wochenplan ({WOCHENTAGE[d.weekday()]} immer {wp_eintrag})"
        else:
            parent = aktueller_block_owner
            grund = "regulär (Wechselrhythmus)"

        if parent == "Vater":
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

# ---------- Auswertung ----------
gesamt = len(df)
vater_n = int((df["elternteil"] == "Vater").sum())
mutter_n = int((df["elternteil"] == "Mutter").sum())

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
    c2.metric("Vater", f"{vater_n} Tage", f"{vater_n/gesamt*100:.0f}% (ergibt sich aus Wochenplan)")
    c3.metric("Mutter", f"{mutter_n} Tage", f"{mutter_n/gesamt*100:.0f}% (ergibt sich aus Wochenplan)")
else:
    c2.metric("Vater", f"{vater_n} Tage", f"{vater_n/gesamt*100:.0f}% (Ziel {ziel_vater_pct}%)")
    c3.metric("Mutter", f"{mutter_n} Tage", f"{mutter_n/gesamt*100:.0f}% (Ziel {ziel_mutter_pct}%)")

ferien_df = df[df["ferien"].notna()]
if len(ferien_df) > 0:
    fv = int((ferien_df["elternteil"] == "Vater").sum())
    fm = int((ferien_df["elternteil"] == "Mutter").sum())
    c4.metric("Ferientage", f"{len(ferien_df)} Tage", f"Vater {fv} / Mutter {fm}")
    with st.expander("Ferien im Detail"):
        for name in ferien_df["ferien"].unique():
            sub = ferien_df[ferien_df["ferien"] == name]
            fv_n = int((sub["elternteil"] == "Vater").sum())
            fm_n = int((sub["elternteil"] == "Mutter").sum())
            st.write(f"**{name}**: {len(sub)} Tage – Vater {fv_n}, Mutter {fm_n}")
else:
    c4.metric("Ferientage", "keine erfasst")

feiertage_df = df[df["feiertag"].notna()]
if len(feiertage_df) > 0:
    with st.expander(f"🎉 Feiertage im Zeitraum ({len(feiertage_df)})"):
        st.caption("Rein informativ – zeigt zur Orientierung, bei wem das Kind an diesem Feiertag laut Plan ist.")
        for _, row in feiertage_df.sort_values("datum").iterrows():
            st.write(f"**{row['feiertag']}** – {row['datum'].strftime('%d.%m.%Y')} ({row['wochentag'][:2]}), bei {row['elternteil']}")

konflikte = df[df["konflikt"].notna()]
if len(konflikte) > 0:
    st.warning(f"⚠️ {len(konflikte)} Tag(e) mit widersprüchlichen Angaben – bitte manuell klären.")
    with st.expander("Konflikte anzeigen"):
        st.dataframe(konflikte[["datum", "wochentag", "konflikt"]], hide_index=True, use_container_width=True)

st.divider()

# ---------- Kalenderansicht ----------
st.subheader("Kalender")


legende = f"""
<div style="display:flex; gap:20px; margin-bottom:10px; font-size:14px; align-items:center; flex-wrap:wrap;">
  <div>🟦 Vater</div>
  <div>🟧 Mutter</div>
  <div>🏖️ Ferien</div>
  <div>🎉 Feiertag</div>
  <div>🎯 Wunschtag</div>
  <div>🚫 Verzichtstag</div>
  <div>⚠️ Konflikt</div>
  <div style="display:flex; align-items:center; gap:6px;">
    <span style="display:inline-block; width:20px; height:14px; border-radius:4px;
                 background:linear-gradient(90deg, {VATER_FARBE} 50%, {MUTTER_FARBE} 50%);"></span>
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
    if b1.button("🎯 Vater will", key="tag_panel_wv", width="stretch"):
        _tag_setzen("wunsch_vater", tag, notiz_eingabe)
    if b2.button("🎯 Mutter will", key="tag_panel_wm", width="stretch"):
        _tag_setzen("wunsch_mutter", tag, notiz_eingabe)
    b3, b4 = st.columns(2)
    if b3.button("🚫 Vater verzichtet", key="tag_panel_vv", width="stretch"):
        _tag_setzen("verzicht_vater", tag, notiz_eingabe)
    if b4.button("🚫 Mutter verzichtet", key="tag_panel_vm", width="stretch"):
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

            tooltip_teile = [f"{WOCHENTAGE[d.weekday()]}, {d.strftime('%d.%m.%Y')} – {info['elternteil']}"]
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

            farbe = VATER_FARBE if info["elternteil"] == "Vater" else MUTTER_FARBE
            # An einem Wechseltag zeigt die Zelle beide Farben (statt eines Icons): links die
            # Farbe des Elternteils, der das Kind bis zur Uebergabezeit noch hat, rechts die
            # Farbe des Elternteils, der ab der Uebergabezeit uebernimmt - intuitiver als ein
            # Symbol, die genaue Uhrzeit steht weiterhin im Tooltip/Popup.
            if info.get("wechsel") and isinstance(info.get("voriger_elternteil"), str):
                farbe_vorher = VATER_FARBE if info["voriger_elternteil"] == "Vater" else MUTTER_FARBE
                hintergrund = f"linear-gradient(90deg, {farbe_vorher} 50%, {farbe} 50%)"
            else:
                hintergrund = farbe
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
