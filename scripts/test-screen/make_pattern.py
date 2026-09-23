#!/usr/bin/env python3
"""Write a screen test pattern as PNG, using only the standard library.

    python3 make_pattern.py [WIDTHxHEIGHT] [out.png]      (default 1920x1080 test-pattern.png)

Top two thirds: 8 colour bars (colours/cabling). Bottom third: grey ramp
(gamma/banding). White 1 px border (overscan: all four edges must be visible),
grid every 120 px and a centred circle (scaling: it must look round).
"""

import struct
import sys
import zlib

BARS = [(255, 255, 255), (255, 255, 0), (0, 255, 255), (0, 255, 0),
        (255, 0, 255), (255, 0, 0), (0, 0, 255), (0, 0, 0)]
WHITE = (255, 255, 255)
GRID = 120


def pixel(x: int, y: int, w: int, h: int, r: int) -> tuple[int, int, int]:
    if x in (0, w - 1) or y in (0, h - 1):
        return WHITE
    dx, dy = x - w // 2, y - h // 2
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


def main() -> None:
    size = sys.argv[1] if len(sys.argv) > 1 else "1920x1080"
    out = sys.argv[2] if len(sys.argv) > 2 else "test-pattern.png"
    w, h = map(int, size.split("x"))
    r = min(w, h) * 2 // 5
    rows = (bytes(c for x in range(w) for c in pixel(x, y, w, h, r)) for y in range(h))
    with open(out, "wb") as f:
        f.write(png(w, h, rows))
    print(f"wrote {out} ({w}x{h})")


if __name__ == "__main__":
    main()
