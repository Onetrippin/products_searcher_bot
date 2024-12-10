from typing import Tuple

import aiosqlite


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