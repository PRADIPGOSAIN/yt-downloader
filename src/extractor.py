import yt_dlp
import logging
from urllib.parse import urlparse

def is_valid_youtube_url(url):
    """Validate YouTube URL."""
    try:
        parsed_url = urlparse(url)
        return any(host in parsed_url.netloc for host in ['youtube.com', 'youtu.be'])
    except Exception as e:
        logging.error(f"URL validation error: {e}")
        return False

def extract_video_data_from_url(url):
    """Extract video metadata safely."""
    logging.info(f"Extracting metadata for URL: {url}")
    
    # Validate URL first
    if not is_valid_youtube_url(url):
        return {"error": "Invalid YouTube URL"}

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(url, download=False)

            if not video_info:
                return {"error": "Could not extract video information"}

            # Advanced format filtering
            valid_formats = []
            for fmt in video_info.get('formats', []):
                if fmt.get('height') and fmt.get('ext'):
                    resolution = fmt.get('height')
                    valid_formats.append({
                        'format_id': fmt['format_id'],
                        'ext': fmt['ext'],
                        'resolution': f"{resolution}p" if resolution else 'Unknown',
                        'filesize': fmt.get('filesize', 'Unknown'),
                        'format_note': fmt.get('format_note', 'Unknown')
                    })

            return {
                "title": video_info.get('title', 'Unknown Title'),
                "thumbnail": video_info.get('thumbnail', ''),
                "formats": sorted(valid_formats, key=lambda x: x.get('resolution', '0p'), reverse=True)
            }

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Download error: {e}")
        return {"error": f"Download error: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"error": f"An unexpected error occurred: {e}"}
