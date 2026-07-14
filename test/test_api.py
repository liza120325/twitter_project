import json

import pytest

CONTENT_TYPE = "Content-Type"
APP_JSON = "application/json"


@pytest.mark.asyncio
async def test_get_me(client):
    query_parameters = {"api-key": "hobbit"}
    response = await client.get('/api/users/me', headers=query_parameters)
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data == {
        "result": "true",
        "user": {
            "id": 1,
            "name": 'Frodo Baggins',
            "followers": [{"id": 2, "name": 'Legolas Greenleaf'},
                          {"id": 3, "name": 'Gandalf the Grey'}],
            "following": [{"id": 2, "name": 'Legolas Greenleaf'}],
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