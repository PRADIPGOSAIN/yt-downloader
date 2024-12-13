import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    DEBUG = os.getenv('FLASK_DEBUG', True)
    
    # Download settings
    DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'downloads')
    MAX_DOWNLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2GB limit
    ALLOWED_VIDEO_HOSTS = ['youtube.com', 'youtu.be', 'www.youtube.com']
    
    # Logging configuration
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.log')
    
    # Ensure download folder exists
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
