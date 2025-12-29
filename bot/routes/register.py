import os

import jwt
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.formatting import Text

from ..dependencies import redis_async_client, async_session_local
from ..usecases.check_authentication import code_is_valid, code_already_used, user_is_authenticated
from ..usecases.validation.registration_data import valid_fullname, valid_birth_date

register_tutor_router = Router()


class Form(StatesGroup):
    fullname = State()
    birth_date = State()
    data_is_correct = State()

    edited_fullname = State()
    edited_birth_date = State()


    registration_token = State()

# TODO: протестировать ручками

@register_tutor_router.message(Command("register"))
async def register(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    async with async_session_local() as session:
        if await user_is_authenticated(user_id, session) or user_id == int(os.getenv("HEAD_MANAGER_ID")):
            await msg.answer("Вы уже зарегистрированы")
            return

    await state.clear()
    await state.set_state(Form.registration_token)

    await msg.answer("Введите одноразовый код")


@register_tutor_router.message(Form.registration_token)
async def process_registration_token(msg: Message, state: FSMContext):
    reg_token = msg.text
    if not code_is_valid(reg_token):
        await msg.answer("Время активации истекло. Запросите новый код")
        return

    if await code_already_used(reg_token, redis_async_client):
        return

    await msg.answer("Код успешно активирован")

    # TODO: Добавить согласие на обработку персональных данных (др). Отдельной фичей/коммитом

    await state.update_data(registration_token=reg_token)
    await state.set_state(Form.fullname)

    await msg.answer((
        "Укажите ваше ФИО __*кириллицей*__ через пробел\n\nПример: *Иванов Иван Иванович*\n\n"
        "При отсутствии отчества укажите только фамилию и имя, в этом же формате"
    ),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@register_tutor_router.message(Form.fullname)
async def process_fullname(msg: Message, state: FSMContext):
    state_data = await state.get_data()

    reg_token = state_data.get("registration_token")
    if not code_is_valid(reg_token):
        await msg.answer("Время активации истекло. Запросите новый код")
        return

    fullname = msg.text.strip()
    if not valid_fullname(fullname):
        await msg.answer(
            (
            "Некорректный ввод\\. ФИО должно состоять из кириллицы и указано через пробел"
            "\nПример: *Иванов Иван Иванович*"
            "\n\nПопробуйте еще раз"
            ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(fullname=fullname)
    await state.set_state(Form.birth_date)

    await msg.answer((
        "Ваша дата рождения в формате: день\\.месяц\\.год\nПример: *01\\.12\\.1990*"
    ),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@register_tutor_router.message(Form.birth_date)
async def process_birth_date(msg: Message, state: FSMContext):
    state_data = await state.get_data()

    reg_token = state_data.get("registration_token")
    if not code_is_valid(reg_token):
        await msg.answer("Время активации истекло. Запросите новый код")
        return

    birth_date = msg.text.strip()
    if not valid_birth_date(birth_date):
        await msg.answer((
            "Некорректный ввод\\. Формат даты рождения должен быть представлен в виде число\\.месяц\\.год"
            "\nПример: *01\\.12\\.1990*"
            "\n\nПопробуйте еще раз"
        ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(birth_date=birth_date)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # TODO: сделать методы колбеков
        [InlineKeyboardButton(text="Изменить ФИО ✏️", callback_data="edit_fullname")],
        [InlineKeyboardButton(text="Изменить Дату Рождения 📅", callback_data="edit_birth_date")],
        [InlineKeyboardButton(text="Подтвердить ✅", callback_data="process_confirmed_data")]
        # TODO: в этом колбеке обязательно сделать state.finish()
    ])

    fullname = state_data.get("fullname")
    await msg.answer(
        (
            "Подтвердите введенные данные\n\n"
            f"*ФИО*: {fullname}\n"
            f"*Дата рождения*: {Text(birth_date).as_markdown()}\n\n"
            "*Обратите внимание*: указанные данные используются для проведения финансовых операций в рамках сервиса\\."
            "Пожалуйста, убедитесь в их корректности перед подтверждением"
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=keyboard
    )
