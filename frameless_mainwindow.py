from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

from PyQt6.QtCore import QPoint, QRect, QTimer, Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QStyle, QVBoxLayout, QWidget


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

# ------------------------------ Windows API ------------------------------
if IS_WINDOWS:
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi

    WM_NCCALCSIZE = 0x0083
    WM_NCACTIVATE = 0x0086
    WM_NCHITTEST = 0x0084
    WM_GETMINMAXINFO = 0x0024
    WM_NCLBUTTONDOWN = 0x00A1
    WM_NCLBUTTONUP = 0x00A2
    WM_NCLBUTTONDBLCLK = 0x00A3
    WM_NCRBUTTONUP = 0x00A5
    WM_NCMOUSEMOVE = 0x00A0
    WM_LBUTTONUP = 0x0202
    WM_MOUSEMOVE = 0x0200
    WM_CANCELMODE = 0x001F
    WM_CAPTURECHANGED = 0x0215
    WM_NCMOUSELEAVE = 0x02A2
    WM_MOUSELEAVE = 0x02A3
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
    WS_CAPTION = 0x00C00000
    WS_THICKFRAME = 0x00040000
    WS_MINIMIZEBOX = 0x00020000
    WS_MAXIMIZEBOX = 0x00010000
    WS_SYSMENU = 0x00080000

    MONITOR_DEFAULTTONEAREST = 2
    TPM_RETURNCMD = 0x0100
    TPM_RIGHTBUTTON = 0x0002
    TME_LEAVE = 0x00000002
    TME_NONCLIENT = 0x00000010
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOZORDER = 0x0004
    SWP_NOACTIVATE = 0x0010
    SWP_FRAMECHANGED = 0x0020

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWA_BORDER_COLOR = 34
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_COLOR_NONE = 0xFFFFFFFE
    DWMWCP_DEFAULT = 0
    DWMWCP_ROUND = 2
    DWMSBT_AUTO = 0
    DWMSBT_NONE = 1
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

    class TRACKMOUSEEVENT(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                    ("hwndTrack", wintypes.HWND), ("dwHoverTime", wintypes.DWORD)]

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
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.GetCursorPos.argtypes = (ctypes.POINTER(POINT),)
    user32.TrackMouseEvent.restype = wintypes.BOOL
    user32.TrackMouseEvent.argtypes = (ctypes.POINTER(TRACKMOUSEEVENT),)
    user32.GetSystemMenu.restype = wintypes.HMENU
    user32.GetSystemMenu.argtypes = (wintypes.HWND, wintypes.BOOL)
    user32.TrackPopupMenu.restype = wintypes.UINT
    user32.TrackPopupMenu.argtypes = (wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, wintypes.HWND, ctypes.c_void_p)
    user32.PostMessageW.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    user32.SetWindowPos.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = (
        wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
        ctypes.c_int, ctypes.c_int, wintypes.UINT,
    )
    user32.SetCapture.restype = wintypes.HWND
    user32.SetCapture.argtypes = (wintypes.HWND,)
    user32.GetCapture.restype = wintypes.HWND
    user32.GetCapture.argtypes = ()
    user32.ReleaseCapture.restype = wintypes.BOOL
    user32.ReleaseCapture.argtypes = ()
    user32.IsZoomed.restype = wintypes.BOOL
    user32.IsZoomed.argtypes = (wintypes.HWND,)
    user32.DefWindowProcW.restype = ctypes.c_ssize_t
    user32.DefWindowProcW.argtypes = (
        wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
    )
    get_dpi_for_window = getattr(user32, "GetDpiForWindow", None)
    if get_dpi_for_window is not None:
        get_dpi_for_window.restype = wintypes.UINT
        get_dpi_for_window.argtypes = (wintypes.HWND,)

    # ctypes otherwise assumes 32-bit integer arguments, which is unsafe for
    # HWND/WPARAM/LPARAM on 64-bit Python.
    dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long  # HRESULT
    dwmapi.DwmSetWindowAttribute.argtypes = (
        wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
    )


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
        self.dark_mode = True
        self.native_hovered = False
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFixedWidth(46)
        self.setFlat(True)
        self._apply_style()

    def setActive(self, active: bool) -> None:
        self.active = active
        self._apply_style()
        self.update()

    def setDarkMode(self, enabled: bool) -> None:
        self.dark_mode = bool(enabled)
        self._apply_style()
        self.update()

    def setNativeHover(self, hovered: bool) -> None:
        """Mirror a native non-client hover state in the Qt button style."""
        hovered = bool(hovered)
        if self.native_hovered == hovered:
            return
        self.native_hovered = hovered
        self.setProperty("nativeHover", hovered)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _apply_style(self) -> None:
        if self.kind == "close":
            self.setStyleSheet(
                "QPushButton{border:0;background:transparent;}"
                "QPushButton:hover{background:rgb(196,43,28);}"
                "QPushButton:pressed{background:rgb(150,32,22);}"
            )
        else:
            hover = "rgba(255,255,255,28)" if self.dark_mode else "rgba(0,0,0,20)"
            pressed = "rgba(255,255,255,42)" if self.dark_mode else "rgba(0,0,0,32)"
            self.setStyleSheet(
                "QPushButton{border:0;background:transparent;}"
                f"QPushButton:hover,QPushButton[nativeHover=\"true\"]{{background:{hover};}}"
                f"QPushButton:pressed{{background:{pressed};}}"
            )

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        if self.dark_mode:
            c = QColor(235, 235, 235) if self.active else QColor(155, 155, 155)
        else:
            c = QColor(30, 30, 30) if self.active else QColor(130, 130, 130)
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
        # Keep QWidget.window() intact: the native hit-test code relies on it to
        # map child geometry to the top-level window. Shadowing it with an
        # instance attribute causes a TypeError as soon as the cursor reaches
        # the title bar.
        self._host_window = window
        self.active = True
        self.dark_mode = True
        self._drag_press_global: QPoint | None = None
        self._drag_press_local: QPoint | None = None
        self._drag_was_maximized = False
        self._system_move_started = False
        self.setObjectName("customTitleBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(self.HEIGHT)

        self.icon = QLabel(self)
        self.icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.icon.setScaledContents(True)

        self.title = QLabel(window.windowTitle(), self)
        self.title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._apply_title_color()

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
        icon = self._host_window.windowIcon()
        if icon.isNull() and QApplication.instance():
            icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.icon.setPixmap(icon.pixmap(16, 16))

    def setActive(self, active: bool) -> None:
        self.active = active
        self._apply_title_color()
        for b in (self.min_button, self.max_button, self.close_button):
            b.setActive(active)
        self.setProperty("activeWindow", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def setDarkMode(self, enabled: bool) -> None:
        self.dark_mode = bool(enabled)
        self._apply_title_color()
        for b in (self.min_button, self.max_button, self.close_button):
            b.setDarkMode(enabled)

    def _apply_title_color(self) -> None:
        if self.dark_mode:
            color = 235 if self.active else 150
        else:
            color = 30 if self.active else 130
        self.title.setStyleSheet(f"color:rgb({color},{color},{color});")

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
        # This is a client region on every platform. Keep a short press as a
        # click (so double-click still maximizes), then ask the window manager
        # to move only after the user actually drags.
        if (
            event.button() == Qt.MouseButton.LeftButton
            and not self._over_caption_button(event.position().toPoint())
        ):
            self._drag_press_global = event.globalPosition().toPoint()
            self._drag_press_local = event.position().toPoint()
            self._drag_was_maximized = self._host_window._is_chrome_maximized()
            self._system_move_started = False
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if (
            not self._system_move_started
            and self._drag_press_global is not None
            and self._drag_press_local is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            global_pos = event.globalPosition().toPoint()
            if (
                global_pos - self._drag_press_global
            ).manhattanLength() >= QApplication.startDragDistance():
                if self._drag_was_maximized:
                    normal_geometry = self._host_window._normal_geometry_for_restore()
                    horizontal_fraction = self._drag_press_local.x() / max(1, self.width())
                    self._host_window._restore_normal_geometry(
                        QPoint(
                            global_pos.x() - round(normal_geometry.width() * horizontal_fraction),
                            global_pos.y() - min(self._drag_press_local.y(), self.HEIGHT - 1),
                        )
                    )
                    # Do not repeatedly restore/reposition if a platform does
                    # not support startSystemMove() for this window.
                    self._drag_was_maximized = False
                handle = self._host_window.windowHandle()
                self._system_move_started = bool(handle and handle.startSystemMove())
                if self._system_move_started:
                    event.accept()
                    return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._reset_drag_state()
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event) -> None:
        if IS_WINDOWS:
            # TrackPopupMenu expects physical screen pixels. Qt's global point
            # may be device-independent on a mixed-DPI desktop, so ask Windows
            # for the native cursor location instead.
            global_pos = POINT()
            if not user32.GetCursorPos(ctypes.byref(global_pos)):
                fallback = event.globalPos()
                global_pos.x, global_pos.y = fallback.x(), fallback.y()
            self._host_window._show_system_menu(
                self._host_window._hwnd(), int(global_pos.x), int(global_pos.y)
            )
            event.accept()
            return
        super().contextMenuEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and not self._over_caption_button(event.position().toPoint()):
            self._reset_drag_state()
            self._host_window.toggleMaximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _reset_drag_state(self) -> None:
        self._drag_press_global = None
        self._drag_press_local = None
        self._drag_was_maximized = False
        self._system_move_started = False

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
      - System menu on title-bar right click
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
        self._title_bar_color: QColor | None = None
        self._inactive_title_bar_color: QColor | None = None
        self._max_button_pressed = False
        self._saved_normal_geometry: QRect | None = None
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

    def setTitleBarColor(
        self, color: QColor | str, inactive_color: QColor | str | None = None
    ) -> None:
        """Set the active title-bar color.

        ``color`` accepts any QColor-supported name or CSS-style color, such
        as ``"#2563eb"`` or ``"steelblue"``. Supply ``inactive_color`` to
        explicitly control the inactive-window color; otherwise a slightly
        darker shade of the active color is used.
        """
        self._title_bar_color = self._coerce_color(color, "color")
        self._inactive_title_bar_color = (
            self._coerce_color(inactive_color, "inactive_color")
            if inactive_color is not None
            else None
        )
        self._apply_palette()

    def resetTitleBarColor(self) -> None:
        """Restore the title-bar colors selected by :meth:`setDarkMode`."""
        self._title_bar_color = None
        self._inactive_title_bar_color = None
        self._apply_palette()

    def titleBarColor(self) -> QColor:
        """Return the effective active title-bar color."""
        active, _ = self._effective_title_bar_colors()
        return QColor(active)

    def setMicaEnabled(self, enabled: bool = True) -> None:
        """Enable Win11 Mica backdrop where supported; no-op elsewhere.

        DWM can only be visible through pixels your application does not paint
        opaquely. This method configures the native backdrop; applications can
        choose their own translucent/transparent content treatment.
        """
        self._backdrop_type = (
            (DWMSBT_MAINWINDOW if enabled else DWMSBT_NONE) if IS_WINDOWS else 0
        )
        if IS_WINDOWS:
            self._apply_windows_dwm_options()

    def setWindowsBackdrop(self, mode: str = "auto") -> None:
        """Set Win11 backdrop: auto, mica, acrylic, mica_alt, or none."""
        if not IS_WINDOWS:
            return
        modes = {
            "auto": DWMSBT_AUTO,
            "none": DWMSBT_NONE,
            "mica": DWMSBT_MAINWINDOW,
            "acrylic": DWMSBT_TRANSIENTWINDOW,
            "mica_alt": DWMSBT_TABBEDWINDOW,
        }
        if mode not in modes:
            raise ValueError(f"Unknown backdrop mode: {mode!r}")
        self._backdrop_type = modes[mode]
        self._apply_windows_dwm_options()

    def toggleMaximized(self) -> None:
        if self._is_chrome_maximized():
            self._restore_normal_geometry()
        else:
            self.showMaximized()

    def showMaximized(self) -> None:
        """Maximize while retaining the exact pre-maximize Qt geometry."""
        if not self._is_chrome_maximized() and not self.isMinimized():
            geometry = self.geometry()
            if geometry.isValid():
                self._saved_normal_geometry = QRect(geometry)
        super().showMaximized()

    def titleBar(self) -> CustomTitleBar:
        return self.title_bar

    def contentWidget(self) -> QWidget:
        return self.content

    def _is_chrome_maximized(self, hwnd_value: int | None = None) -> bool:
        """Return the actual maximize state used for caption behavior."""
        if self.isMaximized():
            return True
        if IS_WINDOWS:
            # Native-event callers provide MSG.hwnd so this check never tries
            # to create a native handle while Windows is already dispatching a
            # message for that handle.
            hwnd = hwnd_value if hwnd_value is not None else int(self.winId())
            if hwnd:
                return bool(user32.IsZoomed(wintypes.HWND(hwnd)))
        return False

    def _normal_geometry_for_restore(self) -> QRect:
        """Return the normal bounds remembered before the current maximize."""
        if self._saved_normal_geometry is not None and self._saved_normal_geometry.isValid():
            return QRect(self._saved_normal_geometry)
        geometry = self.normalGeometry()
        return QRect(geometry if geometry.isValid() else self.geometry())

    def _restore_normal_geometry(self, top_left: QPoint | None = None) -> None:
        """Leave maximized state and restore the saved normal bounds exactly."""
        geometry = self._normal_geometry_for_restore()
        super().showNormal()
        if geometry.isValid():
            if top_left is not None:
                geometry.moveTopLeft(top_left)
            self.setGeometry(geometry)

    # ----------------------------- Qt events ------------------------------
    @staticmethod
    def _coerce_color(color: QColor | str, parameter: str) -> QColor:
        converted = QColor(color)
        if not converted.isValid():
            raise ValueError(f"{parameter} must be a valid QColor or color name")
        return converted

    @staticmethod
    def _color_to_css(color: QColor) -> str:
        return f"rgba({color.red()},{color.green()},{color.blue()},{color.alpha()})"

    @staticmethod
    def _title_bar_uses_dark_chrome(color: QColor) -> bool:
        """Choose white glyphs for backgrounds with low relative luminance."""
        def linear(channel: int) -> float:
            value = channel / 255.0
            return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

        luminance = (
            0.2126 * linear(color.red())
            + 0.7152 * linear(color.green())
            + 0.0722 * linear(color.blue())
        )
        return luminance < 0.42

    def _effective_title_bar_colors(self) -> tuple[QColor, QColor]:
        if self._title_bar_color is None:
            if self._dark_mode:
                return QColor(45, 45, 48), QColor(39, 39, 41)
            return QColor(243, 243, 243), QColor(238, 238, 238)

        active = QColor(self._title_bar_color)
        inactive = (
            QColor(self._inactive_title_bar_color)
            if self._inactive_title_bar_color is not None
            else active.darker(115)
        )
        return active, inactive

    def _apply_palette(self) -> None:
        if not hasattr(self, "root"):
            return
        active_title_bar, inactive_title_bar = self._effective_title_bar_colors()
        title_bar_style = (
            f"#customTitleBar{{background:{self._color_to_css(active_title_bar)};}}"
            f"#customTitleBar[activeWindow=\"false\"]{{background:{self._color_to_css(inactive_title_bar)};}}"
        )
        if self._dark_mode:
            self.setStyleSheet(
                "#windowRoot{background:rgb(32,32,32);}"
                + title_bar_style
                + "QLabel{color:rgb(230,230,230);}"
            )
        else:
            self.setStyleSheet(
                "#windowRoot{background:rgb(248,248,248);}"
                + title_bar_style
                + "QLabel{color:rgb(30,30,30);}"
            )
        if hasattr(self, "title_bar"):
            self.title_bar.setDarkMode(self._title_bar_uses_dark_chrome(active_title_bar))

    def changeEvent(self, event):
        super().changeEvent(event)
        if hasattr(self, "title_bar"):
            self.title_bar.max_button.kind = "restore" if self._is_chrome_maximized() else "max"
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
            # FramelessWindowHint does not always strip all caption-button bits
            # after Qt creates the HWND. Keeping WS_SYSMENU / WS_MINIMIZEBOX
            # makes Windows paint a second caption-button set over the custom
            # controls. Retain only the resize frame and maximize capability
            # required for edge resize and Windows 11 Snap Layouts.
            style &= ~(WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX)
            style |= WS_THICKFRAME | WS_MAXIMIZEBOX
            user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)
            # Tell Windows to re-read the modified non-client style immediately.
            # Without SWP_FRAMECHANGED, stale caption buttons can remain visible
            # until a later unrelated geometry change.
            user32.SetWindowPos(
                wintypes.HWND(hwnd), None, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
            )
            self._apply_windows_dwm_options()

        def _apply_windows_dwm_options(self, hwnd_value: int | None = None) -> None:
            hwnd = wintypes.HWND(hwnd_value if hwnd_value is not None else self._hwnd())
            corner = ctypes.c_int(DWMWCP_ROUND)
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                                         ctypes.byref(corner), ctypes.sizeof(corner))
            # WS_THICKFRAME is necessary for native resize behavior, but on
            # Windows 11 DWM can draw a visible one-pixel frame around this
            # otherwise frameless window (especially noticeable while maximized).
            # Hide that DWM border consistently; unsupported builds report an
            # HRESULT and keep their normal appearance.
            border_color = ctypes.c_uint(DWMWA_COLOR_NONE)
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_BORDER_COLOR,
                                         ctypes.byref(border_color), ctypes.sizeof(border_color))
            dark = wintypes.BOOL(self._dark_mode)
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                         ctypes.byref(dark), ctypes.sizeof(dark))
            backdrop = ctypes.c_int(self._backdrop_type)
            # Attribute 38 is supported on modern Windows 11. An unsupported
            # build reports an HRESULT; it does not raise a Python exception.
            # Ignoring that result deliberately leaves the normal DWM backdrop.
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_SYSTEMBACKDROP_TYPE,
                                         ctypes.byref(backdrop), ctypes.sizeof(backdrop))

        @staticmethod
        def _screen_to_client_native(hwnd: int, x: int, y: int) -> tuple[int, int]:
            pt = POINT(x, y)
            user32.ScreenToClient(wintypes.HWND(hwnd), ctypes.byref(pt))
            return int(pt.x), int(pt.y)

        @staticmethod
        def _native_rect(widget: QWidget, dpr: float) -> tuple[int, int, int, int]:
            top_left = widget.mapTo(widget.window(), QPoint(0, 0))
            return (round(top_left.x() * dpr), round(top_left.y() * dpr),
                    round((top_left.x() + widget.width()) * dpr),
                    round((top_left.y() + widget.height()) * dpr))

        def _window_dpr(self, hwnd: int | None = None) -> float:
            # The hit test arrives in physical pixels. GetDpiForWindow tracks the
            # target monitor during a per-monitor DPI transition more directly
            # than QWindow's cached DPR; Qt remains the fallback for older Windows.
            if get_dpi_for_window is not None:
                dpi = get_dpi_for_window(wintypes.HWND(hwnd if hwnd is not None else self._hwnd()))
                if dpi:
                    return dpi / 96.0
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
                return HTCLIENT
            if inside(self._native_rect(tb.max_button, dpr)):
                return HTMAXBUTTON  # Required for Windows 11 Snap Layout hover.
            if inside(self._native_rect(tb.min_button, dpr)):
                return HTCLIENT
            # The remaining title bar is a Qt client region. CustomTitleBar
            # starts QWindow.startSystemMove() from its mouse press event.
            return HTCLIENT

        def _resize_hit_test(
            self, x: int, y: int, dpr: float, hwnd_value: int | None = None
        ) -> int | None:
            if self._is_chrome_maximized(hwnd_value) or self.isFullScreen():
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
            dpr = self._window_dpr(int(msg.hwnd))
            minimum = self.minimumSize()
            mmi.ptMinTrackSize.x = max(mmi.ptMinTrackSize.x, round(minimum.width() * dpr))
            mmi.ptMinTrackSize.y = max(mmi.ptMinTrackSize.y, round(minimum.height() * dpr))

        def _set_max_button_pressed(self, pressed: bool) -> None:
            self._max_button_pressed = pressed
            self.title_bar.max_button.setDown(pressed)

        def _max_button_contains_native_point(self, x: int, y: int, dpr: float) -> bool:
            left, top, right, bottom = self._native_rect(self.title_bar.max_button, dpr)
            return left <= x < right and top <= y < bottom

        def _begin_max_button_press(
            self, hwnd_value: int, screen_x: int, screen_y: int
        ) -> bool:
            x, y = self._screen_to_client_native(hwnd_value, screen_x, screen_y)
            dpr = self._window_dpr(hwnd_value)
            if not self._max_button_contains_native_point(x, y, dpr):
                return False
            self._set_max_button_pressed(True)
            user32.SetCapture(wintypes.HWND(hwnd_value))
            return True

        def _clear_max_button_press(self, hwnd_value: int) -> None:
            self._set_max_button_pressed(False)
            if int(user32.GetCapture() or 0) == hwnd_value:
                user32.ReleaseCapture()

        def _finish_max_button_press(
            self, hwnd_value: int, x: int, y: int, dpr: float
        ) -> None:
            should_toggle = (
                self._max_button_pressed
                and self._max_button_contains_native_point(x, y, dpr)
            )
            self._clear_max_button_press(hwnd_value)
            if should_toggle:
                # A taskbar restore can still be completing while the first
                # non-client button-up arrives. Queue the transition so Qt and
                # the native HWND agree on the pre-click maximize state.
                QTimer.singleShot(0, self.toggleMaximized)

        def _set_max_button_native_hover(self, hovered: bool) -> None:
            self.title_bar.max_button.setNativeHover(hovered)

        @staticmethod
        def _track_nonclient_mouse_leave(hwnd_value: int) -> None:
            # WM_NCMOUSELEAVE is only guaranteed after explicitly registering
            # a non-client leave tracker. This prevents the custom hover color
            # from getting stuck when the pointer exits the window directly.
            tracker = TRACKMOUSEEVENT()
            tracker.cbSize = ctypes.sizeof(TRACKMOUSEEVENT)
            tracker.dwFlags = TME_LEAVE | TME_NONCLIENT
            tracker.hwndTrack = wintypes.HWND(hwnd_value)
            user32.TrackMouseEvent(ctypes.byref(tracker))

        @staticmethod
        def _show_system_menu(hwnd_value: int, screen_x: int, screen_y: int) -> None:
            hwnd = wintypes.HWND(hwnd_value)
            menu = user32.GetSystemMenu(hwnd, False)
            if not menu:
                return
            command = user32.TrackPopupMenu(menu, TPM_RETURNCMD | TPM_RIGHTBUTTON,
                                             screen_x, screen_y, 0, hwnd, None)
            if command:
                user32.PostMessageW(hwnd, WM_SYSCOMMAND, command, 0)

        def nativeEvent(self, eventType, message):
            msg = ctypes.cast(int(message), ctypes.POINTER(MSG)).contents

            if msg.message == WM_NCACTIVATE:
                # WS_THICKFRAME is retained for native edge-resize behavior, but
                # Windows otherwise repaints that invisible non-client frame on
                # activation. A -1 lParam preserves normal activation while
                # explicitly telling DefWindowProc not to repaint it.
                result = user32.DefWindowProcW(
                    wintypes.HWND(int(msg.hwnd)),
                    wintypes.UINT(msg.message),
                    wintypes.WPARAM(int(msg.wParam)),
                    wintypes.LPARAM(-1),
                )
                return True, int(result)

            if msg.message == WM_NCCALCSIZE:
                return True, 0

            if msg.message == WM_NCMOUSEMOVE:
                # The maximize region is deliberately non-client so Windows 11
                # can offer Snap Layouts. Qt therefore never receives a normal
                # QPushButton hover event for it; mirror that state explicitly
                # while leaving the native message unhandled for the shell.
                if int(msg.wParam) == HTMAXBUTTON:
                    self._track_nonclient_mouse_leave(int(msg.hwnd))
                    self._set_max_button_native_hover(True)
                else:
                    self._set_max_button_native_hover(False)
                return False, 0

            if msg.message == WM_MOUSEMOVE and self.title_bar.max_button.native_hovered:
                x = _signed_word(int(msg.lParam))
                y = _signed_word(int(msg.lParam) >> 16)
                self._set_max_button_native_hover(
                    self._max_button_contains_native_point(
                        x, y, self._window_dpr(int(msg.hwnd))
                    )
                )
                return False, 0

            if msg.message in (WM_NCMOUSELEAVE, WM_MOUSELEAVE):
                self._set_max_button_native_hover(False)
                return False, 0

            if (
                msg.message in (WM_NCLBUTTONDOWN, WM_NCLBUTTONDBLCLK)
                and int(msg.wParam) == HTMAXBUTTON
            ):
                # HTMAXBUTTON is necessary for the Windows 11 Snap Layout hover,
                # but the default non-client click handler would also paint and
                # track a second native maximize button. Keep the hit-test result
                # for Snap and capture the click for the custom button instead.
                screen_x = _signed_word(int(msg.lParam))
                screen_y = _signed_word(int(msg.lParam) >> 16)
                if self._begin_max_button_press(int(msg.hwnd), screen_x, screen_y):
                    return True, 0

            if msg.message == WM_NCLBUTTONUP and self._max_button_pressed:
                screen_x = _signed_word(int(msg.lParam))
                screen_y = _signed_word(int(msg.lParam) >> 16)
                x, y = self._screen_to_client_native(int(msg.hwnd), screen_x, screen_y)
                self._finish_max_button_press(
                    int(msg.hwnd), x, y, self._window_dpr(int(msg.hwnd))
                )
                return True, 0

            if msg.message == WM_LBUTTONUP and self._max_button_pressed:
                x = _signed_word(int(msg.lParam))
                y = _signed_word(int(msg.lParam) >> 16)
                self._finish_max_button_press(
                    int(msg.hwnd), x, y, self._window_dpr(int(msg.hwnd))
                )
                return True, 0

            if msg.message in (WM_CANCELMODE, WM_CAPTURECHANGED) and self._max_button_pressed:
                self._clear_max_button_press(int(msg.hwnd))
                return True, 0

            if msg.message == WM_GETMINMAXINFO:
                self._handle_getminmaxinfo(msg)
                return True, 0

            if msg.message == WM_NCHITTEST:
                screen_x = _signed_word(int(msg.lParam))
                screen_y = _signed_word(int(msg.lParam) >> 16)
                x, y = self._screen_to_client_native(int(msg.hwnd), screen_x, screen_y)
                dpr = self._window_dpr(int(msg.hwnd))
                resize = self._resize_hit_test(x, y, dpr, int(msg.hwnd))
                if resize is not None:
                    return True, resize
                caption = self._caption_hit_test(x, y, dpr)
                if caption is not None:
                    return True, caption
                return True, HTCLIENT

            if msg.message == WM_NCRBUTTONUP and int(msg.wParam) in (HTCAPTION, HTSYSMENU):
                screen_x = _signed_word(int(msg.lParam))
                screen_y = _signed_word(int(msg.lParam) >> 16)
                self._show_system_menu(int(msg.hwnd), screen_x, screen_y)
                return True, 0

            if msg.message == WM_DPICHANGED:
                # Qt applies the suggested geometry itself. Re-apply DWM options
                # after the transition; hit tests always query the current DPR.
                self._apply_windows_dwm_options(int(msg.hwnd))

            # Do *not* call QMainWindow.nativeEvent() here. In PyQt6 that can
            # recurse through the Python override while the HWND is being created
            # and terminate the process with an access violation. Returning False
            # is Qt's documented way to let it dispatch an unhandled native event.
            return False, 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessMainWindow()
    window.show()
    sys.exit(app.exec())
