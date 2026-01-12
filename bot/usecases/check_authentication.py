import logging
import os
from typing import Optional

import jwt
from redis import Redis

from sqlalchemy import text, select, exists
from sqlalchemy.ext.asyncio.session import AsyncSession

from models import Tutor

logger = logging.getLogger(__name__)

def user_is_head_manager(user_account_id: int) -> bool:
    head_manager_id = int(os.getenv("HEAD_MANAGER_ID"))

    if head_manager_id == user_account_id:
        return True

    return False


async def user_is_authenticated(user_account_id: int, db_session: AsyncSession) -> bool:
    # Возможное место для ускорения бота. Сейчас на каждое сообщение идет запрос в базу на проверку
    # существования юзера. Можно кешировать проверенных юзеров

    statement = select(
        exists().where(Tutor.account_id == user_account_id)
    )

    res = await db_session.execute(statement)

    return bool(res.scalar()) or user_is_head_manager(user_account_id)


def code_is_valid(code: str) -> Optional[str]:
    try:
        jwt.decode(code, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return None
    except jwt.ExpiredSignatureError:
        return "Время регистрации истекло. Запросите новый код и запустите регистрацию сначала"

    except jwt.InvalidSignatureError:
        logger.warning("Подпись регистрационного токена не валидна")

    except jwt.PyJWTError:
        return "Сообщение не является регистрационным токеном"


async def code_already_used(code: str, redis_client: Redis) -> bool:
    owner = await redis_client.get(code)

    if not owner:
        return False

    logger.warning("Попытка входа с уже использованным токеном. "
                   "Под этим токеном ранее регистрировался юзер с id=[%s]",
                   owner.decode())
    return True
