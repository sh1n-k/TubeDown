# Tube Downloader

[한국어 버전](./README.ko.md)

A desktop application that automatically downloads YouTube videos from copied URLs.

## Features

- Automatic download when YouTube URL is copied to clipboard
- Support for video quality selection (FHD, Best, Worst, etc.)
- Video thumbnail preview on hover
- Multi-language subtitle download support (English/Korean)
- Concurrent download management
- Download progress tracking
- Customizable download path

## Requirements

- Python 3.7+
- FFmpeg (for post-processing)
- Required Python packages:
  ```
  PyQt5>=5.15.0
  yt-dlp>=2023.3.4
  requests>=2.25.1
  ```

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/youtube-downloader.git
   cd youtube-downloader
   ```

2. Install required packages
   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg
    - Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
    - macOS: `brew install ffmpeg`
    - Linux: `sudo apt-get install ffmpeg`

## Usage

1. Run the application
   ```bash
   python -m youtube_downloader
   ```

2. Copy any YouTube URL to your clipboard
    - The application will automatically detect and start downloading
    - Progress will be shown in the main window

3. Configure settings (optional)
    - Click the "Settings" button
    - Adjust download path, quality, and other options

## License

MIT License

## Notice

This is a personal project created for learning and personal use. Feel free to use, modify, or share the code however you like. No restrictions or attribution required.


---

# YouTube 다운로더

[English version](./)

YouTube URL을 복사하면 자동으로 동영상을 다운로드하는 데스크톱 애플리케이션입니다.

## 주요 기능

- 클립보드에 복사된 YouTube URL 자동 감지 및 다운로드
- 영상 품질 선택 지원 (FHD, 최고화질, 최저화질 등)
- 마우스 오버 시 영상 썸네일 미리보기
- 다국어 자막 다운로드 지원 (영어/한국어)
- 동시 다운로드 관리
- 다운로드 진행 상황 추적
- 다운로드 경로 설정

## 필요 사항

- Python 3.7 이상
- FFmpeg (후처리용)
- 필수 Python 패키지:
  ```
  PyQt5>=5.15.0
  yt-dlp>=2023.3.4
  requests>=2.25.1
  ```

## 설치 방법

1. 저장소 복제
   ```bash
   git clone https://github.com/yourusername/youtube-downloader.git
   cd youtube-downloader
   ```

2. 필수 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```

3. FFmpeg 설치
    - Windows: [FFmpeg 웹사이트](https://ffmpeg.org/download.html)에서 다운로드
    - macOS: `brew install ffmpeg`
    - Linux: `sudo apt-get install ffmpeg`

## 사용 방법

1. 애플리케이션 실행
   ```bash
   python -m youtube_downloader
   ```

2. YouTube URL을 클립보드에 복사
    - 자동으로 감지하여 다운로드를 시작합니다
    - 메인 창에서 진행 상황을 확인할 수 있습니다

3. 설정 구성 (선택사항)
    - "Settings" 버튼 클릭
    - 다운로드 경로, 품질 등 옵션 조정

## 라이선스

MIT License


## 안내

이 프로젝트는 학습과 개인 사용을 위해 만들어졌습니다. 코드를 자유롭게 사용, 수정 및 공유하실 수 있습니다. 별도의 제한이나 출처 표시가 필요하지 않습니다.