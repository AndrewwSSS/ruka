import sys

from PySide6.QtWidgets import QApplication

from ruka_app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Ruka Control")
    app.setOrganizationName("Ruka")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
