import os

import yt_dlp
from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject


class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str, float)


class DownloadWorker(QRunnable):
    QUALITY_MAPPING = {
        "FHD": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "best": "best",
        "worst": "worst",
        "bestvideo+bestaudio": "bestvideo+bestaudio/best",
        "bestvideo": "bestvideo/best",
        "bestaudio": "bestaudio/best",
    }

    def __init__(self, url, download_path, quality, signals, download_subtitles):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.quality = quality
        self.signals = signals
        self.download_subtitles = download_subtitles

    @pyqtSlot()
    def run(self):
        def progress_hook(d):
            if d["status"] == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
                if total_bytes:
                    progress = d.get("downloaded_bytes", 0) / total_bytes * 100
                    self.signals.progress.emit(self.url, progress)
            elif d["status"] == "finished":
                self.signals.progress.emit(self.url, 100.0)

        ydl_opts = {
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "format": self.QUALITY_MAPPING.get(self.quality, "best"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [progress_hook],
        }

        if self.download_subtitles:
            ydl_opts.update(
                {
                    "writesubtitles": True,
                    "subtitleslangs": ["en", "ko"],
                    "writeautomaticsub": True,
                    "subtitle_format": "best",
                }
            )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.signals.progress.emit(self.url, 0.0)
                ydl.download([self.url])
            self.signals.finished.emit(self.url)
        except Exception as e:
            self.signals.error.emit(f"Error downloading {self.url}: {str(e)}")
