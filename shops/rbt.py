import asyncio
from typing import Tuple

import aiohttp
from aiohttp import ClientSession
from selectolax.parser import HTMLParser


url = 'https://www.rbt.ru/'

async def get_search_request(session: ClientSession, query: str, offset: int) -> Tuple[list, int]:
    offset += 1
    headers = {
        'Accept - Language': 'ru-RU,ru;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'PHPSESSID=nlvvbptt30da0q10g5h6d5nhap; _gcl_au=1.1.320542628.1730961623; rrpvid=658912263136192; tmr_lvid=f6a377208dbc18bdea39603a43e634c3; tmr_lvidTS=1730961624106; _ym_uid=1730961625706420784; _ym_d=1730961625; rcuid=672c60d8f20f8995ff345dd7; adrcid=AlfXLrna0z6clHGyBKcgZ9w; _ym_isad=2; adrdel=1731097738923; acs_3=%7B%22hash%22%3A%22261894c87994c528f5fc093a35dcf7e6de8e3e95%22%2C%22nextSyncTime%22%3A1731176277654%2C%22syncLog%22%3A%7B%22224%22%3A1731089877654%2C%221228%22%3A1731089877654%2C%221230%22%3A1731089877654%7D%7D; rrlevt=1731097745885; _ym_visorc=b; _gid=GA1.2.831699718.1731132484; _ga=GA1.1.1724194305.1730961624; city=15; region=3; rerf=AAAAAGcu/RWwt6Q9AwMHAg==; class=class_a; ipp_uid=1731132693801/WoARbPZHs0KGgDEo/EJUonjsFy0ZExKUHjoy+vA==; ipp_key=v1731132693801/v33947245ba5adc7a72e273/QMEgWj1Wz92xcPyxFrh2IQ==; _userGUID=0:m39rpkk7:jwxTwaHvdCIO13XYd3z6RktDlvEDOaP0; _ymab_param=5aVGV0copiaPI7AdXPJvB1Shsf3t82l6eK5Jcin-C5d7Osa6d6JaUdVdGo8z4yJwz9fEDEHFsf4JZO1E9ifu7wWQeB4; adrcid=AlfXLrna0z6clHGyBKcgZ9w; _ga=GA1.3.1724194305.1730961624; _gid=GA1.3.831699718.1731132484; domain_sid=txgphAAaGsVkx4KS7ob-_%3A1731132696503; catalogue_view=1; digi_uc=|v:173109:805241|s:173096:805241!173113:542750:395523:793092; dSesn=b26a2dd5-4125-f613-4557-891294eb6775; _dvs=0:m39rq50v:NCcWpsPpmngdSfVtwz3mjCx~ulmZweN8; ItemsOnPage=44; tmr_detect=0%7C1731132755878; _ga_X6PN0CQMVL=GS1.1.1731131171.3.1.1731132771.46.0.0',
        'Dnt': '1',
        'Host': 'ekat.rbt.ru',
        'Referer': 'https://ekat.rbt.ru/search/~/sort/price/dir/asc/page/2/?q=%D0%BF%D0%B5%D1%80%D0%B5%D1%85%D0%BE%D0%B4%D0%BD%D0%B8%D0%BA&search_provider=anyquery&strategy=vectors_extended,zero_queries&ajax_items=1',
        'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    params = {
        'search_provider': 'anyquery',
        'strategy': 'vectors_extended, zero_queries',
        'q': query,
        'ajax_items': '1'
    }
    try:
        async with session.get(f'{url}search/~/sort/price/dir/asc/page/{offset}/',
                               headers=headers,
                               params=params) as response:
            response.raise_for_status()
            return await parse_search_result(await response.text())
    except aiohttp.ClientError as err:
        print(f'Ошибка {err} при отправке запроса к рбт')
        return [], 0

async def parse_search_result(html_code: str) -> Tuple[list, int]:
    tree = HTMLParser(html_code)
    total_products = tree.css_first('span.item-catalogue-list__title-amount')
    products_divs = tree.css('div.item-catalogue')
    products_list = []
    for product_div in products_divs:
        title_32 = product_div.css_first('a.link').attributes.get('title')[:29]
        rating_div = product_div.css_first('div.rating__stars')
        for class_name in rating_div.attributes.get('class', '').split():
            if class_name.startswith('rating__stars_value_'):
                rating_value = int(class_name.split('_')[-1]) / 10
                break
        else:
            rating_value = 0
        products_list.append({
            'title': title_32[:title_32.rfind(' ')] + '...',
            'rating': rating_value,
            'image': product_div.css_first('img.image__adaptive').attributes.get('src'),
            'shop': 'RBT',
            'price': product_div.css_first('div.price__row_current'),
            'orig_price': product_div.css_first('div.price__row_old') \
                if product_div.css_first('div.price__row_old') \
                else product_div.css_first('div.price__row_current')
        })
    print(products_list)
    print(total_products)
    return products_list, total_products

async def get_search_result(session: ClientSession, query: str, offset: int, link: str) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0