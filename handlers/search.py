import asyncio
import logging

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from curl_cffi.requests import AsyncSession

from . import router
from services import UserData, SourceManager, load_or_set_filters, extract_selected_filters
from utils import (product_page, product_page_keyboard, link_message, link_keyboard, main_menu_keyboard,
                   products_search_result_page, page_navigation_keyboard)
from utils.constants import DELAY_BETWEEN_API_REQUESTS, SEARCH_LINES_PER_PAGE
from utils.translator import SHOPS_NORMAL_TO_SHORT
from data.user_queries import user_queries
from shops import (ozon_search, wb_search, mvideo_search, rbt_search, citilink_search, eldorado_search,
                   megamarket_search, aliexpress_search, onlinetrade_search)
from data import DatabaseConnection, add_to_db, load_products_to_db, log_search_and_product_view


@router.inline_query(lambda query: True)
@add_to_db
@load_or_set_filters
async def inline_search(query: types.InlineQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    chat_type = query.chat_type
    if (not user_queries.get(query.from_user.id, {}).get('filters') or
            not any([data.get('any_selected') for category, data in user_queries.get(query.from_user.id, {}).get('filters', {}).items()])):
        switch_button = types.InlineQueryResultsButton(text='Настроить фильтры', start_parameter=f'filters-{chat_type}')
    else:
        switch_button = types.InlineQueryResultsButton(text='Изменить настроенные фильтры', start_parameter=f'filters-{chat_type}')
    user_queries.setdefault(query.from_user.id, {})['need_switch'] = None
    if len(query.query) < 3:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id='few_characters',
                    title='Подсказка',
                    input_message_content=types.InputTextMessageContent(
                        message_text='Для начала поиска введи <b>хотя бы 3</b> символа',
                        disable_web_page_preview=True
                    ),
                    description='Для начала поиска введи хотя бы 3 символа',
                    thumbnail_url='https://img.icons8.com/?size=100&id=63684&format=png&color=000000',
                    button=switch_button
                )
            ],
            cache_time=15,
            button=switch_button
        )
        return
    elif len(query.query) > 70:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id='many_characters',
                    title='Подсказка',
                    input_message_content=types.InputTextMessageContent(
                        message_text='<b>Слишком длинный</b> запрос, ищи более конкретно',
                        disable_web_page_preview=True
                    ),
                    description='Слишком длинный запрос, ищи более конкретно',
                    thumbnail_url='https://img.icons8.com/?size=100&id=63684&format=png&color=000000'
                )
            ],
            cache_time=15,
            button=switch_button
        )
        return
    user_id = query.from_user.id
    new_query = query.query
    user_queries[user_id] = user_queries.setdefault(user_id, {})
    user_queries[user_id]['query'] = [new_query, None]
    user_queries[user_id]['session'] = AsyncSession(impersonate='chrome123') if not user_queries[user_id].get('session')\
        else user_queries[user_id]['session']
    if user_queries[user_id]['query'][1] is not None:
        user_queries[user_id]['query'][1].cancel()
    user_queries[user_id]['query'][1] = asyncio.create_task(send_query_with_delay(query,
                                                                                  user_queries[user_id]['session'],
                                                                                  switch_button,
                                                                                  logger,
                                                                                  db))

