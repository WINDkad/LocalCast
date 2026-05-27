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
    FileResponse,
    JSONResponse
)

from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import (
    SessionMiddleware
)

from config import (
    MEDIA_ROOT,
    HOST,
    PORT,
    COMMON_FOLDER,
    VIDEO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    SECRET_KEY,
    SESSION_MAX_AGE
)

from media_lib import (
    ensure_system_folders,
    load_folders_meta,
    create_folder,
    delete_folder,
    list_folder_items,
    safe_resolve_media_path,
    load_credentials,
    save_credentials
)

# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="LocalCast",
    version="3.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=SESSION_MAX_AGE
)

templates = Jinja2Templates(
    directory="templates"
)

ensure_system_folders()

# =========================================================
# AUTH
# =========================================================

def is_authenticated(
    request: Request
) -> bool:

    return request.session.get(
        "admin"
    ) is True

# =========================================================
# LOGIN
# =========================================================

@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None
        }
    )


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    credentials = load_credentials()

    if (
        username == credentials["username"] and
        password == credentials["password"]
    ):

        request.session["admin"] = True

        return RedirectResponse(
            url="/admin",
            status_code=302
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
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

# =========================================================
# CHANGE CREDENTIALS
# =========================================================

@app.post("/admin/change-credentials")
def change_credentials(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    if password != confirm_password:

        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    save_credentials(
        username=username,
        password=password
    )

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=302
    )

# =========================================================
# ADMIN ROOT
# =========================================================

@app.get("/admin")
def admin_page(request: Request):

    if not is_authenticated(request):

        return RedirectResponse(
            url="/login",
            status_code=302
        )

    folders = load_folders_meta()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "folders": folders
        }
    )

# =========================================================
# CREATE FOLDER
# =========================================================

@app.post("/admin/create-folder")
def create_new_folder(
    request: Request,
    folder_name: str = Form(...)
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    folders = load_folders_meta()

    new_id = str(
        max(
            [
                int(x)
                for x in folders.keys()
                if x.isdigit()
            ] + [0]
        ) + 1
    )

    create_folder(
        folder_id=new_id,
        display_name=folder_name
    )

    return RedirectResponse(
        url="/admin",
        status_code=302
    )

# =========================================================
# DELETE FOLDER
# =========================================================

@app.delete("/admin/delete-folder/{folder_id}")
def remove_folder(
    request: Request,
    folder_id: str
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    delete_folder(folder_id)

    return {"deleted": True}

# =========================================================
# FOLDER PAGE
# =========================================================

@app.get("/admin/folder/{folder_id}")
def folder_page(
    request: Request,
    folder_id: str
):

    if not is_authenticated(request):

        return RedirectResponse(
            url="/login",
            status_code=302
        )

    folders = load_folders_meta()

    if folder_id not in folders:
        raise HTTPException(status_code=404)

    items = list_folder_items(folder_id)

    files = [
        item.filename
        for item in items
    ]

    return templates.TemplateResponse(
        request=request,
        name="folder.html",
        context={
            "folder_id": folder_id,
            "folder_name": folders[folder_id],
            "files": files,
            "is_common": (
                folder_id == COMMON_FOLDER
            )
        }
    )

# =========================================================
# UPLOAD
# =========================================================

@app.post("/admin/folder/{folder_id}/upload")
def upload_files(
    request: Request,
    folder_id: str,
    files: list[UploadFile] = File(...)
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    folder_path = (
        MEDIA_ROOT / folder_id
    )

    folder_path.mkdir(
        parents=True,
        exist_ok=True
    )

    for file in files:

        filepath = (
            folder_path / file.filename
        )

        with open(filepath, "wb") as f:

            shutil.copyfileobj(
                file.file,
                f
            )

    return {"ok": True}

# =========================================================
# DELETE FILE
# =========================================================

@app.delete(
    "/admin/folder/{folder_id}/delete/{filename}"
)
def delete_file(
    request: Request,
    folder_id: str,
    filename: str
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    path = (
        MEDIA_ROOT /
        folder_id /
        filename
    )

    if path.exists():
        path.unlink()

    return {"deleted": True}

# =========================================================
# DELETE ALL FILES
# =========================================================

@app.delete(
    "/admin/folder/{folder_id}/delete-all"
)
def delete_all_files(
    request: Request,
    folder_id: str
):

    if not is_authenticated(request):
        raise HTTPException(status_code=401)

    folder_path = (
        MEDIA_ROOT / folder_id
    )

    if folder_path.exists():

        for file in folder_path.iterdir():

            if file.is_file():
                file.unlink()

    return {"deleted": True}

# =========================================================
# PLAYER API
# =========================================================

@app.get("/api/media/{folder_id}")
def api_media(folder_id: str):

    items = list_folder_items(folder_id)

    media = []

    for item in items:

        ext = Path(
            item.filename
        ).suffix.lower()

        if ext in VIDEO_EXTENSIONS:

            media.append({
                "type": "video",
                "url": (
                    f"/media/"
                    f"{folder_id}/"
                    f"{item.filename}"
                )
            })

        elif ext in IMAGE_EXTENSIONS:

            media.append({
                "type": "image",
                "url": (
                    f"/media/"
                    f"{folder_id}/"
                    f"{item.filename}"
                )
            })

    return JSONResponse(media)

# =========================================================
# PLAYER
# =========================================================

@app.get("/player/{folder_id}")
def player_page(
    request: Request,
    folder_id: str
):

    folders = load_folders_meta()

    if folder_id not in folders:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        request=request,
        name="player.html",
        context={
            "folder_id": folder_id,
            "folder_name": folders[folder_id]
        }
    )

# =========================================================
# MEDIA
# =========================================================

@app.get("/media/{folder_id}/{filename}")
def media_file(
    folder_id: str,
    filename: str
):

    try:

        path = safe_resolve_media_path(
            folder_id,
            filename
        )

    except Exception:

        raise HTTPException(
            status_code=403
        )

    if not path.exists():

        raise HTTPException(
            status_code=404
        )

    return FileResponse(path)

# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=True
    )