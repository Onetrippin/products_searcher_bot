import json

from utils.constants import FILTERS, ADDITIONAL_FILTERS
from data import DatabaseConnection
from bot import user_queries


def get_formatted_filters(filters: dict) -> dict:
    formatted_filters = {}
    for key, value in filters.items():
        formatted_filters[key] = {
            'params': {item: False for item in value},
            'any_selected': False
        }
    return formatted_filters

async def form_filters(db: DatabaseConnection, chat_id: int) -> dict:
    last_filters = await db.execute('SELECT filters FROM filters WHERE chat_id = ? ORDER BY id DESC LIMIT 1',
                                     (chat_id,))
    if isinstance(last_filters, int) or not last_filters[0]:
        all_filters = FILTERS.copy()
        return get_formatted_filters(all_filters)
    return json.loads(last_filters[0][0])

async def get_filters_by_product_type(db: DatabaseConnection, product_type: str) -> dict:
    all_filters = ADDITIONAL_FILTERS.copy()
    category_id, max_price, min_price = (await db.execute('''
    SELECT id, max_price, min_price
    FROM categories
    WHERE name = ?
    ''', (product_type,)))[0]
    brands = [item[0] for item in (await db.execute('''
    SELECT name
    FROM categories_brands
    WHERE category_id = ?
    ''', (category_id,)))]
    params_info = await db.execute('''
    SELECT id, name
    FROM categories_params
    WHERE category_id = ?
    ''', (category_id,))
    params_ids = [result[0] for result in params_info]
    placeholders = ', '.join('?' for _ in params_ids)
    params_values = await db.execute(f'''
    SELECT param_id, name
    FROM params_values
    WHERE param_id IN ({placeholders})
    ''', tuple(params_ids))
    all_filters['Бренд'] = brands
    all_filters['Цена'] = get_prices_ranges(min_price, max_price)
    for param_id, param_name in params_info:
        all_filters[param_name] = [param_value[1] for param_value in params_values if param_value[0] == param_id]
    return all_filters

def get_prices_ranges(min_price: int, max_price: int) -> list:
    range_coef = 0.5
    lower_limit = 0
    upper_limit = custom_round(min_price * (1 + 0.8))
    prices = []
    while max_price / 2.5 > lower_limit:
        prices.append(f'{lower_limit}-{upper_limit}')
        lower_limit = upper_limit + 1
        upper_limit *= (1 + range_coef)
        upper_limit = custom_round(upper_limit)
    else:
        prices.append(f'{upper_limit + 1}-∞')
    return prices

def custom_round(number: int | float) -> int:
    number = int(number)
    if number <= 3000:
        return round(number, -2)
    elif number <= 30000:
        return round(number, -3)
    elif number <= 300000:
        return round(number, -4)
    return round(number, -5)

async def actualize_filters(db: DatabaseConnection, chat_id: int, is_type_filter: bool = False) -> None:
    filters = user_queries.get(chat_id).get('filters')
    if not filters.get('Тип').get('any_selected'):
        filters = {filter_: data for filter_, data in filters.items() if filter_ in ['Магазин', 'Тип']}
    else:
        product_types = filters.get('Тип').get('params')
        for product_type, value in product_types.items():
            if value:
                now_product_type = product_type
                break
        else:
            now_product_type = 'Смартфон'
        all_filters = await get_filters_by_product_type(db, now_product_type)
        filters = {**{'Магазин': filters.get('Магазин'), 'Тип': filters.get('Тип')},
                   **{filter_: data for filter_, data in filters.items() if filter_ in all_filters.keys()},
                   **{filter_: data for filter_, data in all_filters.items() if filter_ not in filters.keys()}} \
            if not is_type_filter else {**{'Магазин': filters.get('Магазин'), 'Тип': filters.get('Тип')},
                                        **get_formatted_filters(all_filters)}
    user_queries[chat_id]['filters'] = filters
