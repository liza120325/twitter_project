import pytest
from app.app import app
from app.schemas import UserOut, TweetOut, TweetIn, MediaOut, DoUndoLike, TweetId, MediaIn, Follow, FollowUser, TweetDelete, TweetsByFollowing, Likes, TweetInfo, Author



# @pytest.mark.asyncio
# async def test_get_any_user(client, db_session):
#     query_parameters = {"api_key": 'hobbit'}
#     response = await app.get('/api/users/1', params=query_parameters)
#     data = response.json()
#     assert response.status_code == 200
#     assert data == {
#         "result": "true",
#         "user": {
#             "id": 1,
#             "name": 'Frodo Baggins',
#             "followers": [{"id": 2, "name": 'Legolas Greenleaf'},
#                           {"id": 3, "name": 'Gandalf the Grey'}],
#             "following": [{"id": 2, "name": 'Legolas Greenleaf'}],
#         },
#     }



# @pytest.mark.asyncio
# async def test_post_new_tweet():
#     async with AsyncClient(transport=ASGITransport(app=app),
#                            base_url='http://test') as ac:
#         response = await app.post('/api/tweets', json={'api_key': 'test', 'tweet': })
#         data = response.json()
#         assert response.status_code == 200
#         assert data == {"result": "true", "tweet_id": 1}