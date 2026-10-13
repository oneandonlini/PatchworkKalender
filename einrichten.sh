#!/usr/bin/env bash
# =============================================================================
#  PatchEasy – Einrichtung des Servers (Ubuntu 24.04)
#
#  Richtet ein: PocketBase, die Streamlit-App, HTTPS (Caddy), Firewall und
#  automatische Sicherheitsupdates. Kann gefahrlos mehrfach ausgefuehrt werden.
#
#  Aufruf auf dem Server (als root):   bash einrichten.sh
# =============================================================================
set -euo pipefail

DOMAIN="app.patcheasy.de"
REPO="https://github.com/oneandonlini/PatchworkKalender.git"
BRANCH="pocketbase"
PB_VERSION="0.40.4"

BENUTZER="patcheasy"
BASIS="/opt/patcheasy"
PB_ORDNER="$BASIS/pocketbase"
APP_ORDNER="$BASIS/app"
VENV="$BASIS/venv"

schritt() { echo; echo "==> $*"; }

if [[ $EUID -ne 0 ]]; then
  echo "Bitte als root ausfuehren (Anmeldung mit: ssh root@<IP-Adresse>)."
  exit 1
fi

# ----------------------------------------------------------------------------
schritt "1/8 System aktualisieren und Grundpakete installieren"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get upgrade -yq
apt-get install -yq python3 python3-venv python3-pip git unzip curl ufw \
  unattended-upgrades debian-keyring debian-archive-keyring apt-transport-https gnupg

# ----------------------------------------------------------------------------
schritt "2/8 Automatische Sicherheitsupdates einschalten"
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

# ----------------------------------------------------------------------------
schritt "3/8 Eigenen Systembenutzer '$BENUTZER' anlegen (ohne Login)"
if ! id "$BENUTZER" &>/dev/null; then
  useradd --system --create-home --home-dir "$BASIS" --shell /usr/sbin/nologin "$BENUTZER"
fi
mkdir -p "$BASIS"
chown "$BENUTZER:$BENUTZER" "$BASIS"
chmod 750 "$BASIS"

# ----------------------------------------------------------------------------
schritt "4/8 PocketBase $PB_VERSION installieren"
mkdir -p "$PB_ORDNER"
if [[ ! -x "$PB_ORDNER/pocketbase" ]] || ! "$PB_ORDNER/pocketbase" --version | grep -q "$PB_VERSION"; then
  tmp=$(mktemp -d)
  curl -fsSL -o "$tmp/pb.zip" \
    "https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_linux_amd64.zip"
  unzip -oq "$tmp/pb.zip" -d "$tmp"
  install -m 755 "$tmp/pocketbase" "$PB_ORDNER/pocketbase"
  rm -rf "$tmp"
fi
chown -R "$BENUTZER:$BENUTZER" "$PB_ORDNER"

