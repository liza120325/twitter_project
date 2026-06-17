import os
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from models import User, Likes, Twits, Followers, Following
from database import engine, async_session, Base

STATIC_FOLDER_ABSOLUTE = os.path.abspath(os.path.join("..", "static"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up...")
    # Initialize databases, load ML models, or open network connections here

    async with engine.begin() as conn:
        # здесь передаем синхронную функцию - create_all, которую нужно дождаться
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        async with session.begin():
            follower_1 = Followers(name="Вася")
            following_1 = Following(name="Света")
            session.add(follower_1)
            session.add(following_1)

            user_1 = User(name="Коля", api_key="123456", followers=1, following=1)
            session.add(user_1)


    yield

    print("Application is shutting down...")

app = FastAPI(lifespan=lifespan)


@app.get("/check")
def check():
    return {"message": "Привет, это простой API на FastAPI!"}


@app.get("/api/users/me")
def get_my_api():
    return {"message": "Привет!"}




