import json
from typing import Tuple

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession

from utils.constants import OFFSET_COEFFICIENTS


url = 'https://www.mvideo.ru/'

cookies = {
    'MVID_REGION_ID': '5',
    'MVID_CITY_ID': 'CityCZ_2030',
    'MVID_TIMEZONE_OFFSET': '5',
    'MVID_REGION_SHOP': 'S953',
}
headers = {
    'accept': 'application/json',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'baggage': 'sentry-environment=production,sentry-release=release_24_10_3(9240),sentry-public_key=ae7d267743424249bfeeaa2e347f4260,sentry-trace_id=d80d89d71755443caa2a9edcffc1657e,sentry-sample_rate=0.1,sentry-transaction=%2F,sentry-sampled=true',
    'priority': 'u=1, i',
    'referer': 'https://www.mvideo.ru/product-list-page?q=honor&category=noutbuki-118',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sentry-trace': 'b9685cfe00c34e7c95911bfc8788d315-a754d38c18e437b8-1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'x-set-application-id': '49bbe7f6-bf7d-4964-b41b-3e8f99c8c05a',
}


async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    products_ids, total_products = await get_products_ids(session, query, offset)
    if not products_ids:
        return [], 0
    products_list = await get_products_info(session, products_ids)
    if not products_list:
        return [], 0
    products_prices = await get_products_prices(session, products_ids)
    if not products_prices:
        return [], 0
    for product in products_list:
        prices = products_prices[product.get('id')]
        product['orig_price'] = prices.get('orig_price')
        product['price'] = prices.get('price')
    return products_list, total_products


async def get_products_ids(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    params = {
        'query': query,
        'offset': str(OFFSET_COEFFICIENTS['mvideo'] * offset),
        'limit': str(OFFSET_COEFFICIENTS['mvideo']),
        'sort': 'price_asc',
        'filterParams': 'WyLQotC%2B0LvRjNC60L4g0LIg0L3QsNC70LjRh9C40LgiLCItMTIiLCLQlNCwIl0%3D'
    }
    try:
        response = await session.get(f'{url}bff/products/v2/search',
                                     params=params,
                                     cookies=cookies,
                                     headers=headers)
        response.raise_for_status()
        return await parse_products_ids(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к мвидео')
        return [], 0

async def parse_products_ids(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    body = result.get('body')
    total_products = body.get('total')
    products_ids = body.get('products')
    return products_ids, total_products

async def get_products_info(session: AsyncSession, products_ids: list) -> list:
    data = {
        'productIds': products_ids,
        'mediaTypes': [
            'images',
        ],
        'category': True,
        'status': True,
        'brand': True,
        'propertyTypes': [
            'KEY',
        ],
        'propertiesConfig': {
            'propertiesPortionSize': 5,
        },
    }
    try:
        response = await session.post(f'{url}bff/product-details/list',
                                      cookies=cookies,
                                      headers=headers,
                                      json=data)
        response.raise_for_status()
        return await parse_products_info(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к мвидео')
        return []

async def parse_products_info(result_str: str) -> list:
    result = json.loads(result_str)
    products_list = result.get('body', {}).get('products')
    if not products_list:
        return []
    products = []
    for product in products_list:
        title = product.get('name')
        title_32 = title[:29]
        product_id = product.get('productId')
        products.append({
            'full_title': title,
            'title': title_32[:title_32.rfind(' ')] + '...',
            'rating': product.get('rating').get('star'),
            'image': f'https://img.mvideo.ru/Pdb/small_pic/480/{product_id}b.jpg',
            'shop': 'М.Видео',
            'id': product_id
        })
    return products

async def get_products_prices(session: AsyncSession, products_ids: list) -> dict:
    params = {
        'productIds': ','.join(products_ids),
        'addBonusRubles': 'true',
        'isPromoApplied': 'true',
    }
    try:
        response = await session.get(f'{url}bff/products/prices',
                                     params=params,
                                     cookies=cookies,
                                     headers=headers)
        response.raise_for_status()
        return await parse_products_prices(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к мвидео')
        return {}

async def parse_products_prices(result_str: str) -> dict:
    result = json.loads(result_str)
    prices = result.get('body', {}).get('materialPrices')
    if not prices:
        return {}
    return {
        price.get('productId'):
            {
                'orig_price': price.get('price', {}).get('basePrice'),
                'price': price.get('price', {}).get('salePrice')
            }
        for price in prices
    }

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0