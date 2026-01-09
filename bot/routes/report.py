
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import BufferedInputFile


from bot.dependencies import async_session_local
from bot.middleware.filters.Authenticated import Authenticated
from bot.usecases.get_all_students_report import get_all_students_report



report_router = Router()


@report_router.message(Command("report"), Authenticated(async_session_local))
async def report(msg: Message):
    tutor_account_id = msg.from_user.id
    async with async_session_local() as session:
        report_bytes = await get_all_students_report(tutor_account_id, session)

    await msg.answer_document(
        document=BufferedInputFile(
            file=report_bytes,
            filename="Оплаты учеников.xlsx"
        )
    )
