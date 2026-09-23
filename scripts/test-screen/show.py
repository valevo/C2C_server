#!/usr/bin/env python3
"""Show an image fullscreen on X outputs, each labelled with the output's name.

    python3 show.py [OUTPUT ... | all] [--image FILE]

    (no output)   every connected DisplayPort output (DP-1, DP-1-1, DP-1-2, ...)
    all           every connected output, HDMI included
    OUTPUT ...    just these, e.g.  python3 show.py DP-1-1

Connected outputs that X left switched off are enabled to the right of the
others. Needs a running X server (see README.md) and python3-tk.
Any key or click quits.
"""

import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path

# "DP-1-1 connected 1920x1080+1920+0 (normal ..."   /   "DP-1-2 connected (normal ..."
OUTPUT_RE = re.compile(r"^(\S+) connected(?: primary)?(?: (\d+)x(\d+)\+(\d+)\+(\d+))?")


def connected() -> dict[str, tuple[int, int, int, int] | None]:
    """Connected outputs -> (w, h, x, y), or None if connected but switched off."""
    out = subprocess.run(["xrandr", "--query"], capture_output=True, text=True, check=True).stdout
    found = {}
    for line in out.splitlines():
        if m := OUTPUT_RE.match(line):
            found[m[1]] = tuple(map(int, m.group(2, 3, 4, 5))) if m[2] else None
    return found


def enable(names: list[str]) -> None:
    """Switch on connected-but-off outputs, placed right of everything already on."""
    for name in names:
        right = max((w + x for w, h, x, y in filter(None, connected().values())), default=0)
        subprocess.run(["xrandr", "--output", name, "--auto", "--pos", f"{right}x0"], check=True)


def main() -> None:
    args = sys.argv[1:]
    image = str(Path(__file__).with_name("test-pattern.png"))
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
        targets = [n for n in outputs if n.startswith("DP")]

    missing = [n for n in targets if n not in outputs]
    if not targets or missing:
        sys.exit(f"not connected: {', '.join(missing) or 'no DisplayPort output'}\n"
                 + subprocess.run(["xrandr"], capture_output=True, text=True).stdout)

    enable([n for n in targets if outputs[n] is None])
    outputs = connected()
    print("showing on:", ", ".join(targets), flush=True)

    root = tk.Tk()
    root.withdraw()                                 # only the per-output windows are shown
    photo = tk.PhotoImage(file=image)
    for name in targets:
        w, h, x, y = outputs[name]
        win = tk.Toplevel(root)
        win.overrideredirect(True)                  # no decorations, no window manager needed
        win.geometry(f"{w}x{h}+{x}+{y}")            # cover exactly this output
        canvas = tk.Canvas(win, width=w, height=h, bg="black", highlightthickness=0, cursor="none")
        canvas.pack()
        canvas.create_image(w // 2, h // 2, image=photo)
        canvas.create_text(w // 2, h // 2, fill="white", font=("DejaVu Sans", 48, "bold"),
                           text=f"{name}\n{w}x{h} +{x}+{y}", justify="center")
        win.bind("<Key>", lambda e: root.destroy())
        win.bind("<Button>", lambda e: root.destroy())
        win.focus_force()
    root.mainloop()


if __name__ == "__main__":
    main()
