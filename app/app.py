from typing import Annotated
from pathlib import Path
import aiofiles
from sqlalchemy import select, update, insert, delete, and_, func, or_
from sqlalchemy.orm import selectinload
from schemas import UserOut, TweetOut, TweetIn, MediaOut, DoUndoLike, SendMediaId, MediaIn, Follow, FollowUser, TweetDelete, TweetsByFollowing, Likes, TweetInfo, Author
from fastapi import FastAPI, Header, UploadFile
from fastapi.responses import FileResponse
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
from crud import create_data, get_my_profile, get_any_user_profile, form_data_for_user

logger = logging.getLogger("logger_for_app")
logging.basicConfig(level=logging.DEBUG, filename="fastapi.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # здесь передаем синхронную функцию - create_all, которую нужно дождаться
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # async with async_session() as start_session:
    #     async with start_session.begin():
    #         user_1 = User(name="Harry Potter", api_key="test")
    #         user_2 = User(name="Марина", api_key="tsvetaeva")
    #         user_3 = User(name="Александр", api_key="pushkin")
    #         user_4 = User(name="Михаил", api_key="lermontov")
    #
    #         start_session.add_all([user_1, user_2, user_3, user_4])
    #
    #         user_4.followers = [user_1]
    #
    #         tweet_1 = Twits(context="Я помню чудное мгновенье", author=3)
    #         tweet_2 = Twits(context="Выхожу один я на дорогу", author=4)
    #         tweet_3 = Twits(context="Мне Нравится, что вы больны не мной", author=2)
    #         tweet_4 = Twits(context="Сегодня чудесный день!", author=1)
    #
    #         start_session.add_all([tweet_1, tweet_2, tweet_3, tweet_4])
    #
    #         like_1 = Likes(user_id=1, user_name="Harry Potter", tweet_id=1)
    #         like_2 = Likes(user_id=2, user_name="Марина", tweet_id=1)
    #         like_3 = Likes(user_id=4, user_name="Михаил", tweet_id=1)
    #
    #         start_session.add_all([like_1, like_2, like_3])
    await create_data()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/api/users/me", response_model=UserOut)
async def get_users_me(api_key: Annotated[str, Header()]):
    '''
    Эндпоинт по получению информации о своем профиле
    :param api_key: api_key текущего пользователя
    :return: объект класса User
    '''
    async with async_session() as session:
        # user = await session.execute(
        #     select(User)
        #     .where(User.api_key == api_key)
        #     .options(selectinload(User.following), selectinload(User.followers))
        # )
        # result = user.scalars().first()
        result = await get_my_profile(api_key)
        data = await form_data_for_user(result)
        # data = {
        #     "result": "true",
        #     "user": {
        #         "id": result.id,
        #         "name": result.name,
        #         "followers": [{"id": x.id, "name": x.name} for x in result.followers],
        #         "following": [{"id": x.id, "name": x.name} for x in result.following],
        #     },
        # }
    return data


@app.get("/api/users/{user_id}", response_model=UserOut)
async def get_users_me(user_id: int):
    '''
    Эндпоинт по получению информации о профиле конкретного пользователя
    :param user_id: ID пользователя, информацию о профиле которого хотим получить
    :return: объект класса User
    '''
    async with async_session() as session:
        # user = await session.execute(
        #     select(User)
        #     .where(User.id == user_id)
        #     .options(selectinload(User.following), selectinload(User.followers))
        # )
        # result = user.scalars().first()
        result = await get_any_user_profile(user_id)
        data = await form_data_for_user(result)
        # data = {
        #     "result": "true",
        #     "user": {
        #         "id": result.id,
        #         "name": result.name,
        #         "followers": [{"id": x.id, "name": x.name} for x in result.followers],
        #         "following": [{"id": x.id, "name": x.name} for x in result.following],
        #     },
        # }
    return data


@app.post("/api/users/{id}/follow", response_model=FollowUser)
async def follow_user(api_key: Annotated[str, Header()], id: int):
    '''
    Эндпоинт на оформление подписки на пользователя
    :param api_key: api_key текущего пользователя
    :param id: ID пользователя, на которого подписываемся
    :return: data = {"result": "true"}
    '''
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


@app.delete("/api/users/{id}/follow", response_model=FollowUser)
async def unfollow_user(api_key: Annotated[str, Header()], id: int):
    '''
    Эндпоинт на отписку от пользователя
    :param api_key: api_key текущего пользователя
    :param id: ID пользователя, от которого отписываемся
    :return: data = {"result": "true"}
    '''
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


@app.post("/api/tweets/{id}/likes", response_model=DoUndoLike)
async def send_like(api_key: Annotated[str, Header()], id: int):
    async with async_session() as session:

        # Получаем ID и Имя пользователя, который ставит лайк
        get_user = await session.execute(
            select(User.id, User.name)
            .where(User.api_key == api_key)
        )
        user_me = get_user.all()
        logger.info(f"Получен текущий пользователь {user_me}")

        # Добавляем ID и Имя пользователя, ID твита в таблицу лайков
        add_like = await session.execute(insert(Likes).values(user_id=user_me[0][0],
                                                              user_name=user_me[0][1],
                                                              tweet_id=id))
        logger.info("Лайк поставлен")
        await session.commit()

    data = {"result": "true"}
    return data


@app.delete("/api/tweets/{id}/likes", response_model=DoUndoLike)
async def send_like(api_key: Annotated[str, Header()], id: int):
    async with async_session() as session:

        # Получаем ID пользователя, который убирает лайк
        get_user = await session.execute(
            select(User.id).where(User.api_key == api_key)
        )
        user_me = get_user.all()
        logger.info(f"Получен текущий пользователь {user_me}")


        # Удалеяем ID твита из таблицы лайков
        delete_like = await session.execute(delete(Likes).where(and_(Likes.tweet_id == id,
                                                                     Likes.user_id == user_me[0][0])))
        logger.info("Лайк удален")
        await session.commit()

    data = {"result": "true"}
    return data


@app.post("/api/medias", response_model=MediaOut)
async def post_new_media(api_key: Annotated[str, Header()], file: UploadFile):
    # Сохранить файл
    #directory = Path("media")
    directory = Path("../static/media")
    directory.mkdir(parents=True, exist_ok=True)
    contents = file.file.read()
    file_path = directory / f'{file.filename}'
    logger.info(f"Путь для сохранения файла {file_path}")

    async with aiofiles.open(str(file_path), mode="wb") as f:
        await f.write(contents)
        logger.info("Файл сохранен")

    async with async_session() as session:
        # Внести в базу данных путь к папке с изображением
        new_file = Images(path=str(file_path))
        logger.info("Файл добавлен в БД")
        session.add(new_file)
        await session.commit()

        #return {"result": "true", "media_id": new_file.media_id}
    data = {"result": "true", "media_id": new_file.media_id}
    return data


@app.post("/api/tweets", response_model=TweetOut)
async def post_new_tweet(api_key: Annotated[str, Header()],
                          tweet: TweetIn):
    tweet_context = tweet.tweet_data
    tweet_images = tweet.tweet_media_ids

    async with async_session() as session:

        # Получаем автора твита
        get_user = await session.execute(
            select(User.id).where(User.api_key == api_key)
        )
        user_me = get_user.scalars().first()
        logger.info(f"Получен текущий пользователь {user_me}")

        # Добавляем новый твит
        stmt = (insert(Twits).values(context=tweet_context, author=user_me).returning(Twits.id))
        result = await session.execute(stmt)

        new_tweet_id = result.scalar()
        logger.info(f"Твит добавлен в БД")

        # Добавляем изображение к новому твиту
        if tweet_images:
            logger.info(f"Твит содержит картинку")

            # ОБновляем в таблице изображений ID твита
            update_tweet_id = await session.execute(update(Images).where(
                Images.media_id == tweet_images[0]).values(tweet_id=new_tweet_id))
            logger.info(f"в таблице изображений ID твита обновлен")

            await session.commit()
            logger.info(f"Обновлена инфо в БД в таблице Изображений, присвоен ID твита")

            return {"result": "true", "tweet_id": new_tweet_id}

        else:
            await session.commit()
            return {"result": "true", "tweet_id": new_tweet_id}


@app.delete("/api/tweets/{id}", response_model=TweetDelete)
async def delete_tweet(api_key: Annotated[str, Header()], id: int):

    async with async_session() as session:
        # Получаем текущего пользователя
        get_user = await session.execute(
            select(User.id).where(User.api_key == api_key)
        )
        user_me = get_user.scalars().first()
        logger.info(f"Получен текущий пользователь {user_me}")

        # Удаляем твит
        try:
            tweet_delete = await session.execute(delete(Twits).where(and_(Twits.author == user_me,
                                                                          Twits.id == id)))
            await session.commit()
            logger.info('Твит удален')

        except Exception as ex:
            logger.info('Нельзя удалить чужой твит')
            return (f"'result': 'false', 'error_type': {type(ex).__name__}, "
                    f"'error_message': {str(ex)}")

    data = {"result": "true"}
    return data


@app.get("/api/medias/{media_id}")
async def get_pictures(api_key: Annotated[str, Header()], media_id: int) -> FileResponse:
    async with async_session() as session:

        # Получаем путь к картинке
        get_picture_path = await session.execute(select(Images.path).where(
            Images.media_id == media_id))
        image_path = get_picture_path.scalars().first()

        return FileResponse(image_path)




@app.get("/api/tweets", response_model=TweetsByFollowing)
async def get_tweets(api_key: Annotated[str, Header()]):
    async with async_session() as session:

        # Получаем текущего пользователя
        get_user = await session.execute(
            select(User).options(selectinload(User.following)).where(
                User.api_key == api_key)
        )
        user_me = get_user.scalars().first()
        logger.info(f"Получены данные пользователя {user_me}")

        following = [x.id for x in user_me.following]
        logger.info(f"Получены подписки текущего пользователя {following}")

        likes_subquery = (
            select(func.count(Likes.id))
            .where(Likes.tweet_id == Twits.id)
            .correlate(Twits)
            .scalar_subquery()
        )

        # Получаем твиты
        query = await session.execute(
            select(Twits,likes_subquery.label("likes_count"))
            .options(
            selectinload(Twits.likes),
                      selectinload(Twits.attachments),
                      selectinload(Twits.user_id))
            .where(or_(Twits.author.in_(following),
                       Twits.author == user_me.id))
            .order_by(likes_subquery.desc())
        )
        tweets = query.scalars().all()
        logger.info(f"Получены твиты  {tweets}")


        # Получаем твиты
        # query = await session.execute(select(Twits,
        #                                      func.count(Twits.likes).label("likes_count")).options(
        #     selectinload(Twits.likes),
        #               selectinload(Twits.attachments),
        #               selectinload(Twits.user_id)).
        #                               where(or_(
        #                                     Twits.author.in_(following),
        #                                     Twits.author == user_me.id)).
        #                                         group_by(Twits).
        #                                         order_by(func.count(Twits.likes).desc())
        # )
        # tweets = query.scalars().all()
        # logger.info(f"Получены твиты  {tweets}")


        # Преобразуем полученные твиты
        tweets_list = []
        for tweet in tweets:
            twit = {
                "id": tweet.id,
                "content": tweet.context,
                "attachments": [f'/api/medias/{media.media_id}' for media in tweet.attachments],
                "author": {"id": tweet.user_id.id,
                                  "name": tweet.user_id.name},
                "likes": [{"user_id": x.user_id,
                                  "name": x.user_name} for x in tweet.likes]
            }
            logger.info(f"Собраны данные одного твита  {twit}")
            tweets_list.append(twit)
        logger.info(f"Собраны общие данные {tweets_list}")


        data = {
            "result": "true",
            "tweets": tweets_list
        }
        return data





