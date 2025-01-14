import logging

from aiogram import types, F
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.utils.magic_filter import MagicFilter

from data import DatabaseConnection, add_to_db
from services import get_search_history, get_saved_products
from utils import (start_message, help_message, format_saved_message, format_history_message,
                   search_message, other_message,
                   main_menu_keyboard, page_navigation_keyboard, search_default_keyboard,
                   product_reviews_page, reviews_keyboard)
from . import router


@router.message(Command('help'))
@router.message(F.text.lower() == '❓ помощь')
@add_to_db
async def help_command_handler(message: types.Message, logger: logging.Logger, db: DatabaseConnection) -> None:
    await message.answer(
        help_message()
    )

@router.message(F.text.lower() == '⭐ избранное')
@add_to_db
async def saved_command_handler(message: types.Message, logger: logging.Logger, db: DatabaseConnection) -> None:
    saved_products = await get_saved_products(db, message.chat.id)
    await message.answer(
        format_saved_message(saved_products),
        reply_markup=page_navigation_keyboard('saved', len(saved_products)),
        disable_web_page_preview=True
    )

@router.message(F.text.lower() == '🕒 история поиска')
@add_to_db
async def history_command_handler(message: types.Message, logger: logging.Logger, db: DatabaseConnection) -> None:
    search_history = await get_search_history(db, message.chat.id)
    await message.answer(
        format_history_message(search_history),
        reply_markup=page_navigation_keyboard('history', len(search_history)),
        disable_web_page_preview=True
    )

@router.message(F.text.lower() == '🔎 искать товары')
@add_to_db
async def search_command_handler(message: types.Message, logger: logging.Logger, db: DatabaseConnection) -> None:
    await message.answer(
        search_message(),
        reply_markup=search_default_keyboard()
    )

@router.message(CommandStart(deep_link=True))
@add_to_db
async def deep_link_handler(message: types.Message, logger: logging.Logger, db: DatabaseConnection) -> None:
    args = message.text.split(maxsplit=1)[1]
    if args.startswith('filters'):
        await message.answer(
            search_message(),
            reply_markup=search_default_keyboard()
        )
    elif args.startswith('reviews'):
        product_uuid = args[8:]
        await message.answer(
            product_reviews_page(product_uuid),
            reply_markup=reviews_keyboard(message.chat.id, product_uuid)
        )
    elif args.startswith('product_page'):
        await message.answer(
            'Тут должна быть отправка страницы товара по заданному uuid'
        )
    elif args.startswith('search'):
        await message.answer(
            'Тут должна быть отправка страницы поиска'
        )
    else:
        await start_command_handler(message, logger, db)

@router.message(Command('start'))
@add_to_db
async def start_command_handler(message: types.Message, logger: logging.Logger, db: DatabaseConnection) -> None:
    await message.answer(
        start_message(message),
        reply_markup=main_menu_keyboard()
    )

@router.message(F.text)
@add_to_db
async def other_message_handler(message: types.Message, logger: logging.Logger, db: DatabaseConnection) -> None:
    if not message.via_bot:
        await message.answer(
            other_message(),
            reply_markup=main_menu_keyboard()
        )