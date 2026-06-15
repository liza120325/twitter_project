import os

from fastapi import FastAPI, Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

STATIC_FOLDER_ABSOLUTE = os.path.abspath(os.path.join("..", "static"))

# 1. Создаем экземпляр приложения
# uvicorn app:app --host 127.0.0.1 --port 8000
app = FastAPI()

app.mount("/static", StaticFiles(directory=(os.path.join("..", "static"))))

# 2. Создаем маршрут для GET-запроса на главную страницу
@app.get("/check")
def read_root():
    return {"message": "Привет, это простой API на FastAPI!"}

#
# app.mount("/static", StaticFiles(directory=STATIC_FOLDER_ABSOLUTE), name="static")
#
# @app.get("/favicon.ico", include_in_schema=False)
# async def favicon():
#     return FileResponse("static/favicon.ico")
#
# @app.middleware("http")
# async def static_file_middleware(request: Request, call_next):
#     path = request.url.path
#     if path.startswith("/js/"):
#         new_path = path.replace("/js/", "/static/js/", 1)
#         try:
#             return FileResponse(os.path.join(STATIC_FOLDER_ABSOLUTE, "js", new_path.split("/static/js/", 1)[1]))
#         except FileNotFoundError:
#             return await call_next(request)  # Если файл не найден, передаем дальше
#     elif path.startswith("/css/"):
#         new_path = path.replace("/css/", "/static/css/", 1)
#         try:
#             return FileResponse(os.path.join(STATIC_FOLDER_ABSOLUTE, "css", new_path.split("/static/css/", 1)[1]))
#         except FileNotFoundError:
#             return await call_next(request)  # Если файл не найден, передаем дальше
#
#     response = await call_next(request)
#     return response






