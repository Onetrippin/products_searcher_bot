from aiogram import types, F
from aiogram.filters import Command

from utils import (start_message, help_message, saved_message, history_message, search_message, other_message,
                   main_menu_keyboard, navigation_inline_keyboard)
from . import router

@router.message(Command('start'))
async def start_command_handler(message: types.Message) -> None:
    await message.answer(
        start_message(message),
        reply_markup=main_menu_keyboard()
    )

@router.message(Command('help'))
@router.message(F.text.lower() == '❓ помощь')
async def help_command_handler(message: types.Message) -> None:
    await message.answer(
        help_message()
    )

@router.message(F.text.lower() == '⭐ избранное')
async def saved_command_handler(message: types.Message) -> None:
    await message.answer(
        saved_message(message),
        reply_markup=navigation_inline_keyboard('saved', 1, 30)
    )

@router.message(F.text.lower() == '🕒 история поиска')
async def history_command_handler(message: types.Message) -> None:
    await message.answer(
        history_message(message)
    )

@router.message(F.text.lower() == '🔎 искать товары')
async def search_command_handler(message: types.Message) -> None:
    await message.answer(
        search_message(message)
    )

@router.message(F.text)
async def other_message_handler(message: types.Message) -> None:
    await message.answer(
        other_message(),
        reply_markup=main_menu_keyboard()
    )