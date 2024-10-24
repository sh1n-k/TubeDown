import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from config import Config
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("MyCompany")
    QCoreApplication.setApplicationName("YouTubeDownloader")

    config = Config()
    window = MainWindow(config, app.clipboard())
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
