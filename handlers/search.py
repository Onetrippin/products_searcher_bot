from aiogram import types

from . import router
from data import get_search_result
from utils import product_page, product_page_keyboard

@router.inline_query(lambda query: True)
async def inline_search(query: types.InlineQuery):
    products = await get_search_result(query.query)
    current_page = int(query.offset) if query.offset else 0
    results = []
    results_per_page = 50
    start_index = current_page * results_per_page
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
            thumbnail_url='https://img.icons8.com/color/search',
        ))
    next_offset = current_page + 1
    await query.answer(results, next_offset=str(next_offset))