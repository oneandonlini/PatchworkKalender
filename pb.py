"""
pb.py – Verbindung zwischen PatchEasy (Streamlit) und PocketBase.

Alle Anfragen laufen mit dem Ausweis (Token) der angemeldeten Person.
Was jemand sehen oder ändern darf, entscheidet PocketBase über die API-Regeln.
"""
import json
from collections import Counter

import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    PB_URL = st.secrets["PB_URL"]
except Exception:
    PB_URL = "http://127.0.0.1:8090"

# "Angemeldet bleiben": der Ausweis wird in einem Browser-Cookie gemerkt
COOKIE_NAME = "patcheasy_sitzung"
COOKIE_TAGE = 7

# Schlüssel aus speichere_daten(), die im Datensatz "plan" landen
PLAN_SCHLUESSEL = [
    "rollennamen", "rollenfarben", "start_date", "end_date", "ziel_vater_pct",
    "wechseltag", "wechselmodell", "wochenplan", "wechsel_start_parent",
    "wechselzeit", "wechselzeit_ausnahmen", "feste_wochentage",
]


# Listen, die Eintrag fuer Eintrag in PocketBase liegen: {Sammlung: [Listen-Namen]}
# "eintraege" duerfen Eltern UND Bezugspersonen sehen.
LISTEN = {
    "eintraege": ["ferien", "feiertage",
                  "wunsch_vater", "verzicht_vater", "wunsch_mutter", "verzicht_mutter",
                  "notfallkontakte", "uebergabe_checkliste", "feste_infos"],
    # "eltern_eintraege" sehen NUR die Eltern (Finanzen, Journal).
    "eltern_eintraege": ["ausgaben", "ausgleichszahlungen", "journal_eintraege"],
}


def listen_schluessel():
    return [name for namen in LISTEN.values() for name in namen]


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


# ---------------------------------------------------------------- Aenderungsprotokoll

BEREICHE = {
    "ferien": "Kalender", "feiertage": "Kalender",
    "wunsch_vater": "Kalender", "verzicht_vater": "Kalender",
    "wunsch_mutter": "Kalender", "verzicht_mutter": "Kalender",
    "notfallkontakte": "Pinnwand", "uebergabe_checkliste": "Pinnwand", "feste_infos": "Pinnwand",
    "ausgaben": "Kosten", "ausgleichszahlungen": "Kosten",
    "journal_eintraege": "Journal",
}

PLAN_BEZEICHNUNGEN = {
    "rollennamen": "Namen", "rollenfarben": "Farben", "start_date": "Zeitraum",
    "end_date": "Zeitraum", "ziel_vater_pct": "Zielverteilung", "wechseltag": "Wechseltag",
    "wechselmodell": "Wechselmodell", "wochenplan": "Wochenplan",
    "wechsel_start_parent": "Wochenplan", "wechselzeit": "Wechselzeit",
    "wechselzeit_ausnahmen": "Wechselzeit an einzelnen Tagen",
    "feste_wochentage": "Feste Wochentage",
}


def _datum(text):
    """'2026-10-03' -> '03.10.2026' (alles andere unveraendert)."""
    if isinstance(text, str) and len(text) == 10 and text[4] == "-" and text[7] == "-":
        return f"{text[8:10]}.{text[5:7]}.{text[0:4]}"
    return text or ""


def _euro(betrag):
    try:
        return f"{float(betrag):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return ""


def _elternname(daten, nummer):
    namen = daten.get("rollennamen") or {}
    return namen.get(f"Elternteil {nummer}", f"Elternteil {nummer}")


def _beschreibe(name, e, daten):
    """Kurze, lesbare Bezeichnung eines Eintrags fuers Protokoll.
    Bewusst OHNE sensible Inhalte (Journal-Text, feste Infos wie Passwoerter)."""
    if name == "ferien":
        return f"Ferien „{e.get('name', '')}“ ({_datum(e.get('start'))}–{_datum(e.get('end'))})"
    if name == "feiertage":
        return f"Feiertag „{e.get('name', '')}“ ({_datum(e.get('datum'))})"
    if name.startswith(("wunsch_", "verzicht_")):
        art = "Wunschtag" if name.startswith("wunsch_") else "Verzichtstag"
        nummer = 1 if name.endswith("_vater") else 2
        return f"{art} {_elternname(daten, nummer)} am {_datum(e.get('datum'))}"
    if name == "notfallkontakte":
        return f"Notfallkontakt „{e.get('name', '')}“"
    if name == "uebergabe_checkliste":
        return f"Checklisten-Punkt „{e.get('text', '')}“"
    if name == "feste_infos":
        return "Feste Info"
    if name == "ausgaben":
        return f"Ausgabe „{e.get('beschreibung', '')}“ ({_euro(e.get('betrag'))})"
    if name == "ausgleichszahlungen":
        return f"Ausgleichszahlung über {_euro(e.get('betrag'))}"
    if name == "journal_eintraege":
        return f"Journal-Eintrag vom {_datum(e.get('datum'))}"
    return "Eintrag"


