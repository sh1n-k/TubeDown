import shutil
import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QMessageBox

from config import Config
from ui.main_window import MainWindow


def check_ffmpeg():
    """
    시스템 PATH 환경 변수에서 FFmpeg 실행 파일 존재 여부를 확인합니다.

    Returns:
        bool: FFmpeg가 시스템 PATH 에서 발견되면 True, 아니면 False
    """
    return shutil.which("ffmpeg") is not None


def main():
    """
    어플리케이션 메인 함수.

    - QApplication 초기화
    - QSettings organization/application name 설정
    - FFmpeg 존재 여부 확인 및 에러 메시지 표시 (미설치 시)
    - Config, MainWindow 객체 생성 및 실행
    """
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("MyCompany") # QSettings organization name 설정
    QCoreApplication.setApplicationName("YouTubeDownloader") # QSettings application name 설정

    if not check_ffmpeg(): # FFmpeg 설치 여부 확인
        QMessageBox.critical(
            None,
            "Error",
            "FFmpeg is not installed or not found in system PATH. Please install FFmpeg to use this application.", # FFmpeg 미설치 시 에러 메시지 표시
        )
        sys.exit(1) # FFmpeg 미설치 시 어플리케이션 종료

    config = Config() # Config 객체 생성 (설정 관리)
    window = MainWindow(config, app.clipboard()) # MainWindow 객체 생성 (UI, 기능 통합)
    window.show() # 메인 윈도우 표시

    sys.exit(app.exec_()) # 어플리케이션 이벤트 루프 실행 (GUI 시작)


if __name__ == "__main__":
    main() # main 함수 호출 (어플리케이션 시작)