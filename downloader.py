import os

import yt_dlp
from PyQt5.QtCore import QRunnable, pyqtSlot, pyqtSignal, QObject


class WorkerSignals(QObject):
    """
    DownloadWorker 스레드에서 발생하는 시그널을 정의합니다.

    finished: 다운로드 완료 시그널, URL을 인자로 전달합니다.
    error: 다운로드 에러 시그널, 에러 메시지를 인자로 전달합니다.
    progress: 다운로드 진행률 시그널, URL과 진행률(0.0~100.0)을 인자로 전달합니다.
    """
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str, float)


class DownloadWorker(QRunnable):
    """
    yt-dlp를 사용하여 비디오를 다운로드하는 워커 스레드입니다.

    Attributes:
        QUALITY_MAPPING (dict): 비디오 품질 옵션과 yt-dlp format string 매핑
    """
    QUALITY_MAPPING = {
        "FHD": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "best": "best",
        "worst": "worst",
        "bestvideo+bestaudio": "bestvideo+bestaudio/best",
        "bestvideo": "bestvideo/best",
        "bestaudio": "bestaudio/best",
    }

    def __init__(self, url, download_path, quality, signals, download_subtitles):
        """
        DownloadWorker 초기화.

        Args:
            url (str): 다운로드할 YouTube URL
            download_path (str): 다운로드 경로
            quality (str): 비디오 품질 설정
            signals (WorkerSignals): WorkerSignals 객체 (시그널 emit 용)
            download_subtitles (bool): 자막 다운로드 여부
        """
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.quality = quality
        self.signals = signals
        self.download_subtitles = download_subtitles
        self.is_interrupted = False # 다운로드 중단 플래그 추가

    @pyqtSlot()
    def run(self):
        """
        워커 스레드의 메인 실행 함수입니다. yt-dlp를 사용하여 다운로드를 실행하고,
        진행률, 완료, 에러 시그널을 emit 합니다.
        """
        def progress_hook(d):
            """yt-dlp progress hook function. 다운로드 진행 상황을 signals.progress 시그널로 emit 합니다."""
            if self.is_interrupted:  # 다운로드 중단 요청 확인
                raise yt_dlp.DownloadError("다운로드 중단됨", interrupted=True)
            if d["status"] == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
                if total_bytes:
                    progress_percent = d.get("downloaded_bytes", 0) / total_bytes * 100
                    self.signals.progress.emit(self.url, progress_percent)
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
                    "subtitleslangs": ["en", "ko"], # 영어, 한국어 자막 다운로드
                    "writeautomaticsub": True, # 자동 생성 자막 다운로드
                    "subtitle_format": "best", # 최적 자막 포맷
                }
            )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.signals.progress.emit(self.url, 0.0) # 초기 진행률 0% emit
                ydl.download([self.url])
            self.signals.finished.emit(self.url) # 다운로드 완료 시 finished 시그널 emit
        except yt_dlp.DownloadError as e: # yt-dlp 다운로드 에러 처리
            if e.exc_info and isinstance(e.exc_info[1], yt_dlp.DownloadError) and e.exc_info[1].interrupted:
                self.signals.error.emit(f"다운로드 중단됨: {self.url}") # 사용자에게 중단 메시지 표시
            else:
                error_message = f"다운로드 오류: {self.url} - {e}"
                self.signals.error.emit(error_message) # 다운로드 에러 시 error 시그널 emit
        except Exception as e: # 예상치 못한 에러 처리
            error_message = f"예상치 못한 오류 발생: {self.url} - {e}"
            self.signals.error.emit(error_message) # 예외 발생 시 error 시그널 emit

    def stop(self):
        """
        다운로드 작업을 중단합니다. `is_interrupted` 플래그를 설정하고, progress_hook 에서 확인하여 yt-dlp 다운로드를 중단시킵니다.
        """
        self.is_interrupted = True