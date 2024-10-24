import os

from PyQt5.QtWidgets import (QDialog, QFormLayout, QSpinBox, QLineEdit,
                             QPushButton, QVBoxLayout, QComboBox, QCheckBox,
                             QHBoxLayout, QFileDialog, QMessageBox)


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("Settings")
        self.layout = QFormLayout(self)

        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 10)
        self.layout.addRow("Concurrent Downloads:", self.concurrent_spin)

        self.path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        path_layout = QVBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        self.layout.addRow("Download Path:", path_layout)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['FHD', 'best', 'worst', 'bestvideo+bestaudio', 'bestvideo', 'bestaudio'])
        self.layout.addRow("Video Quality:", self.quality_combo)

        self.subtitles_checkbox = QCheckBox()
        self.layout.addRow("Download Subtitles:", self.subtitles_checkbox)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addRow(button_layout)

    def load_settings(self):
        self.concurrent_spin.setValue(self.config.concurrent_downloads)
        self.path_edit.setText(self.config.download_path or '')
        index = self.quality_combo.findText(self.config.video_quality)
        if index != -1:
            self.quality_combo.setCurrentIndex(index)
        self.subtitles_checkbox.setChecked(self.config.download_subtitles)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.path_edit.setText(folder)

    def accept(self):
        if not self.path_edit.text() or not os.path.isdir(self.path_edit.text()):
            QMessageBox.warning(self, "Invalid Path", "Please select a valid download path.")
            return
        self.config.save_settings(
            self.concurrent_spin.value(),
            self.path_edit.text(),
            self.quality_combo.currentText(),
            self.subtitles_checkbox.isChecked()
        )
        super().accept()
