"""Smoke and regression tests for the standalone frameless-window example."""

from __future__ import annotations

import ctypes
import os
import sys
import unittest

# This needs to run before PyQt6 is imported on CI Linux runners. Windows uses
# the real QPA backend so the native-handle creation path is covered there.
if sys.platform != "win32":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6 import sip
from PyQt6.QtWidgets import QApplication, QWidget

import frameless_mainwindow as fw

FramelessMainWindow = fw.FramelessMainWindow
IS_WINDOWS = fw.IS_WINDOWS


class FramelessMainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = FramelessMainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self) -> None:
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_window_starts_and_title_bar_preserves_qwidget_window_method(self) -> None:
        self.assertTrue(self.window.isVisible())
        self.assertIs(self.window.titleBar().window(), self.window)

    def test_title_and_theme_stay_in_sync(self) -> None:
        self.window.setWindowTitle("Regression test")
        self.assertEqual(self.window.titleBar().title.text(), "Regression test")

        self.window.setDarkMode(False)
        self.assertFalse(self.window.titleBar().dark_mode)
        self.assertFalse(self.window.titleBar().max_button.dark_mode)
        self.assertIn("rgb(30,30,30)", self.window.titleBar().title.styleSheet())

        self.window.setMicaEnabled(False)
        self.assertEqual(self.window._backdrop_type, 1 if IS_WINDOWS else 0)

        if IS_WINDOWS:
            self.window.setWindowsBackdrop("none")
            self.assertEqual(self.window._backdrop_type, 1)

    def test_custom_title_bar_color_is_applied_and_can_be_reset(self) -> None:
        self.window.setTitleBarColor("#2563eb", "#1e3a8a")
        self.app.processEvents()
        self.assertEqual(self.window.titleBarColor().name(), "#2563eb")
        self.assertTrue(self.window.titleBar().dark_mode)
        self.assertIn("rgba(37,99,235,255)", self.window.styleSheet())
        self.assertIn("rgba(30,58,138,255)", self.window.styleSheet())
        rendered_color = self.window.titleBar().grab().toImage().pixelColor(300, 20)
        self.assertEqual(rendered_color.getRgb(), (37, 99, 235, 255))

        self.window.resetTitleBarColor()
        self.assertEqual(self.window.titleBarColor().name(), "#2d2d30")
        self.assertTrue(self.window.titleBar().dark_mode)

        with self.assertRaises(ValueError):
            self.window.setTitleBarColor("not a color")

    @unittest.skipUnless(IS_WINDOWS, "Windows-only native hit test")
    def test_windows_caption_hit_test_uses_title_bar_geometry(self) -> None:
        dpr = self.window._window_dpr()
        left, top, right, bottom = self.window._native_rect(self.window.titleBar().title, dpr)
        self.assertEqual(
            self.window._caption_hit_test((left + right) // 2, (top + bottom) // 2, dpr),
            fw.HTCAPTION,
        )

    @unittest.skipUnless(IS_WINDOWS, "Windows-only custom caption controls")
    def test_windows_caption_styles_do_not_draw_native_buttons(self) -> None:
        style = fw.user32.GetWindowLongPtrW(self.window._hwnd(), fw.GWL_STYLE)
        native_caption_bits = fw.WS_CAPTION | fw.WS_SYSMENU | fw.WS_MINIMIZEBOX
        self.assertEqual(style & native_caption_bits, 0)
        self.assertTrue(style & fw.WS_THICKFRAME)
        self.assertTrue(style & fw.WS_MAXIMIZEBOX)

        dpr = self.window._window_dpr()
        for button in (self.window.titleBar().min_button, self.window.titleBar().close_button):
            left, top, right, bottom = self.window._native_rect(button, dpr)
            self.assertEqual(
                self.window._caption_hit_test((left + right) // 2, (top + bottom) // 2, dpr),
                fw.HTCLIENT,
            )

        max_left, max_top, max_right, max_bottom = self.window._native_rect(
            self.window.titleBar().max_button, dpr
        )
        close_left, close_top, close_right, close_bottom = self.window._native_rect(
            self.window.titleBar().close_button, dpr
        )
        self.assertEqual(
            self.window._caption_hit_test(max_right - 1, (max_top + max_bottom) // 2, dpr),
            fw.HTMAXBUTTON,
        )
        self.assertEqual(
            self.window._caption_hit_test(close_left, (close_top + close_bottom) // 2, dpr),
            fw.HTCLIENT,
        )

    @unittest.skipUnless(IS_WINDOWS, "Windows-only custom maximize handler")
    def test_windows_maximize_button_does_not_delegate_to_native_caption_tracking(self) -> None:
        dpr = self.window._window_dpr(self.window._hwnd())
        left, top, right, bottom = self.window._native_rect(
            self.window.titleBar().max_button, dpr
        )
        client_x, client_y = (left + right) // 2, (top + bottom) // 2
        screen_point = fw.POINT(client_x, client_y)
        client_to_screen = fw.user32.ClientToScreen
        client_to_screen.restype = fw.wintypes.BOOL
        client_to_screen.argtypes = (fw.wintypes.HWND, ctypes.POINTER(fw.POINT))
        self.assertTrue(
            client_to_screen(
                fw.wintypes.HWND(self.window._hwnd()), ctypes.byref(screen_point)
            )
        )

        down = fw.MSG()
        down.hwnd = self.window._hwnd()
        down.message = fw.WM_NCLBUTTONDOWN
        down.wParam = fw.HTMAXBUTTON
        down.lParam = (screen_point.x & 0xFFFF) | ((screen_point.y & 0xFFFF) << 16)
        self.assertEqual(
            self.window.nativeEvent(
                b"windows_generic_MSG", sip.voidptr(ctypes.addressof(down))
            ),
            (True, 0),
        )
        self.assertTrue(self.window._max_button_pressed)
        self.assertTrue(self.window.titleBar().max_button.isDown())

        up = fw.MSG()
        up.hwnd = self.window._hwnd()
        up.message = fw.WM_LBUTTONUP
        up.lParam = (client_x & 0xFFFF) | ((client_y & 0xFFFF) << 16)
        self.assertEqual(
            self.window.nativeEvent(
                b"windows_generic_MSG", sip.voidptr(ctypes.addressof(up))
            ),
            (True, 0),
        )
        self.app.processEvents()
        self.assertFalse(self.window._max_button_pressed)
        self.assertFalse(self.window.titleBar().max_button.isDown())
        self.assertEqual(int(fw.user32.GetCapture() or 0), 0)
        self.assertTrue(self.window.isMaximized())

    @unittest.skipUnless(IS_WINDOWS, "Windows-only native messages")
    def test_windows_unhandled_messages_and_caption_hit_are_safe(self) -> None:
        generic = fw.MSG()
        generic.hwnd = self.window._hwnd()
        generic.message = 0x0046  # WM_WINDOWPOSCHANGING
        generic_result = self.window.nativeEvent(
            b"windows_generic_MSG", sip.voidptr(ctypes.addressof(generic))
        )
        self.assertEqual(generic_result, (False, 0))

        dpr = self.window._window_dpr(self.window._hwnd())
        left, top, right, bottom = self.window._native_rect(self.window.title_bar.title, dpr)
        point = fw.POINT((left + right) // 2, (top + bottom) // 2)
        client_to_screen = fw.user32.ClientToScreen
        client_to_screen.restype = fw.wintypes.BOOL
        client_to_screen.argtypes = (fw.wintypes.HWND, ctypes.POINTER(fw.POINT))
        self.assertTrue(
            client_to_screen(fw.wintypes.HWND(self.window._hwnd()), ctypes.byref(point))
        )

        hit = fw.MSG()
        hit.hwnd = self.window._hwnd()
        hit.message = fw.WM_NCHITTEST
        hit.lParam = (point.x & 0xFFFF) | ((point.y & 0xFFFF) << 16)
        hit_result = self.window.nativeEvent(
            b"windows_generic_MSG", sip.voidptr(ctypes.addressof(hit))
        )
        self.assertEqual(hit_result, (True, fw.HTCAPTION))

    @unittest.skipUnless(IS_WINDOWS, "Windows-only taskbar-aware maximize")
    def test_windows_maximize_uses_the_screen_work_area(self) -> None:
        self.window.showMaximized()
        self.app.processEvents()
        self.assertEqual(self.window.geometry(), self.window.screen().availableGeometry())

    @unittest.skipUnless(IS_WINDOWS, "Windows-only non-client activation behavior")
    def test_windows_activation_does_not_paint_a_native_frame(self) -> None:
        other_window = QWidget()
        other_window.resize(200, 100)
        other_window.show()
        try:
            other_window.activateWindow()
            self.app.processEvents()
            self.window.activateWindow()
            self.window.raise_()
            self.app.processEvents()

            image = self.window.screen().grabWindow(self.window._hwnd()).toImage()
            self.assertEqual(image.pixelColor(0, 100).getRgb(), (32, 32, 32, 255))
        finally:
            other_window.close()
            self.app.processEvents()


if __name__ == "__main__":
    unittest.main()
