import json
from typing import Tuple

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession


async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9',
        'dnt': '1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    params = {
        'ab_testing': 'false',
        'appType': '1',
        'curr': 'rub',
        'dest': '-5818883',
        'query': query,
        'resultset': 'catalog',
        'sort': 'priceup',
        'spp': '30',
        'suppressSpellcheck': 'false',
        'page': str(offset + 1)
    }
    try:
        response = await session.get('https://search.wb.ru/exactmatch/ru/common/v7/search',
                                     headers=headers,
                                     params=params)
        response.raise_for_status()
        return await parse_search_request(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к вб')
        return [], 0

async def parse_search_request(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    data = result.get('data', {})
    total_products = int(data.get('total'))
    products = data.get('products')
    products_list = []
    for product in products:
        product_info = {'link': f'https://www.wildberries.ru/catalog/{product.get("id")}/detail.aspx'}
        brand = f'{product.get("brand")} ' if product.get('brand') else ''
        title = brand + product.get('name')
        title_32 = title[:29]
        product_info['full_title'] = title
        product_info['title'] = title_32[:title_32.rfind(' ')] + '...'
        product_info['rating'] = product.get('reviewRating')
        prices = product.get('sizes', {})[0].get('price')
        product_info['orig_price'] = prices.get('basic') / 100
        product_info['price'] = int((prices.get('product') / 100) * 0.97)
        product_id = product.get('id')
        vol = product_id // 100000
        part = product_id // 1000
        product_info['image'] = (f'https://basket-{await get_basket_number(vol)}.wbbasket.ru'
                                 f'/vol{vol}'
                                 f'/part{part}/{product_id}'
                                 f'/images/c516x688/1.webp')
        product_info['shop'] = 'Wildberries'
        products_list.append(product_info)
    return products_list, total_products

async def get_basket_number(vol: int) -> str:
    if vol <= 143:
        return '01'
    elif vol <= 287:
        return '02'
    elif vol <= 431:
        return '03'
    elif vol <= 719:
        return '04'
    elif vol <= 1007:
        return '05'
    elif vol <= 1061:
        return '06'
    elif vol <= 1115:
        return '07'
    elif vol <= 1169:
        return '08'
    elif vol <= 1313:
        return '09'
    elif vol <= 1601:
        return '10'
    elif vol <= 1655:
        return '11'
    elif vol <= 1919:
        return '12'
    elif vol <= 2045:
        return '13'
    elif vol <= 2189:
        return '14'
    elif vol <= 2405:
        return '15'
    elif vol <= 2621:
        return '16'
    elif vol <= 2837:
        return '17'
    return '18'

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0