from sqlalchemy import insert

from my_app.database import User, Twits, Likes, user_following, Images # Импорты вашей базы

user_data = [
    {"name": "Frodo Baggins", "api_key": "hobbit"},
    {"name": "Legolas Greenleaf", "api_key": "elf"},
    {"name": "Gandalf the Grey", "api_key": "wizard"}
]

tweet_data = [
    {"context": "I live in Shire", "author": 1},
    {"context": "I am a skilled archer", "author": 2},
    {"context": "You must destroy the ring", "author": 3}
]

likes_data = [
    {"user_id": 1, "user_name": "Frodo Baggins", "tweet_id": 3},
    {"user_id": 2, "user_name": "Legolas Greenleaf", "tweet_id": 3}
]

followed_data = [
    {"i_follow": 1, "i_am_followed": 2},
    {"i_follow": 1, "i_am_followed": 3},
    {"i_follow": 2, "i_am_followed": 1},
]

images_data = [
    {"tweet_id": 1, "path": "./shire.jpeg"}
]


async def create_data(conn):
    await conn.execute(insert(User), user_data)
    await conn.execute(insert(Twits), tweet_data)
    await conn.execute(insert(Likes), likes_data)
    await conn.execute(insert(user_following), followed_data)
    await conn.execute(insert(Images), images_data)






