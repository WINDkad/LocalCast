from __future__ import annotations

import os

from dataclasses import dataclass
from pathlib import Path

from config import ALLOWED_EXTENSIONS, MEDIA_ROOT


@dataclass(frozen=True)
class MediaItem:
    scope: str
    tv_id: str | None
    filename: str


def _is_allowed_media(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS


def list_common_items() -> list[MediaItem]:
    common_dir = MEDIA_ROOT / "common"

    if not common_dir.exists():
        return []

    files = [p for p in common_dir.iterdir() if _is_allowed_media(p)]

    files.sort(key=lambda p: p.name.lower())

    return [
        MediaItem(
            scope="common",
            tv_id=None,
            filename=p.name
        )
        for p in files
    ]

def safe_resolve_media_path(scope: str, tv_id: str | None, filename: str) -> Path:

    if scope not in {"common", "tv"}:
        raise ValueError("Invalid scope")

    if scope == "common":
        base_dir = MEDIA_ROOT / "common"
    else:
        if not tv_id:
            raise ValueError("tv_id is required")

        base_dir = MEDIA_ROOT / f"tv_{tv_id}"

    base_dir = base_dir.resolve()

    candidate = (base_dir / filename).resolve()

    if str(candidate).startswith(str(base_dir) + os.sep):
        return candidate

    raise PermissionError("Invalid file path")