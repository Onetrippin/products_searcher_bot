import os
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy
import http.server
import socketserver
import threading

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from handlers import router


load_dotenv()

PORT = 8000

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

selected_filters = {}
current_index = {}
user_queries = {}

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
    dp = Dispatcher()
    dp.include_router(router)
    print('Бот запущен')
    await dp.start_polling(bot)

def start_server() -> None:
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Сервер запущен на http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    asyncio.run(main())