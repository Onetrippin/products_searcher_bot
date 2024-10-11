from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from utils import start_message, help_message, saved_message, history_message, search_message

router = Router()

def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Поиск')],
            [KeyboardButton(text='Каталог'), KeyboardButton(text='Избранное')],
            [KeyboardButton(text='История поиска'), KeyboardButton(text='Помощь')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@router.message(Command('start'))
async def start_command_handler(message: types.Message) -> None:
    await message.answer(
        start_message(message),
        reply_markup=create_main_menu_keyboard()
    )

@router.message(Command('help'))
@router.message(F.text.lower() == 'помощь')
async def help_command_handler(message: types.Message) -> None:
    await message.answer(
        help_message()
    )

@router.message(F.text.lower() == 'избранное')
async def saved_command_handler(message: types.Message) -> None:
    await message.answer(
        saved_message(message)
    )

@router.message(F.text.lower() == 'история поиска')
async def history_command_handler(message: types.Message) -> None:
    await message.answer(
        history_message(message)
    )

@router.message(F.text.lower() == 'поиск')
async def search_command_handler(message: types.Message) -> None:
    await message.answer(
        search_message(message)
    )