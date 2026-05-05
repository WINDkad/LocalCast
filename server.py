from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse
from pathlib import Path
import shutil

from config import MEDIA_ROOT, PUBLIC_BASE_URL, HOST, PORT
from media_lib import (
    list_common_items,
    build_m3u,
    safe_resolve_media_path,
)

app = FastAPI(title="LocalCast", version="1.0")

COMMON_DIR = MEDIA_ROOT / "common"
COMMON_DIR.mkdir(parents=True, exist_ok=True)


# ================= ADMIN =================

@app.get("/admin", response_class=HTMLResponse)
def admin_panel():
    files = []

    for file in COMMON_DIR.iterdir():
        if file.is_file():
            files.append(file.name)

    file_list_html = "".join([
        f"""
        <div style='display:flex; justify-content:space-between; align-items:center;
                    background:#f8fafc; padding:12px 16px; border-radius:12px;
                    margin-bottom:10px; border:1px solid #e2e8f0;'>

            <span style='font-size:15px; color:#1e293b;'>
                {name}
            </span>

            <a href="#"
               onclick="deleteFile('{name}')"
               style='text-decoration:none; color:white;
                      background:#dc2626; padding:8px 14px;
                      border-radius:8px; font-size:14px;'>

                Удалить
            </a>
        </div>
        """
        for name in files
    ])

    return f"""
    <html>
        <head>
            <title>LocalCast Admin Panel</title>
            <meta charset="UTF-8">
        </head>

        <body style="margin:0;
                     font-family:Arial, sans-serif;
                     background:#f1f5f9;">

            <div style="max-width:900px;
                        margin:40px auto;
                        background:white;
                        border-radius:20px;
                        padding:40px;
                        box-shadow:0 10px 30px rgba(0,0,0,0.08);">

                <h1 style="margin-top:0;
                           color:#0f172a;
                           font-size:32px;">
                    LocalCast Admin Panel
                </h1>

                <p style="color:#475569;
                          font-size:16px;
                          margin-bottom:30px;">
                    Управление мультимедийным контентом для Smart TV
                </p>

                <div style="background:#eff6ff;
                            border:1px solid #bfdbfe;
                            padding:24px;
                            border-radius:16px;
                            margin-bottom:35px;">

                    <h2 style="margin-top:0;
                               color:#1d4ed8;">
                        Загрузка файлов
                    </h2>

                    <form id="uploadForm"
                          enctype="multipart/form-data">

                        <input type="file"
                               name="files"
                               multiple
                               required
                               style="margin-bottom:15px;
                                      font-size:14px;">

                        <br>

                        <button type="submit"
                                style="background:#2563eb;
                                       color:white;
                                       border:none;
                                       padding:12px 24px;
                                       border-radius:10px;
                                       font-size:15px;
                                       cursor:pointer;">

                            Загрузить файлы
                        </button>
                    </form>
                </div>

                <div>
                    <h2 style="color:#0f172a;
                               margin-bottom:20px;">
                        Файлы в папке common
                    </h2>

                    <form action="/delete-all"
                          method="post"
                          style="margin-bottom:20px;">

                        <button type="submit"
                                onclick="return confirm('Удалить все файлы из папки common?')"
                                style="background:#b91c1c;
                                       color:white;
                                       border:none;
                                       padding:12px 24px;
                                       border-radius:10px;
                                       font-size:15px;
                                       cursor:pointer;">

                            Удалить все файлы
                        </button>
                    </form>

                    {file_list_html if file_list_html else '<p style="color:#64748b;">Файлы пока не загружены</p>'}
                </div>

            </div>

            <script>
                function showMessage(text, success = true) {{
                    const box = document.createElement("div");

                    box.innerText = text;
                    box.style.position = "fixed";
                    box.style.top = "20px";
                    box.style.right = "20px";
                    box.style.padding = "14px 20px";
                    box.style.borderRadius = "12px";
                    box.style.color = "white";
                    box.style.fontSize = "14px";
                    box.style.zIndex = "9999";
                    box.style.boxShadow = "0 10px 20px rgba(0,0,0,0.15)";
                    box.style.background = success ? "#16a34a" : "#dc2626";

                    document.body.appendChild(box);

                    setTimeout(() => {{
                        box.remove();
                    }}, 2500);
                }}

                async function deleteFile(filename) {{
                    const response = await fetch(`/admin/delete/${{filename}}`);

                    if (response.ok) {{
                        showMessage("Файл успешно удалён", false);

                        setTimeout(() => {{
                            location.reload();
                        }}, 200);
                    }}
                }}

                document
                    .getElementById("uploadForm")
                    .addEventListener("submit", async function(e) {{

                        e.preventDefault();

                        const formData = new FormData(this);

                        const response = await fetch("/admin/upload", {{
                            method: "POST",
                            body: formData
                        }});

                        if (response.ok) {{
                            showMessage("Файлы успешно загружены", true);
                            this.reset();

                            setTimeout(() => {{
                                location.reload();
                            }}, 700);
                        }}
                    }});
            </script>

        </body>
    </html>
    """


@app.post("/admin/upload")
def upload(files: list[UploadFile] = File(...)):
    for file in files:
        with open(COMMON_DIR / file.filename, "wb") as f:
            shutil.copyfileobj(file.file, f)
    return {"ok": True}


@app.get("/admin/delete/{filename}")
def delete_file(filename: str):
    path = COMMON_DIR / filename
    if path.exists():
        path.unlink()
    return {"deleted": True}


@app.post("/delete-all")
def delete_all():
    for f in COMMON_DIR.iterdir():
        if f.is_file():
            f.unlink()
    return RedirectResponse("/admin", status_code=303)


# ================= PLAYLIST =================

@app.get("/playlist/common.m3u", response_class=PlainTextResponse)
def playlist_common():
    items = list_common_items()

    base_url = PUBLIC_BASE_URL or f"http://{HOST}:{PORT}"

    urls = [
        f"{base_url}/media/common/{item.filename}"
        for item in items
    ]

    return build_m3u(urls)


# ================= MEDIA =================

@app.get("/media/common/{filename}")
def media_common(filename: str):
    try:
        path = safe_resolve_media_path("common", None, filename)
    except Exception:
        raise HTTPException(status_code=403)

    if not path.exists():
        raise HTTPException(status_code=404)

    return FileResponse(path)


# ================= HEALTH =================

@app.get("/health")
def health():
    return "OK"


# ================= RUN =================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=True
    )