#!/usr/bin/env bash
# Show the test pattern on the screens. Run on the NUC from a text console
# (Ctrl+Alt+F2), not over SSH:
#
#   ./run.sh            every connected DisplayPort output
#   ./run.sh all        every connected output
#   ./run.sh DP-1-2     just this output
#
# Any key or click closes the pattern and X.
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

[ -f "$DIR/test-pattern.png" ] || python3 "$DIR/make_pattern.py" 1920x1080 "$DIR/test-pattern.png"

# First free X display number (normally :0)
disp=0
while [ -e "/tmp/.X$disp-lock" ]; do disp=$((disp + 1)); done

xinit /usr/bin/python3 "$DIR/show.py" "$@" -- ":$disp" "vt$vt" -nolisten tcp
