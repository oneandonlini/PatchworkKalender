"""
pb.py – Verbindung zwischen PatchEasy (Streamlit) und PocketBase.

Alle Anfragen laufen mit dem Ausweis (Token) der angemeldeten Person.
Was jemand sehen oder ändern darf, entscheidet PocketBase über die API-Regeln.
"""
import json

import requests
import streamlit as st

try:
    PB_URL = st.secrets["PB_URL"]
except Exception:
    PB_URL = "http://127.0.0.1:8090"

# Schlüssel aus speichere_daten(), die im Datensatz "plan" landen
PLAN_SCHLUESSEL = [
    "rollennamen", "rollenfarben", "start_date", "end_date", "ziel_vater_pct",
    "wechseltag", "wechselmodell", "wochenplan", "wechsel_start_parent",
    "wechselzeit", "wechselzeit_ausnahmen", "feste_wochentage",
]


class PBFehler(Exception):
    """PocketBase hat eine Anfrage abgelehnt."""

    def __init__(self, status, nachricht):
        super().__init__(f"{status}: {nachricht}")
        self.status = status


# ---------------------------------------------------------------- Grundfunktionen

def _anfrage(methode, pfad, **kwargs):
    headers = {"Authorization": st.session_state.get("pb_token", "")}
    try:
        r = requests.request(methode, f"{PB_URL}/api/{pfad}", headers=headers, timeout=10, **kwargs)
    except requests.ConnectionError:
        st.error("Die Datenbank ist gerade nicht erreichbar. Bitte später erneut versuchen.")
        st.stop()
    if r.status_code == 401:                       # Ausweis abgelaufen
        abmelden()
    if r.status_code >= 400:
        try:
            nachricht = r.json().get("message", r.text)
        except ValueError:
            nachricht = r.text
        raise PBFehler(r.status_code, nachricht)
    return r.json() if r.content else None


def liste(sammlung, filter=None, sort=None):
    """Alle Datensätze einer Sammlung, die die angemeldete Person sehen darf."""
    ergebnis, seite = [], 1
    while True:
        params = {"page": seite, "perPage": 500}
        if filter:
            params["filter"] = filter
        if sort:
            params["sort"] = sort
        antwort = _anfrage("GET", f"collections/{sammlung}/records", params=params)
        ergebnis.extend(antwort["items"])
        if seite >= antwort["totalPages"]:
            return ergebnis
        seite += 1


def anlegen(sammlung, daten):
    return _anfrage("POST", f"collections/{sammlung}/records", json=daten)


def aendern(sammlung, datensatz_id, daten):
    return _anfrage("PATCH", f"collections/{sammlung}/records/{datensatz_id}", json=daten)


def loeschen(sammlung, datensatz_id):
    return _anfrage("DELETE", f"collections/{sammlung}/records/{datensatz_id}")


# ---------------------------------------------------------------- Login

def abmelden():
    st.session_state.clear()
    st.rerun()


def login_seite():
    """Zeigt das Login-Formular und hält die App an, bis jemand angemeldet ist."""
    if "pb_token" in st.session_state:
        with st.sidebar:
            nutzer = st.session_state["pb_nutzer"]
            st.caption(f"Angemeldet als {nutzer.get('name') or nutzer['email']}")
            if st.button("Abmelden"):
                abmelden()
        return

    st.title("PatchEasy – Anmelden")
    with st.form("pb_login"):
        email = st.text_input("E-Mail")
        passwort = st.text_input("Passwort", type="password")
        absenden = st.form_submit_button("Anmelden")
    if absenden:
        try:
            r = requests.post(f"{PB_URL}/api/collections/users/auth-with-password",
                              json={"identity": email.strip().lower(), "password": passwort},
                              timeout=10)
        except requests.ConnectionError:
            st.error("Die Datenbank ist gerade nicht erreichbar.")
            st.stop()
        if r.status_code == 200:
            st.session_state["pb_token"] = r.json()["token"]
            st.session_state["pb_nutzer"] = r.json()["record"]
            st.rerun()
        st.error("E-Mail oder Passwort falsch.")
    st.stop()


# ---------------------------------------------------------------- Familie

def familie_waehlen():
    """Gibt die aktuelle Familie zurück. Wer zu mehreren gehört (z. B. als
    Bezugsperson), wählt in der Seitenleiste."""
    familien = liste("familie", sort="name")
    if not familien:
        st.info("Dein Konto ist noch keiner Familie zugeordnet. Bitte melde dich bei PatchEasy.")
        st.stop()

    nach_id = {f["id"]: f for f in familien}
    aktuell = st.session_state.get("pb_familie_id")
    if aktuell not in nach_id:
        aktuell = familien[0]["id"]
        st.session_state["pb_familie_id"] = aktuell

    if len(familien) > 1:
        with st.sidebar:
            auswahl = st.selectbox("Familie", list(nach_id),
                                   index=list(nach_id).index(aktuell),
                                   format_func=lambda i: nach_id[i]["name"])
        if auswahl != aktuell:                     # Familie gewechselt → alles neu laden
            behalten = {k: st.session_state[k] for k in ("pb_token", "pb_nutzer")}
            st.session_state.clear()
            st.session_state.update(behalten)
            st.session_state["pb_familie_id"] = auswahl
            st.rerun()
    return nach_id[aktuell]


def ist_elternteil(familie):
    return st.session_state["pb_nutzer"]["id"] in familie["eltern"]


# ---------------------------------------------------------------- Plan

def plan_laden(familie):
    """Liefert die gespeicherten Plan-Einstellungen im selben Format wie die
    frühere JSON-Datei (oder {}, wenn es noch keinen Plan gibt)."""
    treffer = liste("plan", filter=f'familie = "{familie["id"]}"')
    if not treffer:
        st.session_state["pb_plan_id"] = None
        return {}
    plan = treffer[0]
    st.session_state["pb_plan_id"] = plan["id"]
    einstellungen = plan.get("einstellungen") or {}
    st.session_state["pb_plan_stand"] = json.dumps(einstellungen, sort_keys=True)
    return einstellungen


def plan_speichern(familie, daten):
    """Schreibt die Plan-Einstellungen nach PocketBase – aber nur, wenn sich
    seit dem letzten Speichern etwas geändert hat."""
    if not ist_elternteil(familie):                # Bezugspersonen dürfen nur lesen
        return
    einstellungen = {k: daten[k] for k in PLAN_SCHLUESSEL if k in daten}
    stand = json.dumps(einstellungen, sort_keys=True)
    if stand == st.session_state.get("pb_plan_stand"):
        return
    try:
        if st.session_state.get("pb_plan_id"):
            aendern("plan", st.session_state["pb_plan_id"], {"einstellungen": einstellungen})
        else:
            eltern = familie["eltern"]
            neu = anlegen("plan", {
                "familie": familie["id"],
                "elternteil_1": eltern[0],
                "elternteil_2": eltern[1] if len(eltern) > 1 else "",
                "einstellungen": einstellungen,
            })
            st.session_state["pb_plan_id"] = neu["id"]
        st.session_state["pb_plan_stand"] = stand
    except PBFehler as fehler:
        st.warning(f"Der Plan konnte nicht gespeichert werden ({fehler}).")
