#!/usr/bin/env python3
"""Write a screen test pattern as PNG, using only the standard library.

    python3 make_pattern.py [SIZE] [out.png]       (default 1920x1080 test-pattern.png)

SIZE is WIDTHxHEIGHT, or screen widths joined by + for a row of screens,
e.g. 1920+1920+1920x1080.

Top two thirds: 8 colour bars (colours/cabling). Bottom third: grey ramp
(gamma/banding). Both, and the grid every 120 px, run across the whole row.
Each screen gets its own white 1 px border (overscan: all four edges must be
visible) and centred circle (scaling: it must look round).
"""

import struct
import sys
import zlib

BARS = [(255, 255, 255), (255, 255, 0), (0, 255, 255), (0, 255, 0),
        (255, 0, 255), (255, 0, 0), (0, 0, 255), (0, 0, 0)]
WHITE = (255, 255, 255)
GRID = 120


def pixel(x: int, y: int, w: int, h: int, r: int, s0: int, sw: int) -> tuple[int, int, int]:
    """Colour at (x, y) of a w x h row; this pixel's screen starts at s0, sw wide."""
    if x - s0 in (0, sw - 1) or y in (0, h - 1):
        return WHITE
    dx, dy = x - (s0 + sw // 2), y - h // 2
    if abs(dx * dx + dy * dy - r * r) <= r * 2:   # ~2 px ring
        return WHITE
    if x % GRID == 0 or y % GRID == 0:
        return (128, 128, 128)
    if y < h * 2 // 3:
        return BARS[x * len(BARS) // w]
    g = x * 255 // (w - 1)
    return (g, g, g)


def png(w: int, h: int, rows) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
    raw = b"".join(b"\x00" + row for row in rows)   # filter type 0 per row
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def write(widths: list[int], h: int, out: str) -> None:
    """Write the pattern for a row of screens with these widths (left to right)."""
    w = sum(widths)
    r = min(min(widths), h) * 2 // 5
    screen_of = [(s0, sw) for i, sw in enumerate(widths) for s0 in [sum(widths[:i])] for _ in range(sw)]
    rows = (bytes(c for x in range(w) for c in pixel(x, y, w, h, r, *screen_of[x])) for y in range(h))
    with open(out, "wb") as f:
        f.write(png(w, h, rows))


def main() -> None:
    size = sys.argv[1] if len(sys.argv) > 1 else "1920x1080"
    out = sys.argv[2] if len(sys.argv) > 2 else "test-pattern.png"
    widths, h = size.split("x")
    write([int(sw) for sw in widths.split("+")], int(h), out)
    print(f"wrote {out} ({size})")


if __name__ == "__main__":
    main()
