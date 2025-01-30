from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QCursor
import requests
from urllib.parse import parse_qs, urlparse


class ThumbnailCache:
    """
    다운로드한 썸네일을 캐싱하는 클래스입니다.

    메모리에 썸네일을 저장하여, 동일한 썸네일을 다시 다운로드하는 것을 방지하여 효율성을 높입니다.
    """
    def __init__(self):
        """ThumbnailCache 초기화."""
        self.thumbnails = {} # 썸네일 저장 딕셔너리 (video_id: QPixmap)

    def get(self, video_id):
        """
        캐시에서 video_id에 해당하는 썸네일을 가져옵니다.

        Args:
            video_id (str): YouTube 비디오 ID

        Returns:
            QPixmap: 캐시에 썸네일이 있으면 QPixmap, 없으면 None
        """
        return self.thumbnails.get(video_id)

    def set(self, video_id, pixmap):
        """
        캐시에 video_id와 썸네일(QPixmap)을 저장합니다.

        Args:
            video_id (str): YouTube 비디오 ID
            pixmap (QPixmap): 썸네일 이미지 (QPixmap 객체)
        """
        self.thumbnails[video_id] = pixmap


class ThumbnailLabel(QLabel):
    """
    썸네일 이미지를 툴팁처럼 보여주기 위한 커스텀 QLabel 입니다.

    마우스 호버 시 썸네일을 표시하고, 마우스 이동에 따라 썸네일 위치를 업데이트합니다.
    """
    def __init__(self):
        """ThumbnailLabel 초기화."""
        super().__init__()
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint) # 툴팁 스타일, 테두리 제거
        self.setAttribute(Qt.WA_TranslucentBackground) # 배경 투명
        self.setStyleSheet(
            """
            QLabel {
                background-color: white; # 배경색 흰색
                border: 1px solid #ccc; # 테두리 스타일
                padding: 5px; # 패딩
            }
        """
        )
        self.hide() # 초기 상태: 숨김


