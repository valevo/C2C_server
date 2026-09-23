#!/usr/bin/env python3
"""Stretch a test pattern across X outputs, each labelled with the output's name.

    python3 show.py [OUTPUT ... | all] [--image FILE]

    (no output)   every connected DisplayPort screen (DP-1-1, DP-1-2, ...);
                  HDMI screens are ignored, including ones on the NUC8's HDMI
                  port, which Linux also names DP-x (see c2c/screens.py)
    all           every connected output, HDMI included
    OUTPUT ...    just these, e.g.  python3 show.py DP-1-1

The chosen outputs are arranged side by side (in the order given, else name
order) and one pattern the size of the whole row is drawn across them: colour
bars, grid and grey ramp continue from screen to screen, and each screen gets
its own border and circle. Other connected outputs are
placed to the right if the GPU has a display pipe left for them (the NUC8
drives at most 3 screens), else switched off.

--image FILE shows FILE across the row instead, unscaled, from the top left.
Needs a running X server (see README.md) and python3-tk. Any key or click quits.
"""

import subprocess
import sys
import tempfile
import tkinter as tk
from pathlib import Path

import make_pattern

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # repo root, for c2c.screens
from c2c.screens import connected, dp_screens  # noqa: E402


def arrange(targets: list[str], others: list[str]) -> None:
    """Targets side by side from 0x0, each in its preferred mode. Others are switched
    off first (they may hold a display pipe a target needs), then re-added to the
    right one by one while the GPU still has a pipe free."""
    args = [a for n in others for a in ("--output", n, "--off")]
    args += ["--output", targets[0], "--auto", "--pos", "0x0"]
    for prev, name in zip(targets, targets[1:]):
        args += ["--output", name, "--auto", "--right-of", prev]
    subprocess.run(["xrandr", *args], check=True)
    last = targets[-1]
    for name in others:
        if subprocess.run(["xrandr", "--output", name, "--auto", "--right-of", last],
                          capture_output=True).returncode == 0:
            print(f"{name}: placed right of the pattern", flush=True)
            last = name
        else:
            print(f"{name}: switched off (no display pipe left)", flush=True)


def pattern(widths: list[int], h: int) -> str:
    """Test pattern for a row of screens, generated once and cached in /tmp."""
    size = "+".join(map(str, widths)) + f"x{h}"
    path = Path(tempfile.gettempdir()) / f"c2c-test-pattern-{size}.png"
    if not path.exists():
        print(f"generating {size} test pattern …", flush=True)
        make_pattern.write(widths, h, str(path))
    return str(path)


def main() -> None:
    args = sys.argv[1:]
    image = None
    if "--image" in args:
        i = args.index("--image")
        image = args[i + 1]
        del args[i:i + 2]

    outputs = connected()
    print("connected outputs:", ", ".join(outputs) or "none", flush=True)
    if args == ["all"]:
        targets = list(outputs)
    elif args:
        targets = args
    else:
        targets = dp_screens(outputs, log=lambda msg: print(msg, flush=True))

    missing = [n for n in targets if n not in outputs]
    if not targets or missing:
        sys.exit(f"not connected: {', '.join(missing) or 'no DisplayPort screen'}\n"
                 + subprocess.run(["xrandr"], capture_output=True, text=True).stdout)

    arrange(targets, [n for n in outputs if n not in targets])
    outputs = connected()
    widths = [outputs[n][0] for n in targets]
    total_h = max(outputs[n][1] for n in targets)
    print(f"showing on: {', '.join(targets)} ({sum(widths)}x{total_h})", flush=True)

    root = tk.Tk()
    root.withdraw()                                 # only the per-output windows are shown
    photo = tk.PhotoImage(file=image or pattern(widths, total_h))
    for name in targets:
        w, h, x, y = outputs[name]
        win = tk.Toplevel(root)
        win.overrideredirect(True)                  # no decorations, no window manager needed
        win.geometry(f"{w}x{h}+{x}+{y}")            # cover exactly this output
        canvas = tk.Canvas(win, width=w, height=h, bg="black", highlightthickness=0, cursor="none")
        canvas.pack()
        canvas.create_image(-x, -y, image=photo, anchor="nw")   # this output's slice of the row
        canvas.create_text(w // 2, h // 2, fill="white", font=("DejaVu Sans", 48, "bold"),
                           text=f"{name}\n{w}x{h} +{x}+{y}", justify="center")
        win.bind("<Key>", lambda e: root.destroy())
        win.bind("<Button>", lambda e: root.destroy())
        win.focus_force()
    root.mainloop()


if __name__ == "__main__":
    main()
