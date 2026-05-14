from pathlib import Path

MEDIA_ROOT: Path = (
    Path(__file__).resolve().parent / "tv_content"
)

HOST: str = "0.0.0.0"

PORT: int = 8000


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".m4v"
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}


ALLOWED_EXTENSIONS = (
    VIDEO_EXTENSIONS |
    IMAGE_EXTENSIONS
)

# Admin credentials

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123123"

# Secret key for session cookies

SECRET_KEY = "localcast_secret_key"