async def send_query_with_delay(query: types.InlineQuery, session: AsyncSession, switch_button: types.InlineQueryResultsButton,
                                logger: logging.Logger, db: DatabaseConnection) -> None:
    await asyncio.sleep(DELAY_BETWEEN_API_REQUESTS if not query.offset else 0)
    results = []
    results_per_page = 50
    current_page = int(query.offset) if query.offset else 0
    if not query.offset:
        filters = extract_selected_filters(query.from_user.id)
        sources = [
            SourceManager(ozon_search, session, query.query, 'ozon', filters),
            SourceManager(wb_search, session, query.query, 'wb', filters),
            SourceManager(mvideo_search, session, query.query, 'mvideo', filters),
            SourceManager(citilink_search, session, query.query, 'citilink', filters),
            SourceManager(rbt_search, session, query.query, 'rbt', filters),
            SourceManager(eldorado_search, session, query.query, 'eldorado', filters),
            SourceManager(megamarket_search, session, query.query, 'megamarket', filters),
            SourceManager(aliexpress_search, session, query.query, 'aliexpress', filters),
            SourceManager(onlinetrade_search, session, query.query, 'onlinetrade', filters)
        ]
        if user_queries.get(query.from_user.id, {}).get('filters', {}).get('Магазин').get('any_selected'):
            shops_filter = list(map(lambda shop_name: SHOPS_NORMAL_TO_SHORT.get(shop_name, shop_name),
                                    [param for param, value in user_queries.get(query.from_user.id).get(
                                        'filters').get('Магазин').get('params').items() if value]))
            filtered_sources = [source for source in sources if source.name in shops_filter]
            sources = filtered_sources
        user_queries[query.from_user.id]['data'] = UserData(sources=sources)
        await user_queries[query.from_user.id]['data'].fill_heap()
    products = await user_queries[query.from_user.id]['data'].get_next_batch(results_per_page)
    product_ids, product_uuids = await load_products_to_db(db, products)
    all_products = []
    for i, product in enumerate(products):
        all_products.append({
            'id': str(product_ids[i]),
            'uuid': product_uuids[i],
            'link': product.get('link'),
            'page_link': f'https://t.me/product_searcher_bot?start=product_page={product_uuids[i]}',
            'product_name': product.get('title'),
            'product_full_name': product.get('full_title'),
            'best_price': product.get('price'),
            'best_price_shop': product.get('shop'),
            'product_image': product.get('image'),
            'all_offers': [{'price': 39682, 'shop': 'Wildberries'},
                           {'price': 40002, 'shop': 'Wildberries'},
                           {'price': 40142, 'shop': 'Wildberries'}]
        })
    user_queries[query.from_user.id]['now_products'] = user_queries[query.from_user.id].setdefault('now_products', [])
    if user_queries[query.from_user.id]['now_products'] and current_page == 0:
        user_queries[query.from_user.id]['now_products'] = []
    user_queries[query.from_user.id]['now_products'].extend(all_products)
    if current_page == 0:
        results.append(types.InlineQueryResultArticle(
            id='search',
            title=f'Поиск "{query.query}"',
            input_message_content=types.InputTextMessageContent(
                message_text=products_search_result_page(query.query,
                                                         user_queries[query.from_user.id]['now_products'][:SEARCH_LINES_PER_PAGE]),
                disable_web_page_preview=True
            ),
            reply_markup=page_navigation_keyboard('search',
                                                  len(user_queries[query.from_user.id]['now_products']),
                                                  query=query.query),
            description='Ты увидишь все товары найденные по введённому запросу',
            thumbnail_url='https://img.icons8.com/color/search',
        ))
        results_per_page -= 1
    start_index = 0
    end_index = min(results_per_page, len(products))
    for i in range(start_index, end_index):
        results.append(types.InlineQueryResultArticle(
            id=all_products[i]['id'],
            title=all_products[i]['product_name'],
            input_message_content=types.InputTextMessageContent(
                message_text=product_page(all_products[i]),
                disable_web_page_preview=True
            ),
            reply_markup=product_page_keyboard(query.from_user.id, all_products[i]['id'], all_products[i]['uuid'], False),
            description=f'Лучшая цена {all_products[i]["best_price"]} в магазине {all_products[i]["best_price_shop"]}',
            thumbnail_url=all_products[i]['product_image'],
        ))
    next_offset = current_page + 1
    await query.answer(results,
                       next_offset=str(next_offset),
                       cache_time=15,
                       is_personal=True,
                       button=switch_button
                       )

@router.chosen_inline_result(lambda result: result.result_id not in ['few_characters', 'many_characters'])
async def chosen_result_handler(chosen_result: types.ChosenInlineResult, logger: logging.Logger, db: DatabaseConnection):
    chat_id = chosen_result.from_user.id
    result_id = chosen_result.result_id
    logger.debug(f'я задетектил {result_id}')
    if result_id == 'search':
        await log_search_and_product_view(db, chat_id, 'search', chosen_result.query)
    else:
        await log_search_and_product_view(db, chat_id, 'product', result_id)


class LinkStates(StatesGroup):
    waiting_for_link = State()

@router.callback_query(lambda call: call.data == 'link')
@add_to_db
@load_or_set_filters
async def input_link(callback_query: types.CallbackQuery, state: FSMContext, logger: logging.Logger, db: DatabaseConnection) -> None:
    await callback_query.message.answer(
        link_message(),
        reply_markup=link_keyboard()
    )
    await state.set_state(LinkStates.waiting_for_link)

@router.message(StateFilter(LinkStates.waiting_for_link))
@add_to_db
@load_or_set_filters
async def handle_link(message: types.Message, state: FSMContext, logger: logging.Logger, db: DatabaseConnection) -> None:
    if message.text.lower() == "отменить ввод":
        await message.answer(
            'Ввод ссылки отменён',
            reply_markup=main_menu_keyboard()
        )
        await state.clear()
        return
    if message.entities and any(entity.type == 'url' for entity in message.entities):
        await message.answer(
            f'Ты ввёл ссылку: {message.text}'
            '\n'
            '(потом здесь будет страница товара со всеми найденными аналогами в других магазинах)',
            reply_markup=main_menu_keyboard()
        )
        await state.clear()
    else:
        await message.answer('Необходимо ввести ссылку. Попробуйте ещё раз.')