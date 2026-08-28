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
from PyQt6.QtWidgets import QApplication

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

    @unittest.skipUnless(IS_WINDOWS, "Windows-only native hit test")
    def test_windows_caption_hit_test_uses_title_bar_geometry(self) -> None:
        dpr = self.window._window_dpr()
        left, top, right, bottom = self.window._native_rect(self.window.titleBar().title, dpr)
        self.assertEqual(
            self.window._caption_hit_test((left + right) // 2, (top + bottom) // 2, dpr),
            fw.HTCAPTION,
        )

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


if __name__ == "__main__":
    unittest.main()
