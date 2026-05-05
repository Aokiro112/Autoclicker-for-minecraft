# 🖱️ Minecraft Auto-Clicker — SKLauncher Edition

A lightweight, safe, and PvP-optimized auto-clicker built specifically for **Minecraft launched via SKLauncher**.

---

## ⚡ Features

- **R Toggle** — Press `R` to turn ON/OFF anytime
- **23–25 CPS** — Randomized clicks per second for natural, human-like behavior
- **Minecraft-only** — Works **exclusively** inside the Minecraft window; stops instantly if you alt-tab
- **Realistic clicks** — Uses Win32 API (`MOUSEEVENTF_LEFTDOWN/UP`) that Minecraft registers as real hardware clicks
- **Low CPU usage** — Idles at ~5ms sleep when not clicking
- **No system-wide interference** — Safe, no global mouse hooks

---

## 📁 File Structure

```
Autoclicker 1.0/
├── autoclicker.py       ← Main script
├── install_and_run.bat  ← One-click setup & launcher
└── README.md            ← This file
```

---

## 🚀 How to Run

### Option A — Easy (Recommended)
1. Double-click `install_and_run.bat`
2. Click **Yes** on the UAC (admin) prompt
3. Done! Auto-clicker will start automatically

### Option B — Manual
```powershell
pip install keyboard pywin32 psutil
python autoclicker.py
```
> Run as **Administrator** for reliable keyboard hooks.

---

## 🎮 In-Game Usage

| Step | Action |
|------|--------|
| 1 | Launch Minecraft via **SKLauncher** |
| 2 | Join a game (Bedwars, PvP, etc.) |
| 3 | Press **`R`** to start clicking |
| 4 | Press **`R`** again to stop |
| 5 | Alt-tab → clicking **auto-stops** |

---

## 🔒 Safety Behavior

| Situation | Clicks? |
|-----------|---------|
| Minecraft window is focused | ✅ Yes |
| Alt-tabbed to any other app | ❌ No |
| Minecraft minimized | ❌ No |
| Desktop / browser focused | ❌ No |
| R is ON but Minecraft not open | ❌ No |

---

## ⚙️ Configuration

Open `autoclicker.py` and edit the top section:

```python
TOGGLE_KEY = "r"      # Change hotkey (e.g. "f6", "f7")
CPS_MIN    = 23       # Minimum clicks per second
CPS_MAX    = 25       # Maximum clicks per second
```

---

## 📦 Requirements

- **Windows 10/11**
- **Python 3.10+** — [Download here](https://www.python.org/downloads/) *(tick "Add to PATH")*
- **Libraries** — auto-installed by `install_and_run.bat`:
  - `keyboard`
  - `pywin32`
  - `psutil`

---

## ❓ FAQ

**Q: Kya yeh anti-cheat se pakda jaega?**
> Clicks Win32 API se bhejta hai jo real hardware clicks jaisa hota hai. Lekin kisi bhi server pe use karo toh apni zimmedari pe — hum responsible nahi hain.

**Q: R key kaam nahi kar rahi?**
> Script ko **Administrator** ke taur pe run karo. `install_and_run.bat` yeh automatically karta hai.

**Q: CPS badhaana hai?**
> `autoclicker.py` mein `CPS_MIN` aur `CPS_MAX` ki values change karo.

**Q: Koi aur key use karni hai?**
> `TOGGLE_KEY = "r"` ko `"f6"` ya jo bhi chahiye woh karo.

---

## ⚠️ Disclaimer

This tool is intended for **educational and personal use only**. Usage on servers that prohibit auto-clickers may result in a ban. Use responsibly.