if ! sudo -u "$BENUTZER" test -f "$PB_ORDNER/pb_data/data.db"; then
  echo
  echo "Jetzt das Admin-Konto fuer PocketBase anlegen."
  read -rp  "  E-Mail-Adresse fuer den Admin: " PB_EMAIL
  while true; do
    read -rsp "  Passwort (mind. 10 Zeichen, wird nicht angezeigt): " PB_PW; echo
    read -rsp "  Passwort wiederholen: " PB_PW2; echo
    if [[ "$PB_PW" == "$PB_PW2" && ${#PB_PW} -ge 10 ]]; then break; fi
    echo "  Passwoerter stimmen nicht ueberein oder sind zu kurz. Bitte nochmal."
  done
  sudo -u "$BENUTZER" "$PB_ORDNER/pocketbase" superuser upsert "$PB_EMAIL" "$PB_PW" \
    --dir="$PB_ORDNER/pb_data" >/dev/null
  unset PB_PW PB_PW2
  echo "  Admin-Konto angelegt."
fi

cat > /etc/systemd/system/patcheasy-pocketbase.service <<EOF
[Unit]
Description=PatchEasy PocketBase (nur intern erreichbar)
After=network.target

[Service]
Type=simple
User=$BENUTZER
Group=$BENUTZER
ExecStart=$PB_ORDNER/pocketbase serve --http=127.0.0.1:8090 --dir=$PB_ORDNER/pb_data
Restart=always
RestartSec=5
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
EOF

# ----------------------------------------------------------------------------
schritt "5/8 App von GitHub holen (Zweig '$BRANCH') und Python-Pakete installieren"
if [[ -d "$APP_ORDNER/.git" ]]; then
  sudo -u "$BENUTZER" git -C "$APP_ORDNER" fetch -q origin "$BRANCH"
  sudo -u "$BENUTZER" git -C "$APP_ORDNER" reset -q --hard "origin/$BRANCH"
else
  sudo -u "$BENUTZER" git clone -q --branch "$BRANCH" "$REPO" "$APP_ORDNER"
fi
[[ -d "$VENV" ]] || sudo -u "$BENUTZER" python3 -m venv "$VENV"
sudo -u "$BENUTZER" "$VENV/bin/pip" install -q --upgrade pip
sudo -u "$BENUTZER" "$VENV/bin/pip" install -q -r "$APP_ORDNER/requirements.txt"

cat > /etc/systemd/system/patcheasy-app.service <<EOF
[Unit]
Description=PatchEasy App (Streamlit)
After=network.target patcheasy-pocketbase.service
Requires=patcheasy-pocketbase.service

[Service]
Type=simple
User=$BENUTZER
Group=$BENUTZER
WorkingDirectory=$APP_ORDNER
Environment=PYTHONUNBUFFERED=1
ExecStart=$VENV/bin/python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501 --server.headless=true --browser.gatherUsageStats=false
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Hilfsbefehl fuer spaetere Updates
cat > /usr/local/bin/patcheasy-aktualisieren <<EOF
#!/usr/bin/env bash
# Holt den neuesten Stand des Zweigs '$BRANCH' von GitHub und startet die App neu.
set -euo pipefail
sudo -u $BENUTZER git -C $APP_ORDNER fetch -q origin $BRANCH
sudo -u $BENUTZER git -C $APP_ORDNER reset -q --hard origin/$BRANCH
sudo -u $BENUTZER $VENV/bin/pip install -q -r $APP_ORDNER/requirements.txt
systemctl restart patcheasy-app
echo "App aktualisiert: \$(sudo -u $BENUTZER git -C $APP_ORDNER log -1 --format='%h %s (%cr)')"
EOF
chmod 755 /usr/local/bin/patcheasy-aktualisieren

# ----------------------------------------------------------------------------
schritt "6/8 Caddy installieren (Webserver mit automatischem HTTPS)"
if ! command -v caddy &>/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
    | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
    > /etc/apt/sources.list.d/caddy-stable.list
  chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -q
  apt-get install -yq caddy
fi

cat > /etc/caddy/Caddyfile <<EOF
$DOMAIN {
	encode gzip
	reverse_proxy 127.0.0.1:8501
	header {
		Strict-Transport-Security "max-age=31536000"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "strict-origin-when-cross-origin"
		-Server
	}
}
EOF

# ----------------------------------------------------------------------------
schritt "7/8 Firewall: nur SSH (22), HTTP (80) und HTTPS (443) offen"
ufw allow OpenSSH >/dev/null
ufw allow 80/tcp >/dev/null
ufw allow 443/tcp >/dev/null
ufw --force enable >/dev/null
ufw status | sed 's/^/  /'

# ----------------------------------------------------------------------------
schritt "8/8 Dienste starten"
systemctl daemon-reload
systemctl enable --now patcheasy-pocketbase >/dev/null 2>&1
systemctl restart patcheasy-pocketbase
systemctl enable --now patcheasy-app >/dev/null 2>&1
systemctl restart patcheasy-app
systemctl reload caddy || systemctl restart caddy
sleep 5

echo
echo "-----------------------------------------------------------------------"
for dienst in patcheasy-pocketbase patcheasy-app caddy; do
  printf "  %-24s %s\n" "$dienst" "$(systemctl is-active "$dienst")"
done

SERVER_IP=$(hostname -I | awk '{print $1}')
DNS_IP=$(getent ahostsv4 "$DOMAIN" | awk 'NR==1{print $1}' || true)
if [[ "$DNS_IP" != "$SERVER_IP" ]]; then
  echo
  echo "  HINWEIS: $DOMAIN zeigt noch nicht auf diesen Server"
  echo "  (DNS: ${DNS_IP:-nicht gefunden}, Server: $SERVER_IP)."
  echo "  Sobald der DNS-Eintrag stimmt, holt Caddy das HTTPS-Zertifikat von selbst."
fi
echo
echo "  Fertig! Die App ist erreichbar unter:  https://$DOMAIN"
echo "  Spaetere Updates einspielen mit:       patcheasy-aktualisieren"
echo "-----------------------------------------------------------------------"
