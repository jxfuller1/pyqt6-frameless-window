from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QStyle, QVBoxLayout, QWidget


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

# ------------------------------ Windows API ------------------------------
if IS_WINDOWS:
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi

    WM_NCCALCSIZE = 0x0083
    WM_NCHITTEST = 0x0084
    WM_GETMINMAXINFO = 0x0024
    WM_NCRBUTTONUP = 0x00A5
    WM_DPICHANGED = 0x02E0
    WM_SYSCOMMAND = 0x0112

    HTCLIENT = 1
    HTCAPTION = 2
    HTSYSMENU = 3
    HTMINBUTTON = 8
    HTMAXBUTTON = 9
    HTLEFT = 10
    HTRIGHT = 11
    HTTOP = 12
    HTTOPLEFT = 13
    HTTOPRIGHT = 14
    HTBOTTOM = 15
    HTBOTTOMLEFT = 16
    HTBOTTOMRIGHT = 17
    HTCLOSE = 20

    GWL_STYLE = -16
    WS_THICKFRAME = 0x00040000
    WS_MINIMIZEBOX = 0x00020000
    WS_MAXIMIZEBOX = 0x00010000
    WS_SYSMENU = 0x00080000

    MONITOR_DEFAULTTONEAREST = 2
    TPM_RETURNCMD = 0x0100
    TPM_RIGHTBUTTON = 0x0002

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWCP_DEFAULT = 0
    DWMWCP_ROUND = 2
    DWMSBT_AUTO = 0
    DWMSBT_MAINWINDOW = 2       # Mica
    DWMSBT_TRANSIENTWINDOW = 3 # Acrylic-like transient backdrop on supported Win11 builds
    DWMSBT_TABBEDWINDOW = 4    # Mica Alt

    class POINT(ctypes.Structure):
        _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

    class RECT(ctypes.Structure):
        _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                    ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

    class MSG(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND), ("message", wintypes.UINT),
                    ("wParam", wintypes.WPARAM), ("lParam", wintypes.LPARAM),
                    ("time", wintypes.DWORD), ("pt", POINT), ("lPrivate", wintypes.DWORD)]

    class MINMAXINFO(ctypes.Structure):
        _fields_ = [("ptReserved", POINT), ("ptMaxSize", POINT),
                    ("ptMaxPosition", POINT), ("ptMinTrackSize", POINT),
                    ("ptMaxTrackSize", POINT)]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", RECT),
                    ("rcWork", RECT), ("dwFlags", wintypes.DWORD)]

    user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.GetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int)
    user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
    user32.SetWindowLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t)
    user32.MonitorFromWindow.restype = wintypes.HMONITOR
    user32.MonitorFromWindow.argtypes = (wintypes.HWND, wintypes.DWORD)
    user32.GetMonitorInfoW.restype = wintypes.BOOL
    user32.GetMonitorInfoW.argtypes = (wintypes.HMONITOR, ctypes.POINTER(MONITORINFO))
    user32.ScreenToClient.restype = wintypes.BOOL
    user32.ScreenToClient.argtypes = (wintypes.HWND, ctypes.POINTER(POINT))
    user32.GetSystemMenu.restype = wintypes.HMENU
    user32.GetSystemMenu.argtypes = (wintypes.HWND, wintypes.BOOL)
    user32.TrackPopupMenu.restype = wintypes.UINT
    user32.TrackPopupMenu.argtypes = (wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, wintypes.HWND, ctypes.c_void_p)
    user32.PostMessageW.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


def _signed_word(value: int) -> int:
    return ctypes.c_short(value & 0xFFFF).value


