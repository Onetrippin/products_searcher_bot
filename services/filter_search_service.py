from curl_cffi.requests import AsyncSession

from data.user_queries import user_queries
from .search_products_service import SourceManager
from shops import (ozon_search, wb_search, mvideo_search, rbt_search, citilink_search, eldorado_search,
                   megamarket_search, aliexpress_search, onlinetrade_search)
from utils.translator import SHOPS_NORMAL_TO_SHORT


def extract_selected_filters(chat_id: int) -> dict:
    filters = user_queries.get(chat_id).get('filters')
    selected_filters = {filter_: data.get('params') for filter_, data in filters.items() if data.get('any_selected')}
    only_selected_params = {filter_: [param for param, value in params.items() if value] for filter_, params in selected_filters.items()}
    only_selected_params.pop('Магазин', None)
    if only_selected_params.get('Оперативка'):
        for i, value in enumerate(only_selected_params['Оперативка']):
            only_selected_params['Оперативка'][i] = value[:-3]
    if only_selected_params.get('Память'):
        for i, value in enumerate(only_selected_params['Память']):
            if 'ТБ' in value:
                only_selected_params['Память'][i] = value[:-3] + '000'
                continue
            only_selected_params['Память'][i] = value[:-3]
    if only_selected_params.get('Аккумулятор'):
        params = only_selected_params.get('Аккумулятор')
        lower_limit = params[0].split('-')[0] if (params[0].split('-')[0]).isdigit() else '6000'
        upper_limit = params[-1].split()[-2].split('-')[1] if not (params[-1].split()[-2]).isdigit() else 'max'
        only_selected_params['Аккумулятор'] = [lower_limit, upper_limit]
    if only_selected_params.get('Камера'):
        for i, value in enumerate(only_selected_params['Камера']):
            only_selected_params['Камера'][i] = value[:-3]
    if only_selected_params.get('Объем SSD'):
        for i, value in enumerate(only_selected_params['Объем SSD']):
            if 'ТБ' in value:
                only_selected_params['Объем SSD'][i] = value[:-3] + '000'
                continue
            only_selected_params['Объем SSD'][i] = value[:-3]
    if only_selected_params.get('Видеопамять'):
        for i, value in enumerate(only_selected_params['Видеопамять']):
            only_selected_params['Видеопамять'][i] = value[:-3]
    if only_selected_params.get('Цена'):
        params = only_selected_params.get('Цена')
        lower_limit = params[0].split('-')[0]
        upper_limit = params[-1].split('-')[1] if params[-1].split('-')[1].isdigit() else 'max'
        only_selected_params['Цена'] = [lower_limit, upper_limit]
    return only_selected_params

def get_query_if_exists(chat_id: int) -> str:
    if user_queries.get(chat_id, {}).get('filters', {}).get('Тип', {}).get('any_selected'):
        query = (next((param for param, value in user_queries
                     .get(chat_id, {})
                     .get('filters', {})
                     .get('Тип')
                     .get('params')
                     .items() if value), '')).lower()
    else:
        query = ''
    return query

def collect_request_data(session: AsyncSession, chat_id: int, query: str, filters: dict = None, is_group: bool = False) -> list:
    sources = [
        SourceManager(ozon_search, session, query, 'ozon', filters),
        SourceManager(wb_search, session, query, 'wb', filters),
        SourceManager(mvideo_search, session, query, 'mvideo', filters),
        SourceManager(citilink_search, session, query, 'citilink', filters),
        SourceManager(rbt_search, session, query, 'rbt', filters),
        SourceManager(eldorado_search, session, query, 'eldorado', filters),
        SourceManager(megamarket_search, session, query, 'megamarket', filters),
        SourceManager(aliexpress_search, session, query, 'aliexpress', filters),
        SourceManager(onlinetrade_search, session, query, 'onlinetrade', filters)
    ]
    if user_queries.get(chat_id, {}).get('filters', {}).get('Магазин').get('any_selected') and not is_group:
        shops_filter = list(map(lambda shop_name: SHOPS_NORMAL_TO_SHORT.get(shop_name, shop_name),
                                [param for param, value in user_queries.get(chat_id).get(
                                    'filters').get('Магазин').get('params').items() if value]))
        filtered_sources = [source for source in sources if source.name in shops_filter]
        sources = filtered_sources
    elif is_group:
        filtered_sources = [source for source in sources if source.name not in ['citilink', 'onlinetrade']] # ужасный поиск и там, и там. по запросу "пылесос" выдаёт чехлы для телефона за 9 рублей))) так что проще уж без них
        sources = filtered_sources
    return sources