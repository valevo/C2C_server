#!/usr/bin/env bash
# Show the test pattern on the screens. Run on the NUC from a text console
# (Ctrl+Alt+F2), not over SSH:
#
#   ./run.sh            the MST hub's screens (HDMI port ignored)
#   ./run.sh all        every connected output
#   ./run.sh DP-1-2     just this output
#
# Any key or click closes the pattern and X. Afterwards the viewer's messages
# are printed again and saved, with xrandr's view of the screens, to
# /tmp/c2c-test-screen.log.
set -euo pipefail

DIR=$(cd "$(dirname "$0")" && pwd)

# X needs the virtual terminal we're sitting on
vt=$(fgconsole 2>/dev/null) || {
    echo "run.sh: run this from a text console on the NUC (Ctrl+Alt+F2), not over SSH"
    exit 1
}

# The display service would fight us for the screens
if systemctl is-active --quiet c2c-display; then
    echo "run.sh: stopping c2c-display"
    sudo systemctl stop c2c-display
fi

if ! python3 -c 'import tkinter' 2>/dev/null; then
    echo "run.sh: installing python3-tk"
    sudo apt-get install -y python3-tk
fi

# First free X display number (normally :0)
disp=0
while [ -e "/tmp/.X$disp-lock" ]; do disp=$((disp + 1)); done

LOG=/tmp/c2c-test-screen.log
# Inside X: record the outputs, run the viewer, record the layout it left behind
xinit /bin/bash -c '
    log=$1 dir=$2; shift 2
    { echo "== xrandr before =="; xrandr --props; echo "== show.py =="; } > "$log" 2>&1
    python3 "$dir/show.py" "$@" >> "$log" 2>&1
    { echo "== xrandr after =="; xrandr; } >> "$log" 2>&1
' _ "$LOG" "$DIR" "$@" -- ":$disp" "vt$vt" -nolisten tcp || true

echo
sed -n '/^== show.py ==$/,/^== xrandr after ==$/p' "$LOG" | sed '1d;$d'
echo "run.sh: full log (with EDIDs) in $LOG"
