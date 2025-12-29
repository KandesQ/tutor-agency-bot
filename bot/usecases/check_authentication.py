import logging
import os
import jwt
from redis import Redis

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

logger = logging.getLogger(__name__)


# TODO: написать тесты

def user_is_head_manager(user_id: int) -> bool:
    head_manager_id = int(os.getenv("HEAD_MANAGER_ID"))

    if head_manager_id == user_id:
        return True

    return False


async def user_is_authenticated(user_id: int, session: AsyncSession) -> bool:
    # Возможное место для ускорения бота. Сейчас на каждое сообщение идет запрос в базу на проверку
    # существования юзера. Можно кешировать проверенных юзеров


    # TODO:нужно чтобы весь вызывающий код передавал готовую сессию, переделать везде
    res = await session.execute(
        text("SELECT 1 FROM tutors WHERE chat_id = :tutor_chat_id"),
        {"tutor_chat_id": user_id}
    )

    return bool(res.fetchone())


def code_is_valid(code: str) -> bool:
    try:
        jwt.decode(code, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        logger.info("Время активации регистрационного токена истекло")

    except jwt.InvalidSignatureError:
        logger.info("Подпись регистрационного токена не валидна")

    except jwt.PyJWTError:
        logger.info("Сообщение не является регистрационным токеном")

    return False


async def code_already_used(code: str, redis_client: Redis) -> bool:
    owner = await redis_client.get(code)

    if not owner:
        return False

    logger.warning("Попытка входа с уже использованным токеном. "
                   "Под этим токеном ранее регистрировался юзер с chat_id=[%s]",
                   str(owner))
    return True
