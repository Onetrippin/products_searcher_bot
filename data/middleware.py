import logging

from aiogram.types import TelegramObject
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from . import DatabaseConnection


class LoggerAndDatabaseMiddleware(BaseMiddleware):
    def __init__(self, logger: logging.Logger, db_instance: DatabaseConnection) -> None:
        super().__init__()
        self.logger = logger
        self.db_instance = db_instance

    async def __call__(self, handler, event: TelegramObject, data: dict):
        data['logger'] = self.logger
        data['db'] = self.db_instance
        return await handler(event, data)