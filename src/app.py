import os
import logging
import re
import subprocess
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from extractor import extract_video_data_from_url
from config import Config
import yt_dlp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename=Config.LOG_FILE
)

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config.from_object(Config)

def sanitize_filename(filename):
    """Replace special characters in filenames to avoid issues."""
    filename = secure_filename(filename)
    return re.sub(r'[^\w\s.-]', '_', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('video_url')
    
    try:
        video_data = extract_video_data_from_url(video_url)
        
        if 'error' in video_data:
            return render_template('error.html', error=video_data['error'])
        
        return render_template(
            'download.html', 
            title=video_data['title'], 
            thumbnail=video_data['thumbnail'],
            formats=video_data['formats'],
            video_url=video_url
        )
    
    except Exception as e:
        logging.error(f"Download page error: {e}")
        return render_template('error.html', error=str(e))

@app.route('/download_format', methods=['POST'])
def download_format():
    video_url = request.form.get('video_url')
    
    if not video_url:
        return render_template('error.html', error="No video URL provided.")

    try:
        # Set yt_dlp options for downloading video and audio separately
        video_opts = {
            'format': 'bestvideo',
            'outtmpl': os.path.join(Config.DOWNLOAD_FOLDER, '%(title)s_video.%(ext)s'),
            'quiet': False
        }

        audio_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join(Config.DOWNLOAD_FOLDER, '%(title)s_audio.%(ext)s'),
            'quiet': False
        }

        # Download video
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=True)
            video_file = os.path.abspath(ydl.prepare_filename(video_info))

        # Download audio
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            audio_info = ydl.extract_info(video_url, download=True)
            audio_file = os.path.abspath(ydl.prepare_filename(audio_info))

        # Define the output file
        output_file = os.path.abspath(os.path.join(Config.DOWNLOAD_FOLDER, "merged_output.mp4"))

        # Use FFmpeg to merge video and audio
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_file,  # Input video file
            '-i', audio_file,  # Input audio file
            '-c:v', 'copy',    # Copy video stream without re-encoding
            '-c:a', 'aac',     # Encode audio in AAC format
            '-b:a', '192k',    # Set audio bitrate
            '-y',              # Overwrite output file if exists
            output_file
        ]

        logging.info(f"FFmpeg command: {' '.join(ffmpeg_command)}")

        subprocess.run(ffmpeg_command, check=True)

        # Clean up the separate video and audio files
        os.remove(video_file)
        os.remove(audio_file)

        if not os.path.exists(output_file):
            return render_template('error.html', error="Failed to merge video and audio.")

        logging.info(f"Downloaded and merged: {output_file}")
        return send_file(
            output_file,
            as_attachment=True,
            download_name=os.path.basename(output_file)
        )

    except Exception as e:
        logging.error(f"Download error: {e}")
        return render_template('error.html', error=str(e))

@app.route('/thank_you')
def thank_you():
    file_name = request.args.get('file_name', '')
    return render_template('thank_you.html', file_name=file_name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)
