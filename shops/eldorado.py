from typing import Tuple
import json

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession

from utils.constants import OFFSET_COEFFICIENTS


url = 'https://www.eldorado.ru/'

async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    cookies = {
        'gsscgib-w-eldorado': 'qPQ17IOVLTSgvRr2E/mxJyi6NWvCJyy48JaSb5HyVrgsClSOAPMFAsUnr6zDWHEHE9xd4bTEjuuZ0ZK37KjEPejhLBmjduWLrRpwovHfzCLZ87UFoVBjrFr7GPraXStks8GI0VMh+5scQEgyRimDuSJxBtJo/AC1l3DkX1uLsyqdfxyiLKdI/sLQt+49L06ctbX1vJRE7FBjbTxRqfwpiJR/Cd04wZLFWVNWHkrxJ+eBm4tTdDNxHo5EE78eXaZad5AyImfk',
        'cfidsgib-w-eldorado': 'FxMbkM82b6/VW2gZ45noy0dXT1dnE6X9GcCemmQrd8RasA9mwHMT60HylQ0UEsyw4IeggKfefgds+Q28gWQuluPEXRpPWL8tNui0zVqMTjBV3874UtkihsipMWsPPxhUHGyEKIZ/RK6DAdr1FJd48qYmvX816/00gif4',
        'gsscgib-w-eldorado': 'qPQ17IOVLTSgvRr2E/mxJyi6NWvCJyy48JaSb5HyVrgsClSOAPMFAsUnr6zDWHEHE9xd4bTEjuuZ0ZK37KjEPejhLBmjduWLrRpwovHfzCLZ87UFoVBjrFr7GPraXStks8GI0VMh+5scQEgyRimDuSJxBtJo/AC1l3DkX1uLsyqdfxyiLKdI/sLQt+49L06ctbX1vJRE7FBjbTxRqfwpiJR/Cd04wZLFWVNWHkrxJ+eBm4tTdDNxHo5EE78eXaZad5AyImfk',
        'gsscgib-w-eldorado': 'qPQ17IOVLTSgvRr2E/mxJyi6NWvCJyy48JaSb5HyVrgsClSOAPMFAsUnr6zDWHEHE9xd4bTEjuuZ0ZK37KjEPejhLBmjduWLrRpwovHfzCLZ87UFoVBjrFr7GPraXStks8GI0VMh+5scQEgyRimDuSJxBtJo/AC1l3DkX1uLsyqdfxyiLKdI/sLQt+49L06ctbX1vJRE7FBjbTxRqfwpiJR/Cd04wZLFWVNWHkrxJ+eBm4tTdDNxHo5EE78eXaZad5AyImfk',
        'fgsscgib-w-eldorado': 'knsw3e6d97609a3f0928ab5f3104ef7bab50fe22',
        'fgsscgib-w-eldorado': 'knsw3e6d97609a3f0928ab5f3104ef7bab50fe22',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.eldorado.ru/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    params = {
        'rootRestrictedCategoryId': '0',
        'query': query,
        'orderField': 'price',
        'orderDirection': 'ASC',
        'limit': str(OFFSET_COEFFICIENTS['eldorado']),
        'offset': str(OFFSET_COEFFICIENTS['eldorado'] * offset),
        'regionId': '11297',
    }

    try:
        response = await session.get(f'{url}sem/v3/a666/products',
                                     params=params,
                                     cookies=cookies,
                                     headers=headers)
        response.raise_for_status()
        return await parse_search_request(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к эльдорадо')
        return [], 0

async def parse_search_request(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    data = result.get('data')
    if not data:
        return [], 0
    products_list = []
    for item in data:
        if not item.get('fastOrder'):
            continue
        title = item.get('name')
        title_32 = title[:29]
        products_list.append({
            'link': f'{url}cat/detail/{item.get("code")}/',
            'full_title': title,
            'title': title_32[:title_32.rfind(' ')] + '...',
            'rating': item.get('rating'),
            'image': f'https://static.eldorado.ru{item.get("images", [{}])[0].get("url")}',
            'shop': 'Эльдорадо',
            'price': item.get('price'),
            'orig_price': item.get('old_price') \
                if item.get('old_price') \
                else item.get('price')
        })
    total_products = result.get('totalCount')
    return products_list, total_products

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0