import os
from test.insert_data import create_data
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from my_app.app import app  # Импорт вашего приложения FastAPI
from my_app.database import (Base, get_db)
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

# Создаем тестовую базу
TEST_DATABASE_URL = os.getenv("DATABASE_URL")
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
test_async_session = async_sessionmaker(
    bind=test_engine, expire_on_commit=False, class_=AsyncSession
)


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


@pytest_asyncio.fixture()
def mock_async_session(db_session):
    """
    Фикстура перехватывает контекстный менеджер async_session()
    и подставляет вместо него тестовую сессию db_session.
    """
    # 1. Создаем мок для контекстного менеджера `async with`
    mock_cm = AsyncMock()
    # 2. Указываем, что при входе в контекст (as session) возвращается db_session
    mock_cm.__aenter__.return_value = db_session

    # 3. Запускаем патч на время работы теста
    # Замените 'app.main.async_session' на ваш реальный путь к эндпоинту!
    with patch("my_app.app.async_session", return_value=mock_cm) as mocked_factory:
        yield mocked_factory  # Передаем управление тесту
