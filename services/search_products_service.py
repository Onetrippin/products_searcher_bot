import asyncio
import heapq
import itertools
from typing import Tuple, Dict, Any, List, Optional

from curl_cffi.requests import AsyncSession

from shops import ozon_search, wb_search, mvideo_search
from utils.constants import OFFSET_COEFFICIENTS


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


class SourceManager:
    def __init__(self, fetch_data_function, session: AsyncSession, query: str, name: str) -> None:
        self.data = []
        self.index = 0
        self.fetch_data = fetch_data_function
        self.session = session
        self.query = query
        self.offset = 0
        self.next_link = None
        self.name = name
        self.total_products = 0

    async def load_more_data(self) -> None:
        if self.name in ['ozon']:
            self.next_link, data, self.total_products = await self.fetch_data(
                self.session, self.query, self.offset, self.next_link
            )
        elif self.name in ['wb', 'mvideo', 'citilink', 'rbt', 'eldorado']:
            data, self.total_products = await self.fetch_data(
                self.session, self.query, self.offset, self.next_link
            )
            self.next_link = str(self.total_products - OFFSET_COEFFICIENTS[self.name] * self.offset)
        else:
            data = []
        if data:
            self.data = sorted(
                [item for item in data if item.get('price') is not None],
                key=lambda item: item['price']
            )
            self.index = 0
            self.offset += 1

    async def get_next(self) -> dict:
        if self.index < len(self.data):
            result = self.data[self.index]
            self.index += 1
            return result
        await self.load_more_data()
        if self.index < len(self.data):
            result = self.data[self.index]
            self.index += 1
            return result
        return {}


class UserData:
    def __init__(self, sources: List[SourceManager]) -> None:
        self.sources = sources
        self.heap = []
        self.counter = itertools.count()

    async def fill_heap(self) -> None:
        for source in self.sources:
            first_element = await source.get_next()
            if first_element is not None and 'price' in first_element:
                heapq.heappush(self.heap, (first_element['price'], next(self.counter), first_element, source))

    async def get_next_batch(self, batch_size=50) -> List[Dict[str, Any]]:
        current_batch = []
        while len(current_batch) < batch_size:
            if not self.heap:
                break
            _, _, min_item, source = heapq.heappop(self.heap)
            current_batch.append(min_item)
            next_item = await source.get_next()
            if next_item is not None and 'price' in next_item:
                heapq.heappush(self.heap, (next_item['price'], next(self.counter), next_item, source))
        return current_batch

async def get_search_result(query: str, session: AsyncSession, offset: int, links: dict) -> Tuple[dict, list]:
    ozon_next_link, ozon_products, total_ozon_products = await ozon_search(session, query, offset, links)
    wb_products, wb_total_products = await wb_search(session, query, offset, links)
    all_products = []
    unsorted_products = ozon_products + wb_products
    sorted_products = sorted(
        list(filter(
            lambda dictionary: dictionary.get('price'),
            unsorted_products
        )),
        key=lambda dictionary: dictionary['price'])
    next_links = {'ozon': ozon_next_link, 'wb': str(wb_total_products - 100 * offset)}
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