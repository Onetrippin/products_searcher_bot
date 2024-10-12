from typing import Tuple

from aiogram.types import (Message,
                           ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from .constants import LINES_PER_PAGE

def start_message(message: Message) -> str:
    return (
        f'<b>Привет, {message.from_user.first_name}!</b>'
        '\n\n'
        'Я бот для <b><i>поиска электроники по лучшей цене</i></b>'
        '\n\n'
        '<b>Я могу:</b>'
        '\n'
        '<i>- найти необходимый товар по лучшей цене</i>'
        '\n'
        '<i>- показать отзывы о товаре со всех магазинов</i>'
        '\n'
        '<i>- отслеживать изменение цены и наличия товара</i>'
        '\n'
        '<i>- выбрать лучшее предложение в плане цены, качества и надёжности</i>'
        '\n\n'
        'Для навигации <u>используй кнопки</u>'
        '\n\n'
        '<b>Что-то непонятно? - </b>/help'
    )

def help_message() -> str:
    return (
        'Описание кнопок:'
        '\n'
        '"Искать товары" - вы сможете найти необходимый вам товар по названию и настроить фильтры'
        '\n'
        '"Избранное" - вам отобразится список товаров, которые вы добавили в избранное'
        '\n'
        '"История поиска" - отображается список из 50 последних товаров и результатов, которые вы искали'
    )

def saved_message(message: Message, page_number: str = '1') -> str:
    return (
        'Это сообщение с избранным'
    )

def history_message(message: Message, page_number: str = '1') -> str:
    return (
        'Это сообщение с историей поиска'
    )

def search_message(message: Message) -> str:
    return (
        'Это сообщение с поиском'
    )

def other_message() -> str:
    return (
        '<b>Пользуйся кнопками</b>'
        '\n\n'
        '<i>Что-то непонятно? Напиши /help</i>'
    )

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🔎 Искать товары')],
            [KeyboardButton(text='🕒 История поиска'), KeyboardButton(text='⭐ Избранное')],
            [KeyboardButton(text='❓ Помощь')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def calculate_page_numbers(current_page: int, row_count: int) -> Tuple[int, int, int]:
    total_pages = (row_count + (LINES_PER_PAGE - 1)) // LINES_PER_PAGE
    prev_page = total_pages if current_page == 1 else current_page - 1
    next_page = 1 if current_page == total_pages else current_page + 1
    return prev_page, next_page, total_pages

def page_navigation_keyboard(page_type: str, row_count: int, current_page: int = 1, request_id: int = 0) -> InlineKeyboardMarkup:
    prev_page, next_page, total_pages = calculate_page_numbers(current_page, row_count)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'page_{page_type}_{prev_page}_{request_id}'),
                InlineKeyboardButton(text=f'{current_page}/{total_pages}', callback_data=f'counter_{current_page}/{total_pages}'),
                InlineKeyboardButton(text='➡️', callback_data=f'page_{page_type}_{next_page}_{request_id}')
            ]
        ]
    )