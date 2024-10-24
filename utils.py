import re
from urllib.parse import urlparse, parse_qs

YOUTUBE_REGEX = re.compile(
    r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)[\w-]{11}'
)


def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith(('/embed/', '/v/')):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/shorts/'):
            return parsed_url.path.split('/shorts/')[1].split('/')[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None
