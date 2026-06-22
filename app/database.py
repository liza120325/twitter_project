from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

# 1. Строка подключения
DATABASE_URL = "postgresql+asyncpg://admin:secretpassword@db:5432/fastapi_db"

# 2. Создание асинхронного движка
# echo=True будет логгировать в консоль все sql запросы, которые мы будем делать
engine = create_async_engine(DATABASE_URL, echo=True)
# expire_on_commit=False will prevent attributes from being expired
# after commit.

# 3. Фабрика асинхронных сессий
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()
Base = declarative_base()


class User(Base):
    '''Модель пользователя'''
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    api_key = Column(String, default=0)

    # На кого ПОДПИСАН этот пользователь (тех, кого он читает)
    following = relationship(
        'User', lambda: user_following,
        primaryjoin=lambda: User.id == user_following.c.i_follow,
        secondaryjoin=lambda: User.id == user_following.c.i_am_followed,
        back_populates='followers'
    )

    # ПОДПИСЧИКИ этого пользователя (те, кто читают его)
    followers = relationship(
        'User', lambda: user_following,
        primaryjoin=lambda: User.id == user_following.c.i_am_followed,
        secondaryjoin=lambda: User.id == user_following.c.i_follow,
        back_populates='following'
    )

    twits = relationship('Twits', cascade='all, delete-orphan')

user_following = Table(
    'user_following', Base.metadata,
    Column('i_follow', Integer, ForeignKey(User.id), primary_key=True),
    Column('i_am_followed', Integer, ForeignKey(User.id), primary_key=True)
)


class Twits(Base):
    '''Модель твитов, написанных пользователем'''
    __tablename__ = 'twits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    context = Column(String, nullable=False)
    attachments = Column(Integer, default=False)
    author = Column(Integer, ForeignKey('user.id'))
    likes = relationship('Likes', cascade='all, delete-orphan')

    def __repr__(self):
        return f"Твит {self.twit_text}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Likes(Base):
    '''Модель лайков, поставленных на твит'''
    __tablename__ = 'user_likes'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ID пользователя, поставившего лайк
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    # ID твита, на который поставили лайк
    like_belongs_to = Column(Integer, ForeignKey('twits.id'))


class Images(Base):
    pass