# ------------------------------- macOS API -------------------------------
def _configure_macos_nswindow(widget: QWidget) -> None:
    """Best-effort AppKit configuration with no PyObjC dependency.

    Keeps the real NSWindow (shadow, resize, traffic lights, Spaces/full-screen)
    while extending Qt content beneath the title-bar area.
    """
    if not IS_MACOS:
        return
    try:
        objc = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]
        msg = objc.objc_msgSend

        view = ctypes.c_void_p(int(widget.winId()))

        send_ptr = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(
            ctypes.cast(msg, ctypes.c_void_p).value
        )
        send_uint = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong)(
            ctypes.cast(msg, ctypes.c_void_p).value
        )
        send_bool = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool)(
            ctypes.cast(msg, ctypes.c_void_p).value
        )
        get_uint = ctypes.CFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p)(
            ctypes.cast(msg, ctypes.c_void_p).value
        )

        sel_window = objc.sel_registerName(b"window")
        nswindow = send_ptr(view, sel_window)
        if not nswindow:
            return

        # NSWindowStyleMaskFullSizeContentView = 1 << 15. Retain the native
        # titled/resizable/closable/miniaturizable bits already established by Qt.
        sel_style = objc.sel_registerName(b"styleMask")
        sel_set_style = objc.sel_registerName(b"setStyleMask:")
        style = get_uint(nswindow, sel_style)
        send_uint(nswindow, sel_set_style, style | (1 << 15))

        # NSWindowTitleHidden = 1. We paint our own title text but deliberately
        # leave AppKit's standard traffic-light buttons in place.
        send_uint(nswindow, objc.sel_registerName(b"setTitleVisibility:"), 1)
        send_bool(nswindow, objc.sel_registerName(b"setTitlebarAppearsTransparent:"), True)
    except Exception:
        # Qt 6.9+'s flags below normally provide the same effect. This helper is
        # intentionally non-fatal so unsupported macOS/Qt combinations still open.
        pass


