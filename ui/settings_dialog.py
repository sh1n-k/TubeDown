import os

from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QCheckBox,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
)


class SettingsDialog(QDialog):
    """
    어플리케이션 설정 다이얼로그 클래스입니다.

    동시 다운로드 수, 다운로드 경로, 비디오 품질, 자막 다운로드 설정을 변경하고 저장하는 기능을 제공합니다.
    """
    def __init__(self, config, parent=None):
        """
        SettingsDialog 초기화.

        Args:
            config (Config): 어플리케이션 설정 객체 (config.Config)
            parent (QWidget, optional): 부모 위젯. Defaults to None.
        """
        super().__init__(parent)
        self.config = config  # 설정 객체 저장
        self.setup_ui()  # UI 설정
        self.load_settings()  # 설정 로드 및 UI 반영

    def setup_ui(self):
        """다이얼로그 UI 레이아웃 및 위젯 설정."""
        self.setWindowTitle("설정")  # 다이얼로그 타이틀 설정
        self.layout = QFormLayout(self)  # 폼 레이아웃 생성 (Label - Field 쌍으로 구성)

        self._create_concurrent_downloads_spinbox()  # 동시 다운로드 수 스핀박스 생성 및 추가
        self._create_download_path_selector()  # 다운로드 경로 선택 UI (LineEdit + Browse Button) 생성 및 추가
        self._create_video_quality_combobox()  # 비디오 품질 콤보박스 생성 및 추가
        self._create_subtitles_checkbox()  # 자막 다운로드 체크박스 생성 및 추가
        self._create_buttons()  # 저장/취소 버튼 생성 및 추가

    def _create_concurrent_downloads_spinbox(self):
        """동시 다운로드 수 설정 스핀박스 생성 및 레이아웃에 추가."""
        self.concurrent_spin = QSpinBox()  # 스핀박스 생성
        self.concurrent_spin.setRange(1, 10)  # 다운로드 수 범위 설정 (1 ~ 10)
        self.layout.addRow("동시 다운로드:", self.concurrent_spin)  # 폼 레이아웃에 행 추가 (Label - Spinbox)

    def _create_download_path_selector(self):
        """다운로드 경로 설정 UI (LineEdit + Browse Button) 생성 및 레이아웃에 추가."""
        self.path_edit = QLineEdit()  # 경로 표시 LineEdit 생성
        self.browse_button = QPushButton("찾아보기...")  # "찾아보기" 버튼 생성
        self.browse_button.clicked.connect(self.browse_folder)  # 버튼 클릭 시 browse_folder 슬롯 연결

        path_layout = QHBoxLayout()  # QHBoxLayout 생성 (LineEdit + Button 수평 배치)
        path_layout.addWidget(self.path_edit)  # 레이아웃에 LineEdit 추가
        path_layout.addWidget(self.browse_button)  # 레이아웃에 Button 추가
        self.layout.addRow("다운로드 경로:", path_layout)  # 폼 레이아웃에 행 추가 (Label - Horizontal Layout)

    def _create_video_quality_combobox(self):
        """비디오 품질 설정 콤보박스 생성 및 레이아웃에 추가."""
        self.quality_combo = QComboBox()  # 콤보박스 생성
        self.quality_combo.addItems(  # 콤보박스 아이템 추가 (품질 옵션 목록)
            ["FHD", "best", "worst", "bestvideo+bestaudio", "bestvideo", "bestaudio"]
        )
        self.layout.addRow("비디오 품질:", self.quality_combo)  # 폼 레이아웃에 행 추가 (Label - ComboBox)

    def _create_subtitles_checkbox(self):
        """자막 다운로드 설정 체크박스 생성 및 레이아웃에 추가."""
        self.subtitles_checkbox = QCheckBox()  # 체크박스 생성
        self.layout.addRow("자막 다운로드:", self.subtitles_checkbox)  # 폼 레이아웃에 행 추가 (Label - CheckBox)

    def _create_buttons(self):
        """저장 및 취소 버튼 생성 및 레이아웃에 추가."""
        button_layout = QHBoxLayout()  # QHBoxLayout 생성 (버튼 수평 배치)

        self.save_button = QPushButton("저장")  # "저장" 버튼 생성
        self.cancel_button = QPushButton("취소")  # "취소" 버튼 생성
        self.save_button.clicked.connect(self.accept)  # "저장" 버튼 클릭 시 accept 슬롯 연결 (다이얼로그 종료 및 설정 저장)
        self.cancel_button.clicked.connect(self.reject)  # "취소" 버튼 클릭 시 reject 슬롯 연결 (다이얼로그 종료, 설정 저장 취소)

        button_layout.addWidget(self.save_button)  # 레이아웃에 "저장" 버튼 추가
        button_layout.addWidget(self.cancel_button)  # 레이아웃에 "취소" 버튼 추가
        self.layout.addRow(button_layout)  # 폼 레이아웃에 행 추가 (Horizontal Layout - Buttons)

    def load_settings(self):
        """Config 객체에서 설정을 불러와 UI 위젯에 반영합니다."""
        self.concurrent_spin.setValue(self.config.concurrent_downloads)  # 동시 다운로드 수 스핀박스에 값 설정
        self.path_edit.setText(self.config.download_path or "")  # 다운로드 경로 LineEdit에 값 설정
        index = self.quality_combo.findText(self.config.video_quality)  # 비디오 품질 콤보박스에서 현재 설정된 품질의 인덱스 찾기
        if index != -1:  # 찾았으면
            self.quality_combo.setCurrentIndex(index)  # 해당 인덱스로 콤보박스 선택 설정
        self.subtitles_checkbox.setChecked(self.config.download_subtitles)  # 자막 다운로드 체크박스에 값 설정

    def browse_folder(self):
        """폴더 찾아보기 다이얼로그를 열고, 선택된 폴더 경로를 다운로드 경로 LineEdit에 반영합니다."""
        folder = QFileDialog.getExistingDirectory(self, "다운로드 폴더 선택")  # 폴더 선택 다이얼로그 열기
        if folder:  # 폴더가 선택되었으면
            self.path_edit.setText(folder)  # 선택된 폴더 경로를 LineEdit에 설정

    def accept(self):
        """
        "저장" 버튼 클릭 시 호출되는 슬롯.
        입력 유효성 검사 후, 설정을 저장하고 다이얼로그를 닫습니다.
        """
        download_path = self.path_edit.text() # 다운로드 경로 텍스트 가져오기
        if not download_path or not os.path.isdir(download_path): # 다운로드 경로 유효성 검사 (비어있거나 디렉토리가 아니면 오류)
            QMessageBox.warning(
                self, "경로 오류", "유효한 다운로드 경로를 선택해주세요." # 경고 메시지 박스 표시
            )
            return  # 유효하지 않은 경로이면 설정 저장 취소하고 함수 종료

        self.config.save_settings(  # Config 객체를 통해 설정 저장
            concurrent_downloads=self.concurrent_spin.value(), # 동시 다운로드 수
            download_path=download_path, # 다운로드 경로
            video_quality=self.quality_combo.currentText(), # 비디오 품질
            download_subtitles=self.subtitles_checkbox.isChecked(), # 자막 다운로드 여부
        )
        super().accept()  # 다이얼로그 accept 처리 (다이얼로그 닫기)