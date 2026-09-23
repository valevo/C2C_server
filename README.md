# Comment2Conversation — Server Setup (Intel NUC 11 Essential)

Instructions, install scripts and config files for setting up an Intel NUC 11
Essential (SWNUC11ATKC4000, “Atlas Canyon”) as the server of the
*Comment2Conversation* interactive installation.

## What the machine does

- Maintains a small **SQLite database** of user inputs
- Receives user input over the **LAN** (HTTP API on the wired interface)
- Renders **image data to 3 screens** via DisplayPort + an MST hub
- Keeps an **outbound SSH reverse tunnel** open for remote maintenance

```
                                                       ┌──────────▶ screen 1
 visitors ──LAN──▶ ┌─────────────────────┐    ┌─────────┐ │
                   │  NUC  (c2c)         │─DP─▶ MST hub ├─┼──────────▶ screen 2
                   │  Debian 13 (trixie) │    └─────────┘ │
                   └─────────┬───────────┘                └──────────▶ screen 3
                             └──autossh reverse tunnel──▶ maintenance host
```

## Repository layout

| Path        | Contents                                                       |
|-------------|----------------------------------------------------------------|
| `docs/`     | Step-by-step setup guides, in order (`01-…` to `06-…`)         |
| `install/`  | `bootstrap.sh` provisioning script + package list              |
| `config/`   | Config files deployed to the machine (systemd, network, ssh)   |
| `scripts/`  | Runtime/maintenance helpers (display layout, DB backup)        |

## Quick start

1. Follow [`docs/01-hardware.md`](docs/01-hardware.md) (BIOS: auto power-on!)
   and [`docs/02-os-install.md`](docs/02-os-install.md) to install Debian.
2. Clone this repo onto the NUC and run the provisioning script:

   ```sh
   git clone <this-repo> && cd server
   sudo ./install/bootstrap.sh
   ```

3. Continue with [`docs/03-network.md`](docs/03-network.md),
   [`docs/04-displays.md`](docs/04-displays.md) and
   [`docs/05-ssh-tunnel.md`](docs/05-ssh-tunnel.md) to adapt the configs
   (IP addresses, tunnel host, screen layout) to the venue.
4. [`docs/06-operations.md`](docs/06-operations.md) covers day-to-day
   operation: logs, backups, updates, recovery.

## Conventions

- Everything installation-specific runs as the system user **`c2c`**.
- The application lives in `/opt/c2c`, its data (SQLite DB) in
  `/var/lib/c2c`, environment/secrets in `/etc/c2c/c2c.env` (not in git).
- Services are managed by systemd: `c2c-server` (API + DB),
  `c2c-display` (rendering to the screens), `c2c-tunnel` (maintenance SSH).
