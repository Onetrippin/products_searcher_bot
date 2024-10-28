import asyncio
from typing import Tuple

from aiohttp import ClientSession

from shops import ozon_search, wb_search


# async def get_search_result(query: str) -> list:
#     products = [
#         {'product_name': 'Телевизор LG OLED CX 65',
#          'best_price': 130000,
#          'best_price_shop': 'Эльдорадо',
#          'all_offers': [{'price': 134772, 'shop': 'Яндекс Маркет'},
#                         {'price': 132704, 'shop': 'Ситилинк'},
#                         {'price': 133166, 'shop': 'Вайлдберриз'},
#                         {'price': 130769, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Смартфон Samsung Galaxy S21',
#          'best_price': 70000,
#          'best_price_shop': 'ДНС',
#          'all_offers': [{'price': 71176, 'shop': 'Ситилинк'},
#                         {'price': 74238, 'shop': 'Яндекс Маркет'},
#                         {'price': 71738, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Ноутбук Apple MacBook Air M1',
#          'best_price': 95000,
#          'best_price_shop': 'Ситилинк',
#          'all_offers': [{'price': 96795, 'shop': 'Озон'},
#                         {'price': 97246, 'shop': 'Эльдорадо'},
#                         {'price': 99067, 'shop': 'Эльдорадо'}]
#         },
#         {'product_name': 'Планшет iPad Pro 11 2021',
#          'best_price': 86000,
#          'best_price_shop': 'Яндекс Маркет',
#          'all_offers': [{'price': 88969, 'shop': 'Вайлдберриз'},
#                         {'price': 90756, 'shop': 'ДНС'},
#                         {'price': 87724, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Клавиатура Razer BlackWidow V3',
#          'best_price': 15000,
#          'best_price_shop': 'Озон',
#          'all_offers': [{'price': 15224, 'shop': 'Ситилинк'},
#                         {'price': 16347, 'shop': 'Эльдорадо'},
#                         {'price': 15569, 'shop': 'Вайлдберриз'}]
#         },
#         {'product_name': 'Мышь Logitech G502 HERO',
#          'best_price': 4500,
#          'best_price_shop': 'Вайлдберриз',
#          'all_offers': [{'price': 8428, 'shop': 'Озон'},
#                         {'price': 5912, 'shop': 'ДНС'},
#                         {'price': 5939, 'shop': 'Эльдорадо'}]
#         },
#         {'product_name': 'Телевизор Sony Bravia 55',
#          'best_price': 80000,
#          'best_price_shop': 'Эльдорадо',
#          'all_offers': [{'price': 82256, 'shop': 'Ситилинк'},
#                         {'price': 83987, 'shop': 'Озон'},
#                         {'price': 81450, 'shop': 'Яндекс Маркет'}]
#         },
#         {'product_name': 'Смартфон Xiaomi Redmi Note 10',
#          'best_price': 18000,
#          'best_price_shop': 'Ситилинк',
#          'all_offers': [{'price': 18886, 'shop': 'ДНС'},
#                         {'price': 22848, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Наушники AirPods Pro',
#          'best_price': 22000,
#          'best_price_shop': 'Яндекс Маркет',
#          'all_offers': [{'price': 24131, 'shop': 'ДНС'},
#                         {'price': 22772, 'shop': 'Эльдорадо'}]
#         },
#         {'product_name': 'Монитор LG UltraGear 27',
#          'best_price': 25000,
#          'best_price_shop': 'ДНС',
#          'all_offers': [{'price': 26678, 'shop': 'Яндекс Маркет'},
#                         {'price': 25947, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Игровая приставка PlayStation 5',
#          'best_price': 70000,
#          'best_price_shop': 'Озон',
#          'all_offers': [{'price': 71176, 'shop': 'Ситилинк'},
#                         {'price': 74238, 'shop': 'Яндекс Маркет'}]
#         },
#         {'product_name': 'Клавиатура SteelSeries Apex Pro',
#          'best_price': 19000,
#          'best_price_shop': 'Эльдорадо',
#          'all_offers': [{'price': 19526, 'shop': 'Ситилинк'},
#                         {'price': 19375, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Мышь SteelSeries Rival 600',
#          'best_price': 6000,
#          'best_price_shop': 'Вайлдберриз',
#          'all_offers': [{'price': 6158, 'shop': 'Эльдорадо'},
#                         {'price': 6225, 'shop': 'Ситилинк'}]
#         },
#         {'product_name': 'Телевизор Philips 58PUS8505',
#          'best_price': 65000,
#          'best_price_shop': 'Яндекс Маркет',
#          'all_offers': [{'price': 68325, 'shop': 'Вайлдберриз'},
#                         {'price': 65478, 'shop': 'ДНС'},
#                         {'price': 66543, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Смартфон OnePlus 9 Pro',
#          'best_price': 72000,
#          'best_price_shop': 'ДНС',
#          'all_offers': [{'price': 73356, 'shop': 'Яндекс Маркет'},
#                         {'price': 74289, 'shop': 'Ситилинк'},
#                         {'price': 75543, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Наушники Sony WH-1000XM4',
#          'best_price': 25000,
#          'best_price_shop': 'Ситилинк',
#          'all_offers': [{'price': 25896, 'shop': 'ДНС'},
#                         {'price': 26784, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Ноутбук HP Spectre x360',
#          'best_price': 130000,
#          'best_price_shop': 'Озон',
#          'all_offers': [{'price': 132984, 'shop': 'Яндекс Маркет'},
#                         {'price': 134756, 'shop': 'Эльдорадо'},
#                         {'price': 130769, 'shop': 'Ситилинк'}]
#         },
#         {'product_name': 'Планшет Samsung Galaxy Tab S7',
#          'best_price': 62000,
#          'best_price_shop': 'Вайлдберриз',
#          'all_offers': [{'price': 63876, 'shop': 'Озон'},
#                         {'price': 62987, 'shop': 'Ситилинк'},
#                         {'price': 64753, 'shop': 'ДНС'}]
#         },
#         {'product_name': 'Клавиатура Corsair K95 RGB',
#          'best_price': 17000,
#          'best_price_shop': 'Эльдорадо',
#          'all_offers': [{'price': 17489, 'shop': 'Яндекс Маркет'},
#                         {'price': 17956, 'shop': 'Ситилинк'},
#                         {'price': 17340, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Мышь ASUS ROG Gladius II',
#          'best_price': 6500,
#          'best_price_shop': 'Ситилинк',
#          'all_offers': [{'price': 6836, 'shop': 'Эльдорадо'},
#                         {'price': 6925, 'shop': 'Вайлдберриз'},
#                         {'price': 6614, 'shop': 'Озон'}]
#         },
#         {'product_name': 'Телевизор Hisense 55A7100F',
#          'best_price': 43000,
#          'best_price_shop': 'Яндекс Маркет',
#          'all_offers': [{'price': 45582, 'shop': 'ДНС'},
#                         {'price': 44725, 'shop': 'Озон'},
#                         {'price': 44296, 'shop': 'Ситилинк'}]
#         },
#         {'product_name': 'Смартфон Realme GT',
#          'best_price': 30000,
#          'best_price_shop': 'Озон',
#          'all_offers': [{'price': 32345, 'shop': 'ДНС'},
#                         {'price': 31375, 'shop': 'Яндекс Маркет'}]
#         },
#         {'product_name': 'Наушники Bose QuietComfort 35 II',
#          'best_price': 28000,
#          'best_price_shop': 'ДНС',
#          'all_offers': [{'price': 29000, 'shop': 'Эльдорадо'},
#                         {'price': 29500, 'shop': 'Озон'}]
#          },
#         {'product_name': 'Монитор Acer Predator XB273',
#          'best_price': 36000,
#          'best_price_shop': 'Вайлдберриз',
#          'all_offers': [{'price': 37000, 'shop': 'ДНС'},
#                         {'price': 36500, 'shop': 'Ситилинк'}]
#          },
#         {'product_name': 'Игровая приставка Xbox Series X',
#          'best_price': 65000,
#          'best_price_shop': 'Ситилинк',
#          'all_offers': [{'price': 67000, 'shop': 'Яндекс Маркет'},
#                         {'price': 66000, 'shop': 'Эльдорадо'}]
#          },
#         {'product_name': 'Клавиатура HyperX Alloy FPS',
#          'best_price': 10000,
#          'best_price_shop': 'Эльдорадо',
#          'all_offers': [{'price': 10200, 'shop': 'ДНС'},
#                         {'price': 10100, 'shop': 'Озон'}]
#          },
#         {'product_name': 'Мышь Logitech MX Master 3',
#          'best_price': 8000,
#          'best_price_shop': 'Озон',
#          'all_offers': [{'price': 8200, 'shop': 'Ситилинк'},
#                         {'price': 8100, 'shop': 'Яндекс Маркет'}]
#          },
#         {'product_name': 'Телевизор Panasonic TX-55HZ2000',
#          'best_price': 140000,
#          'best_price_shop': 'Яндекс Маркет',
#          'all_offers': [{'price': 145000, 'shop': 'Эльдорадо'},
#                         {'price': 143000, 'shop': 'Ситилинк'}]
#          },
#         {'product_name': 'Смартфон Google Pixel 5',
#          'best_price': 55000,
#          'best_price_shop': 'Вайлдберриз',
#          'all_offers': [{'price': 56000, 'shop': 'ДНС'},
#                         {'price': 57000, 'shop': 'Озон'}]
#          },
#         {'product_name': 'Наушники JBL Live 660NC',
#          'best_price': 12000,
#          'best_price_shop': 'ДНС',
#          'all_offers': [{'price': 12500, 'shop': 'Ситилинк'},
#                         {'price': 12200, 'shop': 'Эльдорадо'}]
#          },
#         {'product_name': 'Ноутбук Lenovo Legion 5',
#          'best_price': 100000,
#          'best_price_shop': 'Ситилинк',
#          'all_offers': [{'price': 102000, 'shop': 'Яндекс Маркет'},
#                         {'price': 101500, 'shop': 'Эльдорадо'}]
#          },
#         {'product_name': 'Планшет Huawei MatePad Pro',
#          'best_price': 43000,
#          'best_price_shop': 'Эльдорадо',
#          'all_offers': [{'price': 44000, 'shop': 'Вайлдберриз'},
#                         {'price': 43500, 'shop': 'Ситилинк'}]
#          },
#         {'product_name': 'Мышь Logitech G Pro X',
#          'best_price': 7500,
#          'best_price_shop': 'Яндекс Маркет',
#          'all_offers': [{'price': 7600, 'shop': 'Эльдорадо'},
#                         {'price': 7550, 'shop': 'ДНС'}]
#          }
#     ]
#     search_result = [product for product in products if
#                          'product_name' in product and query.lower() in product['product_name'].lower()]
#     return search_result

async def get_search_result(query: str, session: ClientSession, offset: int, links: dict) -> Tuple[dict, list]:
    ozon_next_link, ozon_products = await ozon_search(session, query, offset, links)
    wb_products = await wb_search(session, query, offset)
    all_products = []
    unsorted_products = ozon_products + wb_products
    sorted_products = sorted(unsorted_products, key=lambda dictionary: dictionary['price'])
    next_links = {'ozon': ozon_next_link}
    for product in sorted_products:
        all_products.append({
            'product_name': product.get('title'),
            'best_price': product.get('price'),
            'best_price_shop': product.get('shop'),
            'product_image': product.get('image'),
            'all_offers': [{'price': 7600, 'shop': 'Эльдорадо'},
                           {'price': 7550, 'shop': 'ДНС'}]
        })
    return next_links, all_products[:50]