def protokollieren(familie, bereich, beschreibung):
    """Haelt fest, wer was geaendert hat. Darf die App nie blockieren."""
    if not ist_elternteil(familie):
        return
    nutzer = st.session_state["pb_nutzer"]
    try:
        anlegen("aenderungen", {
            "familie": familie["id"],
            "nutzer": nutzer["id"],
            "nutzer_name": nutzer.get("name") or nutzer.get("email", ""),
            "bereich": bereich,
            "beschreibung": beschreibung[:500],
        })
    except PBFehler:
        pass


def _listen_aenderung_beschreiben(name, neu, entfernt, daten):
    """Fasst die Unterschiede einer Liste in einem Satz zusammen."""
    neu = [json.loads(k) for k in neu]
    entfernt = [json.loads(k) for k in entfernt]
    # Gleiche ID in beiden Listen = derselbe Eintrag wurde geaendert
    ids_neu = {e.get("id") for e in neu if e.get("id")}
    geaendert = [e for e in neu if e.get("id") and e["id"] in {x.get("id") for x in entfernt}]
    neu = [e for e in neu if e not in geaendert]
    entfernt = [e for e in entfernt if not (e.get("id") and e["id"] in ids_neu)]

    teile = []
    for wort, eintraege in (("hinzugefügt", neu), ("geändert", geaendert), ("entfernt", entfernt)):
        if not eintraege:
            continue
        if name == "uebergabe_checkliste" and wort == "geändert":
            for e in eintraege:
                status = "abgehakt" if e.get("erledigt") else "Haken entfernt"
                teile.append(f"{_beschreibe(name, e, daten)} {status}")
        elif len(eintraege) > 3:
            teile.append(f"{len(eintraege)} Einträge {wort}")
        else:
            teile.extend(f"{_beschreibe(name, e, daten)} {wort}" for e in eintraege)
    return "; ".join(teile)


def verlauf_laden(familie, anzahl=100):
    """Die letzten Aenderungen einer Familie, neueste zuerst."""
    antwort = _anfrage("GET", "collections/aenderungen/records",
                       params={"filter": f'familie = "{familie["id"]}"', "sort": "-created",
                               "perPage": anzahl})
    return antwort["items"]


def plan_eltern():
    """IDs der Nutzer, die im Plan als Elternteil 1 bzw. 2 hinterlegt sind."""
    return st.session_state.get("pb_plan_eltern", ("", ""))


# ---------------------------------------------------------------- Login

def abmelden():
    st.session_state.clear()
    st.session_state["pb_abgemeldet"] = True      # in dieser Sitzung nicht automatisch neu anmelden
    st.session_state["pb_cookie_loeschen"] = True
    st.rerun()


def _cookie_schreiben(wert, max_age):
    """Setzt bzw. loescht das Cookie im Browser (ueber ein unsichtbares Mini-Skript)."""
    host = st.context.headers.get("Host", "")
    lokal = isinstance(host, str) and host.startswith(("localhost", "127.0.0.1"))
    eigenschaften = f"path=/; max-age={max_age}; SameSite=Strict" + ("" if lokal else "; Secure")
    zeile = json.dumps(f"{COOKIE_NAME}={wert}; {eigenschaften}")
    components.html(f"<script>parent.document.cookie = {zeile};</script>", height=0)


def _automatisch_anmelden():
    """Prueft beim Oeffnen der Seite, ob ein gemerkter Ausweis da ist, und erneuert ihn."""
    if st.session_state.get("pb_abgemeldet"):
        return
    gemerkt = st.context.cookies.get(COOKIE_NAME)
    if not isinstance(gemerkt, str) or not gemerkt:
        return
    try:
        r = requests.post(f"{PB_URL}/api/collections/users/auth-refresh",
                          headers={"Authorization": gemerkt}, timeout=10)
    except requests.ConnectionError:
        return
    if r.status_code == 200:
        st.session_state["pb_token"] = r.json()["token"]
        st.session_state["pb_nutzer"] = r.json()["record"]
        st.session_state["pb_cookie_neu"] = r.json()["token"]   # erneuerten Ausweis merken
    else:
        st.session_state["pb_cookie_loeschen"] = True           # abgelaufen → vergessen


