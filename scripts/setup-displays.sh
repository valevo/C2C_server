#!/usr/bin/env bash
# Runs as the xinit session for c2c-display: arranges the three outputs,
# disables blanking, hides the cursor, then execs the render application.
#
# Adapt OUTPUTS/MODE/positions to the venue — check names with `DISPLAY=:0 xrandr`.
set -euo pipefail

OUT1=HDMI-1     # screen 1 (HDMI port)
OUT2=DP-1-1    # screen 2 (MST hub port 1)
OUT3=DP-1-2    # screen 3 (MST hub port 2)
MODE=1920x1080

# Screens that power up slower than the NUC aren't detected immediately after
# a power cut — retry for up to 60 s until all expected outputs are connected.
for i in $(seq 1 12); do
    connected=$(xrandr | grep -c ' connected') || true
    [ "$connected" -ge 3 ] && break
    echo "setup-displays: $connected/3 outputs connected, waiting… ($i/12)"
    sleep 5
done
[ "$connected" -ge 3 ] || { echo "setup-displays: only $connected/3 outputs found"; xrandr; exit 1; }

# Three screens side by side, left to right
xrandr \
    --output "$OUT1" --mode "$MODE" --pos 0x0 \
    --output "$OUT2" --mode "$MODE" --pos 1920x0 \
    --output "$OUT3" --mode "$MODE" --pos 3840x0

# Never blank or power down
xset s off
xset s noblank
xset -dpms

# Hide the mouse cursor
unclutter -idle 0 &

# Hand over to the render application (adjust to the real entry point)
exec /opt/c2c/.venv/bin/python -m c2c.display
