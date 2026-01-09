import os

import jwt
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.formatting import Text

from ..dependencies import redis_async_client, async_session_local
from ..usecases.check_authentication import code_is_valid, code_already_used, user_is_authenticated
from ..usecases.register_tutor import register_tutor
from ..usecases.validation.user_input import valid_fullname, valid_birth_date

register_tutor_router = Router()


class Form(StatesGroup):
    fullname = State()
    birth_date = State()

    # Используются как триггер для коллбэков. Ничего не хранят
    edited_fullname = State()
    edited_birth_date = State()

    one_time_code = State()



@register_tutor_router.message(Command("register"))
async def register(msg: Message, state: FSMContext):
    user_account_id = msg.from_user.id
    async with async_session_local() as session:
        if await user_is_authenticated(user_account_id, session) or user_account_id == int(os.getenv("HEAD_MANAGER_ID")):
            await msg.answer("Вы уже зарегистрированы")
            return

    await state.clear()
    await state.set_state(Form.one_time_code)

    await msg.answer("Введите код регистрации")


@register_tutor_router.message(Form.one_time_code)
async def process_one_time_code(msg: Message, state: FSMContext):
    one_time_code = msg.text.strip()

    # TODO: если пользователь вводит не регистрационный код - выполняется это условие. Перед этим кодом нужно
    #  добавить проверку, что сообщение является регистрационным кодом
    if not code_is_valid(one_time_code):
        await msg.answer("Время регистрации истекло. Запросите новый код и запустите регистрацию сначала")
        await state.set_state(None)
        return

    if await code_already_used(one_time_code, redis_async_client):
        return

    await msg.answer("Код успешно активирован")

    # TODO: Добавить согласие на обработку персональных данных (др). Отдельной фичей/коммитом

    await state.update_data(one_time_code=one_time_code)
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

    one_time_code = state_data.get("one_time_code")
    if not code_is_valid(one_time_code):
        await msg.answer("Время регистрации истекло. Запросите новый код и запустите регистрацию сначала")
        await state.set_state(None)
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

    one_time_code = state_data.get("one_time_code")
    if not code_is_valid(one_time_code):
        await msg.answer("Время регистрации истекло. Запросите новый код и запустите регистрацию сначала")
        await state.set_state(None)
        return

    birth_date = msg.text.strip()
    if not valid_birth_date(birth_date):
        await msg.answer((
            "Некорректный ввод\\. Формат даты должен быть представлен в виде число\\.месяц\\.год"
            "\nПример: *01\\.12\\.1990*"
            "\n\nПопробуйте еще раз"
        ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(birth_date=birth_date)

    await _confirm_data(state_data.get("fullname"), birth_date, msg, state)


@register_tutor_router.callback_query(F.data == "edit_fullname")
async def edit_fullname_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    await callback.message.answer(
        "Укажите исправленное ФИО __*кириллицей*__ через пробел\n\nПример: *Иванов Иван Иванович*\n\n"
            "При отсутствии отчества укажите только фамилию и имя, в этом же формате",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    await state.set_state(Form.edited_fullname)
    await callback.answer()


@register_tutor_router.message(Form.edited_fullname)
async def edit_fullname(msg: Message, state: FSMContext):
    state_data = await state.get_data()

    one_time_code = state_data.get("one_time_code")
    if not code_is_valid(one_time_code):
        await msg.answer("Время регистрации истекло. Запросите новый код и запустите регистрацию сначала")
        await state.set_state(None)
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

    await _confirm_data(fullname, state_data.get("birth_date"), msg, state)


@register_tutor_router.callback_query(F.data == "edit_birth_date")
async def edit_birth_date_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    await callback.message.answer((
        "Ваша исправленная дата рождения в формате: день\\.месяц\\.год\nПример: *01\\.12\\.1990*"
    ),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    await state.set_state(Form.edited_birth_date)
    await callback.answer()


@register_tutor_router.message(Form.edited_birth_date)
async def edit_birth_date(msg: Message, state: FSMContext):
    state_data = await state.get_data()

    one_time_code = state_data.get("one_time_code")
    if not code_is_valid(one_time_code):
        await msg.answer("Время регистрации истекло. Запросите новый код и запустите регистрацию сначала")
        await state.set_state(None)
        return

    birth_date = msg.text.strip()
    if not valid_birth_date(birth_date):
        await msg.answer((
            "Некорректный ввод\\. Формат даты должен быть представлен в виде число\\.месяц\\.год"
            "\nПример: *01\\.12\\.1990*"
            "\n\nПопробуйте еще раз"
        ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(birth_date=birth_date)

    await _confirm_data(state_data.get("fullname"), birth_date, msg, state)


@register_tutor_router.callback_query(F.data == "process_confirmed_data")
async def process_confirmed_data_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    state_data = await state.get_data()

    user_account_id = callback.from_user.id
    surname, name, fathers_name = state_data.get("fullname").split()
    birth_date = state_data.get("birth_date")
    one_time_code = state_data.get("one_time_code")

    if not code_is_valid(one_time_code):
        await callback.message.answer("Время регистрации истекло. Запросите новый код и запустите регистрацию сначала")
        return

    async with async_session_local() as session:
        error_code = await register_tutor(
            user_account_id, surname, name, fathers_name,
            birth_date, one_time_code, session,
            redis_async_client
        )

    if error_code is not None:
        await callback.message.answer(
            (
            "В данный момент функционал недоступен\\. Попробуйте позже или обратитесь к разработчику\\."
            f"\nКод ошибки: *{Text(error_code).as_markdown()}*"
            ),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await callback.message.answer("Вы успешно зарегистрированы. Доступ к использованию открыт")
    await callback.answer()


async def _confirm_data(fullname: str, birth_date: str, msg: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить ФИО ✏️", callback_data="edit_fullname")],
        [InlineKeyboardButton(text="Изменить Дату Рождения 📅", callback_data="edit_birth_date")],
        [InlineKeyboardButton(text="Подтвердить ✅", callback_data="process_confirmed_data")]
    ])

    await state.set_state(None)

    await msg.answer(
        (
            "Подтвердите введенные данные\n\n"
            f"*ФИО*: {fullname}\n"
            f"*Дата рождения*: {Text(birth_date).as_markdown()}\n\n"
            "*Обратите внимание*: указанные данные используются для проведения финансовых операций в рамках сервиса\\. "
            "Пожалуйста, убедитесь в их корректности перед подтверждением"
        ),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=keyboard
    )