from __future__ import annotations

import json
import os
import re

from dataclasses import dataclass
from pathlib import Path

from config import (
    ALLOWED_EXTENSIONS,
    COMMON_FOLDER,
    FOLDERS_META_FILE,
    MEDIA_ROOT,
    CREDENTIALS_FILE
)

# =========================================================
# MODELS
# =========================================================

@dataclass(frozen=True)
class MediaItem:

    folder_id: str

    filename: str


# =========================================================
# VALIDATION
# =========================================================

def is_valid_folder_name(name: str) -> bool:

    return bool(
        re.fullmatch(r"[a-zA-Z0-9_-]+", name)
    )


# =========================================================
# FOLDERS META
# =========================================================

def load_folders_meta() -> dict[str, str]:

    if not FOLDERS_META_FILE.exists():

        return {
            COMMON_FOLDER: "Common"
        }

    with open(
        FOLDERS_META_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_folders_meta(
    data: dict[str, str]
):

    MEDIA_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        FOLDERS_META_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# INITIALIZATION
# =========================================================

def ensure_system_folders():

    MEDIA_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    common_dir = MEDIA_ROOT / COMMON_FOLDER

    common_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    meta = load_folders_meta()

    if COMMON_FOLDER not in meta:

        meta[COMMON_FOLDER] = "Common"

        save_folders_meta(meta)


# =========================================================
# FOLDER MANAGEMENT
# =========================================================

def create_folder(
    folder_id: str,
    display_name: str
):

    if not is_valid_folder_name(folder_id):

        raise ValueError(
            "Invalid folder name"
        )

    path = MEDIA_ROOT / folder_id

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    meta = load_folders_meta()

    meta[folder_id] = display_name

    save_folders_meta(meta)


def delete_folder(folder_id: str):

    if folder_id == COMMON_FOLDER:

        raise ValueError(
            "Cannot delete common folder"
        )

    folder_path = MEDIA_ROOT / folder_id

    if folder_path.exists():

        for file in folder_path.iterdir():

            if file.is_file():
                file.unlink()

        folder_path.rmdir()

    meta = load_folders_meta()

    meta.pop(folder_id, None)

    save_folders_meta(meta)


# =========================================================
# MEDIA
# =========================================================

def list_folder_items(
    folder_id: str
) -> list[MediaItem]:

    folder_path = MEDIA_ROOT / folder_id

    if not folder_path.exists():
        return []

    files = []

    for file in folder_path.iterdir():

        if (
            file.is_file() and
            file.suffix.lower() in ALLOWED_EXTENSIONS
        ):

            files.append(file)

    files.sort(
        key=lambda x: x.name.lower()
    )

    return [
        MediaItem(
            folder_id=folder_id,
            filename=file.name
        )
        for file in files
    ]


# =========================================================
# PATH SAFETY
# =========================================================

def safe_resolve_media_path(
    folder_id: str,
    filename: str
) -> Path:

    base_dir = (
        MEDIA_ROOT / folder_id
    ).resolve()

    candidate = (
        base_dir / filename
    ).resolve()

    if str(candidate).startswith(
        str(base_dir) + os.sep
    ):

        return candidate

    raise PermissionError(
        "Invalid file path"
    )

# =========================================================
# CREDENTIALS
# =========================================================

def save_credentials(
    username: str,
    password: str
):

    data = {
        "username": username,
        "password": password
    }

    with open(
        CREDENTIALS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_credentials():

    if not CREDENTIALS_FILE.exists():

        default_data = {
            "username": "admin",
            "password": "admin"
        }

        with open(
            CREDENTIALS_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                default_data,
                f,
                ensure_ascii=False,
                indent=4
            )

        return default_data

    with open(
        CREDENTIALS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)