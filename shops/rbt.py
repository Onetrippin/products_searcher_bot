from typing import Tuple
import json

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession

from utils.constants import OFFSET_COEFFICIENTS


url = 'https://ekat.rbt.ru/'

async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'ekat.rbt.ru',
        'Priority': 'u=0, i',
        'Referer': 'https://ekat.rbt.ru/',
        'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.70 Safari/537.36',
    }
    params = {
        'app': 'EXTERNALWEB',
        'query': query,
        'sort': 'price_asc',
        'offset': OFFSET_COEFFICIENTS['rbt'] * offset
    }
    try:
        response = await session.get(f'{url}rest/search/by/',
                                     headers=headers,
                                     params=params,
                                     cookies = {'class': 'class_b'})
        response.raise_for_status()
        return await parse_search_result(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к рбт')
        return [], 0

async def parse_search_result(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    items = result.get('items')
    if not items:
        return [], 0
    if len(items) == OFFSET_COEFFICIENTS['rbt']:
        total_products = 401
    else:
        total_products = 1
    products_list = []
    for item in items:
        title = item.get('name')
        title_32 = title[:29]
        products_list.append({
            'full_title': title,
            'title': title_32[:title_32.rfind(' ')] + '...',
            'rating': item.get('rating'),
            'image': f'{url[:-1]}{item.get("image")}',
            'shop': 'RBT',
            'price': item.get('price'),
            'orig_price': item.get('old_price') \
                if item.get('old_price') \
                else item.get('price')
        })
    return products_list, total_products

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0