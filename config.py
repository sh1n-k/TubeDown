import os
import sys

from PyQt5.QtCore import QSettings


def get_system_download_folder():
    """
    시스템의 기본 다운로드 폴더 경로를 가져옵니다.

    Windows, macOS, Linux 운영체제를 지원합니다.
    Windows: 레지스트리에서 다운로드 폴더 경로를 읽어옵니다.
    macOS/Linux: 사용자 홈 디렉토리의 'Downloads' 폴더 경로를 반환합니다.

    Returns:
        str: 시스템 기본 다운로드 폴더 경로. 찾을 수 없으면 None 반환 (Windows).
    """
    if sys.platform.startswith("win"):
        import winreg

        try:
            sub_key = (
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            )
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                return winreg.QueryValueEx(
                    key, "{374DE290-123F-4565-9164-39C4925E467B}"
                )[0]
        except Exception:
            return None  # Windows 레지스트리에서 다운로드 폴더를 찾을 수 없을 때 None 반환
    return os.path.expanduser("~/Downloads")  # macOS 및 Linux 기본 다운로드 폴더 경로


class Config:
    """
    어플리케이션 설정을 관리하는 클래스입니다.

    QSettings를 사용하여 설정을 저장하고 불러옵니다.
    설정 값은 동시 다운로드 수, 다운로드 경로, 비디오 품질, 자막 다운로드 여부입니다.
    """

    def __init__(self):
        """Config 클래스 초기화."""
        self.settings = QSettings("MyCompany", "YouTubeDownloader")
        self.load_settings()

    def load_settings(self):
        """
        QSettings에서 설정을 불러와 Config 객체 속성에 저장합니다.

        각 설정 값이 없을 경우 기본값을 사용합니다.
        """
        self.concurrent_downloads = self.settings.value(
            "concurrent_downloads", 2, type=int
        )
        self.download_path = self.settings.value(
            "download_path", get_system_download_folder()
        )
        self.video_quality = self.settings.value("video_quality", "FHD", type=str)  # 기본 품질 'FHD' 로 변경
        self.download_subtitles = self.settings.value(
            "download_subtitles", True, type=bool
        )

    def save_settings(
            self, concurrent_downloads, download_path, video_quality, download_subtitles
    ):
        """
        변경된 설정을 QSettings에 저장하고, Config 객체 속성을 업데이트합니다.

        Args:
            concurrent_downloads (int): 동시 다운로드 수
            download_path (str): 다운로드 경로
            video_quality (str): 비디오 품질 설정
            download_subtitles (bool): 자막 다운로드 여부
        """
        self.settings.setValue("concurrent_downloads", concurrent_downloads)
        self.settings.setValue("download_path", download_path)
        self.settings.setValue("video_quality", video_quality)
        self.settings.setValue("download_subtitles", download_subtitles)
        self.load_settings()  # 설정 저장 후 객체 속성 즉시 업데이트
