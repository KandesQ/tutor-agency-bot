import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from dotenv import load_dotenv

from bot.routes.add_tutor import add_tutor_router
from bot.routes.last_month_income import last_month_income_router
from bot.routes.register import register_tutor_router
from bot.routes.report import report_router

load_dotenv()


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )


dp = Dispatcher()

dp.include_router(add_tutor_router)
dp.include_router(report_router)
dp.include_router(register_tutor_router)
dp.include_router(last_month_income_router)


async def main():
    bot_token = os.getenv("BOT_TOKEN")
    bot = Bot(token=bot_token)

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())