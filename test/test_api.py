import json
import os
from pathlib import Path
from typing import Annotated

import pytest
from fastapi import Header
from my_app.crud import get_my_profile

CONTENT_TYPE = "Content-Type"
APP_JSON = "application/json"


@pytest.mark.asyncio
async def test_func_get_my_profile(db_session):
    api_key: Annotated[str, Header()] = "hobbit"
    user_profile = await get_my_profile(api_key, db_session)
    assert user_profile.name == "Frodo Baggins"


@pytest.mark.asyncio
async def test_get_my_profile(client, db_session, mock_async_session):
    query_parameters = {"api-key": "hobbit"}
    response = await client.get("/api/users/me", headers=query_parameters)
    data = response.json()
    assert response.status_code == 200
    assert data == {
        "result": True,
        "user": {
            "id": 1,
            "name": "Frodo Baggins",
            "followers": [{"id": 2, "name": "Legolas Greenleaf"}],
            "following": [
                {"id": 2, "name": "Legolas Greenleaf"},
                {"id": 3, "name": "Gandalf the Grey"},
            ],
        },
    }


@pytest.mark.asyncio
async def test_get_any_user(client, db_session, mock_async_session):
    response = await client.get("/api/users/2")
    data = response.json()
    assert response.status_code == 200
    assert data == {
        "result": True,
        "user": {
            "id": 2,
            "name": "Legolas Greenleaf",
            "followers": [{"id": 1, "name": "Frodo Baggins"}],
            "following": [{"id": 1, "name": "Frodo Baggins"}],
        },
    }


@pytest.mark.asyncio
async def test_get_all_tweets(client, db_session, mock_async_session):
    query_parameters = {"api-key": "hobbit"}
    response = await client.get("/api/tweets", headers=query_parameters)
    data = response.json()
    assert response.status_code == 200
    assert len(data["tweets"]) == 3


@pytest.mark.asyncio
async def test_post_new_tweet(client, db_session, mock_async_session):
    response = await client.post(
        "/api/tweets",
        content=json.dumps(
            {"tweet_data": "And you have my bow", "tweet_media_ids": []}
        ),
        headers={CONTENT_TYPE: APP_JSON, "api-key": "elf"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["tweet_id"] == 4


@pytest.mark.asyncio
async def test_post_follow_user(client, db_session, mock_async_session):
    response = await client.post(
        "/api/users/3/follow",
        headers={CONTENT_TYPE: APP_JSON, "api-key": "elf"},
    )
    data = response.json()
    assert data == {"result": True}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_unfollow_user(client, db_session, mock_async_session):
    response = await client.delete(
        "/api/users/3/follow",
        headers={CONTENT_TYPE: APP_JSON, "api-key": "hobbit"},
    )
    data = response.json()
    assert data == {"result": True}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_send_like(client, db_session, mock_async_session):
    response = await client.post(
        "/api/tweets/1/likes",
        headers={CONTENT_TYPE: APP_JSON, "api-key": "elf"},
    )
    data = response.json()
    assert data == {"result": True}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_unsend_like(client, db_session, mock_async_session):
    response = await client.delete(
        "/api/tweets/3/likes",
        headers={CONTENT_TYPE: APP_JSON, "api-key": "hobbit"},
    )
    data = response.json()
    assert data == {"result": True}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_tweet(client, db_session, mock_async_session):
    response = await client.delete(
        "/api/tweets/1",
        headers={CONTENT_TYPE: APP_JSON, "api-key": "hobbit"},
    )
    data = response.json()
    assert data == {"result": True}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_pictures(client, db_session, mock_async_session):
    response = await client.get(
        "/api/medias/1",
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_new_media(client, db_session, mock_async_session):
    _TEST_ROOT_DIR = Path(__file__).resolve().parents[0]
    image_name = os.path.join(_TEST_ROOT_DIR, "Legolas.jpg")
    image = open(image_name, "rb")

    response = await client.post(
        "/api/medias", files={"file": image}, headers={"api-key": "hobbit"}
    )
    img_data = response.json()
    assert img_data["media_id"] == 2
    assert response.status_code == 200
