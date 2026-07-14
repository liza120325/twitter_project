import json
from typing import Annotated
from sqlalchemy import select, update, insert, delete, and_, func, or_
from sqlalchemy.orm import selectinload
from my_app.database import Base, get_db, async_session, User, Twits, Likes
from fastapi import Header
from my_app.crud import get_my_profile
import pytest

CONTENT_TYPE = "Content-Type"
APP_JSON = "application/json"


@pytest.mark.asyncio
async def test_func_get_my_profile(db_session):
    api_key: Annotated[str, Header()] = 'hobbit'
    user_profile = await get_my_profile(api_key, db_session)
    assert user_profile.name == 'Frodo Baggins'



@pytest.mark.asyncio
async def test_get_me(client, db_session, mock_async_session):
    query_parameters = {"api-key": "hobbit"}
    response = await client.get('/api/users/me', headers=query_parameters)
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data == {
        "result": True,
        "user": {
            "id": 1,
            "name": 'Frodo Baggins',
            "followers": [{"id": 2, "name": 'Legolas Greenleaf'}],
            "following": [{"id": 2, "name": 'Legolas Greenleaf'},
                          {"id": 3, "name": 'Gandalf the Grey'}],
        },
    }




# @pytest.mark.asyncio
# async def test_get_any_user(client):
#     response = await client.get('/api/users/1')
#     data = response.json()
#     print(data)
#     assert response.status_code == 200
#
#
# @pytest.mark.asyncio
# async def test_get_all_tweets(client):
#     query_parameters = {"api_key": "hobbit"}
#     response = await client.get('/api/tweets', headers=query_parameters)
#     data = response.json()
#     print(data)
#     assert response.status_code == 200
#
#
# @pytest.mark.asyncio
# async def test_post_new_tweet(client):
#     response = await client.post(
#         "/api/tweets",
#         content=json.dumps(
#             {"tweet_data": "Tweet for test", "tweet_media_ids": []}
#         ),
#         headers={CONTENT_TYPE: APP_JSON, "api_key": "hobbit"},
#     )
#
#     data = response.json()
#     print(data)
#     assert response.status_code == 200