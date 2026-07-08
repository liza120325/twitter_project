from typing import Annotated
from pathlib import Path
import aiofiles
from sqlalchemy import select, update, insert, delete, and_
from sqlalchemy.orm import selectinload
from schemas import UserOut, TweetOut, TweetIn, MediaOut, MediaIn, Follow
from fastapi import FastAPI, Header, UploadFile
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


async def create_data():
    '''Функция наполняет Базу данных входными данными'''
    async with async_session() as start_session:
        async with start_session.begin():
            user_1 = User(name="Harry Potter", api_key="test")
            user_2 = User(name="Марина", api_key="tsvetaeva")
            user_3 = User(name="Александр", api_key="pushkin")
            user_4 = User(name="Михаил", api_key="lermontov")

            start_session.add_all([user_1, user_2, user_3, user_4])

            user_1.followers = [user_2, user_3]
            user_1.following = [user_2, user_3]

            tweet_1 = Twits(context="Я помню чудное мгновенье", author=3)
            tweet_2 = Twits(context="Выхожу один я на дорогу", author=4)
            tweet_3 = Twits(context="Мне Нравится, что вы больны не мной", author=2)
            tweet_4 = Twits(context="Сегодня чудесный день!", author=1)

            start_session.add_all([tweet_1, tweet_2, tweet_3, tweet_4])

            like_1 = Likes(user_id=1, user_name="Harry Potter", tweet_id=1)
            like_2 = Likes(user_id=2, user_name="Марина", tweet_id=1)
            like_3 = Likes(user_id=4, user_name="Михаил", tweet_id=1)

            start_session.add_all([like_1, like_2, like_3])


async def get_my_profile(api_key: Annotated[str, Header()]) -> User:
    '''Функция по получению данных профиля текущего пользователя из базы данных'''
    user = await session.execute(
        select(User)
        .where(User.api_key == api_key)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    result = user.scalars().first()
    return result


async def get_any_user_profile(user_id) -> User:
    '''Функция по получению данных профиля любого пользователя из базы данных'''
    user = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    result = user.scalars().first()
    return result


async def form_data_for_user(result) -> dict:
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

