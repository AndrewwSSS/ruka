import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from ruka_app.core.paths import resource_path
from ruka_app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Ruka Control")
    app.setOrganizationName("Ruka")
    app.setWindowIcon(QIcon(str(resource_path("resources", "app_icon.png"))))

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
