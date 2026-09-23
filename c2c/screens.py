"""Which X outputs are the exhibition screens: the ones on the DisplayPort MST hub.

    python -m c2c.screens      print them, one per line, in name order (DP-1-1,
                               DP-1-2, DP-1-3); reasons for skipped outputs go to
                               stderr

Screens behind an MST hub get sub-numbered names (DP-<port>-<n>), whatever the
hub's own sockets are (many hubs have HDMI sockets), so when any are connected,
exactly those count. The NUC8's HDMI port is never MST — but it is named DP-x
too, as it's driven by an on-board DP-to-HDMI converter (LSPCON).

Without an MST hub, plain DP-x outputs count unless their screen's EDID says it
is an HDMI screen (see is_hdmi_screen) — which catches the HDMI port only if the
screen sends a full EDID.

Used by scripts/setup-displays.sh and scripts/test-screen/show.py.
"""

import re
import subprocess
import sys

# "DP-1-1 connected 1920x1080+1920+0 (normal ..."   /   "DP-1-2 connected (normal ..."
OUTPUT_RE = re.compile(r"^(\S+) connected(?: primary)?(?: (\d+)x(\d+)\+(\d+)\+(\d+))?")

MST_RE = re.compile(r"^DP-?\d+-\d+$")   # DP-1-1 (modesetting), DP1-1 (intel driver)

HDMI_OUIS = (b"\x03\x0c\x00", b"\xd8\x5d\xc4")    # HDMI Licensing 00-0C-03, HDMI Forum C4-5D-D8


def xrandr(*args: str) -> str:
    return subprocess.run(["xrandr", *args], capture_output=True, text=True, check=True).stdout


def connected() -> dict[str, tuple[int, int, int, int] | None]:
    """Connected outputs -> (w, h, x, y), or None if connected but switched off."""
    found = {}
    for line in xrandr("--query").splitlines():
        if m := OUTPUT_RE.match(line):
            found[m[1]] = tuple(map(int, m.group(2, 3, 4, 5))) if m[2] else None
    return found


def edids() -> dict[str, bytes]:
    """Output name -> EDID of the connected screen, from `xrandr --props`."""
    found, name, hexdata = {}, None, None
    for line in xrandr("--props").splitlines():
        if not line[:1].isspace():                  # "DP-1 connected ..." starts an output
            name = line.split()[0]
        elif line.strip() == "EDID:":
            hexdata = found[name] = ""
            continue
        if hexdata is not None and re.fullmatch(r"[0-9a-f]+", line.strip()):
            hexdata = found[name] = hexdata + line.strip()
        else:
            hexdata = None
    return {n: bytes.fromhex(h) for n, h in found.items()}


def is_hdmi_screen(edid: bytes) -> bool:
    """True if the screen announces itself as an HDMI sink: an HDMI vendor-specific
    data block in a CTA-861 extension. DisplayPort screens don't carry one."""
    for i in range(128, len(edid), 128):
        block = edid[i:i + 128]
        if len(block) < 4 or block[0] != 0x02:      # not a CTA-861 extension
            continue
        j, end = 4, min(block[2], 127)
        while j < end:
            tag, length = block[j] >> 5, block[j] & 0x1F
            if tag == 3 and block[j + 1:j + 4] in HDMI_OUIS:
                return True
            j += 1 + length
    return False


def natural_key(name: str) -> list:
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", name)]


def dp_screens(outputs=None, log=None) -> list[str]:
    """Connected exhibition screens in name order: the MST hub's screens if any are
    connected, else DisplayPort screens that aren't HDMI screens."""
    outputs = connected() if outputs is None else outputs
    names = sorted(outputs, key=natural_key)
    if mst := [n for n in names if MST_RE.match(n)]:
        for name in names:
            if name not in mst and log:
                log(f"ignoring {name}: not behind the MST hub")
        return mst
    screens = edids()
    found = []
    for name in names:
        if not name.startswith("DP"):
            reason = "not DisplayPort"
        elif is_hdmi_screen(screens.get(name, b"")):
            reason = "HDMI screen (HDMI port or DP-to-HDMI adapter)"
        else:
            found.append(name)
            continue
        if log:
            log(f"ignoring {name}: {reason}")
    return found


if __name__ == "__main__":
    for name in dp_screens(log=lambda msg: print(msg, file=sys.stderr)):
        print(name)
