import json
from pathlib import Path

BASE_DOMAIN = "http://172.16.35.149:8000"

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

BACKGROUND_FOLDER_PATH = BASE_DIR / "static/background"

VIDEO_FOLDER_PATH = BASE_DIR / "temp/videos"

TEMP_FOLDER_PATH = BASE_DIR / "temp"

CONF_FOLDER_PATH = BASE_DIR / "config"

UPLOAD_FOLDER_PATH = BASE_DIR / "temp"


# DATABASE
# ------------------------------------------------------------------------------

DB_IP = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "audio2face"
DB_USERNAME = "root"
DB_PASSWORD = "123456"


