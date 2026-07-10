import pytest
import os
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import Base, async_session, User, Twits, Likes # Импорты вашей базы
from app.app import app  # Импорт вашего приложения FastAPI
from app.schemas import UserOut, TweetOut, TweetIn, MediaOut, DoUndoLike, TweetId, MediaIn, Follow, FollowUser, TweetDelete, TweetsByFollowing, Likes, TweetInfo, Author

# Используем драйвер +asyncpg для асинхронного подключения
# TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@test_db:5432/my_app_test"
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://test_user:test_password@test_db:5432/my_app_test")
# Создаем асинхронный движок
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# Фикстура для подготовки таблиц БД
@pytest.fixture(scope="session", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        # Создаем таблицы перед началом всех тестов
        await conn.run_sync(Base.metadata.create_all)
    yield
    # async with engine.begin() as conn:
    #     # Удаляем таблицы после завершения всех тестов
    #     await conn.run_sync(Base.metadata.drop_all)


# Фикстура для создания чистой сессии на каждый тест
@pytest.fixture()
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        # Откатываем любые изменения, чтобы тесты не влияли друг на друга
        await session.rollback()


# Фикстура для асинхронного клиента
@pytest.fixture()
async def client(db_session):
    # Подменяем зависимость async_session в FastAPI на нашу тестовую сессию
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[async_session] = override_get_db

    # Создаем асинхронный клиент для отправки запросов
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Очищаем подмену после теста
    app.dependency_overrides.clear()


# Фикстура для заполнения первичными данными БД
@pytest.fixture(autouse=True)
async def create_data():
    # Создаем отдельную сессию для заполнения первичных данных
    async with TestingSessionLocal() as session:

        user_1 = User(name="Frodo Baggins", api_key="hobbit")
        user_2 = User(name="Legolas Greenleaf", api_key="elf")
        user_3 = User(name="Gandalf the Grey", api_key="wizard")

        session.add_all([user_1, user_2, user_3])

        user_1.followers = [user_2, user_3]
        user_1.following = [user_2]

        tweet_1 = Twits(context="I live in Shire", author=1)
        tweet_2 = Twits(context="I am a skilled archer", author=2)
        tweet_3 = Twits(context="You must destroy the ring", author=3)

        session.add_all([tweet_1, tweet_2, tweet_3])

        like_1 = Likes(user_id=1, user_name="Frodo Baggins", tweet_id=3)
        like_2 = Likes(user_id=2, user_name="Legolas Greenleaf", tweet_id=3)

        session.add_all([like_1, like_2])

        session.commit()

    yield