class DownloadItemWidget(QWidget):
    """
    다운로드 목록에 표시되는 각 다운로드 아이템 위젯입니다.

    YouTube URL, 진행률 표시줄, 자막 상태, 썸네일 미리보기 기능을 제공합니다.
    """
    def __init__(self, url):
        """
        DownloadItemWidget 초기화.

        Args:
            url (str): YouTube 비디오 URL
        """
        super().__init__()
        self.url = url
        self.thumbnail_cache = ThumbnailCache() # 썸네일 캐시 객체 생성
        self.thumbnail_label = ThumbnailLabel() # 썸네일 라벨 객체 생성
        self.setup_ui() # UI 설정
        self.setup_thumbnail() # 썸네일 설정

        self.setMouseTracking(True) # 마우스 트래킹 활성화 (hover event 감지)

        self.preview_timer = QTimer() # 썸네일 미리보기 타이머
        self.preview_timer.setSingleShot(True) # 싱글샷 타이머 설정
        self.preview_timer.timeout.connect(self.show_thumbnail) # 타임아웃 시 show_thumbnail 호출

    def setup_ui(self):
        """UI 레이아웃 및 기본 위젯 설정."""
        layout = QHBoxLayout()
        self.label = QLabel(self.url) # URL 표시 라벨
        self.progress_bar = QProgressBar() # 다운로드 진행률 표시줄
        self.subtitle_label = QLabel("Subtitles: 준비 중") # 자막 상태 표시 라벨 (초기 상태 "준비 중"으로 변경)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.subtitle_label)
        self.setLayout(layout)

    def setup_thumbnail(self):
        """비디오 썸네일을 다운로드하고 캐시에 저장합니다."""
        video_id = self.extract_video_id(self.url) # URL에서 비디오 ID 추출
        if not video_id:
            return # 비디오 ID 없으면 썸네일 설정 중단

        if self.thumbnail_cache.get(video_id):
            return # 캐시에 썸네일이 있으면 다운로드 생략

        try:
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" # 고화질 썸네일 URL
            response = requests.get(thumbnail_url, timeout=10) # 10초 타임아웃 설정
            response.raise_for_status() # HTTP 에러 발생 시 예외 처리

            pixmap = QPixmap()
            pixmap.loadFromData(response.content) # 다운로드한 이미지 데이터로 QPixmap 생성
            pixmap = pixmap.scaled(
                320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation # 썸네일 크기 조정 및 스무딩
            )
            self.thumbnail_cache.set(video_id, pixmap) # 썸네일을 캐시에 저장
        except requests.exceptions.RequestException as e: # requests 관련 예외 처리 (네트워크 에러, 타임아웃 등)
            print(f"Error loading thumbnail for {self.url}: {e}")
        except Exception as e: # 기타 예외 처리
            print(f"Unexpected error loading thumbnail for {self.url}: {e}")


    def extract_video_id(self, url):
        """YouTube URL에서 비디오 ID를 추출합니다."""
        parsed_url = urlparse(url)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            if parsed_url.path == "/watch":
                return parse_qs(parsed_url.query).get("v", [None])[0]
            elif parsed_url.path.startswith("/shorts/"):
                return parsed_url.path.split("/shorts/")[1].split("/")[0]
        elif parsed_url.hostname == "youtu.be":
            return parsed_url.path[1:]
        return None # 비디오 ID 추출 실패 시 None 반환

    def enterEvent(self, event):
        """마우스 커서가 위젯 영역에 진입했을 때 이벤트 핸들러. 썸네일 미리보기 타이머 시작."""
        self.preview_timer.start(100)  # 100ms 후 썸네일 표시 (delay)

    def leaveEvent(self, event):
        """마우스 커서가 위젯 영역을 벗어났을 때 이벤트 핸들러. 썸네일 미리보기 타이머 중지 및 썸네일 숨김."""
        self.preview_timer.stop() # 타이머 중지
        self.thumbnail_label.hide() # 썸네일 라벨 숨김

    def mouseMoveEvent(self, event):
        """마우스 커서가 위젯 영역 내에서 움직일 때 이벤트 핸들러. 썸네일 위치 업데이트."""
        if self.thumbnail_label.isVisible(): # 썸네일이 표시 중일 때만 위치 업데이트
            self.update_thumbnail_position()

    def update_thumbnail_position(self):
        """썸네일 라벨의 위치를 마우스 커서 위치에 상대적으로 조정합니다."""
        cursor_pos = QCursor.pos() # 현재 마우스 커서 위치
        self.thumbnail_label.move(cursor_pos.x() + 10, cursor_pos.y() + 10) # 썸네일 위치 조정 (커서 오른쪽 아래 10px 옵셋)

    def show_thumbnail(self):
        """썸네일을 현재 마우스 커서 위치에 표시합니다."""
        video_id = self.extract_video_id(self.url) # 비디오 ID 추출
        if not video_id:
            return # 비디오 ID 없으면 썸네일 표시 중단

        thumbnail = self.thumbnail_cache.get(video_id) # 캐시에서 썸네일 가져오기
        if not thumbnail:
            return # 캐시에 썸네일 없으면 표시 중단

        self.thumbnail_label.setPixmap(thumbnail) # 썸네일 라벨에 이미지 설정
        self.thumbnail_label.adjustSize() # 라벨 크기를 이미지 크기에 맞게 조정
        self.update_thumbnail_position() # 썸네일 위치 업데이트
        self.thumbnail_label.show() # 썸네일 라벨 표시


    def update_progress(self, percent):
        """다운로드 진행률 표시줄을 업데이트합니다."""
        self.progress_bar.setValue(int(percent)) # 진행률 값 설정 (int 형변환)

    def update_subtitle_status(self, status):
        """자막 다운로드 상태 레이블을 업데이트합니다."""
        self.subtitle_label.setText(f"자막: {status}") # 자막 상태 텍스트 설정

    def __del__(self):
        """DownloadItemWidget 소멸자. 썸네일 라벨 객체를 명시적으로 삭제합니다."""
        self.thumbnail_label.deleteLater() # 썸네일 라벨 삭제 (메모리 누수 방지)