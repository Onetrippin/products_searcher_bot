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
    match vol:
        case vol if vol <= 143:
            return '01'
        case vol if vol <= 287:
            return '02'
        case vol if vol <= 431:
            return '03'
        case vol if vol <= 719:
            return '04'
        case vol if vol <= 1007:
            return '05'
        case vol if vol <= 1061:
            return '06'
        case vol if vol <= 1115:
            return '07'
        case vol if vol <= 1169:
            return '08'
        case vol if vol <= 1313:
            return '09'
        case vol if vol <= 1601:
            return '10'
        case vol if vol <= 1655:
            return '11'
        case vol if vol <= 1919:
            return '12'
        case vol if vol <= 2045:
            return '13'
        case vol if vol <= 2189:
            return '14'
        case vol if vol <= 2405:
            return '15'
        case vol if vol <= 2621:
            return '16'
        case vol if vol <= 2837:
            return '17'
        case vol if vol <= 3053:
            return '18'
        case _:
            return '19'

def get_category_by_name(name: str) -> str | None:
    match name:
        case 'Смартфон':
            return '515'
        case 'Телевизор':
            return '2819'
        case 'Ноутбук':
            return '2290'
        case 'Планшет':
            return '517'
        case 'Клавиатура':
            return '604'
        case 'Мышь':
            return '788'
        case 'Монитор':
            return '2892'
        case 'Видеокарта':
            return '3274'
        case 'Процессор':
            return '3698'
        case 'Наушники':
            return '593'
        case _:
            return

def get_brand_by_name(name: str) -> str | None:
    name = name.lower()
    match name:
        case 'apple':
            return '6049'
        case 'honor':
            return '24012'
        case 'huawei':
            return '6667'
        case 'poco':
            return '132943'
        case 'samsung':
            return '5772'
        case 'tecno':
            return '23233'
        case 'xiaomi':
            return '19467'
        case 'asus':
            return '5786'
        case 'blackview':
            return '24840'
        case 'cmf by nothing':
            return '263232'
        case 'coolpad':
            return '1279813'
        case 'f+':
            return '53823'
        case 'google':
            return '57548'
        case 'iiif150':
            return '221249805'
        case 'infinix':
            return '252622'
        case 'inoi':
            return '22703'
        case 'itel':
            return '23234'
        case 'kenshi':
            return '101660'
        case 'motorola':
            return '11140'
        case 'nothing':
            return '263232'
        case 'nubia (zte)':
            return '5780'
        case 'oneplus':
            return '28380'
        case 'oppo':
            return '10883'
        case 'oukitel':
            return '26210'
        case 'realme':
            return '48914'
        case 'unihertz':
            return '310636654'
        case 'vivo':
            return '33526'
        case 'wiko':
            return '63630'
        case 'bq':
            return '23870'
        case 'doogee':
            return '27800'
        case 'iqoo':
            return '311326180'
        case 'meizu':
            return '6755'
        case 'ulefone':
            return '38697'
        case 'umidigi':
            return '553198'
        case 'black shark':
            return
        case 'nokia':
            return '16111'
        case 'sony':
            return '6013'
        case 'tcl':
            return '20817'
        case 'lenovo':
            return '5891'
        case 'lg':
            return '5788'
        case 'dexp': #####################
            return '146116'
        case 'haier':
            return '26109'
        case 'hisense':
            return '35437'
        case 'accesstyle':
            return '40960'
        case 'aceline':
            return '122195'
        case 'aiwa':
            return '81686'
        case 'akai':
            return
        case 'asano':
            return '33907'
        case 'bbk':
            return '6183'
        case 'blackton':
            return '65848'
        case 'centek':
            return '28838'
        case 'daewoo':
            return
        case 'econ':
            return '29945'
        case 'erisson':
            return '21318'
        case 'evo tv':
            return
        case 'goldstar':
            return '5800'
        case 'harper':
            return '11146'
        case 'hiberg':
            return '50650'
        case 'hyundai':
            return '17380'
        case 'iffalcon':
            return '310744076'
        case 'irbis':
            return '18909'
        case 'jvc':
            return '24273'
        case 'kivi':
            return '44624'
        case 'konka':
            return
        case 'leff':
            return '6113'
        case 'maunfeld':
            return '40304'
        case 'megamax':
            return
        case 'olto':
            return '11147'
        case 'philips':
            return '6012'
        case 'polar':
            return '1296'
        case 'premier':
            return '3732'
        case 'rombica':
            return '38263'
        case 'sber':
            return '106091'
        case 'scoole':
            return '25856'
        case 'sharp':
            return
        case 'shivaki':
            return '6513'
        case 'skyline':
            return '44707'
        case 'skyworth':
            return
        case 'soundmax':
            return '34394'
        case 'starwind':
            return '6820'
        case 'supra':
            return '1802'
        case 'topdevice':
            return '656448'
        case 'vekta':
            return '46267'
        case 'vesta':
            return '7643'
        case 'яндекс':
            return '35479'
        case 'digma':
            return '8321'
        case 'digma pro':
            return '311101834'
        case 'sunwind':
            return '151512'
        case 'yuno':
            return '24174'
        case 'artel':
            return '15293'
        case 'avel':
            return '142697'
        case 'carrera':
            return
        case 'candy':
            return '7229'
        case 'fusion':
            return
        case 'grundig':
            return '178124'
        case 'garlyn':
            return '28531'
        case 'hi':
            return '311112391'
        case 'horizont':
            return '21319'
        case 'hiper':
            return '11399'
        case 'hec':
            return
        case 'maibenben':
            return
        case 'national':
            return
        case 'panasonic':
            return '6108'
        case 'prestigio':
            return '6562'
        case 'red solution':
            return
        case 'renova':
            return '37776'
        case 'schaub lorenz':
            return '46521'
        case 'thomson':
            return '6113'
        case 'toshiba':
            return '7153'
        case 'telefunken':
            return '29168'
        case 'viomi':
            return '40481'
        case 'v-home':
            return
        case 'витязь':
            return
        case 'триколор':
            return '27364'
        case 'doffler':
            return '55925'
        case 'acer': #####################################
            return '3859'
        case 'ardor gaming':
            return '310604878'
        case 'msi':
            return '27445'
        case 'acd':
            return '164028'
        case 'aorus':
            return '1157533'
        case 'chuwi':
            return '167095'
        case 'colorful':
            return '34420'
        case 'dell':
            return '7148'
        case 'gateway':
            return '944003'
        case 'gigabyte':
            return '28928'
        case 'hasee':
            return '461550'
        case 'hp':
            return '6364'
        case 'iru':
            return '53510'
        case 'machcreator':
            return '103867535'
        case 'machenike':
            return '111347'
        case 'microsoft':
            return '5787'
        case 'osio':
            return '516739'
        case 'razer':
            return
        case 'unchartevice':
            return '310516385'
        case 'echips':
            return '58897'
        case 'rikor':
            return '310666128'
        case 'azerty':
            return '431229'
        case 'adata':
            return
        case 'dream-machines':
            return
        case 'kwik':
            return
        case 'lyambda':
            return '38932'
        case 'nerpa':
            return '92618'
        case 'sledgehammer':
            return
        case 'thunderobot':
            return '382736'
        case _:
            return

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str, filters: dict) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset)
    return [], 0