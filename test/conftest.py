import asyncio
from typing import AsyncGenerator

import pytest
import os
import sys
import asyncio

import pytest_asyncio
from sqlalchemy import create_engine, NullPool
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from my_app.database import Base, get_db, async_session, User, Twits, Likes # Импорты вашей базы
from my_app.app import app  # Импорт вашего приложения FastAPI
from test.insert_data import create_data


# Создаем тестовую базу
# TEST_DATABASE_URL = "postgresql+asyncpg://some_user:some_password@localhost:5432/some_user"
TEST_DATABASE_URL = os.getenv("DATABASE_URL")
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
test_async_session = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)



async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


# Фикстура по созданию и наполнению таблиц
@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await create_data(conn)
        await conn.commit()
    yield
    # async with test_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


# Фикстура тестового клиента
@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Создает изолированную сессию БД для теста.
    Все изменения откатываются (ROLLBACK) после завершения теста.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()

    # Связываем сессию с текущим соединением и транзакцией
    session = test_async_session(bind=connection)

    yield session

    # Закрываем сессию и откатываем все изменения
    await session.close()
    await transaction.rollback()
    await connection.close()