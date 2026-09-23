# Screen test

Check the screens (e.g. the DisplayPort screens behind the MST hub) without
the application.

On the NUC, from a text console (Ctrl+Alt+F2 — not over SSH):

```sh
cd scripts/test-screen
./run.sh            # every connected DisplayPort output
./run.sh all        # every connected output, HDMI included
./run.sh DP-1-2     # one specific output
```

`run.sh` stops `c2c-display` if it's running, installs `python3-tk` if it's
missing, and starts a bare X server whose only client is the viewer
(`show.py`); X exits again when the viewer closes.

Without arguments `show.py` finds every connected DisplayPort output itself
(`DP-1-1`, `DP-1-2`, `DP-1-3` behind the MST hub), switches on any that X left
off, and shows the pattern on each, labelled with the output's name. After it
closes, the console shows which outputs were connected and which were used.

`test-pattern.png` is already here; for another resolution regenerate it with
`python3 make_pattern.py 3840x2160`.

If no DisplayPort output (or a named output) is connected, `show.py` exits and
prints `xrandr`'s list of outputs. Any key or mouse click closes it.

What to look at:

- **Label**: the output name on each screen — note which physical screen is
  which (for `C2C_OUTPUTS`). The same label on all three screens means the
  splitter mirrors instead of being an MST hub.
- **Border**: the white 1 px frame must be visible on all four edges (else the
  screen is overscanning — turn off "overscan"/"zoom" in the screen menu).
- **Circle**: round, not oval (else wrong mode or aspect scaling).
- **Colour bars**: white, yellow, cyan, green, magenta, red, blue, black.
- **Grey ramp**: smooth, no visible bands.
