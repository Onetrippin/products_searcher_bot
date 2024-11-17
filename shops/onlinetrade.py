from typing import Tuple
import json
from html import unescape

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession
from selectolax.parser import HTMLParser


url = 'https://www.onlinetrade.ru/'

async def get_search_request(session: AsyncSession, query: str, offset: int) -> Tuple[list, int]:
    cookies = {
        'user_city': '5',
        'search_sort': 'price-asc',
    }
    headers = {
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.onlinetrade.ru/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    params = {
        'handler': 'moregoods',
        'handlermode': 'search',
        'cat_id': '0',
        'pagenext': str(offset), # it's now page :/
        'pagesort': 'price-asc',
        'query': query,
        'brand': '',
        'force_items': '1',
    }
    try:
        response = await session.get(f'{url}search2.php',
                                     params=params,
                                     cookies=cookies,
                                     headers=headers)
        response.raise_for_status()
        return await parse_search_request(response.text)
    except HTTPError as err:
        print(f'Ошибка {err} при отправке запроса к онлайн трейду')
        return [], 0

async def parse_search_request(result_str: str) -> Tuple[list, int]:
    result = json.loads(result_str)
    html_code = result.get('items')
    if not html_code:
        return [], 0
    html_code = unescape(html_code)
    tree = HTMLParser(html_code)
    products_info = tree.css('div.indexGoods__item__flexCover')
    products_prices = tree.css('div.indexGoods__item__dataCover')
    if len(products_info) != len(products_prices):
        return [], 0
    products_list = []
    for i in range(len(products_info)):
        title = products_info[i].css('div.indexGoods__item__descriptionCover')[1].css_first('a').text(deep=True).strip()
        title_32 = title[:29]
        rating = products_info[i].css_first('div.starsSVG').attrs['title'].split()[0]
        try:
            rating = int(rating)
        except ValueError:
            rating = None
        try:
            price = products_prices[i].css_first('span.price.regular').text().strip().replace(' ', '')[:-1]
        except AttributeError:
            continue
        products_list.append({
            'title': title_32[:title_32.rfind(' ')] + '...',
            'rating': rating,
            'image': products_info[i].css_first('img').attrs['src'],
            'shop': 'ОНЛАЙНТРЕЙД',
            'price': int(price),
            'orig_price': int(price)
        })
    pagination = result.get('pagination')
    pagination = unescape(pagination)
    tree = HTMLParser(pagination)
    total_products = int(tree.css_first('div.paginator__count').text().strip().split()[-1])
    return products_list, total_products

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0