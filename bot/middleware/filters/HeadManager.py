from aiogram.filters import Filter
from aiogram.types import Message

from bot.usecases.check_authentication import user_is_head_manager


class HeadManager(Filter):
    async def __call__(self, msg: Message) -> bool:
        user_account_id = msg.from_user.id
        return user_is_head_manager(user_account_id)