# 6 · Operations & maintenance

## Services

| Service       | Purpose                              |
|---------------|--------------------------------------|
| `c2c-server`  | Input API + SQLite database          |
| `c2c-display` | X session + rendering to the 3 screens |
| `c2c-tunnel`  | autossh reverse tunnel               |

```sh
systemctl status c2c-server c2c-display c2c-tunnel
journalctl -u c2c-server -f          # follow logs
sudo systemctl restart c2c-display   # e.g. after a screen was re-plugged
```

All services restart automatically on failure and start on boot; after a
power cut the installation must come back **with no human interaction**
(verify this once before opening: pull the plug, watch it recover).

## Database

- Lives at `/var/lib/c2c/c2c.sqlite`, owned by `c2c`.
- `scripts/backup-db.sh` writes a consistent snapshot (`sqlite3 .backup`)
  to `/var/lib/c2c/backups/` and prunes to the last 30. `bootstrap.sh`
  installs a systemd timer running it nightly.
- Pull a backup off the machine over the tunnel:

  ```sh
  scp -o ProxyJump=relayuser@relay.example.org -P 2222 \
      admin@localhost:/var/lib/c2c/backups/latest.sqlite .
  ```

## Updates

- Security updates: automatic (`unattended-upgrades`), no reboot.
- App updates: `git pull` in `/opt/c2c`, then `sudo systemctl restart c2c-server c2c-display`.
- OS reboots: only during maintenance windows; the installation recovers on
  its own, but stay on the tunnel until all three screens show content again.

## Troubleshooting quick list

| Symptom                     | First move                                              |
|-----------------------------|---------------------------------------------------------|
| A screen is black           | `journalctl -u c2c-display -e`; power-cycle MST hub; `systemctl restart c2c-display` |
| Inputs not arriving         | From a client: `curl http://192.168.10.10:8080/health`; check `ufw status`, `journalctl -u c2c-server` |
| Can't reach NUC remotely    | Tunnel/relay down — check relay host; on-site: connect keyboard+screen or SSH via LAN |
| Machine unreachable, on-site| Hold power 5 s, boot; services self-start                |
