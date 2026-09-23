"""Render the frontend on the exhibition screens: one kiosk browser window per output.

Started by scripts/setup-displays.sh (via `python -m c2c.display`) after xrandr has
arranged the outputs. Screen geometry is read back from `xrandr --listmonitors`, so
the layout only has to be defined once, in the setup script.

Each window loads C2C_DISPLAY_URL with `screen=<n>` appended (1 = leftmost), so the
frontend can tell the screens apart. Windows that exit or crash are restarted.

Environment (from /etc/c2c/c2c.env, C2C_OUTPUTS set by setup-displays.sh):
    C2C_OUTPUTS          outputs to render to, left to right (default: all active
                         monitors); others, e.g. an HDMI dev screen, are left alone
    C2C_DISPLAY_URL      page to show (default http://127.0.0.1:$C2C_PORT/)
    C2C_BROWSER          browser binary (default chromium)
"""

import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

RESTART_DELAY = 3   # seconds before relaunching a window that exited
POLL_INTERVAL = 1   # seconds between child-process checks
WAIT_INTERVAL = 2   # seconds between attempts to reach the frontend

# " 0: +*HDMI-1 1920/527x1080/296+0+0  HDMI-1"
MONITOR_RE = re.compile(r"^\s*\d+:\s+\+?\*?(\S+)\s+(\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)")


@dataclass
class Monitor:
    name: str
    width: int
    height: int
    x: int
    y: int


def log(msg: str) -> None:
    print(f"c2c.display: {msg}", flush=True)


def list_monitors() -> list[Monitor]:
    """Active monitors as arranged by xrandr, ordered left to right."""
    out = subprocess.run(
        ["xrandr", "--listmonitors"], capture_output=True, text=True, check=True
    ).stdout
    monitors = [
        Monitor(m[1], int(m[2]), int(m[3]), int(m[4]), int(m[5]))
        for line in out.splitlines()
        if (m := MONITOR_RE.match(line))
    ]
    return sorted(monitors, key=lambda mon: (mon.x, mon.y))


def screen_url(base: str, screen: int) -> str:
    parts = urlsplit(base)
    query = urlencode([*parse_qsl(parts.query), ("screen", str(screen))])
    return urlunsplit(parts._replace(query=query))


def wait_for(url: str) -> None:
    """Block until the frontend answers, so the browsers don't start on an error page."""
    waited = 0
    while True:
        try:
            with urllib.request.urlopen(url, timeout=3):
                return
        except urllib.error.HTTPError:
            return  # server is up; the page itself decides what to show
        except (urllib.error.URLError, OSError):
            if waited % 30 == 0:
                log(f"waiting for {url} …")
            time.sleep(WAIT_INTERVAL)
            waited += WAIT_INTERVAL


def browser_cmd(browser: str, url: str, mon: Monitor, profile: str) -> list[str]:
    return [
        browser,
        f"--user-data-dir={profile}",   # separate instance per screen, else windows merge
        f"--window-position={mon.x},{mon.y}",
        f"--window-size={mon.width},{mon.height}",
        "--kiosk",
        "--incognito",
        "--no-first-run",
        "--noerrdialogs",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--disable-translate",
        "--disable-features=Translate",
        "--password-store=basic",
        "--autoplay-policy=no-user-gesture-required",
        "--check-for-update-interval=31536000",
        url,
    ]


def main() -> int:
    base = os.environ.get("C2C_DISPLAY_URL") or f"http://127.0.0.1:{os.environ.get('C2C_PORT', '8080')}/"
    browser = os.environ.get("C2C_BROWSER", "chromium")
    if shutil.which(browser) is None:
        log(f"browser '{browser}' not found (set C2C_BROWSER or install chromium)")
        return 1

    monitors = list_monitors()
    if wanted := os.environ.get("C2C_OUTPUTS", "").split():
        active = {m.name: m for m in monitors}
        if missing := [n for n in wanted if n not in active]:
            log(f"outputs not active: {' '.join(missing)}")
            return 1
        monitors = [active[n] for n in wanted]
    if not monitors:
        log("no active monitors reported by xrandr")
        return 1
    log("screens: " + ", ".join(f"{i}={m.name} {m.width}x{m.height}+{m.x}+{m.y}"
                                for i, m in enumerate(monitors, 1)))

    wait_for(base)

    profiles = tempfile.mkdtemp(prefix="c2c-display-")
    windows: dict[int, subprocess.Popen | None] = {i: None for i in range(1, len(monitors) + 1)}
    restart_at: dict[int, float] = {i: 0.0 for i in windows}

    def shutdown(signum, frame):
        for proc in windows.values():
            if proc and proc.poll() is None:
                proc.terminate()
        for proc in windows.values():
            if proc:
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        shutil.rmtree(profiles, ignore_errors=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGHUP, shutdown)

    while True:
        now = time.monotonic()
        for screen, mon in enumerate(monitors, 1):
            proc = windows[screen]
            if proc is not None and proc.poll() is None:
                continue
            if proc is not None:
                log(f"screen {screen} ({mon.name}) exited with {proc.returncode}; restarting")
                windows[screen] = None
                restart_at[screen] = now + RESTART_DELAY
            if now < restart_at[screen]:
                continue
            url = screen_url(base, screen)
            profile = os.path.join(profiles, f"screen{screen}")
            log(f"screen {screen} ({mon.name}): {url}")
            windows[screen] = subprocess.Popen(browser_cmd(browser, url, mon, profile))
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
