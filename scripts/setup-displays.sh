#!/usr/bin/env bash
# Runs as the xinit session for c2c-display: arranges the screens behind the
# DisplayPort MST hub, disables blanking, hides the cursor, then execs the
# render application.
#
# Screens are detected automatically: every connected DisplayPort screen
# (DP-1-1, DP-1-2, DP-1-3 for a 3-port MST hub), placed left to right in name
# order. If the physical order differs, set C2C_OUTPUTS in /etc/c2c/c2c.env,
# e.g. C2C_OUTPUTS="DP-1-3 DP-1-1 DP-1-2". Check names with the test viewer
# (scripts/test-screen) or `DISPLAY=:0 xrandr`.
#
# HDMI screens are not part of the exhibition (see c2c/screens.py for how
# they're told apart — the NUC8's HDMI port is also named DP-x). One attached
# during build-up is placed to the right of the exhibition screens and left
# empty for dev windows (see docs/04-displays.md).
set -euo pipefail

SCREENS=${C2C_SCREENS:-3}   # number of exhibition screens expected
C2C_DIR=$(cd "$(dirname "$0")/.." && pwd)   # /opt/c2c (has the c2c package)
PY=/opt/c2c/.venv/bin/python
[ -x "$PY" ] || PY=python3

dp_screens() { (cd "$C2C_DIR" && "$PY" -m c2c.screens) }

# Screens that power up slower than the NUC (or an MST hub that enumerates
# late) aren't detected immediately after a power cut — retry for up to 60 s.
for i in $(seq 1 12); do
    connected=$(dp_screens 2>/dev/null | wc -l)
    [ "$connected" -ge "$SCREENS" ] && break
    echo "setup-displays: $connected/$SCREENS DisplayPort screens connected, waiting… ($i/12)"
    sleep 5
done
dp_screens 2>&1 >/dev/null | sed 's/^/setup-displays: /'    # log what was ignored, and why
if [ "$connected" -lt "$SCREENS" ]; then
    echo "setup-displays: only $connected/$SCREENS DisplayPort screens found"
    if [ "$connected" -eq 1 ]; then
        echo "setup-displays: a single screen usually means a mirroring splitter, not an MST hub"
    fi
    xrandr
    exit 1
fi

read -r -a outputs <<< "${C2C_OUTPUTS:-$(dp_screens 2>/dev/null | head -n "$SCREENS" | xargs)}"
echo "setup-displays: left to right: ${outputs[*]}"

# Side by side, each in its preferred mode
extras=()
for o in $(xrandr | awk '$2 == "connected" { print $1 }'); do
    [[ " ${outputs[*]} " == *" $o "* ]] || extras+=("$o")
done

# Anything else connected (the HDMI dev screen) is switched off first: the GPU
# drives at most 3 screens, and X may have given one of its pipes to the extra
args=()
for o in "${extras[@]}"; do args+=(--output "$o" --off); done
args+=(--output "${outputs[0]}" --auto --pos 0x0)
for ((n = 1; n < ${#outputs[@]}; n++)); do
    args+=(--output "${outputs[n]}" --auto --right-of "${outputs[n-1]}")
done
xrandr "${args[@]}"

# ...then re-added to the right of the exhibition screens if a pipe is left
last=${outputs[-1]}
for o in "${extras[@]}"; do
    if xrandr --output "$o" --auto --right-of "$last" 2>/dev/null; then
        echo "setup-displays: not an exhibition screen, placed right of $last: $o"
        last=$o
    else
        echo "setup-displays: not an exhibition screen, switched off (no display pipe left): $o"
    fi
done

# Never blank or power down
xset s off
xset s noblank
xset -dpms

# Hide the mouse cursor
unclutter -idle 0 &

# Hand over to the render application; it renders only to these outputs
export C2C_OUTPUTS="${outputs[*]}"
exec /opt/c2c/.venv/bin/python -m c2c.display
