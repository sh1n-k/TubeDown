from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar, QToolTip
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QCursor
import requests
from urllib.parse import parse_qs, urlparse


class ThumbnailCache:
    """Cache for storing downloaded thumbnails."""

    def __init__(self):
        self.thumbnails = {}

    def get(self, video_id):
        return self.thumbnails.get(video_id)

    def set(self, video_id, pixmap):
        self.thumbnails[video_id] = pixmap


class ThumbnailLabel(QLabel):
    """Custom label for thumbnail display."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(
            """
            QLabel {
                background-color: white;
                border: 1px solid #ccc;
                padding: 5px;
            }
        """
        )
        self.hide()


class DownloadItemWidget(QWidget):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.thumbnail_cache = ThumbnailCache()
        self.thumbnail_label = ThumbnailLabel()
        self.setup_ui()
        self.setup_thumbnail()

        # Enable mouse tracking for hover events
        self.setMouseTracking(True)

        # Timer for delayed thumbnail display
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.show_thumbnail)

    def setup_ui(self):
        layout = QHBoxLayout()
        self.label = QLabel(self.url)
        self.progress_bar = QProgressBar()
        self.subtitle_label = QLabel("Subtitles: Not Downloaded")
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.subtitle_label)
        self.setLayout(layout)

    def setup_thumbnail(self):
        """Download and cache the video thumbnail."""
        video_id = self.extract_video_id(self.url)
        if not video_id:
            return

        if self.thumbnail_cache.get(video_id):
            return

        try:
            # Get thumbnail URL (using high quality thumbnail)
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            response = requests.get(thumbnail_url)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                # Scale the thumbnail to a reasonable size
                pixmap = pixmap.scaled(
                    320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.thumbnail_cache.set(video_id, pixmap)
        except Exception as e:
            print(f"Error loading thumbnail: {e}")

    def extract_video_id(self, url):
        """Extract video ID from YouTube URL."""
        parsed_url = urlparse(url)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            if parsed_url.path == "/watch":
                return parse_qs(parsed_url.query).get("v", [None])[0]
            elif parsed_url.path.startswith("/shorts/"):
                return parsed_url.path.split("/shorts/")[1].split("/")[0]
        elif parsed_url.hostname == "youtu.be":
            return parsed_url.path[1:]
        return None

    def enterEvent(self, event):
        """Start timer when mouse enters the widget."""
        self.preview_timer.start(100)  # Show preview after 500ms hover

    def leaveEvent(self, event):
        """Hide thumbnail when mouse leaves the widget."""
        self.preview_timer.stop()
        self.thumbnail_label.hide()

    def mouseMoveEvent(self, event):
        """Update thumbnail position as mouse moves."""
        if self.thumbnail_label.isVisible():
            self.update_thumbnail_position()

    def update_thumbnail_position(self):
        """Update the position of the thumbnail label."""
        cursor_pos = QCursor.pos()
        # Offset the thumbnail so it doesn't appear directly under the cursor
        self.thumbnail_label.move(cursor_pos.x() + 10, cursor_pos.y() + 10)

    def show_thumbnail(self):
        """Show thumbnail at current cursor position."""
        video_id = self.extract_video_id(self.url)
        if not video_id:
            return

        thumbnail = self.thumbnail_cache.get(video_id)
        if not thumbnail:
            return

        # Set the thumbnail image to the label
        self.thumbnail_label.setPixmap(thumbnail)
        self.thumbnail_label.adjustSize()
        self.update_thumbnail_position()
        self.thumbnail_label.show()

    def update_progress(self, percent):
        self.progress_bar.setValue(int(percent))

    def update_subtitle_status(self, status):
        self.subtitle_label.setText(f"Subtitles: {status}")

    def __del__(self):
        """Clean up thumbnail label when widget is destroyed."""
        self.thumbnail_label.deleteLater()
