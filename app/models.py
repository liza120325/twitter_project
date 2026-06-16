from typing import Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    '''Модель пользователя'''
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    age = Column(Integer, index=True)
    api_key = Column(String, default=0)

    twits = relationship('Twits', cascade='all, delete-orphan')

    def __repr__(self):
        return f"Пользователь {self.name, self.surname}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
    belongs_to = Column(Integer, ForeignKey('twits.id'))

