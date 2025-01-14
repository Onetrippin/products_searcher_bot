import json

from data import DatabaseConnection
from utils.constants import LINES_PER_PAGE


# async def get_search_history(chat_id: int) -> list:
#     search_history = [
#         {'input_string': 'ноутбук для игр'},
#         {'product_name': 'Телевизор LG OLED CX 65', 'price': 130000, 'shop': 'Эльдорадо'},
#         {'input_string': 'смартфон 2021'},
#         {'product_name': 'Смартфон Samsung Galaxy S21', 'price': 70000, 'shop': 'ДНС'},
#         {'input_string': 'клавиатура rgb'},
#         {'product_name': 'Ноутбук Apple MacBook Air M1', 'price': 95000, 'shop': 'Ситилинк'},
#         {'product_name': 'Планшет iPad Pro 11 2021', 'price': 86000, 'shop': 'Яндекс Маркет'},
#         {'input_string': 'компьютерная мышь'},
#         {'product_name': 'Клавиатура Razer BlackWidow V3', 'price': 15000, 'shop': 'Озон'},
#         {'input_string': 'монитор для игр'},
#         {'product_name': 'Мышь Logitech G502 HERO', 'price': 4500, 'shop': 'Вайлдберриз'},
#         {'input_string': 'телевизор для дома'},
#         {'product_name': 'Телевизор Sony Bravia 55', 'price': 80000, 'shop': 'Эльдорадо'},
#         {'product_name': 'Смартфон Xiaomi Redmi Note 10', 'price': 18000, 'shop': 'Ситилинк'},
#         {'input_string': 'наушники с шумоподавлением'},
#         {'product_name': 'Наушники AirPods Pro', 'price': 22000, 'shop': 'Яндекс Маркет'},
#         {'input_string': 'монитор 4к'},
#         {'product_name': 'Монитор LG UltraGear 27', 'price': 25000, 'shop': 'ДНС'},
#         {'input_string': 'игровая приставка 2020'},
#         {'product_name': 'Игровая приставка PlayStation 5', 'price': 70000, 'shop': 'Озон'},
#         {'input_string': 'геймерская клавиатура'},
#         {'product_name': 'Клавиатура SteelSeries Apex Pro', 'price': 19000, 'shop': 'Эльдорадо'},
#         {'input_string': 'оптическая мышь'},
#         {'product_name': 'Мышь SteelSeries Rival 600', 'price': 6000, 'shop': 'Вайлдберриз'},
#         {'input_string': 'телевизор oled'},
#         {'product_name': 'Телевизор Philips 58PUS8505', 'price': 65000, 'shop': 'Яндекс Маркет'},
#         {'product_name': 'Смартфон OnePlus 9 Pro', 'price': 72000, 'shop': 'ДНС'},
#         {'input_string': 'беспроводные наушники'},
#         {'product_name': 'Наушники Sony WH-1000XM4', 'price': 25000, 'shop': 'Ситилинк'},
#         {'input_string': 'ультрабук 2021'},
#         {'product_name': 'Ноутбук HP Spectre x360', 'price': 130000, 'shop': 'Озон'},
#         {'input_string': 'планшет для рисования'},
#         {'product_name': 'Планшет Samsung Galaxy Tab S7', 'price': 62000, 'shop': 'Вайлдберриз'},
#         {'product_name': 'Клавиатура Corsair K95 RGB', 'price': 17000, 'shop': 'Эльдорадо'},
#         {'input_string': 'беспроводная мышь'},
#         {'product_name': 'Мышь ASUS ROG Gladius II', 'price': 6500, 'shop': 'Ситилинк'},
#         {'input_string': 'телевизор для гостиной'},
#         {'product_name': 'Телевизор Hisense 55A7100F', 'price': 43000, 'shop': 'Яндекс Маркет'},
#         {'product_name': 'Смартфон Realme GT', 'price': 30000, 'shop': 'Озон'},
#         {'input_string': 'наушники для телефона'},
#         {'product_name': 'Наушники Bose QuietComfort 35 II', 'price': 28000, 'shop': 'ДНС'},
#         {'input_string': 'монитор игровой'},
#         {'product_name': 'Монитор Acer Predator XB273', 'price': 36000, 'shop': 'Вайлдберриз'},
#         {'input_string': 'консоль xbox'},
#         {'product_name': 'Игровая приставка Xbox Series X', 'price': 65000, 'shop': 'Ситилинк'},
#         {'product_name': 'Клавиатура HyperX Alloy FPS', 'price': 10000, 'shop': 'Эльдорадо'},
#         {'input_string': 'эргономичная мышь'},
#         {'product_name': 'Мышь Logitech MX Master 3', 'price': 8000, 'shop': 'Озон'},
#         {'input_string': 'oled телевизор'},
#         {'product_name': 'Телевизор Panasonic TX-55HZ2000', 'price': 140000, 'shop': 'Яндекс Маркет'},
#         {'product_name': 'Смартфон Google Pixel 5', 'price': 55000, 'shop': 'Вайлдберриз'},
#         {'input_string': 'наушники для музыки'},
#         {'product_name': 'Наушники JBL Live 660NC', 'price': 12000, 'shop': 'ДНС'},
#         {'input_string': 'ноутбук для работы'},
#         {'product_name': 'Ноутбук Lenovo Legion 5', 'price': 100000, 'shop': 'Ситилинк'},
#         {'input_string': 'планшет с большим экраном'},
#         {'product_name': 'Планшет Huawei MatePad Pro', 'price': 43000, 'shop': 'Эльдорадо'},
#         {'input_string': 'компьютерная мышь rgb'},
#         {'product_name': 'Мышь Logitech G Pro X', 'price': 7500, 'shop': 'Яндекс Маркет'},
#     ]
#     return search_history

async def get_search_history(db: DatabaseConnection, chat_id: int) -> list:
    query = '''SELECT type, search_query FROM history
               WHERE chat_id = ?
               ORDER BY id DESC'''
    results = await db.execute(query, (chat_id,))
    if not results:
        return []
    history_results = []
    for result in results:
        if result[0] == 'product':
            product_uuid, product_name, product_shop, actual_price = (
                await db.execute('SELECT uuid, name, shop, actual_price FROM products WHERE id = ?',
                                 (result[1],)))[0]
            history_results.append(
                {
                    'product_name': product_name,
                    'price': actual_price,
                    'shop': product_shop,
                    'link': f'https://t.me/products_searcher_bot?start=product_page={product_uuid}'
                })
        else:
            history_results.append(
                {
                    'input_string': result[1],
                    'link': f'https://t.me/products_searcher_bot?start=search=1'
                })
    return history_results