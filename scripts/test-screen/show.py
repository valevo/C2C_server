#!/usr/bin/env python3
"""Show an image fullscreen on one X output, labelled with the output's name.

    python3 show.py OUTPUT [image.png]        e.g.  python3 show.py DP-1-1

Needs a running X server (see README.md) and python3-tk. Any key or click quits.
"""

import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path

# " 1: +DP-1-1 1920/527x1080/296+1920+0  DP-1-1"
MONITOR_RE = re.compile(r"^\s*\d+:\s+\+?\*?(\S+)\s+(\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)")


def geometry(output: str) -> tuple[int, int, int, int] | None:
    out = subprocess.run(["xrandr", "--listmonitors"], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        m = MONITOR_RE.match(line)
        if m and m[1] == output:
            return int(m[2]), int(m[3]), int(m[4]), int(m[5])
    return None


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    output = sys.argv[1]
    image = sys.argv[2] if len(sys.argv) > 2 else str(Path(__file__).with_name("test-pattern.png"))

    geo = geometry(output)
    if geo is None:
        sys.exit(f"output {output} is not active; connected outputs:\n"
                 + subprocess.run(["xrandr"], capture_output=True, text=True).stdout)
    w, h, x, y = geo

    root = tk.Tk()
    root.overrideredirect(True)                 # no decorations, no window manager needed
    root.geometry(f"{w}x{h}+{x}+{y}")           # cover exactly this output
    canvas = tk.Canvas(root, width=w, height=h, bg="black", highlightthickness=0, cursor="none")
    canvas.pack()
    photo = tk.PhotoImage(file=image)
    canvas.create_image(w // 2, h // 2, image=photo)
    canvas.create_text(w // 2, h // 2, fill="white", font=("DejaVu Sans", 48, "bold"),
                       text=f"{output}\n{w}x{h} +{x}+{y}", justify="center")
    root.bind("<Key>", lambda e: root.destroy())
    root.bind("<Button>", lambda e: root.destroy())
    root.focus_force()
    root.mainloop()


if __name__ == "__main__":
    main()
