from typing import Tuple
import json
import functools
import uuid

import aiosqlite
from aiogram.types import Message

from .categories import data


class DatabaseConnection:
    __instance = None

    @staticmethod
    def get_instance(db_file: str):
        if DatabaseConnection.__instance is None:
            DatabaseConnection(db_file)
        return DatabaseConnection.__instance

    def __init__(self, db_file: str) -> None:
        if DatabaseConnection.__instance is not None:
            raise Exception('Для создания используй get_instance()')
        else:
            self.db_file = db_file
            self.connection = None
            DatabaseConnection.__instance = self

    async def connect(self) -> None:
        if self.connection is None:
            try:
                self.connection = await aiosqlite.connect(self.db_file)
                print(f'Подключение к базе данных {self.db_file} установлено')
            except Exception as e:
                print(f'Ошибка при подключении к базе данных: {e}')

    async def create_tables(self) -> None:
        queries = [
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL UNIQUE,
                notifications_enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_search_time TIMESTAMP,
                last_time_action TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                search_query TEXT,
                filters TEXT,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS saved (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_saved BOOLEAN NOT NULL,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            '''
        ]
        for query in queries:
            await self.execute(query)
        await self.create_categories_tables()

    async def create_categories_tables(self) -> None:
        queries = [
            '''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                max_price REAL NOT NULL,
                min_price REAL NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS categories_brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS categories_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS params_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                param_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (param_id) REFERENCES categories_params(id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                shop TEXT NOT NULL,
                url TEXT NOT NULL,
                old_price REAL,
                actual_price REAL NOT NULL,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_check_time TIMESTAMP,
                need_check BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
            '''
        ]
        for query in queries:
            await self.execute(query)

        if not (await self.execute('SELECT COUNT(*) FROM categories'))[0][0]:
            async def fill_categories_info() -> None:
                for category, info in data.items():
                    category_id = await self.execute('INSERT INTO categories (name, max_price, min_price) VALUES (?, ?, ?)',
                                       (category, info.get('Максимальная цена'), info.get('Минимальная цена')))
                    for brand in info.get('Бренды'):
                        await self.execute('INSERT INTO categories_brands (category_id, name) VALUES (?, ?)',
                                           (category_id, brand))
                    for param, values in info.get('Параметры').items():
                        param_id = await self.execute('INSERT INTO categories_params (category_id, name) VALUES (?, ?)',
                                           (category_id, param))
                        for value in values:
                            await self.execute('INSERT INTO params_values (param_id, name) VALUES (?, ?)',
                                               (param_id, value))
            await fill_categories_info()

    async def execute(self, sql: str, params: Tuple = None) -> Tuple | None:
        if self.connection is None:
            await self.connect()
            if self.connection is None:
                raise RuntimeError('Подключение к базе данных не установлено')

        async with self.connection.cursor() as cursor:
            try:
                await cursor.execute(sql, params or ())
            except Exception as e:
                print(f'Ошибка выполнения запроса к базе данных: {e}')
                await self.connection.rollback()
                return None
            result = await cursor.fetchall()
            if not result or not result[0]:
                await self.connection.commit()
                return cursor.lastrowid
            return result

    async def close(self):
        if self.connection:
            await self.connection.close()
            print('Соединение с базой данных закрыто')

def add_to_db(func) -> None:
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        db, logger = kwargs.get('db'), kwargs.get('logger')
        chat_id = message.from_user.id
        query = 'INSERT OR IGNORE INTO users (chat_id) VALUES (?)'
        await db.execute(query, (chat_id,))
        query = 'UPDATE users SET last_time_action = CURRENT_TIMESTAMP WHERE chat_id = ?'
        await db.execute(query, (chat_id,))
        return await func(message, *args, **kwargs)
    return wrapper

async def load_products_to_db(db: DatabaseConnection, products: list) -> Tuple[list, list]:
    ids = []
    uuids = []
    for product in products:
        product_uuid = str(uuid.uuid4())
        uuids.append(product_uuid)
        ids.append(await db.execute('INSERT INTO products (uuid, name, shop, url, old_price, actual_price, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                    (
                                        product_uuid,
                                        product.get('full_title'),
                                        product.get('shop'),
                                        product.get('link'),
                                        product.get('orig_price'),
                                        product.get('price'),
                                        product.get('image')
                                    )))
    return ids, uuids

async def log_search_and_product_view(db: DatabaseConnection, chat_id: int,  type_: str, data_: str) -> None:
    await db.execute('INSERT INTO history (chat_id, type, search_query) VALUES (?, ?, ?)',
                         (chat_id, type_, data_))