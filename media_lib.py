from __future__ import annotations

import os

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from config import ALLOWED_EXTENSIONS, MEDIA_ROOT


@dataclass(frozen=True)
class MediaItem:
    scope: str            # "common" или "tv"
    tv_id: str | None     # например "1" (только для scope="tv")
    filename: str         # имя файла с расширением


def _is_allowed_video(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS


def list_common_items() -> list[MediaItem]:
    common_dir = MEDIA_ROOT / "common"
    if not common_dir.exists():
        return []

    files = [p for p in common_dir.iterdir() if _is_allowed_video(p)]
    files.sort(key=lambda p: p.name.lower())
    return [MediaItem(scope="common", tv_id=None, filename=p.name) for p in files]


def list_tv_items(tv_id: str) -> list[MediaItem]:
    tv_dir = MEDIA_ROOT / f"tv_{tv_id}"
    if not tv_dir.exists():
        return []

    files = [p for p in tv_dir.iterdir() if _is_allowed_video(p)]
    files.sort(key=lambda p: p.name.lower())
    return [MediaItem(scope="tv", tv_id=tv_id, filename=p.name) for p in files]


def build_m3u(urls: Iterable[str]) -> str:
    lines = ["#EXTM3U"]
    lines.extend(urls)
    return "\n".join(lines) + "\n"


def safe_resolve_media_path(scope: str, tv_id: str | None, filename: str) -> Path:
    """
    Защищает от попыток вида ../../something (path traversal).
    Разрешаем только файлы внутри MEDIA_ROOT/common или MEDIA_ROOT/tv_<id>.
    """
    if scope not in {"common", "tv"}:
        raise ValueError("Invalid scope")

    if scope == "common":
        base_dir = MEDIA_ROOT / "common"
    else:
        if not tv_id:
            raise ValueError("tv_id is required for scope=tv")
        base_dir = MEDIA_ROOT / f"tv_{tv_id}"

    base_dir = base_dir.resolve()
    candidate = (base_dir / filename).resolve()

    if str(candidate).startswith(str(base_dir) + os.sep) or candidate == base_dir:
        return candidate

    raise PermissionError("Invalid file path")
