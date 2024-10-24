import os
import sys

from PyQt5.QtCore import QSettings


def get_system_download_folder():
    """Get system's default download folder."""
    if sys.platform.startswith('win'):
        import winreg
        try:
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                return winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
        except Exception:
            return None
    return os.path.expanduser('~/Downloads')


class Config:
    def __init__(self):
        self.settings = QSettings('MyCompany', 'YouTubeDownloader')
        self.load_settings()

    def load_settings(self):
        self.concurrent_downloads = self.settings.value('concurrent_downloads', 2, type=int)
        self.download_path = self.settings.value('download_path', get_system_download_folder())
        self.video_quality = self.settings.value('video_quality', 'best', type=str)
        self.download_subtitles = self.settings.value('download_subtitles', True, type=bool)

    def save_settings(self, concurrent_downloads, download_path, video_quality, download_subtitles):
        self.settings.setValue('concurrent_downloads', concurrent_downloads)
        self.settings.setValue('download_path', download_path)
        self.settings.setValue('video_quality', video_quality)
        self.settings.setValue('download_subtitles', download_subtitles)
        self.load_settings()
