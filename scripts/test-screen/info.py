#!/usr/bin/env python3
"""Print which screens the graphics driver sees, straight from the kernel.

    python3 info.py            every output: connected or not, screen model, modes
    sudo python3 info.py       also the driver's view of the MST hub

Needs no X server, so it works over SSH and while the screens are black. The
names are the kernel's (DP-3, DP-4, ... for screens behind the MST hub) and
don't match xrandr's (DP-2-1, DP-2-2, ...); match them by screen model.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # repo root, for c2c.screens
from c2c.screens import is_hdmi_screen, natural_key  # noqa: E402

DRM = Path("/sys/class/drm")


def read(path: Path) -> str:
    try:
        return path.read_text().strip()
    except OSError:
        return ""


def describe(edid: bytes) -> str:
    """'DEL DELL U2412M (serial ABC123)', from the EDID's header and descriptors."""
    if len(edid) < 128:
        return "no EDID"
    m = int.from_bytes(edid[8:10], "big")
    maker = "".join(chr(64 + (m >> s & 0x1F)) for s in (10, 5, 0))
    name = serial = ""
    for i in (54, 72, 90, 108):
        d = edid[i:i + 18]
        if d[:3] == b"\0\0\0" and d[3] in (0xFC, 0xFF):
            text = d[5:].split(b"\n")[0].decode("ascii", "replace").strip()
            if d[3] == 0xFC:
                name = text
            else:
                serial = text
    out = f"{maker} {name or '(no name)'}"
    if serial:
        out += f" (serial {serial})"
    if is_hdmi_screen(edid):
        out += ", HDMI screen"
    return out


def main() -> None:
    connectors = sorted((p for p in DRM.glob("card*-*") if (p / "status").exists()),
                        key=lambda p: natural_key(p.name))
    if not connectors:
        sys.exit(f"info.py: no outputs in {DRM} — no graphics driver loaded?")
    for p in connectors:
        name = p.name.split("-", 1)[1]
        status = read(p / "status")
        if status != "connected":
            print(f"{name:10} {status}")
            continue
        try:
            edid = (p / "edid").read_bytes()
        except OSError:
            edid = b""
        modes = list(dict.fromkeys(read(p / "modes").split()))   # one per refresh rate
        state = "on" if read(p / "enabled") == "enabled" else "off"
        print(f"{name:10} connected, {state}: {describe(edid)}")
        print(f"{'':10} preferred {modes[0] if modes else '(no modes)'}"
              f"{', also ' + ' '.join(modes[1:6]) if modes[1:] else ''}")

    # dri/0, dri/128 and dri/0000:00:02.0 are the same GPU
    mst = sorted({f.resolve() for f in Path("/sys/kernel/debug/dri").glob("*/i915_dp_mst_info")})
    if mst:
        for f in mst:
            print(f"\n== {f} ==")
            try:
                print(f.read_text().rstrip() or "(empty: no MST hub)")
            except OSError as e:
                print(f"(can't read: {e.strerror})")
    elif Path("/sys/kernel/debug").is_dir():
        print("\n(run with sudo to also see the driver's view of the MST hub)")


if __name__ == "__main__":
    main()
