from sqlalchemy import Column, String, Integer
from database import Base

# модели таблиц sqlalchemy

# модель информации о рецепте
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    age = Column(Integer, index=True)