def login_seite():
    """Zeigt das Login-Formular und hält die App an, bis jemand angemeldet ist."""
    if "pb_token" not in st.session_state:
        _automatisch_anmelden()

    if "pb_token" in st.session_state:
        if "pb_cookie_neu" in st.session_state:
            _cookie_schreiben(st.session_state.pop("pb_cookie_neu"), COOKIE_TAGE * 24 * 3600)
        with st.sidebar:
            nutzer = st.session_state["pb_nutzer"]
            st.caption(f"Angemeldet als {nutzer.get('name') or nutzer['email']}")
            if st.button("Abmelden"):
                abmelden()
        return

    if st.session_state.pop("pb_cookie_loeschen", False):
        _cookie_schreiben("", 0)

    st.title("PatchEasy – Anmelden")
    with st.form("pb_login"):
        email = st.text_input("E-Mail")
        passwort = st.text_input("Passwort", type="password")
        merken = st.checkbox("Angemeldet bleiben", value=True,
                             help="Nicht auf fremden oder gemeinsam genutzten Geräten.")
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
            st.session_state.pop("pb_abgemeldet", None)
            if merken:
                st.session_state["pb_cookie_neu"] = r.json()["token"]
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
            neu_laden(auswahl)
    with st.sidebar:
        if st.button("🔄 Aktualisieren", help="Holt Änderungen, die der andere Elternteil "
                                               "inzwischen gemacht hat."):
            neu_laden(aktuell)
    return nach_id[aktuell]


def neu_laden(familie_id):
    """Vergisst alle geladenen Daten (Login bleibt) und laedt sie frisch."""
    behalten = {k: st.session_state[k] for k in ("pb_token", "pb_nutzer")}
    st.session_state.clear()
    st.session_state.update(behalten)
    st.session_state["pb_familie_id"] = familie_id
    st.rerun()


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
    st.session_state["pb_plan_eltern"] = (plan.get("elternteil_1", ""), plan.get("elternteil_2", ""))
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
    vorher = json.loads(st.session_state.get("pb_plan_stand") or "{}")
    try:
        if st.session_state.get("pb_plan_id"):
            aendern("plan", st.session_state["pb_plan_id"], {"einstellungen": einstellungen})
            geaendert = sorted({PLAN_BEZEICHNUNGEN.get(k, k) for k in einstellungen
                                if _schluessel(einstellungen.get(k)) != _schluessel(vorher.get(k))})
            if geaendert:
                protokollieren(familie, "Einstellungen", "Geändert: " + ", ".join(geaendert))
        else:
            eltern = familie["eltern"]
            neu = anlegen("plan", {
                "familie": familie["id"],
                "elternteil_1": eltern[0],
                "elternteil_2": eltern[1] if len(eltern) > 1 else "",
                "einstellungen": einstellungen,
            })
            st.session_state["pb_plan_id"] = neu["id"]
            st.session_state["pb_plan_eltern"] = (neu.get("elternteil_1", ""), neu.get("elternteil_2", ""))
        st.session_state["pb_plan_stand"] = stand
    except PBFehler as fehler:
        st.warning(f"Der Plan konnte nicht gespeichert werden ({fehler}).")


# ---------------------------------------------------------------- Listen (Ferien, Wuensche ...)

def _vereinheitlichen(wert):
    """12.0 und 12 sind derselbe Betrag – sonst saehe ein unveraenderter Eintrag
    nach dem Laden wie geaendert aus und wuerde bei jedem Speichern neu angelegt."""
    if isinstance(wert, float) and wert.is_integer():
        return int(wert)
    if isinstance(wert, dict):
        return {k: _vereinheitlichen(v) for k, v in wert.items()}
    if isinstance(wert, list):
        return [_vereinheitlichen(v) for v in wert]
    return wert


def _schluessel(eintrag):
    return json.dumps(_vereinheitlichen(eintrag), sort_keys=True, ensure_ascii=False)


