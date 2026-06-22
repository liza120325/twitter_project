from typing import Annotated, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from array import array
from schemas import UserOut, TweetOut, TweetIn, MediaOut
from fastapi import FastAPI, Request, Header, Depends
from contextlib import asynccontextmanager
from database import engine, async_session, session, Base, User, Likes, Twits


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # здесь передаем синхронную функцию - create_all, которую нужно дождаться
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as start_session:
        async with start_session.begin():
            user_1 = User(name="Коля", api_key="test")
            user_2 = User(name="Лев", api_key="tolstoy")
            user_3 = User(name="Александр", api_key="pushkin")
            user_4 = User(name="Михаил", api_key="lermontov")

            start_session.add(user_1)
            start_session.add(user_2)
            start_session.add(user_3)
            start_session.add(user_4)

            user_4.followers = [user_1]
            user_4.following = [user_1]
            user_1.following = [user_4]
            user_1.followers = [user_4]


    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/users/me", response_model=UserOut)
async def get_users_me(api_key: Annotated[str, Header()]):
    async with async_session() as session:

        user = await session.execute(
            select(User).where(User.api_key == api_key).options(
                selectinload(User.following), selectinload(User.followers)
            )
        )
        result = user.scalars().first()

        data = {
            "result": "true",
            "user": {
                "id": result.id,
                "name": result.name,
                "followers": [{"id": x.id, "name": x.name} for x in result.followers],
                "following": [{"id": x.id, "name": x.name} for x in result.following],
            }
        }
    return data


@app.get("/api/users/{user_id}", response_model=UserOut)
async def get_users_me(user_id: int):
    async with async_session() as session:

        user = await session.execute(
            select(User).where(User.id == user_id).options(
                selectinload(User.following), selectinload(User.followers)
            )
        )
        result = user.scalars().first()

        data = {
            "result": "true",
            "user": {
                "id": result.id,
                "name": result.name,
                "followers": [{"id": x.id, "name": x.name} for x in result.followers],
                "following": [{"id": x.id, "name": x.name} for x in result.following],
            }
        }
    return data


@app.post("/api/tweets", response_model=TweetOut)
async def post_new_tweet(api_key: Annotated[str, Header()], tweet_data: TweetIn):
    pass


@app.post("/api/medias", response_model=MediaOut)
async def post_new_media(api_key: Annotated[str, Header()], ):
    pass




