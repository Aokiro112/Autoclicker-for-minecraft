"""
=============================================================
  Minecraft Auto-Clicker  |  SKLauncher Edition
  Author  : Antigravity
  Toggle  : R
  CPS     : 14–16 (Pika/Vulcan sweet spot — max effective hits)
  Safety  : Clicks ONLY when Minecraft window is focused
  Fix     : High-resolution timer (1 ms) + busy-wait loop
            so clicks actually register at ~120 CPS on servers
            like Pika (Windows default sleep = 15 ms, not 8 ms)
=============================================================
"""

import time
import random
import threading
import ctypes
import ctypes.wintypes
import sys

# ── third-party ──────────────────────────────────────────────
try:
    import keyboard
except ImportError:
    sys.exit("[ERROR] Missing 'keyboard' library.  Run:  pip install keyboard")

try:
    import win32gui
    import win32api
    import win32con
    import win32process
    import psutil
except ImportError:
    sys.exit(
        "[ERROR] Missing win32 libraries.  Run:  pip install pywin32 psutil"
    )

# ═══════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════
TOGGLE_KEY       = "r"            # hotkey to toggle ON / OFF
CPS_MIN          = 14             # minimum clicks per second
CPS_MAX          = 16             # maximum clicks per second
# WHY 14–16? Minecraft server = 20 TPS max. Pika's Vulcan anticheat
# cancels hits above ~17 CPS. 14–16 is the sweet spot: maximum
# effective damage output without triggering hit-cancel.

# Window title substrings that identify Minecraft / SKLauncher.
# We check the focused window's title AND the process name.
MC_TITLE_HINTS   = ["minecraft", "sklauncher"]
MC_PROCESS_HINTS = ["javaw.exe", "java.exe", "minecraft.exe", "sklauncher"]

# ═══════════════════════════════════════════════════════════════
#  HIGH-RESOLUTION TIMER  (Windows-specific)
#  timeBeginPeriod(1) drops the OS scheduler tick from ~15 ms
#  down to ~1 ms so that short sleeps actually work.
# ═══════════════════════════════════════════════════════════════
_winmm = ctypes.WinDLL("winmm")

def _enable_hires_timer():
    """Set Windows multimedia timer resolution to 1 ms."""
    _winmm.timeBeginPeriod(1)

def _disable_hires_timer():
    """Restore default timer resolution on exit."""
    _winmm.timeEndPeriod(1)

def _precise_sleep(seconds: float):
    """
    High-precision sleep using busy-wait for the final stretch.
    Uses time.sleep() for most of the duration to keep CPU usage
    reasonable, then spin-waits for the last 2 ms for accuracy.
    """
    if seconds <= 0:
        return
    deadline = time.perf_counter() + seconds
    # Sleep for most of the time (leave 2 ms for busy-wait)
    coarse = seconds - 0.002
    if coarse > 0:
        time.sleep(coarse)
    # Busy-wait for the remaining time
    while time.perf_counter() < deadline:
        pass

# ═══════════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════════
_enabled   = False          # toggled by R
_running   = True           # set to False to kill all threads
_lock      = threading.Lock()

# ═══════════════════════════════════════════════════════════════
#  WIN32 HELPERS
# ═══════════════════════════════════════════════════════════════

def _get_focused_window_info() -> tuple[str, str]:
    """Return (window_title_lower, process_name_lower) for the foreground window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return ("", "")

        title = win32gui.GetWindowText(hwnd).lower()

        # Retrieve PID then process name
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            proc_name = ""

        return title, proc_name
    except Exception:
        return ("", "")


def _is_minecraft_focused() -> bool:
    """Return True only when the active window belongs to Minecraft/SKLauncher."""
    title, proc = _get_focused_window_info()

    # Check process name first (most reliable)
    for hint in MC_PROCESS_HINTS:
        if hint in proc:
            return True

    # Fallback: check window title
    for hint in MC_TITLE_HINTS:
        if hint in title:
            return True

    return False


def _send_left_click():
    """
    Fire a real WM_LBUTTONDOWN / WM_LBUTTONUP pair via Win32.
    Uses busy-wait for the hold duration so it's accurate even
    at 120 CPS where each full cycle is only ~8.3 ms.
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    # Tiny hold ~1 ms using busy-wait (mirrors real hardware)
    _precise_sleep(random.uniform(0.0008, 0.0012))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


# ═══════════════════════════════════════════════════════════════
#  CLICKER THREAD
# ═══════════════════════════════════════════════════════════════

def _clicker_loop():
    """Background thread: fires clicks when enabled and Minecraft is focused."""
    while _running:
        with _lock:
            active = _enabled

        if active and _is_minecraft_focused():
            t_start = time.perf_counter()
            _send_left_click()
            # Target interval for 118–120 CPS
            interval = 1.0 / random.uniform(CPS_MIN, CPS_MAX)
            # Subtract time already spent in _send_left_click
            elapsed = time.perf_counter() - t_start
            remaining = interval - elapsed
            if remaining > 0:
                _precise_sleep(remaining)
        else:
            # Idle sleep – very cheap on CPU
            time.sleep(0.005)


# ═══════════════════════════════════════════════════════════════
#  HOTKEY HANDLER
# ═══════════════════════════════════════════════════════════════

def _toggle(event=None):
    global _enabled
    with _lock:
        _enabled = not _enabled
    state = "ON  ✔" if _enabled else "OFF ✘"
    print(f"\r[Auto-Clicker]  {state}   (press {TOGGLE_KEY.upper()} to toggle)    ", end="", flush=True)


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    global _running

    # Enable 1 ms timer resolution for accurate high-CPS clicks
    _enable_hires_timer()

    print("=" * 60)
    print("  Minecraft Auto-Clicker  |  SKLauncher Edition")
    print("=" * 60)
    print(f"  Toggle key : {TOGGLE_KEY.upper()}")
    print(f"  CPS range  : {CPS_MIN}–{CPS_MAX}  (Pika sweet spot, max effective hits)")
    print(f"  Timer res  : 1 ms  (high-precision mode ON)")
    print(f"  Safety     : only active when Minecraft window is focused")
    print(f"  Exit       : press Ctrl+C  or close this window")
    print("=" * 60)
    print(f"\r[Auto-Clicker]  OFF ✘   (press {TOGGLE_KEY.upper()} to toggle)    ", end="", flush=True)

    # Start clicker thread (daemon → exits with main thread)
    t = threading.Thread(target=_clicker_loop, daemon=True)
    t.start()

    # Register hotkey
    keyboard.on_press_key(TOGGLE_KEY, _toggle, suppress=False)

    try:
        keyboard.wait()          # blocks until Ctrl+C
    except KeyboardInterrupt:
        pass
    finally:
        _running = False
        _disable_hires_timer()   # restore OS timer resolution
        print("\n\n[Auto-Clicker]  Exited cleanly.")


if __name__ == "__main__":
    # Require elevated privileges on Windows for reliable keyboard hooks
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        print("[WARNING] Not running as Administrator.")
        print("          Keyboard hooks may not work in all scenarios.")
        print("          Consider right-clicking and 'Run as Administrator'.\n")
    main()
