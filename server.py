from pathlib import Path
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request,
    Form
)
from fastapi.responses import (
    RedirectResponse,
    JSONResponse,
    FileResponse
)

from starlette.middleware.sessions import SessionMiddleware

from fastapi.templating import Jinja2Templates

from config import (
    MEDIA_ROOT,
    HOST,
    PORT,
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    SECRET_KEY
)

from media_lib import (
    list_common_items,
    safe_resolve_media_path
)

app = FastAPI(
    title="LocalCast",
    version="2.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)

# ========================= STATIC + TEMPLATES =========================

templates = Jinja2Templates(
    directory="templates"
)

# ========================= DIRECTORIES =========================

COMMON_DIR = MEDIA_ROOT / "common"

COMMON_DIR.mkdir(
    parents=True,
    exist_ok=True
)

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

def is_authenticated(request: Request) -> bool:
    return request.session.get("admin") is True

# ========================= LOGIN =========================

@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None
        }
    )


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    if (
        username == ADMIN_USERNAME and
        password == ADMIN_PASSWORD
    ):

        request.session["admin"] = True

        return RedirectResponse(
            url="/admin",
            status_code=302
        )

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Неверный логин или пароль"
        }
    )


@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=302
    )

# ========================= ADMIN PANEL =========================

@app.get("/admin")
def admin_panel(request: Request):

    if not is_authenticated(request):

        return RedirectResponse(
            url="/login",
            status_code=302
        )

    files = []

    for file in COMMON_DIR.iterdir():

        if file.is_file():
            files.append(file.name)

    files.sort()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "files": files
        }
    )

# ========================= UPLOAD =========================

@app.post("/admin/upload")
def upload(
    request: Request,
    files: list[UploadFile] = File(...)
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    for file in files:

        filepath = COMMON_DIR / file.filename

        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)

    return {"ok": True}

# ========================= DELETE FILE =========================

@app.delete("/admin/delete/{filename}")
def delete_file(
    request: Request,
    filename: str
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    path = COMMON_DIR / filename

    if path.exists():
        path.unlink()

    return {"deleted": True}


# ========================= Delete all uploaded files =========================

@app.delete("/admin/delete-all")
def delete_all_files(request: Request):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    for file in COMMON_DIR.iterdir():

        if file.is_file():
            file.unlink()

    return {"deleted": True}

# ========================= Playlist API =========================

@app.get("/api/videos")
def api_videos():

    items = list_common_items()

    media = []

    for item in items:

        ext = Path(item.filename).suffix.lower()

        if ext in VIDEO_EXTENSIONS:

            media.append({
                "type": "video",
                "url": f"/media/common/{item.filename}"
            })

        elif ext in IMAGE_EXTENSIONS:

            media.append({
                "type": "image",
                "url": f"/media/common/{item.filename}"
            })

    return JSONResponse(media)

# ========================= PLAYER =========================

@app.get("/player")
def player(request: Request):

    return templates.TemplateResponse(
        "player.html",
        {
            "request": request
        }
    )

# ========================= Media streaming endpoint =========================

@app.get("/media/common/{filename}")
def media_common(filename: str):

    try:

        path = safe_resolve_media_path(
            "common",
            None,
            filename
        )

    except Exception:
        raise HTTPException(status_code=403)

    if not path.exists():
        raise HTTPException(status_code=404)

    return FileResponse(path)

# ========================= HEALTH =========================

@app.get("/health")
def health():

    return {"status": "ok"}

# ========================= Local development entrypoint =========================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=True
    )