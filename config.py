from pathlib import Path

# =========================================================
# MEDIA
# =========================================================

# Root directory for all media content

MEDIA_ROOT: Path = (
    Path(__file__).resolve().parent / "tv_content"
)

# System folder available by default

COMMON_FOLDER = "common"

# =========================================================
# DATA
# =========================================================

# Directory for service data

DATA_DIR: Path = (
    Path(__file__).resolve().parent / "data"
)

# Auto create data directory

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# File with folders metadata

FOLDERS_META_FILE: Path = (
    DATA_DIR / "folders.json"
)

# File with admin credentials

CREDENTIALS_FILE: Path = (
    DATA_DIR / "credentials.json"
)

# =========================================================
# SERVER
# =========================================================

HOST: str = "0.0.0.0"

PORT: int = 8060

# =========================================================
# MEDIA FORMATS
# =========================================================

# Video formats

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".m4v"
}

# Image formats

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

# All supported formats

ALLOWED_EXTENSIONS = (
    VIDEO_EXTENSIONS |
    IMAGE_EXTENSIONS
)

# =========================================================
# SECURITY
# =========================================================

# Session secret key

SECRET_KEY = "localcast_secret_key"

# Session lifetime (24 hours)

SESSION_MAX_AGE = 86400