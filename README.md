# PyQt6 frameless window

A runnable PyQt6 `QMainWindow` example with a custom title bar and native
window-manager behavior.

On Windows, the example keeps the behaviors users expect from a normal top
level window:

- 8-way resize, move, Aero Snap, and `Win`+Arrow
- minimize, maximize/restore, and close buttons
- native system menu (right-click the title bar or use `Alt`+`Space`)
- Windows 11 Snap Layouts from the custom maximize button
- taskbar-aware maximize bounds on every monitor
- per-monitor-DPI-aware hit testing
- DWM shadow, rounded-corner, dark-mode, and optional system-backdrop support

macOS retains the native traffic lights and window-manager behavior while
extending content beneath the title bar. Other Qt platforms use the portable
frameless fallback and system drag operation when their compositor supports it.

## Run it

Use Python 3.8 or newer.

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python frameless_mainwindow.py
```

If PowerShell execution policy prevents activation, run the virtual
environment's interpreter directly instead:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe frameless_mainwindow.py
```

## Verify it

The test suite exercises startup, title/theme synchronization, and the
title-bar geometry regression that previously made hit testing crash.

```powershell
python -m unittest discover -s tests -v
```

On a headless Linux machine, set `QT_QPA_PLATFORM=offscreen` before running the
tests. The GitHub Actions workflow runs that configuration as well as a native
Windows smoke test.

## Optional Windows appearance APIs

```python
window.setDarkMode(False)
window.setWindowsBackdrop("mica")  # auto, none, mica, acrylic, or mica_alt
window.setTitleBarColor("#2563eb")
window.setTitleBarColor("#2563eb", "#1e3a8a")  # active, inactive
window.resetTitleBarColor()
```

Backdrop materials are available only on supported Windows 11 releases. They
are best-effort settings: unsupported Windows versions keep the normal DWM
appearance rather than failing to open the application.

`setTitleBarColor()` accepts any `QColor`-supported color name or CSS-style
color string. It automatically selects a contrasting title/button glyph color.
