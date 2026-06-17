import os

from fastapi import FastAPI, Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

STATIC_FOLDER_ABSOLUTE = os.path.abspath(os.path.join("..", "static"))

# 1. Создаем экземпляр приложения
# uvicorn app:app --host 127.0.0.1 --port 8000
app = FastAPI()

# app.mount("/static", StaticFiles(directory=STATIC_FOLDER_ABSOLUTE), name="static")

# 2. Создаем маршрут для GET-запроса на главную страницу
@app.get("/check")
def check():
    return {"message": "Привет, это простой API на FastAPI!"}

@app.get("/api")
def get_my_api():
    return {"message": "Привет!"}





