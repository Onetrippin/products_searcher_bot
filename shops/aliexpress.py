from typing import Tuple
import json

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession


url = 'https://aliexpress.ru/'

async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    cookies = {
        'xman_us_f': 'x_locale=ru_RU&x_l=0&x_c_chg=1&acs_rt=828b3cd604ab4bcbb5bc9d160f9b36f8', # expire in 2092 :)
        'xman_f': 'CFu4GHkLLjH89NCMe9xcas1LtaPYBEK0cjMvJFZdPcRvUNC30rniIn9w8eTep8E4Udf32dJiPLY0CpgnJWz6TqxOCZvWBOHBlSmSiEPRdY0yiPmifS/wxg==',
        'aer_lang': 'ru_RU',
        'aep_usuc_f': 'b_locale=ru_RU&c_tp=RUB&region=RU&site=rus&province=917483860000000000&city=917483866975000000',
    }
    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9',
        'bx-v': '2.5.22',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://aliexpress.ru',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://aliexpress.ru/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    data = {
        'catId': '',
        'sortType': 'price_asc',
        'g': 'y',
        'searchText': query,
        'storeIds': [],
        'pgChildren': [],
        'aeBrainIds': [],
        'brandValueIds': '',
        'pvid': '',
        'isBigSale': 'n',
        'isGoldenItems': 'n',
        'isGoldenItemsV2': 'n',
        'isFreeShip': 'n',
        'isFastShip': 'n',
        'isSlowShip': 'n',
        'isFavorite': 'n',
        'page': offset + 1,
        'source': 'direct',
    }
    try:
        response = await session.post(f'{url}aer-webapi/v1/search',
                                      cookies=cookies,
                                      headers=headers,
                                      json=data)
        response.raise_for_status()
        return await parse_search_request(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к алиэкспресс')
        return [], 0

async def parse_search_request(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    products = result.get('data', {}).get('productsFeed', {}).get('productsV2')
    if not products:
        return [], 0
    products_list = []
    for product_dict in products:
        product = product_dict.get('product')
        if not product:
            continue
        title = product.get('productTitle')
        title_32 = title[:29]
        products_list.append({
            'full_title': title,
            'title': title_32[:title_32.rfind(' ')] + '...',
            'rating': product.get('rating'),
            'image': f'https:{product.get("imgSrc")}',
            'shop': 'AliExpress',
            'price': int(float(product.get('finalPrice').replace(' ', '').replace(',', '.')[:-1])),
            'orig_price': int(float(product.get('fullPrice').replace(' ', '').replace(',', '.')[:-1])) \
                if product.get('fullPrice') \
                else int(float(product.get('finalPrice').replace(' ', '').replace(',', '.')[:-1]))
        })
    total_products = result.get('data', {}).get('pagination', {}).get('totalPages')
    return products_list, total_products

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0