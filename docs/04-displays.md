# 4 · Displays (3 screens)

## Cabling

- **Screens 1–3** ← DisplayPort port → **3-port DisplayPort MST hub** → 3× DP

With an MST hub all three appear as independent outputs (`DP-1-1`, `DP-1-2`,
`DP-1-3`). A plain *splitter* instead shows up as a single output and mirrors
the same picture on all three screens — check with the test viewer in
[`scripts/test-screen`](../scripts/test-screen/README.md): three different
labels = MST, the same label everywhere = splitter.

Connect all screens *before* booting — some MST hubs enumerate unreliably
when hot-plugged.

## Graphical stack

Minimal X11 session, no desktop environment, no display manager. The
`c2c-display` systemd service (see
[`config/systemd/c2c-display.service`](../config/systemd/c2c-display.service))
starts X as the `c2c` user on tty1 and runs the render application
fullscreen across all outputs.

The session applies [`scripts/setup-displays.sh`](../scripts/setup-displays.sh)
on start: it detects the connected DisplayPort outputs and arranges them
side-by-side with `xrandr` (each in its preferred mode), disables
DPMS/blanking, and hides the cursor (`unclutter`).

It then hands over to [`c2c/display.py`](../c2c/display.py) (`python -m c2c.display`),
which reads the arranged screens back from `xrandr --listmonitors` and opens one
Chromium kiosk window per screen on `C2C_DISPLAY_URL` (from `/etc/c2c/c2c.env`),
appending `screen=1..3` (left to right). It waits for the page to be reachable
first and relaunches any window that exits.

## Adapting the layout

1. With the screens attached, list outputs:

   ```sh
   DISPLAY=:0 xrandr
   ```

   Typical names: `DP-1-1`, `DP-1-2`, `DP-1-3` (MST outputs get the
   `DP-1-x` sub-names). The test viewer shows each name on its screen.
2. By default the outputs are placed left to right in name order. If the
   screens are cabled in a different order, set `C2C_OUTPUTS` in
   `/etc/c2c/c2c.env`, e.g. `C2C_OUTPUTS="DP-1-3 DP-1-1 DP-1-2"`.
3. Restart the display service: `sudo systemctl restart c2c-display`.

The script exits with an error (and the service log shows it) if an expected
output is missing — the most common cause is an MST hub that didn't
enumerate; power-cycle the hub and restart the service.

## Things that will bite you

- **EDID after power loss**: screens that power up slower than the NUC may
  not be detected. `c2c-display` retries for 60 s before giving up;
  if a venue has this problem chronically, add `Restart` timing in the unit
  or an EDID emulator dongle.
- **Blanking**: DPMS and console blanking are disabled by the setup script;
  also disable any "auto standby / eco mode" *in the screens' own menus*.
