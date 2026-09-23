# Screen test

Check the screens (e.g. the DisplayPort screens behind the MST hub) without
the application.

On the NUC, from a text console (Ctrl+Alt+F2 — not over SSH):

```sh
cd scripts/test-screen
./run.sh            # the MST hub's screens, HDMI port ignored
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

The NUC8's HDMI port is ignored. It is named `DP-1` (or similar) like a real
DisplayPort output, because an on-board DP-to-HDMI converter drives it, so the
name prefix doesn't help. Screens behind the MST hub, however, always get
sub-numbered names (`DP-2-1`, `DP-2-2`, …) — even if the hub has HDMI sockets —
so when any are connected, only those are used. Without a hub, plain `DP-x`
screens are used unless their EDID identifies them as HDMI screens (see
`c2c/screens.py`).

After X closes, `run.sh` prints the viewer's messages again (which outputs
were found, ignored and used) and saves them to `/tmp/c2c-test-screen.log`,
together with `xrandr`'s view of the screens before and after, including
their EDIDs — send that file along when something looks wrong.

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
