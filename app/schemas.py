from pydantic import BaseModel, Field

# данные классы используются для валидации и сериализации данных

# избегаем дублирования кода и выносим все общие детали в отдельный класс
class Follow(BaseModel):
    id: int
    name: str


class User(BaseModel):
    id: int
    name: str
    followers: list[Follow] = Field(default_factory=list)
    following: list[Follow] = Field(default_factory=list)


class UserOut(BaseModel):

    result: bool
    user: User

    class Config:
        orm_mode = True


class TweetOut(BaseModel):

    result: bool
    tweet_id: int

    class Config:
        orm_mode = True


class TweetIn(BaseModel):

    context: str
    attachments: list[int] | None


class MediaOut(BaseModel):

    result: bool
    media_id: int

    class Config:
        orm_mode = True