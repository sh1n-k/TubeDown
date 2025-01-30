# YouTube 다운로더 (Tube Downloader)

[English Version](./README.md)

클립보드에 YouTube URL을 복사하는 즉시 자동으로 다운로드를 시작하는 데스크톱 애플리케이션입니다. PyQt5를 기반으로 제작되었으며, 사용 편의성과 다양한 기능을 제공합니다.

## 주요 기능

- **클립보드 자동 감지**: YouTube URL을 클립보드에 복사하는 즉시 다운로드 시작
- **다양한 품질 옵션**: FHD (1080p)부터 최저 화질까지, 사용자가 원하는 비디오 품질 선택 가능
- **썸네일 미리보기**: 다운로드 목록에서 각 영상 썸네일을 마우스 오버 시 미리보기 제공
- **자막 다운로드**: 영어/한국어 자막은 물론, 지원되는 모든 언어의 자막 다운로드 지원
- **동시 다운로드**: 여러 영상을 동시에 다운로드하여 시간 절약 (설정에서 동시 다운로드 개수 조절 가능)
- **다운로드 진행 상황**: 각 영상별 다운로드 진행률을 실시간으로 확인 가능
- **다운로드 경로 설정**: 다운로드된 영상이 저장될 폴더를 사용자가 직접 지정 가능

## 필요 사항

- **Python 3.7 이상**: 최신 기능과 성능 향상을 위해 Python 3.7 이상의 버전이 필요합니다.
- **FFmpeg**: 비디오와 오디오를 병합하고, 다양한 코덱을 지원하기 위해 FFmpeg가 필요합니다. 시스템에 FFmpeg가 설치되어 있어야 합니다.
- **필수 Python 패키지**: 아래 패키지들이 필요하며, `pip`를 사용하여 설치할 수 있습니다.
  ```
PyQt5>=5.15.0       # GUI 프레임워크
yt-dlp>=2023.3.4    # YouTube 다운로드 엔진
requests>=2.25.1    # HTTP 요청 라이브러리 (썸네일 다운로드 등에 사용)
  ```

## 설치 방법

1. **저장소 복제 (Clone)**
   ```bash
   git clone https://github.com/yourusername/youtube-downloader.git  # (본인 repository 주소로 변경)
   cd youtube-downloader
   ```

2. **필수 패키지 설치 (`requirements.txt` 사용)**
   ```bash
   pip install -r requirements.txt
   ```
   프로젝트 폴더 내 `requirements.txt` 파일에 필요한 패키지 목록이 정의되어 있습니다.

3. **FFmpeg 설치**
   - **Windows**: [FFmpeg 공식 웹사이트](https://ffmpeg.org/download.html)에서 pre-built binaries를 다운로드하여 압축을 풀고, `bin` 폴더를 시스템 환경 변수 `PATH`에 추가합니다. 또는 [Chocolatey](https://chocolatey.org/)나 [Scoop](https://scoop.sh/) 같은 패키지 관리자를 사용하여 더 간편하게 설치할 수 있습니다.
   - **macOS**: Homebrew를 사용하는 경우 터미널에 다음 명령어를 입력하여 설치합니다.
     ```bash
     brew install ffmpeg
     ```
   - **Linux**: 대부분의 Linux 배포판에서 패키지 관리자를 통해 FFmpeg를 설치할 수 있습니다. (예: Ubuntu/Debian: `sudo apt-get install ffmpeg`, Fedora/CentOS: `sudo yum install ffmpeg` 또는 `sudo dnf install ffmpeg`)

## 사용 방법

1. **애플리케이션 실행**
   ```bash
   python -m youtube_downloader
   ```
   또는 프로젝트 폴더에서 `main.py` 파일을 직접 실행합니다.

2. **YouTube URL을 클립보드에 복사**
   - 다운로드하고 싶은 YouTube 영상의 URL을 복사하면, 프로그램이 자동으로 감지하여 다운로드 목록에 추가하고 다운로드를 시작합니다.
   - 다운로드 진행 상황은 메인 창의 목록에서 확인할 수 있습니다.

3. **설정 변경 (선택 사항)**
   - 프로그램 창 하단의 "설정" 버튼을 클릭하여 설정 다이얼로그를 엽니다.
   - 다운로드 경로, 비디오 품질, 동시 다운로드 개수, 자막 다운로드 여부 등을 사용자에 맞게 설정할 수 있습니다.

## 라이선스

MIT License

## 안내

본 프로그램은 개인 학습 및 편의를 위해 제작된 프로젝트입니다. 코드 사용, 수정, 공유에 제한이 없으며, 자유롭게 활용하시기 바랍니다. 별도의 출처 표기 의무 또한 없습니다.

---
