#!/usr/bin/env bash
# Provisions a freshly installed Debian 13 (trixie) NUC as the c2c server.
# Idempotent — safe to re-run after editing configs. Run from the repo root:
#   sudo ./install/bootstrap.sh
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "run as root: sudo ./install/bootstrap.sh"; exit 1; }
REPO_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo "== packages =="
apt-get update
grep -vE '^\s*(#|$)' "$REPO_DIR/install/packages.txt" | xargs apt-get install -y

echo "== c2c user =="
id c2c &>/dev/null || useradd --system --create-home --shell /usr/sbin/nologin c2c
# tty access for the X session on tty1
usermod -aG video,tty c2c

echo "== directories =="
install -d -o c2c -g c2c /opt/c2c /opt/c2c/scripts /var/lib/c2c /var/lib/c2c/backups
install -d -o root -g c2c -m 750 /etc/c2c

echo "== environment file =="
if [ ! -f /etc/c2c/c2c.env ]; then
    install -o root -g c2c -m 640 "$REPO_DIR/config/c2c.env.example" /etc/c2c/c2c.env
    echo "   -> created /etc/c2c/c2c.env from example — EDIT IT (tunnel host etc.)"
fi

echo "== scripts =="
install -o c2c -g c2c -m 755 "$REPO_DIR"/scripts/*.sh /opt/c2c/scripts/

echo "== systemd units =="
install -m 644 "$REPO_DIR"/config/systemd/* /etc/systemd/system/
systemctl daemon-reload
systemctl enable c2c-server c2c-display c2c-tunnel c2c-backup.timer
# no getty fighting the X session on tty1
systemctl disable getty@tty1.service || true

echo "== firewall =="
ufw allow from 192.168.10.0/24 to any port 22 proto tcp
ufw allow from 192.168.10.0/24 to any port 8080 proto tcp
ufw --force enable

echo "== unattended security upgrades =="
dpkg-reconfigure -f noninteractive unattended-upgrades

echo "== ssh hardening =="
# only disable password auth once an admin key is in place
if [ -s /home/admin/.ssh/authorized_keys ]; then
    install -m 644 "$REPO_DIR/config/ssh/10-c2c.conf" /etc/ssh/sshd_config.d/10-c2c.conf
    systemctl reload ssh
else
    echo "   -> SKIPPED: no /home/admin/.ssh/authorized_keys yet."
    echo "      Add your public key, then re-run this script."
fi

echo
echo "Done. Remaining manual steps:"
echo "  1. Edit /etc/c2c/c2c.env (API port, tunnel host)"
echo "  2. Deploy static IP: cp config/network/interfaces.d/c2c-lan /etc/network/interfaces.d/ then remove the installer's stanza from /etc/network/interfaces and 'systemctl restart networking' (docs/03-network.md)"
echo "  3. Create the tunnel key + register it on the relay (docs/05-ssh-tunnel.md)"
echo "  4. Deploy the application to /opt/c2c (with a .venv), then reboot"