# ------------------------------- Qt chrome -------------------------------
class CaptionButton(QPushButton):
    def __init__(self, kind: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.kind = kind
        self.active = True
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFixedWidth(46)
        self.setFlat(True)
        self._apply_style()

    def setActive(self, active: bool) -> None:
        self.active = active
        self._apply_style()
        self.update()

    def _apply_style(self) -> None:
        if self.kind == "close":
            self.setStyleSheet(
                "QPushButton{border:0;background:transparent;}"
                "QPushButton:hover{background:rgb(196,43,28);}"
                "QPushButton:pressed{background:rgb(150,32,22);}"
            )
        else:
            self.setStyleSheet(
                "QPushButton{border:0;background:transparent;}"
                "QPushButton:hover{background:rgba(255,255,255,28);}"
                "QPushButton:pressed{background:rgba(255,255,255,42);}"
            )

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        c = QColor(235, 235, 235) if self.active else QColor(155, 155, 155)
        p.setPen(QPen(c, 1.0))
        cx, cy = self.width() // 2, self.height() // 2
        if self.kind == "min":
            p.drawLine(cx - 5, cy + 2, cx + 5, cy + 2)
        elif self.kind == "max":
            p.drawRect(cx - 5, cy - 5, 10, 10)
        elif self.kind == "restore":
            p.drawRect(cx - 3, cy - 5, 9, 9)
            p.drawRect(cx - 6, cy - 2, 9, 9)
        elif self.kind == "close":
            p.drawLine(cx - 5, cy - 5, cx + 5, cy + 5)
            p.drawLine(cx + 5, cy - 5, cx - 5, cy + 5)


class CustomTitleBar(QWidget):
    HEIGHT = 38

    def __init__(self, window: "FramelessMainWindow"):
        super().__init__(window)
        self.window = window
        self.active = True
        self.setObjectName("customTitleBar")
        self.setFixedHeight(self.HEIGHT)

        self.icon = QLabel(self)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.icon.setScaledContents(True)

        self.title = QLabel(window.windowTitle(), self)
        self.title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.title.setStyleSheet("color:rgb(235,235,235);")

        # Windows uses custom caption buttons. macOS intentionally keeps the
        # genuine AppKit traffic lights because they preserve native full-screen,
        # option-click behavior, accessibility, and platform animation semantics.
        self.min_button = CaptionButton("min", self)
        self.max_button = CaptionButton("max", self)
        self.close_button = CaptionButton("close", self)
        for b in (self.min_button, self.max_button, self.close_button):
            b.setVisible(not IS_MACOS)

        self.min_button.clicked.connect(window.showMinimized)
        self.max_button.clicked.connect(window.toggleMaximized)
        self.close_button.clicked.connect(window.close)
        self.refreshIcon()

    def refreshIcon(self) -> None:
        icon = self.window.windowIcon()
        if icon.isNull() and QApplication.instance():
            icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.icon.setPixmap(icon.pixmap(16, 16))

    def setActive(self, active: bool) -> None:
        self.active = active
        self.title.setStyleSheet(
            f"color:rgb({235 if active else 150},{235 if active else 150},{235 if active else 150});"
        )
        for b in (self.min_button, self.max_button, self.close_button):
            b.setActive(active)
        self.setProperty("activeWindow", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        h = self.height()
        if IS_MACOS:
            # Reserve the left side for AppKit's native traffic lights.
            self.icon.hide()
            self.title.setGeometry(82, 0, max(0, self.width() - 164), h)
            self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return

        bw = 46
        self.icon.show()
        self.icon.setGeometry(12, (h - 16) // 2, 16, 16)
        self.close_button.setGeometry(self.width() - bw, 0, bw, h)
        self.max_button.setGeometry(self.width() - 2 * bw, 0, bw, h)
        self.min_button.setGeometry(self.width() - 3 * bw, 0, bw, h)
        self.title.setGeometry(38, 0, max(0, self.width() - 3 * bw - 48), h)
        self.title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

    def mousePressEvent(self, event: QMouseEvent):
        # On Windows native WM_NCHITTEST turns this area into HTCAPTION. On macOS
        # the custom Qt widget lives in AppKit's title area, so explicitly start
        # the OS-managed drag to retain native window movement/tiling behavior.
        if IS_MACOS and event.button() == Qt.MouseButton.LeftButton:
            handle = self.window.windowHandle()
            if handle and handle.startSystemMove():
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and not self._over_caption_button(event.position().toPoint()):
            self.window.toggleMaximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _over_caption_button(self, pos: QPoint) -> bool:
        if IS_MACOS:
            return False
        return any(b.isVisible() and b.geometry().contains(pos)
                   for b in (self.min_button, self.max_button, self.close_button))


class FramelessMainWindow(QMainWindow):
    """Cross-platform custom-title-bar QMainWindow focused on Windows 11/macOS.

    Windows:
      - Native 8-way resizing, move, Aero Snap and Win+Arrow
      - Windows 11 maximize-button Snap Layout flyout via HTMAXBUTTON
      - Native system menu (title-bar right click and app-icon interactions)
      - DWM shadow, rounded corners, active/inactive chrome
      - Correct taskbar-aware maximize and per-monitor DPI-aware hit testing
      - Optional Win11 Mica/Mica Alt/system backdrop API

    macOS:
      - Real NSWindow retained (native shadow, edge resize and Spaces/full-screen)
      - Client content extended into the native title-bar region
      - Native traffic-light controls retained
      - OS-managed title-bar dragging through QWindow.startSystemMove()

    Other platforms receive a functional Qt frameless fallback using
    startSystemMove(); Windows-only shell features naturally do not apply.
    """

    RESIZE_BORDER = 8

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._dark_mode = True
        self._backdrop_type = 0
        self.setWindowTitle("Frameless PyQt6 Window")
        self.resize(1100, 700)
        self.setMinimumSize(330, 200)

        if IS_WINDOWS:
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        elif IS_MACOS:
            # Qt 6.9+ exposes the intended cross-platform titlebar-extension API.
            expanded = getattr(Qt.WindowType, "ExpandedClientAreaHint", None)
            no_bg = getattr(Qt.WindowType, "NoTitleBarBackgroundHint", None)
            if expanded is not None:
                self.setWindowFlag(expanded, True)
            if no_bg is not None:
                self.setWindowFlag(no_bg, True)
            self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        else:
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        self.root = QWidget(self)
        self.root.setObjectName("windowRoot")
        layout = QVBoxLayout(self.root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        layout.addWidget(self.title_bar)

        self.content = QWidget(self.root)
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        demo = QLabel(
            "Custom title bar with native window-manager behavior.\n\n"
            "Windows: drag, resize, Aero Snap, Win+Arrow, right-click the title bar, "
            "double-click the app icon, or hover the maximize button for Snap Layouts.\n\n"
            "macOS: native traffic lights, shadow, resizing and full-screen are retained.",
            self.content,
        )
        demo.setWordWrap(True)
        demo.setFont(QFont("Segoe UI", 12))
        content_layout.addWidget(demo)
        content_layout.addStretch(1)
        layout.addWidget(self.content, 1)
        self.setCentralWidget(self.root)
        self._apply_palette()

        self.winId()  # Ensure native handle exists.
        if IS_WINDOWS:
            self._configure_native_window()
        elif IS_MACOS:
            _configure_macos_nswindow(self)

    # ----------------------------- Public API -----------------------------
    def setWindowTitle(self, title: str) -> None:
        super().setWindowTitle(title)
        if hasattr(self, "title_bar"):
            self.title_bar.title.setText(title)

    def setWindowIcon(self, icon: QIcon) -> None:
        super().setWindowIcon(icon)
        if hasattr(self, "title_bar"):
            self.title_bar.refreshIcon()

    def setDarkMode(self, enabled: bool) -> None:
        self._dark_mode = bool(enabled)
        self._apply_palette()
        if IS_WINDOWS and int(self.winId()):
            self._apply_windows_dwm_options()

    def setMicaEnabled(self, enabled: bool = True) -> None:
        """Enable Win11 Mica backdrop where supported; no-op elsewhere.

        DWM can only be visible through pixels your application does not paint
        opaquely. This method configures the native backdrop; applications can
        choose their own translucent/transparent content treatment.
        """
        self._backdrop_type = DWMSBT_MAINWINDOW if (IS_WINDOWS and enabled) else 0
        if IS_WINDOWS:
            self._apply_windows_dwm_options()

    def setWindowsBackdrop(self, mode: str = "auto") -> None:
        """Set Win11 backdrop: auto, mica, acrylic, mica_alt, or none."""
        if not IS_WINDOWS:
            return
        modes = {
            "auto": DWMSBT_AUTO,
            "none": DWMSBT_AUTO,
            "mica": DWMSBT_MAINWINDOW,
            "acrylic": DWMSBT_TRANSIENTWINDOW,
            "mica_alt": DWMSBT_TABBEDWINDOW,
        }
        if mode not in modes:
            raise ValueError(f"Unknown backdrop mode: {mode!r}")
        self._backdrop_type = modes[mode]
        self._apply_windows_dwm_options()

    def toggleMaximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def titleBar(self) -> CustomTitleBar:
        return self.title_bar

    def contentWidget(self) -> QWidget:
        return self.content

    # ----------------------------- Qt events ------------------------------
    def _apply_palette(self) -> None:
        if not hasattr(self, "root"):
            return
        if self._dark_mode:
            self.setStyleSheet(
                "#windowRoot{background:rgb(32,32,32);}"
                "#customTitleBar{background:rgb(45,45,48);}"
                "#customTitleBar[activeWindow=\"false\"]{background:rgb(39,39,41);}"
                "QLabel{color:rgb(230,230,230);}"
            )
        else:
            self.setStyleSheet(
                "#windowRoot{background:rgb(248,248,248);}"
                "#customTitleBar{background:rgb(243,243,243);}"
                "#customTitleBar[activeWindow=\"false\"]{background:rgb(238,238,238);}"
                "QLabel{color:rgb(30,30,30);}"
            )

    def changeEvent(self, event):
        super().changeEvent(event)
        if hasattr(self, "title_bar"):
            self.title_bar.max_button.kind = "restore" if self.isMaximized() else "max"
            self.title_bar.max_button.update()
            self.title_bar.setActive(self.isActiveWindow())

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if hasattr(self, "title_bar"):
            self.title_bar.setActive(True)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if hasattr(self, "title_bar"):
            self.title_bar.setActive(False)

    # -------------------------- Windows internals -------------------------
    if IS_WINDOWS:
        def _hwnd(self) -> int:
            return int(self.winId())

        def _configure_native_window(self) -> None:
            hwnd = self._hwnd()
            style = user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
            style |= WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU
            user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)
            self._apply_windows_dwm_options()

        def _apply_windows_dwm_options(self) -> None:
            hwnd = wintypes.HWND(self._hwnd())
            corner = ctypes.c_int(DWMWCP_ROUND)
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                                         ctypes.byref(corner), ctypes.sizeof(corner))
            dark = wintypes.BOOL(self._dark_mode)
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                         ctypes.byref(dark), ctypes.sizeof(dark))
            backdrop = ctypes.c_int(self._backdrop_type)
            # Attribute 38 is supported on modern Windows 11. Failure on an older
            # build is harmless and simply leaves the normal DWM backdrop.
            try:
                dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_SYSTEMBACKDROP_TYPE,
                                             ctypes.byref(backdrop), ctypes.sizeof(backdrop))
            except Exception:
                pass

        def _screen_to_client_native(self, x: int, y: int) -> tuple[int, int]:
            pt = POINT(x, y)
            user32.ScreenToClient(wintypes.HWND(self._hwnd()), ctypes.byref(pt))
            return int(pt.x), int(pt.y)

        @staticmethod
        def _native_rect(widget: QWidget, dpr: float) -> tuple[int, int, int, int]:
            top_left = widget.mapTo(widget.window(), QPoint(0, 0))
            return (round(top_left.x() * dpr), round(top_left.y() * dpr),
                    round((top_left.x() + widget.width()) * dpr),
                    round((top_left.y() + widget.height()) * dpr))

        def _window_dpr(self) -> float:
            # devicePixelRatioF follows the QWindow as it moves between monitors.
            handle = self.windowHandle()
            return handle.devicePixelRatio() if handle else self.devicePixelRatioF()

        def _caption_hit_test(self, x: int, y: int, dpr: float) -> int | None:
            def inside(rect):
                l, t, r, b = rect
                return l <= x < r and t <= y < b

            tb = self.title_bar
            if not inside(self._native_rect(tb, dpr)):
                return None
            if inside(self._native_rect(tb.icon, dpr)):
                return HTSYSMENU
            if inside(self._native_rect(tb.close_button, dpr)):
                return HTCLOSE
            if inside(self._native_rect(tb.max_button, dpr)):
                return HTMAXBUTTON  # Required for Windows 11 Snap Layout hover.
            if inside(self._native_rect(tb.min_button, dpr)):
                return HTMINBUTTON
            return HTCAPTION

        def _resize_hit_test(self, x: int, y: int, dpr: float) -> int | None:
            if self.isMaximized() or self.isFullScreen():
                return None
            border = max(5, round(self.RESIZE_BORDER * dpr))
            w, h = round(self.width() * dpr), round(self.height() * dpr)
            left, right = x < border, x >= w - border
            top, bottom = y < border, y >= h - border
            if top and left: return HTTOPLEFT
            if top and right: return HTTOPRIGHT
            if bottom and left: return HTBOTTOMLEFT
            if bottom and right: return HTBOTTOMRIGHT
            if left: return HTLEFT
            if right: return HTRIGHT
            if top: return HTTOP
            if bottom: return HTBOTTOM
            return None

        def _handle_getminmaxinfo(self, msg: MSG) -> None:
            mmi = ctypes.cast(msg.lParam, ctypes.POINTER(MINMAXINFO)).contents
            monitor = user32.MonitorFromWindow(msg.hwnd, MONITOR_DEFAULTTONEAREST)
            if not monitor:
                return
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            if not user32.GetMonitorInfoW(monitor, ctypes.byref(mi)):
                return
            work, mon = mi.rcWork, mi.rcMonitor
            mmi.ptMaxPosition.x = work.left - mon.left
            mmi.ptMaxPosition.y = work.top - mon.top
            mmi.ptMaxSize.x = work.right - work.left
            mmi.ptMaxSize.y = work.bottom - work.top
            dpr = self._window_dpr()
            minimum = self.minimumSize()
            mmi.ptMinTrackSize.x = max(mmi.ptMinTrackSize.x, round(minimum.width() * dpr))
            mmi.ptMinTrackSize.y = max(mmi.ptMinTrackSize.y, round(minimum.height() * dpr))

        def _show_system_menu(self, screen_x: int, screen_y: int) -> None:
            hwnd = wintypes.HWND(self._hwnd())
            menu = user32.GetSystemMenu(hwnd, False)
            if not menu:
                return
            command = user32.TrackPopupMenu(menu, TPM_RETURNCMD | TPM_RIGHTBUTTON,
                                             screen_x, screen_y, 0, hwnd, None)
            if command:
                user32.PostMessageW(hwnd, WM_SYSCOMMAND, command, 0)

        def nativeEvent(self, eventType, message):
            msg = ctypes.cast(int(message), ctypes.POINTER(MSG)).contents

            if msg.message == WM_NCCALCSIZE:
                return True, 0

            if msg.message == WM_GETMINMAXINFO:
                self._handle_getminmaxinfo(msg)
                return True, 0

            if msg.message == WM_NCHITTEST:
                screen_x = _signed_word(int(msg.lParam))
                screen_y = _signed_word(int(msg.lParam) >> 16)
                x, y = self._screen_to_client_native(screen_x, screen_y)
                dpr = self._window_dpr()
                resize = self._resize_hit_test(x, y, dpr)
                if resize is not None:
                    return True, resize
                caption = self._caption_hit_test(x, y, dpr)
                if caption is not None:
                    return True, caption
                return True, HTCLIENT

            if msg.message == WM_NCRBUTTONUP and int(msg.wParam) in (HTCAPTION, HTSYSMENU):
                screen_x = _signed_word(int(msg.lParam))
                screen_y = _signed_word(int(msg.lParam) >> 16)
                self._show_system_menu(screen_x, screen_y)
                return True, 0

            if msg.message == WM_DPICHANGED:
                # Qt applies the suggested geometry itself. Re-apply DWM options
                # after the transition; hit tests always query the current DPR.
                self._apply_windows_dwm_options()

            return super().nativeEvent(eventType, message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessMainWindow()
    window.show()
    sys.exit(app.exec())
