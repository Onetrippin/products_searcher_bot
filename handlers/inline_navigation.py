from aiogram import types

from utils import (format_saved_message, page_navigation_keyboard, format_history_message, products_search_result_page)
from services import get_search_history, get_saved_products
from utils.constants import SEARCH_LINES_PER_PAGE
from . import router
from bot import user_queries
from utils.bot_singleton import BotSingleton
from utils.other import get_data_info


@router.callback_query(lambda call: call.data.startswith('page_saved'))
async def saved_page_changer(callback_query: types.CallbackQuery, data: dict) -> None:
    logger, data = get_data_info(data)
    saved_products = await get_saved_products(callback_query.message.chat.id)
    _, page_type, current_page, _ = callback_query.data.split('_')
    await callback_query.message.edit_text(
        format_saved_message(saved_products, current_page),
        reply_markup=page_navigation_keyboard(page_type, len(saved_products), int(current_page)),
        disable_web_page_preview=True
    )

@router.callback_query(lambda call: call.data.startswith('page_history'))
async def history_page_changer(callback_query: types.CallbackQuery, data: dict) -> None:
    logger, data = get_data_info(data)
    search_history = await get_search_history(callback_query.message.chat.id)
    _, page_type, current_page, _ = callback_query.data.split('_')
    await callback_query.message.edit_text(
        format_history_message(search_history, current_page),
        reply_markup=page_navigation_keyboard(page_type, len(search_history), int(current_page)),
        disable_web_page_preview=True
    )

@router.callback_query(lambda call: call.data.startswith('page_search'))
async def search_page_changer(callback_query: types.CallbackQuery, data: dict) -> None:
    logger, data = get_data_info(data)
    _, _, current_page, query = callback_query.data.split('_', 3)
    current_page = int(current_page)
    user_id = callback_query.from_user.id
    products = user_queries.get(user_id, {}).get('now_products', [])
    if (len(products) - current_page * SEARCH_LINES_PER_PAGE) < SEARCH_LINES_PER_PAGE * 2 and len(products) % 50 == 0:
        new_products = await user_queries[user_id]['data'].get_next_batch(50)
        if not new_products:
            current_page = 1
        else:
            all_products = []
            for product in new_products:
                all_products.append({
                    'product_name': product.get('title'),
                    'product_full_name': product.get('full_title'),
                    'best_price': product.get('price'),
                    'best_price_shop': product.get('shop'),
                    'product_image': product.get('image'),
                    'all_offers': [{'price': 0, 'shop': None},
                                   {'price': 0, 'shop': None},
                                   {'price': 0, 'shop': None}]
                })
            user_queries[user_id]['now_products'].extend(all_products)
    current_page_products = user_queries[user_id]['now_products'] \
        [(current_page - 1) * SEARCH_LINES_PER_PAGE:current_page * SEARCH_LINES_PER_PAGE]
    bot = await BotSingleton.instance()
    await bot.edit_message_text(
        products_search_result_page(query, current_page_products),
        inline_message_id=callback_query.inline_message_id,
        reply_markup=page_navigation_keyboard('search',
                                              len(user_queries[callback_query.from_user.id]['now_products']),
                                              current_page,
                                              query),
        disable_web_page_preview=True
    )

@router.callback_query(lambda call: call.data.startswith('counter_'))
async def page_counter(callback_query: types.CallbackQuery, data: dict) -> None:
    logger, data = get_data_info(data)
    current_page, total_page = callback_query.data.split('_')[1].split('/')
    await callback_query.answer(
        f'Ты смотришь {current_page} страницу из {total_page}',
        show_alert=True
    )

@router.callback_query(lambda call: call.data.startswith('saved_'))
async def change_saved_status(callback_query: types.CallbackQuery, data: dict) -> None:
    logger, data = get_data_info(data)
    await callback_query.answer(
        f'Товар {callback_query.data.split("_")[1]} добавлен в избранное'
    )