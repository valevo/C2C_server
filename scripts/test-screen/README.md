# Screen test

Check the screens (e.g. the DisplayPort screens behind the MST hub) without
the application.

On the NUC, from a text console (Ctrl+Alt+F2 — not over SSH):

```sh
cd scripts/test-screen
./run.sh            # every connected DisplayPort screen, HDMI ignored
./run.sh all        # every connected output, HDMI included
./run.sh DP-1-2     # one specific output
```

`run.sh` stops `c2c-display` if it's running, installs `python3-tk` if it's
missing, and starts a bare X server whose only client is the viewer
(`show.py`); X exits again when the viewer closes.

Without arguments `show.py` finds every connected DisplayPort screen itself
(`DP-1-1`, `DP-1-2`, `DP-1-3` behind the MST hub), arranges them side by side
in name order and stretches one test pattern across all of them: colour bars,
grid and grey ramp continue from screen to screen, while each screen gets its
own border and circle and is labelled with its output name. After it closes,
the console shows which outputs were connected, which were ignored and which
were used.

The pattern is generated to fit the row of screens (a few seconds the first
time, then cached in `/tmp`).

HDMI screens are ignored. On the NUC8 that takes more than looking at the
output name: its HDMI port is driven by an on-board DP-to-HDMI converter, so
X calls it `DP-1` (or similar) too. `show.py` therefore reads each screen's
EDID and skips screens that identify as HDMI — which also skips an HDMI screen
on a DP-to-HDMI adapter. With only an HDMI screen attached, nothing is shown
and X exits straight away.

The NUC8's GPU drives at most 3 screens, so with the MST hub's three screens
and the HDMI screen connected, the HDMI screen is switched off while the test
runs.

`test-pattern.png` is a single-screen copy of the pattern for viewing
elsewhere; make others with `python3 make_pattern.py 3840x2160` or, for a row,
`python3 make_pattern.py 1920+1920+1920x1080 row.png`.

If no DisplayPort output (or a named output) is connected, `show.py` exits and
prints `xrandr`'s list of outputs. Any key or mouse click closes it.

What to look at:

- **Row**: the bars, grid lines and grey ramp line up across the screen
  edges; if not, the screens are in the wrong order (set `C2C_OUTPUTS`).
- **Label**: the output name on each screen — note which physical screen is
  which (for `C2C_OUTPUTS`). The same label on all three screens means the
  splitter mirrors instead of being an MST hub.
- **Border**: the white 1 px frame must be visible on all four edges (else the
  screen is overscanning — turn off "overscan"/"zoom" in the screen menu).
- **Circle**: round, not oval (else wrong mode or aspect scaling).
- **Colour bars**: white, yellow, cyan, green, magenta, red, blue, black.
- **Grey ramp**: smooth, no visible bands.
