from aiogram import types
from aiogram.exceptions import TelegramForbiddenError

from utils import (format_saved_message, page_navigation_keyboard, format_history_message,
                   product_reviews_page, reviews_keyboard)
from data import get_search_history, get_saved_products
from . import router

@router.callback_query(lambda call: call.data.startswith('page_saved'))
async def saved_page_changer(callback_query: types.CallbackQuery) -> None:
    saved_products = await get_saved_products(callback_query.message.chat.id)
    _, page_type, current_page, _ = callback_query.data.split('_')
    await callback_query.message.edit_text(
        format_saved_message(saved_products, current_page),
        reply_markup=page_navigation_keyboard(page_type, len(saved_products), int(current_page)),
        disable_web_page_preview=True
    )

@router.callback_query(lambda call: call.data.startswith('page_history'))
async def history_page_changer(callback_query: types.CallbackQuery) -> None:
    search_history = await get_search_history(callback_query.message.chat.id)
    _, page_type, current_page, _ = callback_query.data.split('_')
    await callback_query.message.edit_text(
        format_history_message(search_history, current_page),
        reply_markup=page_navigation_keyboard(page_type, len(search_history), int(current_page)),
        disable_web_page_preview=True
    )

@router.callback_query(lambda call: call.data.startswith('counter_'))
async def page_counter(callback_query: types.CallbackQuery) -> None:
    current_page, total_page = callback_query.data.split('_')[1].split('/')
    await callback_query.answer(
        f'Ты смотришь {current_page} страницу из {total_page}',
        show_alert=True
    )

@router.callback_query(lambda call: call.data.startswith('saved_'))
async def change_saved_status(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(
        f'Товар {callback_query.data.split("_")[1]} добавлен в избранное'
    )

@router.callback_query(lambda call: call.data.startswith('reviews_'))
async def send_reviews_message(callback_query: types.CallbackQuery) -> None:
    product_name = callback_query.data.split('_')[1]
    try:
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=product_reviews_page(product_name),
            reply_markup=reviews_keyboard(callback_query.from_user.id, product_name)
        )
    except TelegramForbiddenError:
        await callback_query.answer(
            'Напиши /start в боте, чтобы увидеть отзывы для товара',
            show_alert=True
        )