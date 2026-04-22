import sys
from PyQt6.QtWidgets import (
    QApplication,
    QSplashScreen,
)
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtCore import Qt, QTimer, QSize
from constants import (
    LOGO
)
from util import (
    isDevMode
)
from windows import UDPConfigWindow

global_main_window = None

def main():
    app = QApplication(sys.argv)
    screen_size = QGuiApplication.primaryScreen().size()/2

    # set application to scale according to user screen size
    pixmap = QPixmap(f"{LOGO}").scaled(QSize(screen_size))
    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)

    # Ensure window splashes on top of all other applications on start up
    splash.show()
    app.processEvents()
    
    def show_config():
        splash.close()
        config = UDPConfigWindow(splash.size())
        config.show()

        global global_main_window
        global_main_window = config

    QTimer.singleShot(0 if isDevMode() else 3000, show_config)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()