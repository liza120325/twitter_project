from typing import Annotated, Dict, List, Optional

import uvicorn
from sqlalchemy import select, update, insert, exists
from sqlalchemy.orm import selectinload
from array import array
from schemas import UserOut, TweetOut, TweetIn, MediaOut, MediaIn, Follow
from fastapi import FastAPI, Request, Header, Depends, UploadFile
from contextlib import asynccontextmanager
from database import engine, async_session, session, Base, User, Likes, Twits, user_following
import logging

logger = logging.getLogger('logger_for_app')
logging.basicConfig(level=logging.DEBUG, filename='fastapi.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # здесь передаем синхронную функцию - create_all, которую нужно дождаться
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as start_session:
        async with start_session.begin():
            user_1 = User(name="Коля", api_key="test")
            user_2 = User(name="Марина", api_key="tsvetaeva")
            user_3 = User(name="Александр", api_key="pushkin")
            user_4 = User(name="Михаил", api_key="lermontov")

            start_session.add_all([user_1, user_2, user_3, user_4])

            user_4.followers = [user_1]

            tweet_1 = Twits(context='Я помню чудное мгновенье', author=3)
            tweet_2 = Twits(context='Выхожу один я на дорогу', author=4)
            tweet_3 = Twits(context='Мне Нравится, что вы больны не мной', author=2)
            tweet_4 = Twits(context='Сегодня чудесный день!', author=1)

            start_session.add_all([tweet_1, tweet_2, tweet_3, tweet_4])

            like_1 = Likes(user_id=1, tweet_id=1)
            like_2 = Likes(user_id=2, tweet_id=1)
            like_3 = Likes(user_id=4, tweet_id=1)

            start_session.add_all([like_1, like_2, like_3])


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


@app.get("/api/tweets", response_model=TweetOut)
async def get_user_tweets(api_key: Annotated[str, Header()]):
    pass


# @app.post("/api/medias/{media_id}", response_model=MediaOut)
# async def post_new_media(api_key: Annotated[str, Header()], file: UploadFile):
#     async with async_session() as session:
#         pass


@app.post("/api/users/{id}/follow", response_model=Follow)
async def follow_user(api_key: Annotated[str, Header()], id: int):
    async with (async_session() as session):

        # Получаем текущего пользователя
        get_user = await session.execute(select(User).where(User.api_key == api_key).options(
            selectinload(User.following), selectinload(User.followers)
            )
        )
        user_me = get_user.scalars().first()
        logger.info("Получен текущий пользователь")

        # Получаем пользователя, на которого подписываемся
        get_following = await session.execute(select(User).where(User.id == id).options(
            selectinload(User.following), selectinload(User.followers))
        )
        user_following = get_following.scalars().first()
        logger.info("Получен пользователь, на которого подписываемся")

        # Проверяем, подписан ли текущий пользователь на выбранного
        logger.info("Пороверяем подписку")
        check = user_following in user_me.following

        if not check:
            logger.info("Пользователь не подписан")
            try:
                # Оформляем подписку
                user_me.following.append(user_following)
                logger.info("Подписка оформлена")

            except Exception as ex:
                return f"'result': 'false', 'error_type': {type(ex).__name__}, 'error_message': {str(ex)}"

        await session.commit()
    data = {"result": "true"}
    return data







