from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse

from config import MEDIA_ROOT, PORT, PUBLIC_BASE_URL
from media_lib import (
    build_m3u,
    list_common_items,
    list_tv_items,
    safe_resolve_media_path,
)

app = FastAPI(title="LocalCast", version="1.0")


@app.get("/health", response_class=PlainTextResponse)
def health() -> str:
    return "OK"

@app.get("/media/common/{filename}")
def media_common(filename: str):
    return _serve_media_file(scope="common", tv_id=None, filename=filename)


@app.get("/media/tv/{tv_id}/{filename}")
def media_tv(tv_id: str, filename: str):
    return _serve_media_file(scope="tv", tv_id=tv_id, filename=filename)

@app.get("/playlist/common.m3u", response_class=PlainTextResponse)
def playlist_common(request: Request) -> PlainTextResponse:
    common = list_common_items()

    base_url = PUBLIC_BASE_URL.rstrip("/") if PUBLIC_BASE_URL else str(request.base_url).rstrip("/")
    urls = [f"{base_url}/media/common/{it.filename}" for it in common]

    body = build_m3u(urls)
    return PlainTextResponse(content=body, media_type="audio/x-mpegurl; charset=utf-8")

@app.get("/playlist/tv/{tv_id}.m3u", response_class=PlainTextResponse)
def playlist_tv_only(tv_id: str, request: Request) -> PlainTextResponse:
    personal = list_tv_items(tv_id)

    base_url = PUBLIC_BASE_URL.rstrip("/") if PUBLIC_BASE_URL else str(request.base_url).rstrip("/")
    urls = [f"{base_url}/media/tv/{tv_id}/{it.filename}" for it in personal]

    body = build_m3u(urls)
    return PlainTextResponse(content=body, media_type="audio/x-mpegurl; charset=utf-8")

def _serve_media_file(scope: str, tv_id: str | None, filename: str) -> FileResponse:
    try:
        path: Path = safe_resolve_media_path(scope=scope, tv_id=tv_id, filename=filename)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Forbidden")
    except ValueError:
        raise HTTPException(status_code=400, detail="Bad request")

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=str(path), filename=path.name)


if __name__ == "__main__":
    import uvicorn

    # Создаём папки, если их нет
    (MEDIA_ROOT / "common").mkdir(parents=True, exist_ok=True)

    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)
