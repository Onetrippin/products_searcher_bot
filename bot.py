from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError

import os
import asyncio

from handlers import register_start_handlers

load_dotenv()

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
        bot = Bot(token=token)
    except TokenValidationError as e:
        print(f'Ошибка при валидации токена: {e}\nВозможно, токен некорректный')
        with open('.env', 'w'):
            pass
        exit(1)
    except Exception as e:
        print(f'Произошла ошибка: {e}')
        exit(1)
    dp = Dispatcher()
    register_start_handlers(dp)
    print('Бот запущен')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
