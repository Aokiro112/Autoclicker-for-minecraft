"""
=============================================================
  Minecraft Auto-Clicker  |  SKLauncher Edition
  Author  : Antigravity
  Toggle  : F6
  CPS     : 23–25 (randomized for realism)
  Safety  : Clicks ONLY when Minecraft window is focused
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
TOGGLE_KEY       = "f6"          # hotkey to toggle ON / OFF
CPS_MIN          = 23            # minimum clicks per second
CPS_MAX          = 25            # maximum clicks per second

# Window title substrings that identify Minecraft / SKLauncher.
# We check the focused window's title AND the process name.
MC_TITLE_HINTS   = ["minecraft", "sklauncher"]
MC_PROCESS_HINTS = ["javaw.exe", "java.exe", "minecraft.exe", "sklauncher"]

# ═══════════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════════
_enabled   = False          # toggled by F6
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
    These are indistinguishable from a physical click at the OS level.
    """
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    # Tiny hold – mirrors actual hardware (1–3 ms)
    time.sleep(random.uniform(0.001, 0.003))
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
            _send_left_click()
            # Randomized delay between clicks → 23–25 CPS
            delay = 1.0 / random.uniform(CPS_MIN, CPS_MAX)
            time.sleep(delay)
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

    print("=" * 60)
    print("  Minecraft Auto-Clicker  |  SKLauncher Edition")
    print("=" * 60)
    print(f"  Toggle key : {TOGGLE_KEY.upper()}")
    print(f"  CPS range  : {CPS_MIN}–{CPS_MAX}  (randomized)")
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
        print("\n\n[Auto-Clicker]  Exited cleanly.")


if __name__ == "__main__":
    # Require elevated privileges on Windows for reliable keyboard hooks
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        print("[WARNING] Not running as Administrator.")
        print("          Keyboard hooks may not work in all scenarios.")
        print("          Consider right-clicking and 'Run as Administrator'.\n")
    main()
