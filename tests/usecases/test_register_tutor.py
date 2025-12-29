import datetime

import pytest

from bot.usecases.create_one_time_code import create_one_time_code
from bot.usecases.register_tutor import register_tutor

from sqlalchemy import select

from models import Tutor


@pytest.mark.asyncio
async def test_register_tutor(db_session, redis_client):
    expected_user = {
        "user_account_id": 1424125,
        "surname": "test",
        "name": "test",
        "fathers_name": "test",
        "birth_date": "01.01.1999",
        "one-time-code": create_one_time_code()
    }

    await register_tutor(
        expected_user["user_account_id"], expected_user["surname"],
        expected_user["name"], expected_user["fathers_name"],
        expected_user["birth_date"], expected_user["one-time-code"],
        db_session, redis_client
    )

    st = select(Tutor).where(Tutor.account_id == expected_user["user_account_id"])
    res = await db_session.execute(st)
    actual_user = res.scalar_one_or_none()

    assert actual_user is not None
    assert actual_user.account_id == expected_user["user_account_id"]
    assert actual_user.surname == expected_user["surname"]
    assert actual_user.name == expected_user["name"]
    assert actual_user.fathers_name == expected_user["fathers_name"]
    assert actual_user.birthday_date == datetime.datetime.strptime(expected_user["birth_date"], "%d.%m.%Y").date()


    user_account_id = await redis_client.get(expected_user["one-time-code"])

    assert user_account_id is not None
    assert int(user_account_id.decode()) == expected_user["user_account_id"]