from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Поиск')],
            [KeyboardButton(text='Каталог'), KeyboardButton(text='Избранное')],
            [KeyboardButton(text='История поиска'), KeyboardButton(text='Помощь')]
        ],
        resize_keyboard=True
    )

async def start_command_handler(message: types.Message) -> None:
    await message.answer('Это приветственное сообщение после нажатия /start',
                         reply_markup=create_main_menu_keyboard())

def register_start_handlers(dp: Dispatcher):
    dp.message.register(start_command_handler, Command('start'))