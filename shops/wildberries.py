import json
from typing import Tuple

from curl_cffi.requests.exceptions import HTTPError
from curl_cffi.requests import AsyncSession


async def get_search_request(session: AsyncSession, query: str, offset: int, filters: dict) -> Tuple[list, int]:
    wb_filters = get_wb_filters(filters)
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
        **{
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
        },
        **wb_filters
    }
    try:
        response = await session.get('https://search.wb.ru/exactmatch/ru/common/v9/search',
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

def get_wb_filters(filters: dict) -> dict:
    if not filters:
        return {}
    wb_filters = {}
    device = filters.get('Тип', [None])[0]
    for filter_, params in filters.items():
        wb_filter = get_filter_by_name(filter_)
        wb_params = get_params_function_match(filter_, params, device)
        if wb_params:
            wb_filters[wb_filter] = wb_params
    return wb_filters

def get_params_function_match(filter_name, params: list | str, device: str = None) -> str:
    match filter_name:
        case 'Тип':
            return get_category_by_name(params[0])
        case 'Цена':
            return get_wb_formatted_price(params)
        case 'Бренд':
            return ';'.join([get_brand_by_name(brand) for brand in params])
        case 'Высокий рейтинг':
            return '1'
        case 'Оперативка':
            return get_ram_by_numbers(params)
        case 'Память':
            return get_rom_by_numbers(params)
        case 'Аккумулятор':
            return get_mah_by_limits(params)
        case 'Камера':
            return get_cam_by_numbers(params)
        case 'Цвет':
            return get_color_by_names(params, device)
        case 'NFC':
            return '18636'
        case 'Операционка':
            return get_os_by_names(params)
        case 'Разрешение':
            return get_resolution_by_names(params)
        case 'Smart TV':
            return '122537'
        case 'Процессор':
            return get_processor_by_names(params)
        case 'Тип видеокарты':
            return get_videocard_type_by_names(params)
        case 'Объем SSD':
            return get_ssd_by_numbers(params)
        case 'Игровой':
            return '948847801'
        case 'Матрица':
            return get_screen_type_by_names(params)
        case 'Корпус':
            return get_body_material_by_names(params)
        case 'Вид':
            return get_keyboard_type_by_names(params)
        case 'Игровая':
            return '218769'
        case 'Подключение':
            return get_mouse_conn_type_by_names(params)
        case 'Сенсор':
            return get_sensor_type_by_names(params)
        case 'Видеопроцессор':
            return get_videoprocessor_by_names(params)
        case 'Видеопамять':
            return get_video_memory_by_numbers(params)
        case 'Тип памяти':
            return get_video_memory_type_by_names(params)
        case 'Сокет':
            return get_socket_by_names(params)
        case 'Семейство':
            return get_processor_family_by_names(params)
        case 'Ядра':
            return get_core_amount_by_numbers(params)
        case 'Подключение ':
            return get_headphones_type_by_names(params)
        case _:
            return ''


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

def get_wb_formatted_price(price_range: list) -> str:
    price_range[0] = str(int(int(price_range[0]) * 1.03)) + '00'
    # price_range[-1] = str(int(int(price_range[-1]) * 1.03)) + '00'
    price_range[-1] += '00'
    return ';'.join(price_range)

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
            return '291465'
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
            return '16972'
        case 'asano':
            return '33907'
        case 'bbk':
            return '6183'
        case 'blackton':
            return '65848'
        case 'centek':
            return '28838'
        case 'daewoo':
            return '19077'
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
            return '151014'
        case 'leff':
            return '6113'
        case 'maunfeld':
            return '40304'
        case 'megamax':
            return '40454'
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
            return '21630'
        case 'shivaki':
            return '6513'
        case 'skyline':
            return '44707'
        case 'skyworth':
            return '41926'
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
            return '169'
        case 'candy':
            return '7229'
        case 'fusion':
            return '12130'
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
            return '100080'
        case 'maibenben':
            return '1357107'
        case 'national':
            return '29944'
        case 'panasonic':
            return '6108'
        case 'prestigio':
            return '6562'
        case 'red solution':
            return '310601835'
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
            return '54368'
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
            return '10122'
        case 'unchartevice':
            return '310516385'
        case 'echips':
            return '58897'
        case 'rikor':
            return '310666128'
        case 'azerty':
            return '431229'
        case 'adata':
            return '63789'
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
        case 'alcatel': ########################
            return '5789'
        case 'edpad':
            return
        case 'teclast':
            return '249177'
        case 'htc':
            return '5779'
        case 'kvadra':
            return '92197'
        case 'oscal':
            return '311079601'
        case 'arian':
            return
        case 'alldocube':
            return '434922'
        case 'a4tech': ##########################
            return '9292'
        case 'logitech':
            return '7156'
        case 'red square':
            return '276556'
        case 'дарк проджект':
            return '67541'
        case '8bitdo':
            return '316983'
        case 'akko':
            return '260685'
        case 'aula':
            return '138187'
        case 'by':
            return '27988'
        case 'cougar':
            return '14392'
        case 'crown':
            return '41227'
        case 'dareu':
            return '472234'
        case 'defender':
            return '10987'
        case 'dialog':
            return '32944'
        case 'durgod':
            return
        case 'edifier':
            return '43088'
        case 'exegate':
            return '24708'
        case 'gembird':
            return '22645'
        case 'genius':
            return '6363'
        case 'glorious':
            return '438734'
        case 'hyperx':
            return '94352'
        case 'jet.a':
            return '62822'
        case 'jetaccess':
            return '63026'
        case 'keychron':
            return '256491'
        case 'keyron':
            return '30453334'
        case 'lamzu':
            return '310746048'
        case 'mchose':
            return '311163176'
        case 'montech':
            return '310596965'
        case 'nuphy':
            return '1443003'
        case 'oklick':
            return '7995'
        case 'pro legend':
            return '9715'
        case 'qumo':
            return '19322'
        case 'rapoo':
            return '17565'
        case 'redragon':
            return '21270'
        case 'ritmix':
            return '11017'
        case 'royal kludge':
            return '225285'
        case 'satechi':
            return '39071'
        case 'shurikey gear':
            return '311186219'
        case 'smartbuy':
            return '22850'
        case 'steelseries':
            return '21761'
        case 'sven':
            return '7157'
        case 'ugreen':
            return '44588'
        case 'varmilo':
            return '571448'
        case 'гарнизон':
            return '22644'
        case 'gmng':
            return '310461772'
        case 'blackzid':
            return '311122195'
        case 'canyon':
            return '6561'
        case 'intro':
            return '9829'
        case 'lunacy':
            return '599282'
        case 'perfeo':
            return '36889'
        case 'red line':
            return '35617'
        case 'sonnen':
            return '20183'
        case 'tfn':
            return '9134'
        case 'trust':
            return '8861'
        case 'ducky':
            return '278461'
        case 'deppa':
            return '6428'
        case 'free wolf':
            return '235183934'
        case 'havit':
            return '38526'
        case 'luazon':
            return '20888'
        case 'marvo':
            return '17571'
        case 'mad-catz':
            return '66264'
        case 'olmio':
            return '17586'
        case 'sharkoon':
            return '42565'
        case 'wisebot':
            return '592190'
        case 'xtrfy':
            return '121603'
        case 'baseus': ##########################
            return '19107'
        case 'cbr':
            return '24558'
        case 'delux':
            return '13225'
        case 'dled':
            return '245541'
        case 'energy':
            return '85836'
        case 'kensington':
            return '85776'
        case 'nakatomi':
            return '35320'
        case 'pulsar':
            return '757'
        case 'thermaltake':
            return '63810'
        case 'zdk':
            return '29756'
        case 'hama':
            return '3097'
        case 'jarvisen':
            return '1154577'
        case 'speedlink':
            return '10123'
        case 'lorgar':
            return '310518189'
        case 'bootleg':
            return '892339'
        case 'hoco':
            return '10569'
        case 'lofree':
            return '32919'
        case 'mijia':
            return '82912'
        case 'qub':
            return '52973'
        case 'windigo':
            return '129819'
        case 'xtrike me':
            return '84079'
        case 'xpg':
            return '444693'
        case 'titan army': #####################
            return '311160063'
        case 'alienware':
            return '40305'
        case 'aoc':
            return '27488'
        case 'aopen':
            return '30790'
        case 'benq':
            return '6140'
        case 'coolermaster':
            return '19181'
        case 'delta computers':
            return '311112335'
        case 'elsa':
            return '20049'
        case 'iiyama':
            return '27489'
        case 'lime':
            return '20246'
        case 'raskat':
            return '535797'
        case 'sanc':
            return '1127038'
        case 'viewsonic':
            return '27731'
        case 'zowie':
            return '94500'
        case 'бештау':
            return '233077'
        case 'bloody':
            return '94508'
        case 'dahua':
            return '45006'
        case 'lightcom':
            return '720463'
        case 'npc':
            return '1396508'
        case 'pinebro':
            return '310863972'
        case 'rdw computers':
            return '310988910'
        case 'гравитон':
            return '1332353'
        case 'abr technology':
            return '325829'
        case 'carcam':
            return '40842'
        case 'compit':
            return '1110270'
        case 'hikvision':
            return '43335'
        case 'tesla':
            return '17919'
        case 'zeuslap':
            return '912991'
        case 'amcv':
            return '55940'
        case 'asrock': ########################
            return '54438'
        case 'kfa2':
            return '51947'
        case 'palit':
            return '28901'
        case 'powercolor':
            return '70343'
        case 'sapphire':
            return '17080'
        case 'gainward':
            return '685855'
        case 'inno3d':
            return '71914'
        case 'nvidia':
            return '6010'
        case 'pny':
            return '123403'
        case 'zotac':
            return '69603'
        case 'afox':
            return '80648'
        case 'biostar':
            return '96289'
        case 'ninja':
            return '37203'
        case 'maxsun':
            return '939134'
        case 'sinotex':
            return '800409'
        case 'intel': ################################
            return '21223'
        case 'amd':
            return '28933'
        case 'jbl': ##############################
            return '7658'
        case 'corsair':
            return '19182'
        case 'creative':
            return '1008'
        case 'sennheiser':
            return '6855'
        case 'fifine':
            return '68465'
        case 'nacon':
            return '369694'
        case 'panteon':
            return '63026'
        case 'sades':
            return '714980'
        case 'somic':
            return '470294'
        case 'zone 51':
            return '83388'
        case 'jabra':
            return '24338'
        case 'jlab':
            return '10072'
        case 'koss':
            return '21126'
        case 'plantronics':
            return '36166'
        case 'poly':
            return '135724'
        case 'takstar':
            return '395542'
        case 'yealink':
            return '22161'
        case 'borofone':
            return '27920'
        case 'onikuma':
            return '243815'
        case 'anker':
            return '38699'
        case 'atvel':
            return '18468'
        case 'bigben':
            return '4516'
        case 'daswerk':
            return '380355'
        case 'eksa':
            return '146711'
        case 'enkor':
            return '2728750'
        case 'easysmx':
            return '532298'
        case 'gamemax':
            return '62829'
        case 'gravastar':
            return '681108'
        case 'haylou':
            return '51253'
        case 'marshall':
            return '28840'
        case 'mpow':
            return '36988'
        case 'microlab':
            return '6367'
        case 'nebula':
            return '131573'
        case 'otl':
            return '310785111'
        case 'oneodio':
            return '436601'
        case 'pdp':
            return '57481'
        case 'white shark':
            return '100900'
        case 'zebronics':
            return
        case _:
            return

def get_filter_by_name(name: str) -> str:
    match name:
        case 'Оперативка':
            return 'f4710'
        case 'Память':
            return 'f4424'
        case 'Аккумулятор':
            return 'f12445458'
        case 'Камера':
            return 'f62054'
        case 'Цвет':
            return 'fcolor'
        case 'NFC':
            return 'f10466'
        case 'Операционка':
            return 'f4346'
        case 'Разрешение':
            return 'f92867'
        case 'Smart TV':
            return 'f122500'
        case 'Процессор':
            return 'f4521'
        case 'Тип видеокарты':
            return 'f116361'
        case 'Объем SSD':
            return 'f202872'
        case 'Игровой':
            return 'f207425'
        case 'Матрица':
            return 'f13996'
        case 'Корпус':
            return 'f4370'
        case 'Вид':
            return 'f15740'
        case 'Игровая':
            return 'f218768'
        case 'Подключение':
            return 'f366629'
        case 'Сенсор':
            return 'f18638'
        case 'Видеопроцессор':
            return 'f4665'
        case 'Видеопамять':
            return 'f74650'
        case 'Тип памяти':
            return 'f125810'
        case 'Сокет':
            return 'f143281'
        case 'Семейство':
            return 'f143560'
        case 'Ядра':
            return 'f4658'
        case 'Подключение ':
            return 'f15883'
        case 'Цена':
            return 'priceU'
        case 'Высокий рейтинг':
            return 'frating'
        case 'Бренд':
            return 'fbrand'
        case 'Тип':
            return 'xsubject'

def get_ram_by_numbers(numbers: list) -> str:
    filter_ = []
    for number in numbers:
        match number:
            case '2':
                filter_.append('13233')
            case '4':
                filter_.append('14213')
            case '6':
                filter_.append('90162')
            case '8':
                filter_.append('13279')
            case '12':
                filter_.append('98507')
            case '16':
                filter_.append('98508')
            case '18':
                filter_.append('63330755')
            case '24':
                filter_.append('33489995')
            case '32':
                filter_.append('125969')
            case '36':
                filter_.append('852505247')
            case '48':
                filter_.append('33491118')
            case '64':
                filter_.append('159262')
            case '96':
                filter_.append('656843986')
            case '128':
                filter_.append('3854359')
            case _:
                pass
    return ';'.join(filter_)

def get_rom_by_numbers(numbers: list) -> str:
    filter_ = []
    for number in numbers:
        match number:
            case '16':
                filter_.append('12865')
            case '32':
                filter_.append('12866')
            case '64':
                filter_.append('12867')
            case '128':
                filter_.append('12868')
            case '256':
                filter_.append('25425')
            case '512':
                filter_.append('117419')
            case '1000':
                filter_.append('231154')
            case '2000':
                filter_.append('703821030')
            case _:
                pass
    return ';'.join(filter_)

def get_mah_by_limits(limits: list) -> str:
    lower = limits[0]
    upper = limits[-1]
    mahs = ['-20179', '-20180', '-20181', '-20182', '-20183', '-20184', '-20185', '-20186', '-20187', '-20188', '-20189',
            '-20190', '-20191']
    match lower:
        case '1':
            low_index = 0
        case '4000':
            low_index = 5
        case '4500':
            low_index = 6
        case '5000':
            low_index = 7
        case '6000':
            low_index = 8
        case _:
            low_index = 0
    match upper:
        case '3999':
            up_index = 5
        case '4499':
            up_index = 6
        case '4999':
            up_index = 7
        case '5999':
            up_index = 8
        case 'max':
            up_index = 13
        case _:
            up_index = 13
    return ';'.join(mahs[low_index:up_index])

def get_cam_by_numbers(numbers: list) -> str:
    filter_ = set()
    for number in numbers:
        match number:
            case '8':
                filter_.add('-20369')
            case '12':
                filter_.add('-20370')
            case '13':
                filter_.add('-20371')
            case '16':
                filter_.add('-20372')
            case '20':
                filter_.add('-20373')
            case '32':
                filter_.add('-20375')
            case '48':
                filter_.add('-20377')
            case '50':
                filter_.add('-20378')
            case '64':
                filter_.add('-20379')
            case '100':
                filter_.add('-20380')
            case '108':
                filter_.add('-20381')
            case '180':
                filter_.add('-20381')
            case '200':
                filter_.add('-20382')
    return ';'.join(list(filter_))

def get_color_by_names(names: list, device: str) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'бежевый':
                filter_.append('16119260')
            case 'белый':
                filter_.append('16777215')
            case 'голубой':
                filter_.append('11393254')
            case 'желтый':
                filter_.append('16776960')
            case 'зеленый':
                filter_.append('32768')
            case 'золотистый':
                pass
            case 'красный':
                filter_.append('16711680')
            case 'оранжевый':
                filter_.append('16753920')
            case 'розовый':
                filter_.append('16761035')
            case 'серебристый':
                pass
            case 'серый':
                filter_.append('8421504')
            case 'синий':
                filter_.append('255')
            case 'фиолетовый':
                filter_.append('15631086')
            case 'черный':
                filter_.append('0')
            case 'другой':
                if device == 'Смартфон':
                    filter_.append('10824234')
                elif device in ['Телевизор', 'Планшет', 'Клавиатура', 'Наушники']:
                    filter_ += ['16119260', '32768', '10824234', '16711680', '16761035', '255', '15631086']
                elif device == 'Ноутбук':
                    filter_ += ['16119260', '11393254', '16776960', '32768', '10824234', '16711680', '16753920',
                                '16761035', '15631086']
                else:
                    pass
            case _:
                pass
    return ';'.join(filter_)

def get_os_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'Android':
                filter_.append('12787')
            case 'IOS':
                filter_.append('89400')
            case 'без ОС':
                filter_.append('4613884')
            case 'Windows':
                filter_.append('89401')
            case 'macOS':
                filter_.append('9601761')
            case 'Linux':
                filter_ += ['78354', '4051968', '4138274']
            case 'FreeDOS':
                filter_.append('189170')
            case 'HarmonyOS':
                filter_.append('5880009')
            case _:
                pass
    return ';'.join(filter_)

def get_resolution_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'HD':
                filter_.append('96906')
            case 'FullHD':
                filter_.append('200446')
            case '4K UltraHD':
                filter_.append('96905')
            case '8K UltraHD':
                filter_.append('432316')
    return ';'.join(filter_)

def get_processor_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'Intel':
                filter_ += ['14054', '7566020', '1322409509', '224622', '360696', '14701759', '14922807', '1193808587',
                            '74890871', '99143', '126063', '1425856556', '115223', '1136054', '758658852', '132196',
                            '3703383', '937432970', '5992955', '14847326', '98352690', '9561881', '87535856',
                            '1199163419', '1034781179', '1271140196', '1303208290', '1068339905', '256242',
                            '1173605210', '4628708', '953544027', '3728464', '5572150', '1080788173', '109026553',
                            '608210841', '957214670', '674631099', '4563066', '1033368965', '818525014', '100163',
                            '5256849', '1136005', '1411097690', '1033698214', '1182207432', '1136039', '1135992',
                            '3678860', '9576907', '1136020', '8107760', '5572166', '770106282', '98145051',
                            '1079935444', '890179042', '398977386', '14867775', '269731843', '1046787334', '43962079',
                            '1071755495', '10853781', '1196841835', '1063730546', '674600951', '851205831', '758495882',
                            '675059975', '1185760580', '621423402', '674992213', '736493247', '957225231', '1071755457',
                            '1032543126', '1032542874', '1032542409', '1032174906', '970244531', '955886804',
                            '10607302', '126025', '5557496', '189174', '1029757522', '773441864', '5441290',
                            '915363071', '3701886', '1136031', '1136009', '5572205', '61329149', '620962534', '403979',
                            '5572139', '1028873830', '502607', '14215744', '1073258188', '586819046', '89499452',
                            '14827491', '11426356', '70228573', '1083669674', '1182500835', '674618166', '758660020',
                            '758186065', '873863906', '1028851965', '943868781', '689313093', '1070243874',
                            '1027762116', '1112120711', '217705', '1402088552', '817041942', '1028789182', '1028788146',
                            '1264907951', '1028787385', '1028786009', '1028785163', '1028779660', '1028779297',
                            '1136036', '384963', '586868069', '892075492', '736481274', '640377439', '949367133',
                            '1028724330', '7591183', '1425996834', '1373627671', '989619848', '1073258262', '949340565',
                            '989619983', '1425723113', '985727171', '5380687', '815331131', '394733', '446196',
                            '814604390', '5209149', '1227590935', '219419', '99144', '127423', '482781', '5665137',
                            '818327179', '867468691', '1189773148', '701155729', '1082552717', '1035088364']
            case 'AMD':
                filter_ += ['5031247', '5441363', '161279', '1079728412', '1076986715', '384964', '663991454',
                            '933136565', '134110', '156131', '360464', '249188', '620256', '620255', '583417780',
                            '699933322', '810438817', '1216935897', '1237838445', '11597151', '9772260', '155883',
                            '249189', '254091', '1190177347', '82890819', '1154911175', '620250', '791978859', '620245',
                            '620249', '444904680', '1171958880', '73376947', '1070198126', '699926896', '818402298',
                            '674592838', '758305847', '1299129122', '775399846', '902056994', '1071755504', '577387570',
                            '697105088', '1198900198', '127421', '155882', '249190', '254092', '3702104', '682354874',
                            '620253', '51683505', '620251', '85803056', '73326571', '205078411', '1094999020',
                            '1198871285', '736729085', '717798620', '750356351', '882074173', '1045420376', '911840136',
                            '775387950', '919735589', '1021911203', '1017785191', '1172649770', '1040971639',
                            '1071755476', '577333666', '577170575', '831623552', '927690370', '892566200', '961029398',
                            '998556051', '1066884002', '1352358966', '1290507140']
            case 'Apple':
                filter_ += ['399510', '9232253', '7945791', '39601384', '624360891', '608315828', '791005971',
                            '911857197', '902023870', '1061845929']
            case 'Qualcomm':
                filter_ += ['622231117', '1195978875']
            case 'Zhaoxin':
                pass
    return ';'.join(filter_)

def get_videocard_type_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        if name == 'дискретная':
            filter_ += ['374121', '116429', '116822', '177370', '358694', '748327702', '673258913', '5850444', '116599',
                        '1866831921', '125974', '125975', '148200', '1136010', '1136038', '775740497', '14827764',
                        '116895', '197339', '353431', '428658', '14827494', '5105218', '5442911', '446188', '446189',
                        '10831521', '446192', '586837698', '633672330', '674677696', '660611858', '679834292',
                        '640377440', '646054823', '9839733']
        elif name == 'интегрированная':
            filter_ += ['145670', '941611712', '9556571', '9518135', '9557541', '9442223', '127420', '8646696',
                        '384747', '14230778', '155046', '121078', '127516', '387989', '116916', '145673', '9653895',
                        '14967826', '919366867', '918444485', '63336495', '918612110', '918612239', '116440', '265700',
                        '116492', '116715', '116698', '116462', '124482', '116470', '116497', '403956', '234228',
                        '135238', '384959', '428657', '12113630', '446193', '446194', '116977', '116472', '165905',
                        '125933', '117211', '11563274', '11563271', '384960', '14969518']
        else:
            pass
    return ';'.join(filter_)

def get_ssd_by_numbers(numbers: list) -> str:
    filter_ = []
    for number in numbers:
        match number:
            case '128':
                filter_.append('202879')
            case '256':
                filter_.append('202883')
            case '512':
                filter_.append('202886')
            case '1000':
                filter_.append('2404432')
            case '2000':
                filter_.append('3702058')
            case '4000':
                filter_.append('3964407')
            case _:
                pass
    return ';'.join(filter_)

def get_screen_type_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'IPS':
                filter_.append('222635')
            case 'OLED':
                filter_.append('96771')
            case 'TN':
                filter_.append('222634')
            case 'AMOLED':
                filter_.append('498426')
            case 'VA':
                filter_.append('358518')
            case 'другой':
                filter_ += ['5442183', '240690', '358518', '4037549']
            case _:
                pass
    return ';'.join(filter_)

def get_body_material_by_names(names: list) -> str:
    if len(names) >= 2:
        return ';'.join(['12814', '12809', '12812', '12810', '12813', '12816'])
    if names[0] == 'металл':
        return ';'.join(['12812', '12809', '12816'])
    if names[0] == 'пластик':
        return ';'.join(['12814'])
    return ''

def get_keyboard_type_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        if name == 'механическая':
            filter_.append('23637')
        elif name == 'мембранная':
            filter_.append('23635')
        else:
            pass
    return ';'.join(filter_)

def get_mouse_conn_type_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'беспроводное':
                filter_.append('366630')
            case 'проводное':
                filter_.append('366632')
            case _:
                pass
    return ';'.join(filter_)

def get_sensor_type_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'оптический':
                filter_.append('140875')
            case 'лазерный':
                filter_.append('2406502')
            case _:
                pass
    return ';'.join(filter_)

def get_videoprocessor_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        if name == 'NVIDIA':
            filter_ += ['120088', '700411263', '356293', '131362', '120089', '120091', '165956', '202476', '135234',
                        '14568829', '1483286407', '624308', '418478', '709871687', '678324866', '572742519',
                        '939048284', '1505354224', '62835199']
        elif name == 'AMD':
            filter_ += ['146702', '120086', '120087', '146652', '162619', '146664', '9635219', '3651090', '719345473',
                        '1045979631', '943069628', '834765778', '1022867377', '678740815']
        elif name == 'Intel':
            filter_ += ['1211368194', '14231823']
        else:
            pass
    return ';'.join(filter_)

def get_video_memory_by_numbers(numbers: list) -> str:
    filter_ = []
    for number in numbers:
        match number:
            case '1':
                filter_.append('80582')
            case '2':
                filter_.append('80583')
            case '4':
                filter_.append('80585')
            case '6':
                filter_.append('125971')
            case '8':
                filter_.append('80586')
            case '10':
                filter_.append('384933')
            case '12':
                filter_.append('608963')
            case '16':
                filter_.append('545784')
            case '20':
                filter_.append('101455718')
            case '24':
                filter_.append('418511')
            case _:
                pass
    return ';'.join(filter_)

def get_video_memory_type_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        if name == 'GDDR3':
            filter_.append('125814')
        elif name == 'GDDR5':
            filter_.append('125817')
        elif name == 'GDDR6':
            filter_.append('125819')
        else:
            pass
    return ';'.join(filter_)

def get_socket_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'AM4':
                filter_.append('143286')
            case 'AM5':
                filter_.append('29286127')
            case 'LGA 1200':
                filter_.append('267884')
            case 'LGA 1700':
                filter_.append('10850389')
            case 'LGA 1851':
                filter_.append('962017894')
            case 'LGA 1151':
                filter_.append('143294')
            case 'другой':
                filter_ += ['143284', '143285', '907139606', '408448249', '143289', '3658853', '143290', '619553033',
                            '766555851', '143291', '143293', '5890465', '143296', '143297', '143299', '143300',
                            '143301', '143303', '99421245', '825958417', '143304', '143305', '682605823', '631537261',
                            '921724707', '766555850', '606095242', '366289']
            case _:
                pass
    return ';'.join(filter_)

def get_processor_family_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        match name:
            case 'AMD Athlon':
                filter_.append('143566')
            case 'AMD Ryzen 3':
                filter_.append('143579')
            case 'AMD Ryzen 5':
                filter_.append('143580')
            case 'AMD Ryzen 7':
                filter_.append('143581')
            case 'AMD Ryzen 9':
                filter_.append('199336')
            case 'Intel Celeron':
                filter_.append('143585')
            case 'Intel Pentium':
                filter_.append('143599')
            case 'Intel Core i3':
                filter_.append('143593')
            case 'Intel Core i5':
                filter_.append('143594')
            case 'Intel Core i7':
                filter_.append('143595')
            case 'Intel Core i9':
                filter_.append('143597')
            case 'другое':
                filter_ += ['143564', '143565', '143561', '143562', '143563', '143575', '143576', '143578', '382643740',
                            '143582', '143583', '143588', '9432368', '143603']
            case _:
                pass
    return ';'.join(filter_)

def get_core_amount_by_numbers(numbers: list) -> str:
    filter_ = []
    for number in numbers:
        match number:
            case '2':
                filter_.append('13062')
            case '4':
                filter_.append('13063')
            case '6':
                filter_.append('13064')
            case '8':
                filter_.append('13065')
            case '10':
                filter_.append('31914')
            case '12':
                filter_.append('165663')
            case '14':
                filter_.append('11498689')
            case '16':
                filter_.append('165664')
            case '18':
                filter_.append('9308651')
            case '24':
                filter_.append('99383254')
            case _:
                pass
    return ';'.join(filter_)

def get_headphones_type_by_names(names: list) -> str:
    filter_ = []
    for name in names:
        if name == 'проводное':
            filter_ += ['25833066', '23755']
        elif name == 'беспроводное':
            filter_.append('417068')
        else:
            pass
    return ';'.join(filter_)

async def get_search_result(session: AsyncSession, query: str, offset: int, link: str, filters: dict) -> Tuple[list, int]:
    if not link or int(link) > 0:
        return await get_search_request(session, query, offset, filters)
    return [], 0