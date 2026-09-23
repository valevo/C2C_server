# Screen test

Check a single output (e.g. a DisplayPort screen behind the MST hub) without
the application.

On the NUC, from a text console (Ctrl+Alt+F2), with `c2c-display` stopped:

```sh
sudo systemctl stop c2c-display
sudo apt install python3-tk

cd scripts/test-screen
python3 make_pattern.py              # optional: test-pattern.png is already here
                                     # other resolution: python3 make_pattern.py 3840x2160

# start a bare X server whose only client is the viewer; exits when it closes
xinit /usr/bin/python3 "$PWD/show.py" DP-1-1 -- :0 vt$(fgconsole)
```

If the output name is wrong, `show.py` exits and prints `xrandr`'s list of
outputs. Any key or mouse click closes it.

What to look at:

- **Border**: the white 1 px frame must be visible on all four edges (else the
  screen is overscanning — turn off "overscan"/"zoom" in the screen menu).
- **Circle**: round, not oval (else wrong mode or aspect scaling).
- **Colour bars**: white, yellow, cyan, green, magenta, red, blue, black.
- **Grey ramp**: smooth, no visible bands.

To test all three screens at once, lay them out first (as `setup-displays.sh`
does) and run one viewer per output:

```sh
cat > /tmp/xtest.sh <<EOF
xrandr --output HDMI-1 --auto --pos 0x0 --output DP-1-1 --auto --pos 1920x0 --output DP-1-2 --auto --pos 3840x0
for o in HDMI-1 DP-1-1 DP-1-2; do python3 "$PWD/show.py" \$o & done
wait
EOF
xinit /bin/sh /tmp/xtest.sh -- :0 vt$(fgconsole)
```
