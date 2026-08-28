# from help_manager import Console
# Console.hide()
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import time
import asyncio
import io
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from PIL import ImageGrab

from backend.commands import (
    FLAT_COMMANDS,
    COMMAND_CATEGORIES,
    execute_command,
    start_chaos,
    stop_chaos,
    chaos_active
)

ADMIN_PASSWORD = os.environ.get("WEB_BOT_PASSWORD")  # задаётся в переменной окружения
if not ADMIN_PASSWORD:
    raise SystemExit("Задайте пароль: переменная окружения WEB_BOT_PASSWORD")

app = FastAPI(title="Кеша Веб-Бот")
BASE_DIR = Path(__file__).parent.parent

# Раздача статики
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend")), name="static")

# Папка для загрузок
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

def check_password(request: Request) -> bool:
    """Проверяет пароль в заголовке X-Password."""
    password = request.headers.get("X-Password")
    return password == ADMIN_PASSWORD

# ---- Страницы ----
@app.get("/", response_class=HTMLResponse)
async def login_page():
    login_path = BASE_DIR / "frontend" / "login.html"
    with open(login_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    chat_path = BASE_DIR / "frontend" / "chat.html"
    with open(chat_path, "r", encoding="utf-8") as f:
        return f.read()

# ---- API ----
@app.post("/login")
async def login(request: Request):
    data = await request.json()
    password = data.get("password")
    if password == ADMIN_PASSWORD:
        return JSONResponse({"success": True})
    else:
        return JSONResponse({"success": False, "error": "Неверный пароль"}, status_code=401)

@app.get("/api/commands")
async def get_commands(request: Request):
    if not check_password(request):
        raise HTTPException(status_code=401, detail="Неверный пароль")
    return {
        "commands": FLAT_COMMANDS,
        "categories": COMMAND_CATEGORIES
    }

@app.post("/api/command")
async def api_execute_command(request: Request):
    if not check_password(request):
        raise HTTPException(status_code=401, detail="Неверный пароль")
    data = await request.json()
    text = data.get("command", "")
    result, image_url = await asyncio.to_thread(execute_command, text)
    return {"result": result, "image_url": image_url}

@app.post("/api/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if not check_password(request):
        raise HTTPException(status_code=401, detail="Неверный пароль")
    try:
        contents = await file.read()
        filename = Path(file.filename).name  # без "../", файл не уйдёт за пределы uploads/
        save_path = UPLOAD_DIR / filename
        with open(save_path, "wb") as f:
            f.write(contents)
        return {"file_url": f"/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- Трансляция (без OpenCV, только Pillow) ----
def generate_frames():
    """Генератор кадров для MJPEG-потока."""
    while True:
        try:
            screenshot = ImageGrab.grab()
            with io.BytesIO() as output:
                screenshot.save(output, format='JPEG', quality=50)
                frame_bytes = output.getvalue()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)  # ~30 FPS
        except Exception as e:
            print(f"Ошибка в стриме: {e}")
            time.sleep(0.1)

@app.get("/stream")
async def stream_screen(request: Request, password: str = None):
    """Эндпоинт для MJPEG-трансляции. Пароль можно передать в URL или заголовке."""
    if password != ADMIN_PASSWORD and request.headers.get("X-Password") != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)