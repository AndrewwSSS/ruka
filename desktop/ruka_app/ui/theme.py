"""Forces a light UI regardless of the OS theme.

macOS/Windows dark mode would otherwise repaint the whole app dark. The
native styles ignore palette overrides in dark mode, so this switches to
Fusion -- which honours the palette on every platform -- and hands it an
explicit light palette.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

WINDOW = QColor("#ffffff")
BASE = QColor("#ffffff")
ALTERNATE_BASE = QColor("#f5f5f5")
BUTTON = QColor("#f0f0f0")
TEXT = QColor("#1a1a1a")
DISABLED_TEXT = QColor("#9a9a9a")
HIGHLIGHT = QColor("#3874d8")
BORDER = QColor("#c8c8c8")


def light_palette() -> QPalette:
    palette = QPalette()

    palette.setColor(QPalette.Window, WINDOW)
    palette.setColor(QPalette.WindowText, TEXT)
    palette.setColor(QPalette.Base, BASE)
    palette.setColor(QPalette.AlternateBase, ALTERNATE_BASE)
    palette.setColor(QPalette.Text, TEXT)
    palette.setColor(QPalette.Button, BUTTON)
    palette.setColor(QPalette.ButtonText, TEXT)
    palette.setColor(QPalette.BrightText, QColor("#d32f2f"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffdc"))
    palette.setColor(QPalette.ToolTipText, TEXT)
    palette.setColor(QPalette.PlaceholderText, DISABLED_TEXT)
    palette.setColor(QPalette.Highlight, HIGHLIGHT)
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.Light, QColor("#ffffff"))
    palette.setColor(QPalette.Midlight, QColor("#e3e3e3"))
    palette.setColor(QPalette.Mid, BORDER)
    palette.setColor(QPalette.Dark, QColor("#a0a0a0"))
    palette.setColor(QPalette.Shadow, QColor("#707070"))

    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText, QPalette.HighlightedText):
        palette.setColor(QPalette.Disabled, role, DISABLED_TEXT)
    palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor("#dcdcdc"))

    return palette


def apply_light_theme(app: QApplication) -> None:
    # Qt 6.8+ only: also keeps native dialogs and window frames light.
    try:
        app.styleHints().setColorScheme(Qt.ColorScheme.Light)
    except AttributeError:
        pass

    app.setStyle("Fusion")
    app.setPalette(light_palette())
