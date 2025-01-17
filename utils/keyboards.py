from typing import Tuple
from itertools import zip_longest
from math import ceil

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat)
from aiogram.types.web_app_info import WebAppInfo

from .constants import LINES_PER_PAGE, SEARCH_LINES_PER_PAGE
from services import get_query_if_exists
from data.user_queries import user_queries


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

def calculate_page_numbers(current_page: int, row_count: int, type_: str = None) -> Tuple[int, int, int]:
    if type_ == 'search':
        lines_amount = SEARCH_LINES_PER_PAGE
    else:
        lines_amount = LINES_PER_PAGE
    total_pages = (row_count + (lines_amount - 1)) // lines_amount
    prev_page = total_pages if current_page == 1 else current_page - 1
    next_page = 1 if current_page == total_pages else current_page + 1
    return prev_page, next_page, total_pages

def page_navigation_keyboard(page_type: str, row_count: int, current_page: int = 1, query: str = None) -> InlineKeyboardMarkup:
    prev_page, next_page, total_pages = calculate_page_numbers(current_page, row_count, page_type)
    if total_pages == 0 or total_pages == 1:
        return InlineKeyboardMarkup(inline_keyboard=[])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'page_{page_type}_{prev_page}_{query}'),
                InlineKeyboardButton(text=f'{current_page}/{total_pages}', callback_data=f'counter_{current_page}/{total_pages}'),
                InlineKeyboardButton(text='➡️', callback_data=f'page_{page_type}_{next_page}_{query}')
            ]
        ]
    )

def search_default_keyboard(is_filters_set: bool, chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Поиск', switch_inline_query_current_chat=f'{get_query_if_exists(chat_id)}'),
                InlineKeyboardButton(text=f'Фильтры{" ✅" if is_filters_set else ""}', callback_data='filters_add')
            ],
            [
                InlineKeyboardButton(text='Отправить ссылку', callback_data='link')
            ]
        ]
    )

def product_page_keyboard(chat_id: int, product_id: str, product_uuid: str, is_saved: bool) -> InlineKeyboardMarkup:
    saved_button_text = 'Добавить в избранное' if not is_saved else 'Удалить из избранного'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=saved_button_text, callback_data=f'saved_{product_id}')
            ],
            [
                InlineKeyboardButton(text='Посмотреть отзывы',
                                     url=f'https://t.me/products_searcher_bot?start=reviews={product_uuid}')
            ]
        ]
    )

def search_page_keyboard(search_query, filter_uuid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Поиск', switch_inline_query_current_chat=f'{search_query}')
            ],
            [
                InlineKeyboardButton(text='Вернуть фильтры', callback_data=f'reset_filters_{filter_uuid}')
            ]
        ]
    )

def reviews_keyboard(chat_id: int, product_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отзывы', web_app=WebAppInfo(url='https://teaching-jennet-heavily.ngrok-free.app/reviews.html'))
            ]
        ]
    )

def link_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отменить ввод')
            ]
        ],
        resize_keyboard = True
    )

def group_by_two(array: list) -> list:
    return [list(filter(None, group)) for group in zip_longest(*[iter(array)]*2)]

def filter_keyboard(list_number: int = 1,
                    product_filters: dict = None,
                    any_selected: dict = False,
                    switch_chat: bool | str = None,
                    chat_id: int = None) -> InlineKeyboardMarkup:
    inline_keyboard = []
    starting_place = (list_number - 1) * 10
    last_place = list_number * 10
    if product_filters:
        for group in group_by_two(list(product_filters.keys())[starting_place:last_place]):
            row = []
            for filter_name in group:
                icon = ''
                if any_selected.get(filter_name):
                    icon = ' ✅'
                row.append(InlineKeyboardButton(text=f'{filter_name}{icon}', callback_data=f'filters_set_{filter_name}_{list_number}'))
            inline_keyboard.append(row)
        if len(product_filters) > 10:
            pages_number = ceil((len(product_filters) + 2) / 10)
            inline_keyboard.append([
                InlineKeyboardButton(text='⬅️',
                                     callback_data=f'filters_{list_number - 1 if list_number > 1 else pages_number}'),
                InlineKeyboardButton(text=f'{list_number}/{pages_number}', callback_data=f'filters_counter_{list_number}'),
                InlineKeyboardButton(text='➡️',
                                     callback_data=f'filters_{list_number + 1 if list_number < pages_number else 1}')
            ])
    inline_keyboard.append([
        InlineKeyboardButton(text='Сбросить фильтры',
                             callback_data=f'reset_filters_{list_number}')
    ])
    if switch_chat is None:
        inline_keyboard.append([
            InlineKeyboardButton(text='Назад', callback_data='back_to_menu')
        ])
    else:
        query = user_queries.get(chat_id, {}).get('query', [''])[0]
        if switch_chat == 'later':
            pass
        elif switch_chat:
            inline_keyboard.append([
                InlineKeyboardButton(text='Вернуться к поиску', switch_inline_query=query)
            ])
        else:
            inline_keyboard.append([
                InlineKeyboardButton(text='Вернуться к поиску', switch_inline_query_current_chat=query)
            ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def filter_params_keyboard(filter_name: str,
                           filter_params: dict,
                           list_number: int = 1,
                           filters_list_number: int = 1) -> InlineKeyboardMarkup:
    inline_keyboard = []
    starting_place = (list_number - 1) * 10
    last_place = list_number * 10
    for group in group_by_two(list(filter_params.keys())[starting_place:last_place]):
        row = []
        for param in group:
            icon = ''
            if filter_params.get(param):
                icon = ' ✅'
            row.append(InlineKeyboardButton(text=f'{param}{icon}', callback_data=f'filters_set_{filter_name}_{param}_{list_number}'))
        inline_keyboard.append(row)
    if len(filter_params) > 10:
        pages_number = ceil((len(filter_params)) / 10)
        inline_keyboard.append([
            InlineKeyboardButton(text='⬅️',
                                 callback_data=f'params_{filter_name}_{list_number - 1 if list_number > 1 else pages_number}'),
            InlineKeyboardButton(text=f'{list_number}/{pages_number}', callback_data=f'params_counter_{list_number}'),
            InlineKeyboardButton(text='➡️',
                                 callback_data=f'params_{filter_name}_{list_number + 1 if list_number < pages_number else 1}')
        ])
    inline_keyboard.append([
        InlineKeyboardButton(text='Выбрать все', callback_data=f'filters_set_{filter_name}_all_{list_number}'),
        InlineKeyboardButton(text='Очистить выбор', callback_data=f'filters_set_{filter_name}_clear_{list_number}'),
    ])
    inline_keyboard.append([
        InlineKeyboardButton(text='Назад', callback_data=f'back_to_filters_{filters_list_number}')
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)