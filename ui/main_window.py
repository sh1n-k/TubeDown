import os
from threading import Lock

from PyQt5.QtCore import QTimer, QThreadPool
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from downloader import WorkerSignals, DownloadWorker
from utils import YOUTUBE_REGEX, extract_video_id
from .download_item import DownloadItemWidget
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """
    Main application window that handles:
    - Clipboard monitoring for YouTube URLs
    - Download management
    - UI updates
    - Settings management
    """

    def __init__(self, config, clipboard):
        """
        Initialize the main window with configuration and clipboard access.

        Args:
            config: Application configuration object
            clipboard: System clipboard instance
        """
        super().__init__()
        self.config = config
        self.clipboard = clipboard

        # Initialize internal state
        self.downloaded_urls = set()  # Track completed downloads
        self.active_downloads = {}  # Current download operations
        self.download_progress = {}  # Progress for each download
        self.clipboard_lock = Lock()  # Thread safety for clipboard operations

        # Setup UI and systems
        self._setup_window()
        self._setup_threadpool()
        self._setup_clipboard_monitoring()

    def _setup_window(self):
        """Configure the main window appearance and layout."""
        self.setWindowTitle("YouTube Downloader")
        self.resize(600, 400)

        # Create main layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Add UI components
        self._create_status_label()
        self._create_download_list()
        self._create_settings_button()

    def _setup_threadpool(self):
        """Configure the thread pool for download operations."""
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(self.config.concurrent_downloads)

    def _setup_clipboard_monitoring(self):
        """Initialize clipboard monitoring system."""
        self.last_clipboard = self.clipboard.text()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)

        # Backup timer for clipboard monitoring
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(1000)  # Check every second

    def _create_status_label(self):
        """Create and add the status label to the layout."""
        self.status_label = QLabel("Monitoring clipboard for YouTube URLs...")
        self.layout.addWidget(self.status_label)

    def _create_download_list(self):
        """Create and add the download list widget to the layout."""
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

    def _create_settings_button(self):
        """Create and add the settings button to the layout."""
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        self.layout.addWidget(self.settings_button)

    def check_clipboard(self):
        """Periodic clipboard content check."""
        with self.clipboard_lock:
            current_text = self.clipboard.text()
            if current_text != self.last_clipboard:
                self.last_clipboard = current_text
                self.on_clipboard_change()

    def on_clipboard_change(self):
        """Handle clipboard content changes and detect YouTube URLs."""
        text = self.clipboard.text()
        if YOUTUBE_REGEX.match(text):
            video_id = extract_video_id(text)
            if video_id and video_id not in self.downloaded_urls:
                self.start_download(text)
                self.clipboard.clear()

    def start_download(self, url):
        """
        Initialize and start a new download operation.

        Args:
            url: YouTube URL to download
        """
        # Create signals for the download worker
        signals = WorkerSignals()
        signals.finished.connect(self.on_download_finished)
        signals.error.connect(self.on_download_error)
        signals.progress.connect(self.on_download_progress)

        # Create and start download worker
        worker = DownloadWorker(
            url=url,
            download_path=self.config.download_path,
            quality=self.config.video_quality,
            signals=signals,
            download_subtitles=self.config.download_subtitles,
        )
        self.active_downloads[url] = worker
        self.threadpool.start(worker)

        # Add download item to UI
        self._add_download_item(url)

    def _add_download_item(self, url):
        """Add a new download item to the list widget."""
        item = QListWidgetItem()
        widget = DownloadItemWidget(url)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def on_download_finished(self, url):
        """
        Handle completed downloads.

        Args:
            url: URL of completed download
        """
        self.downloaded_urls.add(url)
        self._update_download_widget(url, status="complete")
        self._cleanup_download(url)

    def on_download_error(self, message):
        """
        Handle download errors.

        Args:
            message: Error message string
        """
        QMessageBox.critical(self, "Download Error", message)
        url = message.split(":")[0]
        self._update_download_widget(url, status="error")
        self._cleanup_download(url)

    def _cleanup_download(self, url):
        """Clean up after download completion or error."""
        self.active_downloads.pop(url, None)
        self.download_progress.pop(url, None)
        self.update_status_label()

    def _update_download_widget(self, url, status):
        """
        Update the UI widget for a download.

        Args:
            url: Download URL
            status: New status ("complete" or "error")
        """
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            widget = self.list_widget.itemWidget(item)
            if widget.label.text() == url:
                if status == "complete":
                    widget.label.setText(f"Downloaded: {url}")
                    widget.update_progress(100.0)
                    if self.config.download_subtitles:
                        widget.update_subtitle_status("Downloaded")
                else:
                    widget.label.setText(f"Failed: {url}")
                    widget.update_progress(0.0)
                    if self.config.download_subtitles:
                        widget.update_subtitle_status("Failed")
                break

    def on_download_progress(self, url, percent):
        """
        Update download progress in UI.

        Args:
            url: Download URL
            percent: Progress percentage
        """
        self.download_progress[url] = percent
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            widget = self.list_widget.itemWidget(item)
            if widget.label.text() == url:
                widget.update_progress(percent)
                break
        self.update_status_label()

    def update_status_label(self):
        """Update the status label with current download progress."""
        if not self.active_downloads:
            self.status_label.setText("Monitoring clipboard for YouTube URLs...")
            return

        status_text = []
        for url, progress in self.download_progress.items():
            if progress < 100:
                status_text.append(f"{url.split('/')[-1]}: {progress:.1f}%")

        if status_text:
            self.status_label.setText(" | ".join(status_text))

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            self.threadpool.setMaxThreadCount(self.config.concurrent_downloads)
            if not self.config.download_path or not os.path.isdir(
                self.config.download_path
            ):
                QMessageBox.warning(
                    self,
                    "Download Path Missing",
                    "Please set a valid download path in Settings.",
                )

    def closeEvent(self, event):
        """Handle application close event."""
        reply = QMessageBox.question(
            self,
            "Quit",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        event.accept() if reply == QMessageBox.Yes else event.ignore()
