import os
from typing import Annotated, Dict, List, Optional
from pathlib import Path
import uvicorn
import aiofiles
import asyncio
from sqlalchemy import select, update, insert, exists, delete, and_
from sqlalchemy.orm import selectinload
from array import array
from schemas import UserOut, TweetOut, TweetIn, MediaOut, MediaIn, Follow
from fastapi import FastAPI, Request, Header, Depends, UploadFile, File
from contextlib import asynccontextmanager
from database import (
    engine,
    async_session,
    session,
    Base,
    User,
    Likes,
    Twits,
    user_following,
    Images
)
import logging

logger = logging.getLogger("logger_for_app")
logging.basicConfig(level=logging.DEBUG, filename="fastapi.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # здесь передаем синхронную функцию - create_all, которую нужно дождаться
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as start_session:
        async with start_session.begin():
            user_1 = User(name="Harry Potter", api_key="test")
            user_2 = User(name="Марина", api_key="tsvetaeva")
            user_3 = User(name="Александр", api_key="pushkin")
            user_4 = User(name="Михаил", api_key="lermontov")

            start_session.add_all([user_1, user_2, user_3, user_4])

            user_4.followers = [user_1]

            tweet_1 = Twits(context="Я помню чудное мгновенье", author=3)
            tweet_2 = Twits(context="Выхожу один я на дорогу", author=4)
            tweet_3 = Twits(context="Мне Нравится, что вы больны не мной", author=2)
            tweet_4 = Twits(context="Сегодня чудесный день!", author=1)

            start_session.add_all([tweet_1, tweet_2, tweet_3, tweet_4])

            like_1 = Likes(user_id=1, user_name="Harry Potter", tweet_id=1)
            like_2 = Likes(user_id=2, user_name="Марина", tweet_id=1)
            like_3 = Likes(user_id=4, user_name="Михаил", tweet_id=1)

            start_session.add_all([like_1, like_2, like_3])

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/users/me", response_model=UserOut)
async def get_users_me(api_key: Annotated[str, Header()]):
    async with async_session() as session:

        user = await session.execute(
            select(User)
            .where(User.api_key == api_key)
            .options(selectinload(User.following), selectinload(User.followers))
        )
        result = user.scalars().first()

        data = {
            "result": "true",
            "user": {
                "id": result.id,
                "name": result.name,
                "followers": [{"id": x.id, "name": x.name} for x in result.followers],
                "following": [{"id": x.id, "name": x.name} for x in result.following],
            },
        }
    return data


@app.get("/api/users/{user_id}", response_model=UserOut)
async def get_users_me(user_id: int):
    async with async_session() as session:

        user = await session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.following), selectinload(User.followers))
        )
        result = user.scalars().first()

        data = {
            "result": "true",
            "user": {
                "id": result.id,
                "name": result.name,
                "followers": [{"id": x.id, "name": x.name} for x in result.followers],
                "following": [{"id": x.id, "name": x.name} for x in result.following],
            },
        }
    return data


@app.post("/api/users/{id}/follow", response_model=Follow)
async def follow_user(api_key: Annotated[str, Header()], id: int):
    async with async_session() as session:

        # Получаем текущего пользователя
        get_user = await session.execute(
            select(User)
            .where(User.api_key == api_key)
            .options(selectinload(User.following), selectinload(User.followers))
        )
        user_me = get_user.scalars().first()
        logger.info("Получен текущий пользователь")

        # Получаем пользователя, на которого подписываемся
        get_following = await session.execute(
            select(User)
            .where(User.id == id)
            .options(selectinload(User.following), selectinload(User.followers))
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
                return (f"'result': 'false', 'error_type': {type(ex).__name__}, "
                        f"'error_message': {str(ex)}")

        await session.commit()
    data = {"result": "true"}
    return data


@app.delete("/api/users/{id}/follow", response_model=Follow)
async def unfollow_user(api_key: Annotated[str, Header()], id: int):
    async with async_session() as session:

        # Получаем текущего пользователя
        get_user = await session.execute(
            select(User)
            .where(User.api_key == api_key)
            .options(selectinload(User.following), selectinload(User.followers))
        )
        user_me = get_user.scalars().first()
        logger.info("Получен текущий пользователь")

        # Получаем пользователя, от которого отписываемся
        get_following = await session.execute(
            select(User)
            .where(User.id == id)
            .options(selectinload(User.following), selectinload(User.followers))
        )
        user_following = get_following.scalars().first()
        logger.info("Получен пользователь, от которого отписываемся")

        # Проверяем, подписан ли текущий пользователь на того, от кого он хочет отписаться
        logger.info("Проверяем, подписан ли текущий пользователь на того, от кого он хочет отписаться")
        check = user_following in user_me.following

        if check:
            logger.info("Отписываемся")
            try:
                # Отписываемся
                user_me.following.remove(user_following)
                logger.info("Вы успешно отписались")

            except Exception as ex:
                return (f"'result': 'false', 'error_type': {type(ex).__name__}, "
                        f"'error_message': {str(ex)}")

        await session.commit()
    data = {"result": "true"}
    return data


@app.post("/api/tweets/{id}/likes", response_model=Follow)
async def send_like(api_key: Annotated[str, Header()], id: int):
    async with async_session() as session:

        # Получаем ID и Имя пользователя, который ставит лайк
        get_user = await session.execute(
            select(User.id, User.name)
            .where(User.api_key == api_key)
        )
        user_me = get_user.scalars().first()
        logger.info(f"Получен текущий пользователь {user_me}")

        # Добавляем ID и Имя пользователя, ID твита в таблицу лайков
        add_like = await session.execute(insert(Likes).values(user_id=user_me[0],
                                                              user_name=user_me[1],
                                                              tweet_id=id))
        logger.info("Лайк поставлен")
        await session.commit()

    data = {"result": "true"}
    return data


@app.delete("/api/tweets/{id}/likes", response_model=Follow)
async def send_like(api_key: Annotated[str, Header()], id: int):
    async with async_session() as session:

        # Получаем ID пользователя, который убирает лайк
        get_user = await session.execute(
            select(User.id).where(User.api_key == api_key)
        )
        user_me = get_user.scalars().first()
        logger.info(f"Получен текущий пользователь {user_me}")


        # Удалеяем ID твита из таблицы лайков
        delete_like = await session.execute(delete(Likes).where(and_(Likes.tweet_id == id,
                                                                     Likes.user_id == user_me[0])))
        logger.info("Лайк удален")
        await session.commit()

    data = {"result": "true"}
    return data


@app.get("/api/tweets", response_model=TweetOut)
async def get_user_tweets(api_key: Annotated[str, Header()]):
    pass


@app.post("/api/medias", response_model=MediaOut)
async def post_new_media(api_key: Annotated[str, Header()], insert_file: UploadFile = File(...)):
    # Сохранить файл
    directory = Path("media_storage")
    directory.mkdir(parents=True, exist_ok=True)
    contents = insert_file.file.read()
    file_path = directory / insert_file.filename

    async with aiofiles.async_open(file_path, mode="wb") as f:
        await f.write(contents)

    # Внести в базу данных путь к папке с изображением
    insert_data = await session.execute(insert(Images).values(path=file_path))