def listen_laden(familie):
    """Liefert {Listen-Name: [Eintraege]} im Format der frueheren JSON-Datei und
    merkt sich, welcher Eintrag zu welchem Datensatz in PocketBase gehoert."""
    ergebnis, stand = {}, {}
    for sammlung, namen in LISTEN.items():
        for name in namen:
            ergebnis[name], stand[name] = [], []
        for datensatz in liste(sammlung, filter=f'familie = "{familie["id"]}"', sort="created"):
            name = datensatz.get("liste")
            if name not in ergebnis:
                continue
            eintrag = datensatz.get("eintrag")
            if not isinstance(eintrag, dict) or not eintrag:
                continue                           # leere/kaputte Zeile ueberspringen
            ergebnis[name].append(eintrag)
            stand[name].append((_schluessel(eintrag), datensatz["id"]))
    st.session_state["pb_listen_stand"] = stand
    return ergebnis


def listen_speichern(familie, daten):
    """Vergleicht die Listen mit dem zuletzt gespeicherten Stand und schickt nur
    die Unterschiede: neue Eintraege anlegen, entfernte loeschen. Eine Aenderung an
    einem Eintrag ist dabei 'alten loeschen + neuen anlegen'."""
    if not ist_elternteil(familie) or "pb_listen_stand" not in st.session_state:
        return
    stand = st.session_state["pb_listen_stand"]
    for sammlung, namen in LISTEN.items():
        for name in namen:
            offen = Counter(_schluessel(e) for e in daten.get(name, []))
            behalten, zu_loeschen = [], []
            for schluessel, datensatz_id in stand.get(name, []):
                if offen[schluessel] > 0:
                    offen[schluessel] -= 1
                    behalten.append((schluessel, datensatz_id))
                else:
                    zu_loeschen.append((schluessel, datensatz_id))
            neue = list(offen.elements())
            try:
                for schluessel, datensatz_id in zu_loeschen:
                    loeschen(sammlung, datensatz_id)
                for schluessel in neue:
                    neu = anlegen(sammlung, {"familie": familie["id"], "liste": name,
                                             "eintrag": json.loads(schluessel)})
                    behalten.append((schluessel, neu["id"]))
            except PBFehler as fehler:
                st.warning(f"Änderungen an '{name}' konnten nicht gespeichert werden ({fehler}).")
                continue
            stand[name] = behalten
            if neue or zu_loeschen:
                text = _listen_aenderung_beschreiben(name, neue, [k for k, _ in zu_loeschen], daten)
                if text:
                    protokollieren(familie, BEREICHE.get(name, name), text)


# ---------------------------------------------------------------- Kinder

def kinder_laden(familie):
    """Vornamen der Kinder aus der Sammlung 'kinder' (in der App zaehlen nur die Namen)."""
    datensaetze = liste("kinder", filter=f'familie = "{familie["id"]}"', sort="created")
    st.session_state["pb_kinder_stand"] = [(d["vorname"], d["id"]) for d in datensaetze]
    namen = [d["vorname"] for d in datensaetze]
    return {"kinder": namen} if namen else {}


def kinder_speichern(familie, daten):
    if not ist_elternteil(familie) or "pb_kinder_stand" not in st.session_state:
        return
    stand = st.session_state["pb_kinder_stand"]
    namen = list(daten.get("kinder", []))
    if not stand and namen == ["Kind 1"]:          # nur der Platzhalter der App
        return
    offen = Counter(namen)
    behalten, zu_loeschen = [], []
    for vorname, datensatz_id in stand:
        if offen[vorname] > 0:
            offen[vorname] -= 1
            behalten.append((vorname, datensatz_id))
        else:
            zu_loeschen.append(datensatz_id)
    try:
        for datensatz_id in zu_loeschen:
            loeschen("kinder", datensatz_id)
        for vorname in offen.elements():
            neu = anlegen("kinder", {"familie": familie["id"], "vorname": vorname})
            behalten.append((vorname, neu["id"]))
    except PBFehler as fehler:
        st.warning(f"Änderungen an den Kindern konnten nicht gespeichert werden ({fehler}).")
        return
    st.session_state["pb_kinder_stand"] = behalten
    hinzu = list(offen.elements())
    weg = [v for v, i in stand if i in zu_loeschen]
    if hinzu or weg:
        teile = [f"„{v}“ hinzugefügt" for v in hinzu] + [f"„{v}“ entfernt" for v in weg]
        protokollieren(familie, "Kinder", "Kind " + "; ".join(teile))
