import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from aiohttp import ClientSession

from . import router
from services import get_search_result
from utils import (product_page, product_page_keyboard, link_message, link_keyboard, main_menu_keyboard,
                   products_search_result_page)
from utils.constants import DELAY_BETWEEN_API_REQUESTS
from bot import user_queries


@router.inline_query(lambda query: True)
async def inline_search(query: types.InlineQuery) -> None:
    if len(query.query) < 3:
        await query.answer([types.InlineQueryResultArticle(
            id='few_characters',
            title='Подсказка',
            input_message_content=types.InputTextMessageContent(
                message_text='Для начала поиска введи <b>хотя бы 3</b> символа',
                disable_web_page_preview=True
            ),
            description='Для начала поиска введи хотя бы 3 символа',
            thumbnail_url='https://img.icons8.com/?size=100&id=63684&format=png&color=000000',
        )])
        return
    elif len(query.query) > 70:
        await query.answer([types.InlineQueryResultArticle(
            id='many_characters',
            title='Подсказка',
            input_message_content=types.InputTextMessageContent(
                message_text='<b>Слишком длинный</b> запрос, ищи более конкретно',
                disable_web_page_preview=True
            ),
            description='Слишком длинный запрос, ищи более конкретно',
            thumbnail_url='https://img.icons8.com/?size=100&id=63684&format=png&color=000000',
        )])
        return
    user_id = query.from_user.id
    new_query = query.query
    user_queries[user_id] = user_queries.setdefault(user_id, {})
    user_queries[user_id]['query'] = [new_query, None]
    user_queries[user_id]['session'] = ClientSession() if not user_queries[user_id].get('session')\
        else user_queries[user_id]['session']
    if user_queries[user_id]['query'][1] is not None:
        user_queries[user_id]['query'][1].cancel()
    user_queries[user_id]['query'][1] = asyncio.create_task(send_query_with_delay(query, user_queries[user_id]['session']))

async def send_query_with_delay(query: types.InlineQuery, session: ClientSession) -> None:
    await asyncio.sleep(DELAY_BETWEEN_API_REQUESTS if not query.offset else 0)
    next_links, products = await get_search_result(query.query,
                                                   session,
                                                   query.offset if query.offset else 0,
                                                   user_queries[query.from_user.id].get('links'))
    user_queries[query.from_user.id]['links'] = next_links
    current_page = int(query.offset) if query.offset else 0
    results = []
    results_per_page = 50
    if current_page == 0:
        results.append(types.InlineQueryResultArticle(
            id='search',
            title=f'Поиск "{query.query}"',
            input_message_content=types.InputTextMessageContent(
                # message_text=products_search_result_page(query.query, products),
                message_text='Это сообщение с результатами поиска',
                disable_web_page_preview=True
            ),
            description='Ты увидишь все товары найденные по вводу и сможешь добавить фильтры',
            thumbnail_url='https://img.icons8.com/color/search',
        ))
        results_per_page -= 1
    # start_index = current_page * results_per_page
    start_index = 0
    end_index = min((current_page + 1) * results_per_page, len(products))
    for i in range(start_index, end_index):
        results.append(types.InlineQueryResultArticle(
            id=str(i),
            title=products[i]['product_name'],
            input_message_content=types.InputTextMessageContent(
                message_text=product_page(products[i]),
                disable_web_page_preview=True
            ),
            reply_markup=product_page_keyboard(query.from_user.id, products[i]['product_name']),
            description=f'Лучшая цена {products[i]["best_price"]} в магазине {products[i]["best_price_shop"]}',
            thumbnail_url=products[i]['product_image'],
        ))
    next_offset = current_page + 1
    await query.answer(results, next_offset=str(next_offset))


class LinkStates(StatesGroup):
    waiting_for_link = State()

@router.callback_query(lambda call: call.data == 'link')
async def input_link(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await callback_query.message.answer(
        link_message(),
        reply_markup=link_keyboard()
    )
    await state.set_state(LinkStates.waiting_for_link)

@router.message(StateFilter(LinkStates.waiting_for_link))
async def handle_link(message: types.Message, state: FSMContext) -> None:
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