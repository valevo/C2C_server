# 4 · Displays (3 screens)

## Cabling

- **Screen 1** ← HDMI 2.0a port
- **Screens 2 + 3** ← USB-C port → **DisplayPort MST hub** → 2× DP

All three appear as independent outputs to the Iris Plus 655 iGPU.
Connect all screens *before* booting — some MST hubs enumerate unreliably
when hot-plugged.

## Graphical stack

Minimal X11 session, no desktop environment, no display manager. The
`c2c-display` systemd service (see
[`config/systemd/c2c-display.service`](../config/systemd/c2c-display.service))
starts X as the `c2c` user on tty1 and runs the render application
fullscreen across all outputs.

The session applies [`scripts/setup-displays.sh`](../scripts/setup-displays.sh)
on start: it arranges the three outputs side-by-side with `xrandr`, disables
DPMS/blanking, and hides the cursor (`unclutter`).

## Adapting the layout

1. With the screens attached, list outputs:

   ```sh
   DISPLAY=:0 xrandr
   ```

   Typical names: `HDMI-1`, `DP-1-1`, `DP-1-2` (MST outputs get the
   `DP-1-x` sub-names).
2. Edit the output names / resolutions / positions at the top of
   `scripts/setup-displays.sh`.
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
