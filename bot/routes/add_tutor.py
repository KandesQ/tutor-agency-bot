from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import Text
from dotenv import load_dotenv

from bot.middleware.filters.HeadManager import HeadManager
from bot.usecases.create_one_time_code import create_one_time_code, get_one_time_code_expiration_in_sec

load_dotenv()

add_tutor_router = Router()


@add_tutor_router.message(Command("add_tutor"), HeadManager())
async def add_tutor(msg: Message):
    code = create_one_time_code()

    md2_code = Text(code).as_markdown()


    await msg.answer(
        (f"Это __*одноразовый*__ код для создания аккаунта\n\n"
        "Отправьте его боту как *первое сообщение* и пройдите регистрацию\\. "
        "При утере обращайтесь к менеджеру, выдавшему код\n\n"
        f"Код действителен в течении {int(get_one_time_code_expiration_in_sec() / 60)} минут: *||{md2_code}||*"),
        parse_mode=ParseMode.MARKDOWN_V2
    )