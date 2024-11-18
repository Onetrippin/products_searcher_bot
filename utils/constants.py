LINES_PER_PAGE = 8
FILTERS = {
    'Магазин': ['Ozon', 'Wildberries', 'Мегамаркет', 'ОНЛАЙНТРЕЙД',
                'Ситилинк', 'М.Видео', 'Эльдорадо', 'RBT',
                'AliExpress', 'Яндекс.Маркет', 'DNS', 'МТС'],
    'Тип': ['Телевизор', 'Смартфон', 'Ноутбук', 'Планшет', 'Клавиатура', 'Мышь', 'Монитор', 'Игровая приставка',
                'Наушники'],
    'Цена': ['0-5000', '5001-10000', '10001-20000', '20001-50000', '50001-100000', '100001-500000'],
    'Бренд': ['LG', 'Samsung', 'Apple', 'Razer', 'Logitech', 'Sony', 'Xiaomi', 'Philips', 'OnePlus', 'HP']
}
DELAY_BETWEEN_API_REQUESTS = 1
OFFSET_COEFFICIENTS = {
    'wb': 100,
    'mvideo': 72,
    'rbt': 400,
    'citilink': 200,
    'eldorado': 210,
    'megamarket': 44,
    'aliexpress': 1,
    'onlinetrade': 30
}