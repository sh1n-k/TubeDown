import shutil
import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QMessageBox

from config import Config
from ui.main_window import MainWindow


def check_ffmpeg():
    """Check if FFmpeg is available in system PATH."""
    return shutil.which("ffmpeg") is not None


def main():
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("MyCompany")
    QCoreApplication.setApplicationName("YouTubeDownloader")

    if not check_ffmpeg():
        QMessageBox.critical(
            None,
            "Error",
            "FFmpeg is not installed or not found in system PATH. Please install FFmpeg to use this application.",
        )
        sys.exit(1)

    config = Config()
    window = MainWindow(config, app.clipboard())
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
