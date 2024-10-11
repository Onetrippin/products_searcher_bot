from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from utils import start_message, help_message

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