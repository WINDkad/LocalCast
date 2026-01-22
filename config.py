from pathlib import Path

# Корневая папка с контентом (по умолчанию рядом с проектом)
MEDIA_ROOT: Path = Path(__file__).resolve().parent / "tv_content"

# Где поднимем сервер
HOST: str = "0.0.0.0"
PORT: int = 8000

# Разрешённые расширения видео (можно дополнять)
ALLOWED_EXTENSIONS: set[str] = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"
}

# Если хочешь жёстко задать базовый URL (обычно НЕ нужно):
# PUBLIC_BASE_URL = "http://192.168.0.10:8000"
PUBLIC_BASE_URL: str | None = None