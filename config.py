import socket
from pathlib import Path

def get_local_ip():
    """Автоматически определяет локальный IP-адрес компьютера в сети"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Используем публичный адрес для инициализации интерфейса (соединение не устанавливается)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

# Корневая папка с контентом
MEDIA_ROOT: Path = Path(__file__).resolve().parent / "tv_content"

# Параметры запуска сервера
HOST: str = "0.0.0.0"
PORT: int = 8000

# Разрешённые расширения файлов
ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".m4v",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

# Автоматическая генерация базового URL на основе текущего IP
PUBLIC_BASE_URL: str = f"http://{get_local_ip()}:{PORT}"