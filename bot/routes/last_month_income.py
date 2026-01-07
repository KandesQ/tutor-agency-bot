from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from bot.dependencies import async_session_local
from bot.usecases.get_last_month_income import get_last_month_income


last_month_income_router = Router()


@last_month_income_router.message(Command("last_month_income"))
async def last_month_income(message: Message):

    tutor_account_id = message.from_user.id
    async with async_session_local() as session:
        res = await get_last_month_income(tutor_account_id, session)

    await message.answer(
        f"Доход за предыдущий месяц составил: {res} ₽",
        parse_mode=ParseMode.HTML
    )