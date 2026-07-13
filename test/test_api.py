import pytest
from app.app import app
from app.schemas import UserOut, TweetOut, TweetIn, MediaOut, DoUndoLike, TweetId, MediaIn, Follow, FollowUser, TweetDelete, TweetsByFollowing, Likes, TweetInfo, Author
from app.database import Base, async_session, User, Twits, Likes # Импорты вашей базы


@pytest.mark.asyncio
async def test_get_me(client):
    query_parameters = {"api_key": "hobbit"}
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


@pytest.mark.asyncio
async def test_get_any_user(client):
    response = await client.get('/api/users/1')
    data = response.json()
    print(data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_all_tweets(client):
    query_parameters = {"api_key": "hobbit"}
    response = await client.get('/api/tweets', headers=query_parameters)
    data = response.json()
    print(data)
    assert response.status_code == 200