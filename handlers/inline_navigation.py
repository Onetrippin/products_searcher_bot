import logging

from aiogram import types

from utils import (format_saved_message, page_navigation_keyboard, format_history_message, products_search_result_page)
from services import get_search_history, get_saved_products
from utils.constants import SEARCH_LINES_PER_PAGE
from . import router
from bot import user_queries
from utils.bot_singleton import BotSingleton
from data import DatabaseConnection, add_to_db, load_products_to_db


@router.callback_query(lambda call: call.data.startswith('page_saved'))
@add_to_db
async def saved_page_changer(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    saved_products = await get_saved_products(db, callback_query.message.chat.id)
    _, page_type, current_page, _ = callback_query.data.split('_')
    await callback_query.message.edit_text(
        format_saved_message(saved_products, current_page),
        reply_markup=page_navigation_keyboard(page_type, len(saved_products), int(current_page)),
        disable_web_page_preview=True
    )

@router.callback_query(lambda call: call.data.startswith('page_history'))
@add_to_db
async def history_page_changer(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    _, page_type, current_page, _ = callback_query.data.split('_')
    search_history = await get_search_history(db, callback_query.message.chat.id)
    await callback_query.message.edit_text(
        format_history_message(search_history, current_page),
        reply_markup=page_navigation_keyboard(page_type, len(search_history), int(current_page)),
        disable_web_page_preview=True
    )

@router.callback_query(lambda call: call.data.startswith('page_search'))
@add_to_db
async def search_page_changer(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    _, _, current_page, query = callback_query.data.split('_', 3)
    current_page = int(current_page)
    user_id = callback_query.from_user.id
    products = user_queries.get(user_id, {}).get('now_products', [])
    if (len(products) - current_page * SEARCH_LINES_PER_PAGE) < SEARCH_LINES_PER_PAGE * 2 and len(products) % 50 == 0:
        new_products = await user_queries[user_id]['data'].get_next_batch(50)
        if not new_products:
            current_page = 1
        else:
            _, product_uuids = await load_products_to_db(db, new_products)
            all_products = []
            for i, product in enumerate(new_products):
                all_products.append({
                    'id': product_uuids[i],
                    'uuid': product_uuids[i],
                    'link': product.get('link'),
                    'page_link': f'https://t.me/product_searcher_bot?start=product_page={product_uuids[i]}',
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
@add_to_db
async def page_counter(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    current_page, total_page = callback_query.data.split('_')[1].split('/')
    await callback_query.answer(
        f'Ты смотришь {current_page} страницу из {total_page}',
        show_alert=True
    )

@router.callback_query(lambda call: call.data.startswith('saved_'))
@add_to_db
async def change_saved_status(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    product_id = callback_query.data.split('_')[1]
    product_name = (await db.execute('SELECT name FROM products WHERE id = (?)', (product_id,)))[0][0]
    chat_id = callback_query.from_user.id
    is_saved = True
    if isinstance(await db.execute('SELECT 1 FROM saved WHERE product_id = (?) AND chat_id = (?)',
                     (product_id, chat_id)), int):
        await db.execute('INSERT INTO saved (chat_id, product_id, is_saved) VALUES (?, ?, ?)',
                         (chat_id, product_id, is_saved))
    else:
        is_saved = (await db.execute('''UPDATE saved 
                            SET is_saved = NOT is_saved, change_time = CURRENT_TIMESTAMP 
                            WHERE product_id = ? AND chat_id = ?
                            RETURNING is_saved''',
                         (product_id, chat_id)))[0][0]
    if is_saved:
        await callback_query.answer(
            f'Товар {product_name[:173]} добавлен в избранное'
        )
    else:
        await callback_query.answer(
            f'Товар {product_name[:173]} удалён из избранного'
        )
