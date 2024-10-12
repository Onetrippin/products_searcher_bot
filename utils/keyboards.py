from typing import Tuple

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from .constants import LINES_PER_PAGE

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