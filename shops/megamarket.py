from typing import Tuple
import json

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession

from utils.constants import OFFSET_COEFFICIENTS


url = 'https://megamarket.ru/'

async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    headers = {
        'accept': 'application/json',
        'accept-language': 'ru-RU,ru;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://megamarket.ru',
        'referer': 'https://megamarket.ru/',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
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
            'experiments': {
                '8': '2',
                '55': '2',
                '58': '2',
                '68': '1',
                '69': '1',
                '79': '3',
                '99': '1',
                '107': '2',
                '109': '2',
                '119': '2',
                '120': '2',
                '121': '2',
                '122': '1',
                '132': '1',
                '144': '3',
                '154': '2',
                '173': '1',
                '182': '1',
                '184': '3',
                '186': '2',
                '190': '1',
                '192': '2',
                '194': '3',
                '200': '2',
                '205': '2',
                '209': '1',
                '218': '1',
                '243': '1',
                '249': '3',
                '645': '4',
                '646': '2',
                '772': '1',
                '775': '1',
                '777': '1',
                '778': '2',
                '790': '1',
                '793': '1',
                '805': '2',
                '808': '3',
                '818': '3',
                '828': '2',
                '837': '1',
                '842': '1',
                '844': '2',
                '845': '2',
                '852': '1',
                '889': '2',
                '893': '2',
                '897': '1',
                '899': '2',
                '903': '2',
                '958': '2',
                '962': '2',
                '5779': '2',
                '20121': '2',
                '43568': '1',
                '67319': '2',
                '70070': '1',
                '80283': '2',
                '85160': '2',
                '91562': '3',
            },
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
            'link': f'{url}catalog/details/{item.get("goods").get("slug")}/',
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

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str, filters: dict) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0