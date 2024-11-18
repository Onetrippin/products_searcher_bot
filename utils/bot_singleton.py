import asyncio
from aiogram import Bot


class BotSingleton:
    __instance = None
    _lock = asyncio.Lock()

    @staticmethod
    async def instance() -> 'Bot':
        if BotSingleton.__instance is None:
            raise RuntimeError(f'Бот ещё не инициализирован')
        return BotSingleton.__instance

    @staticmethod
    async def init_bot(bot: 'Bot') -> None:
        async with BotSingleton._lock:
            if BotSingleton.__instance is not None:
                raise RuntimeError('Бот уже инициализирован')
            BotSingleton.__instance = bot