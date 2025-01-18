import os
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
import logging
import http.server
import socketserver

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from data import DatabaseConnection
from data import LoggerAndDatabaseMiddleware
from handlers import router
from utils.bot_singleton import BotSingleton


load_dotenv()

PORT = 8000

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def check_and_save_token() -> str:
    token = os.getenv('API_TOKEN')
    if not token:
        token = input('Введите токен Telegram бота: ')
        with open('.env', 'a') as env_file:
            env_file.write(f'API_TOKEN={token}')
            os.environ['API_TOKEN'] = token
    return token

async def main() -> None:
    token = check_and_save_token()
    if not token:
        print('API токен не найден и не был введён')
        exit(1)
    try:
        bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except TokenValidationError as e:
        print(f'Ошибка при валидации токена: {e}\nВозможно, токен некорректный')
        with open('.env', 'w'):
            pass
        exit(1)
    except Exception as e:
        print(f'Произошла ошибка: {e}')
        exit(1)
    await BotSingleton.init_bot(bot)
    dp = Dispatcher()
    dp.include_router(router)
    print('Бот запущен')
    db_instance = DatabaseConnection.get_instance('database.db')
    await db_instance.connect()
    await db_instance.create_tables()
    logger = await create_logger()
    dp.update.middleware(LoggerAndDatabaseMiddleware(logger, db_instance))
    print('Бот готов пахать')
    try:
        await dp.start_polling(bot)
    finally:
        await db_instance.close()

async def create_logger():
    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    return logger

def start_server() -> None:
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Сервер запущен на http://localhost:{PORT}")
        httpd.serve_forever()

async def start() -> None:
    bot_task = asyncio.create_task(main())
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, start_server)
    await bot_task

if __name__ == '__main__':
    asyncio.run(start())