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
    어플리케이션 메인 윈도우 클래스입니다.

    - 클립보드 감시 (YouTube URL 감지)
    - 다운로드 관리 (시작, 진행률 표시, 완료/에러 처리)
    - UI 업데이트
    - 설정 관리 (SettingsDialog 연동)
    """
    def __init__(self, config, clipboard):
        """
        MainWindow 초기화.

        Args:
            config (Config): 어플리케이션 설정 객체 (config.Config)
            clipboard (QClipboard): 시스템 클립보드 객체 (QApplication.clipboard())
        """
        super().__init__()
        self.config = config # 설정 객체 저장
        self.clipboard = clipboard # 클립보드 객체 저장

        self.downloaded_urls = set() # 다운로드 완료된 URL 목록 (중복 다운로드 방지)
        self.active_downloads = {} # 현재 활성 다운로드 worker 목록 (URL: Worker 객체)
        self.download_progress = {} # 다운로드 진행률 정보 (URL: 진행률%)
        self.clipboard_lock = Lock() # 클립보드 접근 lock (thread-safe)

        self._setup_window() # 윈도우 UI 설정
        self._setup_threadpool() # 스레드 풀 설정
        self._setup_clipboard_monitoring() # 클립보드 감시 설정

    def _setup_window(self):
        """메인 윈도우 UI 기본 설정 (타이틀, 크기, 레이아웃)."""
        self.setWindowTitle("YouTube Downloader") # 윈도우 타이틀 설정
        self.resize(600, 400) # 윈도우 초기 크기 설정

        self.central_widget = QWidget() # 센트럴 위젯 생성
        self.layout = QVBoxLayout() # 메인 레이아웃 (수직 박스 레이아웃)
        self.central_widget.setLayout(self.layout) # 센트럴 위젯에 레이아웃 설정
        self.setCentralWidget(self.central_widget) # 메인 윈도우에 센트럴 위젯 설정

        self._create_status_label() # 상태 표시 라벨 생성 및 추가
        self._create_download_list() # 다운로드 목록 리스트 위젯 생성 및 추가
        self._create_settings_button() # 설정 버튼 생성 및 추가

    def _setup_threadpool(self):
        """다운로드 작업 스레드 풀 설정."""
        self.threadpool = QThreadPool() # 스레드 풀 생성
        self.threadpool.setMaxThreadCount(self.config.concurrent_downloads) # 동시 다운로드 수 설정 적용

    def _setup_clipboard_monitoring(self):
        """클립보드 감시 기능 설정 (시그널-슬롯 연결, 타이머 설정)."""
        self.last_clipboard = self.clipboard.text() # 초기 클립보드 내용 저장
        self.clipboard.dataChanged.connect(self.on_clipboard_change) # 클립보드 변경 시 on_clipboard_change 슬롯 호출

        self.timer = QTimer() # 타이머 생성 (클립보드 폴링용)
        self.timer.timeout.connect(self.check_clipboard) # 타임아웃 시 check_clipboard 슬롯 호출
        self.timer.start(1000) # 1초마다 클립보드 체크 (dataChanged 시그널 보조)


    def _create_status_label(self):
        """상태 라벨 생성 및 레이아웃에 추가."""
        self.status_label = QLabel("클립보드에서 YouTube URL 감시 중...") # 상태 라벨 생성
        self.layout.addWidget(self.status_label) # 레이아웃에 상태 라벨 추가

    def _create_download_list(self):
        """다운로드 목록 리스트 위젯 생성 및 레이아웃에 추가."""
        self.list_widget = QListWidget() # 리스트 위젯 생성 (다운로드 목록 표시)
        self.layout.addWidget(self.list_widget) # 레이아웃에 리스트 위젯 추가

    def _create_settings_button(self):
        """설정 버튼 생성 및 레이아웃에 추가, 클릭 시 open_settings 슬롯 호출."""
        self.settings_button = QPushButton("설정") # 설정 버튼 생성
        self.settings_button.clicked.connect(self.open_settings) # 클릭 시 open_settings 슬롯 연결
        self.layout.addWidget(self.settings_button) # 레이아웃에 설정 버튼 추가

    def check_clipboard(self):
        """
        타이머 기반 클립보드 체크 함수. 클립보드 내용 변경 여부를 주기적으로 확인합니다.
        `clipboard.dataChanged` 시그널의 보조 역할로, 시그널 누락 방지 및 안정성 향상 목적입니다.
        """
        with self.clipboard_lock: # 클립보드 접근 Lock 획득 (thread-safe)
            current_text = self.clipboard.text() # 현재 클립보드 텍스트 가져오기
            if current_text != self.last_clipboard: # 클립보드 내용 변경 확인
                self.last_clipboard = current_text # 마지막 클립보드 내용 업데이트
                self.on_clipboard_change() # 클립보드 변경 처리 함수 호출

    def on_clipboard_change(self):
        """
        클립보드 내용 변경 시 호출되는 슬롯 함수. 클립보드 텍스트에서 YouTube URL을 감지하고,
        새로운 URL인 경우 다운로드를 시작합니다.
        """
        text = self.clipboard.text() # 현재 클립보드 텍스트 가져오기
        if YOUTUBE_REGEX.match(text): # YouTube URL 정규식 매칭 확인
            video_id = extract_video_id(text) # URL에서 비디오 ID 추출
            if video_id and video_id not in self.downloaded_urls: # 중복 다운로드 방지 (이미 다운로드한 URL인지 확인)
                self.start_download(text) # 다운로드 시작
                self.clipboard.clear() # 클립보드 내용 비우기 (URL 자동 다운로드 후 클립보드 정리)

    def start_download(self, url):
        """
        새로운 다운로드 작업을 시작합니다. DownloadWorker 스레드를 생성하고, 각종 시그널을 연결하며,
        UI에 다운로드 아이템을 추가합니다.

        Args:
            url (str): 다운로드할 YouTube URL
        """
        signals = WorkerSignals() # Worker 시그널 객체 생성
        signals.finished.connect(self.on_download_finished) # 다운로드 완료 시 on_download_finished 슬롯 연결
        signals.error.connect(self.on_download_error) # 다운로드 에러 시 on_download_error 슬롯 연결
        signals.progress.connect(self.on_download_progress) # 다운로드 진행률 변경 시 on_download_progress 슬롯 연결

        worker = DownloadWorker( # DownloadWorker 객체 생성 (다운로드 스레드)
            url=url,
            download_path=self.config.download_path, # 다운로드 경로 (설정에서 가져옴)
            quality=self.config.video_quality, # 비디오 품질 (설정에서 가져옴)
            signals=signals, # 시그널 객체 전달
            download_subtitles=self.config.download_subtitles, # 자막 다운로드 여부 (설정에서 가져옴)
        )
        self.active_downloads[url] = worker # 활성 다운로드 목록에 worker 추가 (URL: Worker)
        self.threadpool.start(worker) # 스레드 풀에 worker 스레드 시작 요청

        self._add_download_item(url) # UI에 다운로드 아이템 추가

    def _add_download_item(self, url):
        """
        UI 다운로드 목록에 새로운 다운로드 아이템 (DownloadItemWidget) 을 추가합니다.

        Args:
            url (str): 다운로드할 YouTube URL
        """
        item = QListWidgetItem() # QListWidgetItem 생성 (리스트 뷰 아이템)
        widget = DownloadItemWidget(url) # DownloadItemWidget 생성 (커스텀 위젯)
        item.setSizeHint(widget.sizeHint()) # 아이템 크기 힌트 설정 (위젯 크기에 맞춤)
        self.list_widget.addItem(item) # 리스트 위젯에 아이템 추가
        self.list_widget.setItemWidget(item, widget) # 아이템에 커스텀 위젯 설정 (아이템 - 위젯 연결)


    def on_download_finished(self, url):
        """
        다운로드 완료 시 호출되는 슬롯 함수. UI 업데이트 및 완료 처리.

        Args:
            url (str): 완료된 다운로드의 YouTube URL
        """
        self.downloaded_urls.add(url) # 다운로드 완료 URL 목록에 추가 (중복 다운로드 방지)
        self._update_download_widget(url, status="complete") # UI 다운로드 아이템 위젯 업데이트 (상태: 완료)
        self._cleanup_download(url) # 다운로드 정리 (활성 다운로드 목록, 진행률 정보 제거)

    def on_download_error(self, message):
        """
        다운로드 에러 발생 시 호출되는 슬롯 함수. 에러 메시지 표시 및 UI 업데이트.

        Args:
            message (str): 에러 메시지
        """
        QMessageBox.critical(self, "다운로드 오류", message) # 에러 메시지 박스 표시
        url = message.split(":")[0].split(' ')[-1] # 에러 메시지에서 URL 추출 (메시지 포맷에 따라 조정 필요)
        self._update_download_widget(url, status="error") # UI 다운로드 아이템 위젯 업데이트 (상태: 에러)
        self._cleanup_download(url) # 다운로드 정리

    def _cleanup_download(self, url):
        """
        다운로드 완료 또는 에러 발생 후 뒷정리 작업 (활성 다운로드 목록, 진행률 정보 제거).

        Args:
            url (str): 다운로드 URL
        """
        self.active_downloads.pop(url, None) # 활성 다운로드 목록에서 제거 (worker 객체 제거)
        self.download_progress.pop(url, None) # 진행률 정보 딕셔너리에서 제거
        self.update_status_label() # 상태 라벨 업데이트 (활성 다운로드 목록 갱신 반영)

    def _update_download_widget(self, url, status):
        """
        UI 다운로드 아이템 위젯의 상태를 업데이트합니다 (진행률, 텍스트 변경 등).

        Args:
            url (str): 다운로드 URL
            status (str): 업데이트할 상태 ("complete", "error")
        """
        for index in range(self.list_widget.count()): # 다운로드 목록 아이템 순회
            item = self.list_widget.item(index) # 아이템 가져오기
            widget = self.list_widget.itemWidget(item) # 아이템에 연결된 위젯 (DownloadItemWidget) 가져오기
            if widget.label.text() == url: # 위젯의 URL 라벨 텍스트가 업데이트 대상 URL과 일치하는지 확인
                if status == "complete": # 다운로드 완료 상태인 경우
                    widget.label.setText(f"다운로드 완료: {url}") # 라벨 텍스트 변경 (다운로드 완료 표시)
                    widget.update_progress(100.0) # 진행률 100%로 업데이트
                    if self.config.download_subtitles: # 자막 다운로드 설정 활성화 시
                        widget.update_subtitle_status("다운로드 완료") # 자막 상태 "다운로드 완료" 로 업데이트
                elif status == "error": # 다운로드 에러 상태인 경우
                    widget.label.setText(f"다운로드 실패: {url}") # 라벨 텍스트 변경 (다운로드 실패 표시)
                    widget.update_progress(0.0) # 진행률 0%로 초기화 (or 에러 상태 표시)
                    if self.config.download_subtitles: # 자막 다운로드 설정 활성화 시
                        widget.update_subtitle_status("다운로드 실패") # 자막 상태 "다운로드 실패" 로 업데이트
                break # URL 찾았으면 루프 종료

    def on_download_progress(self, url, percent):
        """
        다운로드 진행률 변경 시 호출되는 슬롯 함수. UI 진행률 표시줄 업데이트.

        Args:
            url (str): 다운로드 URL
            percent (float): 다운로드 진행률 (0.0 ~ 100.0)
        """
        self.download_progress[url] = percent # 진행률 정보 업데이트 (딕셔너리에 저장)
        for index in range(self.list_widget.count()): # 다운로드 목록 아이템 순회
            item = self.list_widget.item(index) # 아이템 가져오기
            widget = self.list_widget.itemWidget(item) # 아이템에 연결된 위젯 가져오기
            if widget.label.text() == url: # 위젯의 URL 라벨 텍스트가 업데이트 대상 URL과 일치하는지 확인
                widget.update_progress(percent) # 위젯의 진행률 표시줄 업데이트
                break # URL 찾았으면 루프 종료
        self.update_status_label() # 상태 라벨 업데이트 (전체 진행률 요약 표시)

    def update_status_label(self):
        """
        상태 라벨 텍스트를 업데이트합니다. 현재 활성 다운로드 목록 및 진행률을 요약하여 표시합니다.
        활성 다운로드가 없으면 기본 상태 메시지 ("클립보드에서 YouTube URL 감시 중...") 를 표시합니다.
        """
        if not self.active_downloads: # 활성 다운로드 목록이 비어있는 경우
            self.status_label.setText("클립보드에서 YouTube URL 감시 중...") # 기본 상태 메시지 설정
            return # 더 이상 진행 X

        status_text = [] # 상태 텍스트 리스트 초기화
        for url, progress in self.download_progress.items(): # 진행률 정보 딕셔너리 순회
            if progress < 100: # 진행률이 100% 미만인 다운로드만 표시 (진행 중인 다운로드)
                video_title_snippet = url.split('/')[-1] # URL에서 비디오 제목 일부 추출 (간략하게 표시)
                status_text.append(f"{video_title_snippet}: {progress:.1f}%") # 상태 텍스트 생성 및 리스트에 추가

        if status_text: # 상태 텍스트 리스트가 비어있지 않은 경우 (진행 중인 다운로드 O)
            self.status_label.setText(" | ".join(status_text)) # 상태 텍스트들을 " | " 로 연결하여 상태 라벨에 설정

    def open_settings(self):
        """설정 다이얼로그 (SettingsDialog) 를 열고, 설정 변경 사항을 적용합니다."""
        dialog = SettingsDialog(self.config, self) # SettingsDialog 객체 생성 (설정, 부모 윈도우 전달)
        if dialog.exec_(): # 다이얼로그 실행 (Modal), OK 버튼 클릭 시 True 반환
            self.threadpool.setMaxThreadCount(self.config.concurrent_downloads) # 동시 다운로드 수 설정 변경 적용 (스레드 풀 업데이트)
            if not self.config.download_path or not os.path.isdir( # 다운로드 경로 유효성 재확인
                    self.config.download_path
            ):
                QMessageBox.warning( # 다운로드 경로 오류 메시지 박스 표시
                    self,
                    "다운로드 경로 오류",
                    "유효한 다운로드 경로를 설정해주세요.",
                )

    def closeEvent(self, event):
        """
        QMainWindow closeEvent override. 윈도우 닫기 이벤트 처리.
        어플리케이션 종료 전에 사용자에게 종료 확인 메시지 박스를 표시합니다.
        """
        reply = QMessageBox.question( # 종료 확인 메시지 박스 표시 (Yes/No 선택)
            self,
            "종료 확인",
            "정말로 종료하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No, # 기본 선택 버튼: No
        )
        if reply == QMessageBox.Yes: # Yes 버튼 클릭 시
            # 다운로드 중단 로직 (선택 사항, 필요시 활성화)
            # for worker in self.active_downloads.values():
            #     worker.stop() # 활성 다운로드 worker 들에게 stop() 호출 (Graceful shutdown 시도)
            self.threadpool.waitForDone() # 스레드 풀의 모든 작업 완료 대기 (Graceful shutdown)
            event.accept() # 윈도우 닫기 승인 (어플리케이션 종료)
        else: # No 버튼 클릭 시 or 메시지 박스 닫기 시
            event.ignore() # 윈도우 닫기 무시 (어플리케이션 종료 취소)