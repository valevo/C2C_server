#!/usr/bin/env bash
# Runs as the xinit session for c2c-display: arranges the screens behind the
# DisplayPort MST hub, disables blanking, hides the cursor, then execs the
# render application.
#
# Outputs are detected automatically: every connected DisplayPort output
# (DP-1-1, DP-1-2, DP-1-3 for a 3-port MST hub), placed left to right in name
# order. If the physical order differs, set C2C_OUTPUTS in /etc/c2c/c2c.env,
# e.g. C2C_OUTPUTS="DP-1-3 DP-1-1 DP-1-2". Check names with the test viewer
# (scripts/test-screen) or `DISPLAY=:0 xrandr`.
set -euo pipefail

SCREENS=${C2C_SCREENS:-3}   # number of screens expected

dp_outputs() { xrandr | awk '$2 == "connected" && $1 ~ /^DP/ { print $1 }' | sort -V; }

# Screens that power up slower than the NUC (or an MST hub that enumerates
# late) aren't detected immediately after a power cut — retry for up to 60 s.
for i in $(seq 1 12); do
    connected=$(dp_outputs | wc -l)
    [ "$connected" -ge "$SCREENS" ] && break
    echo "setup-displays: $connected/$SCREENS DisplayPort outputs connected, waiting… ($i/12)"
    sleep 5
done
if [ "$connected" -lt "$SCREENS" ]; then
    echo "setup-displays: only $connected/$SCREENS DisplayPort outputs found"
    if [ "$connected" -eq 1 ]; then
        echo "setup-displays: a single output usually means a mirroring splitter, not an MST hub"
    fi
    xrandr
    exit 1
fi

read -r -a outputs <<< "${C2C_OUTPUTS:-$(dp_outputs | head -n "$SCREENS" | xargs)}"
echo "setup-displays: left to right: ${outputs[*]}"

# Side by side, each in its preferred mode
args=(--output "${outputs[0]}" --auto --pos 0x0)
for ((n = 1; n < ${#outputs[@]}; n++)); do
    args+=(--output "${outputs[n]}" --auto --right-of "${outputs[n-1]}")
done
xrandr "${args[@]}"

# Never blank or power down
xset s off
xset s noblank
xset -dpms

# Hide the mouse cursor
unclutter -idle 0 &

# Hand over to the render application
exec /opt/c2c/.venv/bin/python -m c2c.display
