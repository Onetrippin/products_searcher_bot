import asyncio
import json

import aiohttp
from aiohttp import ClientSession
import imageio


async def get_search_request(session: ClientSession, query: str, offset: int) -> list:
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
        'page': str(offset),
        'query': query,
        'resultset': 'catalog',
        'sort': 'priceup',
        'spp': '30',
        'suppressSpellcheck': 'false'
    }
    try:
        async with session.get('https://search.wb.ru/exactmatch/ru/common/v7/search',
                               headers=headers,
                               params=params) as response:
            response.raise_for_status()
            return await parse_search_request(await response.text())
    except aiohttp.ClientError as err:
        print(f'Ошибка {err} при отправке запроса к вб')
        return

async def parse_search_request(result_str: str) -> list:
    result = json.loads(result_str)
    products = result.get('data', {}).get('products')
    products_list = []
    for product in products:
        product_info = {}
        brand = f'{product.get("brand")} ' if product.get('brand') else ''
        title = brand + product.get('name')
        title_32 = title[:29]
        product_info['title'] = title_32[:title_32.rfind(' ')] + '...'
        product_info['rating'] = product.get('reviewRating')
        prices = product.get('sizes', {})[0].get('price')
        product_info['orig_price'] = prices.get('basic') / 100
        product_info['price'] = int((prices.get('product') / 100) * 0.97)
        product_id = str(product.get('id'))
        product_info['image'] = (f'https://basket-17.wbbasket.ru/vol{product_id[:4]}/part{product_id[:6]}/{product_id}'
                                 f'/images/c516x688/1.webp')
        product_info['shop'] = 'Wildberries'
        products_list.append(product_info)
    return products_list

async def get_search_result(session: ClientSession, query: str, offset: int) -> list:
    return await get_search_request(session, query, offset)