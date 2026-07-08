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
    Images
)
import logging


async def create_data() -> None:
    '''
    Функция наполняет базу данных первичной информацией
    :return: None
    '''
    async with async_session() as start_session:
        async with start_session.begin():
            user_1 = User(name="Harry Potter", api_key="test")
            user_2 = User(name="Hermione Granger", api_key="herm")
            user_3 = User(name="Ron Weasley", api_key="ron")
            user_4 = User(name="Albus Dumbledore", api_key="albus")
            user_5 = User(name="Lord Voldemort", api_key="lord")
            user_6 = User(name="Bellatrix Lestrange", api_key="bella")
            user_7 = User(name="Minerva McGonagall", api_key="minerva")

            start_session.add_all([user_1, user_2, user_3, user_4, user_5, user_6, user_7])

            user_1.followers = [user_2, user_3]
            user_1.following = [user_2, user_3, user_4, user_5, user_6, user_7]
            user_2.following = [user_3, user_4, user_5]
            user_6.following = [user_1, user_5]
            user_4.followers = [user_1, user_2, user_3]

            tweet_1 = Twits(context="I am the chosen one", author=1)
            tweet_2 = Twits(context="It is leviOsa, not leviosA", author=2)
            tweet_3 = Twits(context="My dad works at the ministry of magic", author=3)
            tweet_4 = Twits(context="Harry, you must find the horcruxes alone", author=4)
            tweet_5 = Twits(context="Avadacedavra!", author=5)
            tweet_6 = Twits(context="I killed Sirius Black", author=6)
            tweet_7 = Twits(context="Protect Hogwarts!", author=7)

            start_session.add_all([tweet_1, tweet_2, tweet_3, tweet_4, tweet_5, tweet_6, tweet_7])

            like_1 = Likes(user_id=1, user_name="Harry Potter", tweet_id=1)
            like_2 = Likes(user_id=2, user_name="Hermione Granger", tweet_id=1)
            like_3 = Likes(user_id=4, user_name="Albus Dumbledore", tweet_id=2)

            start_session.add_all([like_1, like_2, like_3])


async def get_my_profile(api_key: Annotated[str, Header()]) -> User:
    '''
    Функция по получению профиля текущего пользователя
    :param api_key: api_key текущего пользователя
    :return: User
    '''
    user = await session.execute(
        select(User)
        .where(User.api_key == api_key)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    result = user.scalars().first()
    return result


async def get_any_user_profile(user_id) -> User:
    '''
    Функция по получению информации о профиле любого пользователя
    :param user_id: ID пользователя, информацию о профиле которого хотим получить
    :return: User
    '''
    user = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    result = user.scalars().first()
    return result


async def form_data_for_user(result) -> dict:
    '''
    Функция формирует словарь для отправки данных страницы пользователя
    :param result: объект класса User
    :return: data = {User}
    '''
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


async def get_following_user_profile(user_id) -> User:
    get_following = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.following), selectinload(User.followers))
    )
    user_following = get_following.scalars().first()
    return user_following




