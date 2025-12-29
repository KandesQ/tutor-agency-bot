import datetime
import os

import pytest
from dotenv import load_dotenv

from sqlalchemy import insert
from bot.usecases.check_authentication import user_is_head_manager, user_is_authenticated, code_already_used
from bot.usecases.create_one_time_code import create_one_time_code
from models import Tutor

load_dotenv()

def test_user_is_head_manager():
    head_manager_id = int(os.getenv("HEAD_MANAGER_ID"))
    not_head_manager_id = -1

    assert user_is_head_manager(head_manager_id) is True
    assert user_is_head_manager(not_head_manager_id) is False


@pytest.mark.asyncio
async def test_user_is_authenticated(db_session):
    test_user = {
        "account_id": 124,
        "surname": "test",
        "name": "test",
        "fathers_name": "test",
        "birthday_date": datetime.date(1999, 2, 1),
    }

    st = insert(Tutor).values(
        account_id=test_user["account_id"],
        surname=test_user["surname"],
        name=test_user["name"],
        fathers_name=test_user["fathers_name"],
        birthday_date=test_user["birthday_date"]
    )
    await db_session.execute(st)


    res = await user_is_authenticated(test_user["account_id"], db_session)

    assert res is True


@pytest.mark.asyncio
async def test_user_is_not_authenticated(db_session):
    test_user = {
        "chat_id": 124,
        "surname": "test",
        "name": "test",
        "fathers_name": "test",
        "birthday_date": datetime.date(1999, 2, 1),
    }

    res = await user_is_authenticated(test_user["chat_id"], db_session)

    assert res is False


@pytest.mark.asyncio
async def test_code_already_used(redis_client):
    user_name = "test"
    code = create_one_time_code()

    await redis_client.set(code, user_name)

    res = await code_already_used(code, redis_client)

    assert res is True

@pytest.mark.asyncio
async def test_code_have_not_been_used(redis_client):
    code = create_one_time_code()

    res = await code_already_used(code, redis_client)

    assert res is False