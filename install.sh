#!/usr/bin/env bash
# Installation de letelephone sur Raspberry Pi OS (Debian/Ubuntu).
# Usage : sudo bash install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="letelephone"
INSTALL_USER="${SUDO_USER:-pi}"
INSTALL_HOME="$(getent passwd "$INSTALL_USER" | cut -d: -f6)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[+]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[x]${NC} $*" >&2; exit 1; }

# ── Vérifications préalables ──────────────────────────────────────────────────
[[ "$EUID" -ne 0 ]] && error "Ce script doit être lancé avec sudo : sudo bash install.sh"

if ! grep -qi "raspberry\|raspbian" /proc/cpuinfo /etc/os-release 2>/dev/null; then
    warn "Raspberry Pi non détecté — l'installation continue mais le GPIO ne fonctionnera pas."
fi

# ── Dépendances système ───────────────────────────────────────────────────────
info "Mise à jour de la liste des paquets..."
apt-get update -qq

info "Installation des dépendances système..."
apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-gpiozero \
    python3-lgpio \
    alsa-utils \
    ffmpeg

# ── Paquet Python ─────────────────────────────────────────────────────────────
info "Installation du paquet Python letelephone..."
pip3 install --break-system-packages -e "$REPO_DIR" --quiet

# ── Dossiers de données ───────────────────────────────────────────────────────
info "Création des dossiers de données..."
for dir in recordings logs; do
    mkdir -p "$REPO_DIR/$dir"
    chown "$INSTALL_USER:$INSTALL_USER" "$REPO_DIR/$dir"
done

# ── Service systemd ───────────────────────────────────────────────────────────
info "Installation du service systemd..."
SERVICE_SRC="$REPO_DIR/systemd/${SERVICE_NAME}.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}.service"

# Substituer le chemin réel et l'utilisateur dans le service
sed \
    -e "s|/home/pi/letelephone|$REPO_DIR|g" \
    -e "s|User=pi|User=$INSTALL_USER|g" \
    "$SERVICE_SRC" > "$SERVICE_DEST"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

# ── Permissions audio ─────────────────────────────────────────────────────────
if ! groups "$INSTALL_USER" | grep -q audio; then
    info "Ajout de $INSTALL_USER au groupe audio..."
    usermod -aG audio "$INSTALL_USER"
fi

# ── Résumé ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Installation terminée avec succès !           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Démarrer le service :"
echo "    sudo systemctl start $SERVICE_NAME"
echo ""
echo "  Consulter les logs :"
echo "    journalctl -u $SERVICE_NAME -f"
echo ""
echo "  Préparer un événement :"
echo "    Copier welcome.wav et couple.txt à la racine de la clé USB"
echo ""
