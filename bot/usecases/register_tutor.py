import datetime
import logging

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from models import Tutor

from redis import Redis


logger = logging.getLogger(__name__)

async def register_tutor(
        user_account_id: int, surname: str,
        name: str, fathers_name: str,
        birth_date: str, one_time_code: str,
        db_session: AsyncSession,
        redis_client: Redis
) -> None | int:

    try:
        birth_date = datetime.datetime.strptime(birth_date, "%d.%m.%Y").date()
    except ValueError:
        logger.error("Некорректная дата рождения для пользователя")
        return -3

    statement = insert(Tutor).values(
        account_id=user_account_id,
        surname=surname,
        name=name,
        fathers_name=fathers_name,
        birthday_date=birth_date
    )

    try:
        await db_session.execute(statement)

        await db_session.commit()
    except IntegrityError as e:
        await db_session.rollback()
        logger.warning("Пользователь %s уже зарегистрирован: %s", user_account_id, e)
        return -1
    except Exception as e:
        await db_session.rollback()
        logger.error("Не удалось сохранить зарегистрировать пользователя %s: %s", user_account_id, e)
        return -2

    await redis_client.set(name=str(one_time_code), value=str(user_account_id), ex=11 * 60)

    return None