from typing import Tuple
import json

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession

from utils.constants import OFFSET_COEFFICIENTS


url = 'https://megamarket.ru/'

async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    headers = {
        "accept": "application/json",
        "accept-language": "en",
        "authority": "megamarket.ru",
        "connection": "keep-alive",
        "Content-Type": "application/json",
        "origin": "https://megamarket.ru",
        "referer": "https://megamarket.ru/",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "Sec-Fetch-User": "?1",
        "sec-fetch-dest": "empty",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    data = {
        'requestVersion': 10,
        'merchant': {},
        'limit': OFFSET_COEFFICIENTS['megamarket'],
        'offset': OFFSET_COEFFICIENTS['megamarket'] * offset,
        'isMultiCategorySearch': False,
        'searchByOriginalQuery': False,
        'selectedSuggestParams': [],
        'expandedFiltersIds': [],
        'sorting': 1,
        'ageMore18': None,
        'addressId': None,
        'showNotAvailable': True,
        'selectedFilters': [],
        'searchText': query,
        'auth': {
            'locationId': '66',
            'appPlatform': 'WEB',
            'appVersion': 0,
            'experiments': {},
            'os': 'UNKNOWN_OS'
        }
    }

    try:
        response = await session.post(f'{url}api/mobile/v1/catalogService/catalog/search',
                                      headers=headers,
                                      json=data)
        response.raise_for_status()
        return await parse_search_request(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к мегамаркету')
        return [], 0

async def parse_search_request(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    items = result.get('items')
    if not items:
        return [], 0
    products_list = []
    for item in items:
        title = item.get('goods', {}).get('title')
        title_32 = title[:29]
        if item.get('favoriteOffer', {}).get('price') == 0:
            continue
        products_list.append({
            'full_title': title,
            'title': title_32[:title_32.rfind(' ')] + '...',
            'rating': item.get('rating'),
            'image': item.get('goods', {}).get('titleImage'),
            'shop': 'Мегамаркет',
            'price': item.get('favoriteOffer', {}).get('price'),
            'orig_price': item.get('favoriteOffer', {}).get('oldPrice') \
                if item.get('favoriteOffer', {}).get('oldPrice') \
                else item.get('favoriteOffer', {}).get('price')
        })
    total_products = int(result.get('total'))
    return products_list, total_products

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0