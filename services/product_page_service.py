import json
from typing import Tuple

from curl_cffi.requests import AsyncSession

from data import DatabaseConnection, load_products_to_db, load_products_group
from data.user_queries import user_queries
from utils.bot_singleton import BotSingleton
from .filter_search_service import collect_request_data
from .search_products_service import UserData
from utils import product_page, product_page_keyboard, error_product_page


async def edit_message_with_results(db: DatabaseConnection, chat_id: int, message_id: int, product_id: int) -> None:
    product_uuid, name, url, price, shop = (await db.execute('SELECT uuid, name, url, actual_price, shop FROM products WHERE id = ?',
                                                             (product_id,)))[0]
    name = ' '.join(name.split()[:5])
    is_saved = await is_saved_product(db, chat_id, product_id)
    products, product_ids = await get_related_products(db, chat_id, name, url)
    await load_products_group(db, product_id, json.dumps(product_ids))
    product = format_product_info(url, name, price, shop, products)
    bot = await BotSingleton.instance()
    await bot.edit_message_text(
        product_page(product, False),
        reply_markup=product_page_keyboard(chat_id, str(product_id), product_uuid, is_saved),
        inline_message_id=str(message_id),
        disable_web_page_preview=True
    )

async def get_related_products(db: DatabaseConnection, chat_id: int, query: str, url: str) -> Tuple[list, list]:
    session = user_queries[chat_id]['session'] = AsyncSession(impersonate='chrome123') \
        if not user_queries[chat_id].get('session') \
        else user_queries[chat_id]['session']
    sources = collect_request_data(session, chat_id, query, is_group=True)
    user_queries[chat_id]['data'] = UserData(sources=sources)
    await user_queries[chat_id]['data'].fill_heap()
    related_products = await user_queries[chat_id]['data'].get_next_batch(15)
    product_ids, product_uuids = await load_products_to_db(db, related_products)
    all_products = []
    for i, product in enumerate(related_products):
        if product.get('link')[:70] == url[:70]:
            continue
        all_products.append({
            'id': str(product_ids[i]),
            'uuid': product_uuids[i],
            'link': product.get('link'),
            'product_full_name': product.get('full_title'),
            'price': product.get('price'),
            'shop': product.get('shop'),
            'product_image': product.get('image'),
            'is_main_product': False
        })
    return all_products, product_ids

def format_product_info(url: str, name: str, price: int, shop: str, products: list) -> dict:
    product = {
        'link': url,
        'product_full_name': name,
        'price': price,
        'shop': shop
    }
    products.append(product)
    products[-1]['is_main_product'] = True
    products.sort(key=lambda prod: prod['price'])
    product['all_offers'] = products
    return product

async def get_related_info_by_ids(db: DatabaseConnection, related_ids: list) -> list:
    related_products = []
    for related_id in related_ids:
        url, name, price, shop = (await db.execute('SELECT url, name, actual_price, shop FROM products WHERE id = ?',
                                                   (related_id,)))[0]
        related_products.append({
            'link': url,
            'product_full_name': name,
            'price': price,
            'shop': shop
        })
    return related_products

async def send_product_page(db: DatabaseConnection, chat_id: int, product_uuid: str) -> None:
    bot = await BotSingleton.instance()
    result = await db.execute('''
    SELECT id, name, shop, url, actual_price, image_url
    FROM products
    WHERE uuid = ?
    ''', (product_uuid,))
    if not result or isinstance(result, int):
        await bot.send_message(
            chat_id=chat_id,
            text=error_product_page()
        )
        return
    product_id, name, shop, url, price, image = result[0]
    is_saved = await is_saved_product(db, chat_id, product_id)
    result = await db.execute('SELECT product_id, related_ids FROM groups WHERE product_id = ?',
                              (product_id,))
    if result and not isinstance(result, int):
        product_id, related_ids = result[0]
        related_ids = json.loads(related_ids)
        products = await get_related_info_by_ids(db, related_ids)
    else:
        products, product_ids = await get_related_products(db, chat_id, name, url)
        await load_products_group(db, product_id, json.dumps(product_ids))
    product = format_product_info(url, name, price, shop, products)
    await bot.send_message(
        chat_id=chat_id,
        text=product_page(product, False),
        reply_markup=product_page_keyboard(chat_id, str(product_id), product_uuid, is_saved),
        disable_web_page_preview=True
    )

async def is_saved_product(db: DatabaseConnection, chat_id: int, product_id: int) -> bool:
    res_saved = await db.execute('SELECT is_saved FROM saved WHERE chat_id = (?) AND product_id = (?)',
                                 (chat_id, product_id))
    if not isinstance(res_saved, int) and res_saved[0][0]:
        return True
    return False