from typing import Tuple
import functools

import aiosqlite
from aiogram.types import Message


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
                chat_id INTEGER NOT NULL UNIQUE,
                type TEXT NOT NULL,
                search_query TEXT NOT NULL,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                filters TEXT,
                last_data TEXT,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS saved (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL UNIQUE,
                product_id INTEGER NOT NULL,
                added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            '''
            ,
            '''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                urls TEXT NOT NULL,
                prices TEXT NOT NULL,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_check_time TIMESTAMP
            )
            '''
        ]
        for query in queries:
            await self.execute(query)

    async def execute(self, sql: str, params: Tuple = None) -> Tuple | None:
        if self.connection is None:
            await self.connect()
            if self.connection is None:
                raise RuntimeError('Подключение к базе данных не установлено')

        async with self.connection.cursor() as cursor:
            try:
                await cursor.execute(sql, params or ())
                await self.connection.commit()
                return await cursor.fetchall()
            except Exception as e:
                print(f'Ошибка выполнения запроса к базе данных: {e}')
                await self.connection.rollback()
                return None

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