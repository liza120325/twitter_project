from typing import Annotated

import pytest
from fastapi import Header
from my_app.crud import (get_any_user_profile, get_my_profile,
                         update_tweet_id_in_images)


@pytest.mark.asyncio
async def test_func_get_my_profile(db_session):
    api_key: Annotated[str, Header()] = "hobbit"
    user_profile = await get_my_profile(api_key, db_session)
    assert user_profile.name == "Frodo Baggins"


@pytest.mark.asyncio
async def test_func_get_any_user_profile(db_session):
    user_profile = await get_any_user_profile(2, db_session)
    assert user_profile.name == "Legolas Greenleaf"


@pytest.mark.asyncio
async def test_func_update_tweet_id_in_images(db_session):
    await update_tweet_id_in_images(1, 1, db_session)
    assert True
