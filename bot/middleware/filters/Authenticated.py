from aiogram.filters import Filter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.util import await_only

from bot.usecases.check_authentication import user_is_head_manager, user_is_authenticated


class Authenticated(Filter):
    def __init__(self, session_maker: async_sessionmaker):
        self.session_maker = session_maker

    async def __call__(self, msg: Message) -> bool:
        user_account_id = msg.from_user.id

        async with self.session_maker() as session:
            return await user_is_authenticated(user_account_id, session)