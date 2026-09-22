# 2 · OS installation

We use **Debian 13 (trixie)** (security support to 2028, LTS to 2030) plus a
minimal graphical stack for the screens — no full desktop environment.

## Install

1. Write the Debian 13 **netinst** ISO to a USB stick
   (`dd` / balenaEtcher / Ventoy).
2. Boot the NUC from USB (F10 for boot menu), choose *Install*
   (text-mode is fine).
3. Choices during install:
   - Hostname: `c2c-server`
   - **Leave the root password empty** — the installer then disables the
     root account and gives the first user `sudo` (with a root password set,
     Debian does *not* add the user to `sudo`)
   - User: `admin` (personal admin account; the app runs as `c2c`, created later)
   - Guided partitioning, entire M.2 SSD, **no LVM/encryption** (machine must
     boot unattended after power loss — no one is there to type a passphrase)
   - Software selection (tasksel): **uncheck all desktop environments**,
     check **SSH server** and **standard system utilities**
4. First boot, copy your SSH key over, then update:

   ```sh
   # from your machine:
   ssh-copy-id admin@<nuc-ip>

   # on the NUC:
   sudo apt update && sudo apt full-upgrade -y
   sudo reboot
   ```

## Provision

Clone this repository and run the bootstrap script — it installs packages
(`install/packages.txt`), creates the `c2c` user, deploys the configs from
`config/` and enables the systemd services:

```sh
git clone <this-repo> c2c-server-setup
cd c2c-server-setup
sudo ./install/bootstrap.sh
```

The script is idempotent — safe to re-run after changing configs.

## Unattended operation

`bootstrap.sh` enables `unattended-upgrades` for security patches only.
Kernel updates are installed but the machine is **not** auto-rebooted; reboot
manually during maintenance windows (see `docs/06-operations.md`).
