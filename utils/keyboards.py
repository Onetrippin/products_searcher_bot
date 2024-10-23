from typing import Tuple
from itertools import zip_longest
from math import ceil

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.types.web_app_info import WebAppInfo

from .constants import LINES_PER_PAGE, FILTERS


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
    if total_pages == 1:
        return
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'page_{page_type}_{prev_page}_{request_id}'),
                InlineKeyboardButton(text=f'{current_page}/{total_pages}', callback_data=f'counter_{current_page}/{total_pages}'),
                InlineKeyboardButton(text='➡️', callback_data=f'page_{page_type}_{next_page}_{request_id}')
            ]
        ]
    )

def search_default_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Поиск', switch_inline_query_current_chat=''),
                InlineKeyboardButton(text='Фильтры', callback_data='filters_add')
            ],
            [
                InlineKeyboardButton(text='Отправить ссылку', callback_data='link')
            ]
        ]
    )

def product_page_keyboard(chat_id: int, product_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить в избранное', callback_data=f'saved_{product_name}')
            ],
            [
                InlineKeyboardButton(text='Посмотреть отзывы',
                                     url=f'https://t.me/products_searcher_bot?start=reviews=None')
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


# def filter_keyboard(filter_index: int, selected_filters: dict) -> InlineKeyboardMarkup:
#     filter_name = list(FILTERS.keys())[filter_index]
#     filter_name_left = list(FILTERS.keys())[filter_index-1] \
#         if filter_index > 0 \
#         else list(FILTERS.keys())[len(FILTERS.keys())-1]
#     filter_name_right = list(FILTERS.keys())[filter_index+1] \
#         if filter_index < len(FILTERS.keys()) - 1 \
#         else list(FILTERS.keys())[0]
#     filter_options = FILTERS[filter_name]
#     inline_keyboard = [
#         [
#             InlineKeyboardButton(text=f'{filter_name_left} ←', callback_data=f'filter_left_{filter_index}'),
#             InlineKeyboardButton(text=filter_name, callback_data=f'filters_counter_{filter_name}'),
#             InlineKeyboardButton(text=f'→ {filter_name_right}', callback_data=f'filter_right_{filter_index}')
#         ]
#     ]
#     for group in group_options_by_two(filter_options):
#         buttons = []
#         for option in group:
#             icon = '✅' if option in selected_filters.get(filter_name, []) else '❌'
#             buttons.append(
#                 InlineKeyboardButton(text=f'{option} {icon}', callback_data=f'select_{filter_name}_{option}'))
#         inline_keyboard.append(buttons)
#     inline_keyboard.append([
#         InlineKeyboardButton(text='⬅️', callback_data=f'filter_left_{filter_index}'),
#         InlineKeyboardButton(text='страница 1/1', callback_data=f'filters_counter_{filter_name}'),
#         InlineKeyboardButton(text='➡️', callback_data=f'filter_right_{filter_index}')
#     ])
#     inline_keyboard.append([
#         InlineKeyboardButton(text='Выбрать все', callback_data='select_all'),
#         InlineKeyboardButton(text='Очистить выбор', callback_data='clear_selection'),
#     ])
#     inline_keyboard.append([
#         InlineKeyboardButton(text='Назад', callback_data='back_to_menu')
#     ])
#     return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def filter_keyboard(product_filters: list = None, list_number: int = 1) -> InlineKeyboardMarkup:
    inline_keyboard = []
    starting_place = (list_number - 1) * 10
    last_place = list_number * 10
    if list_number == 1:
        inline_keyboard.append(
            [
                InlineKeyboardButton(text='Тип', callback_data=f'filters_set_Тип'),
                InlineKeyboardButton(text='Магазин', callback_data=f'filters_set_Магазин')
            ])
        starting_place = 2
    if product_filters:
        for group in group_by_two(product_filters[starting_place:last_place]):
            row = []
            for filter_ in group:
                row.append(InlineKeyboardButton(text=filter_, callback_data=f'filters_set_{filter_}'))
            inline_keyboard.append(row)
    if len(product_filters) > 8:
        pages_number = ceil((len(product_filters) + 2) / 10)
        inline_keyboard.append([
            InlineKeyboardButton(text='⬅️',
                                 callback_data=f'filters_left_{list_number - 1 if list_number > 1 else pages_number}'),
            InlineKeyboardButton(text=f'{list_number}/{pages_number}', callback_data=f'filters_counter_{list_number}'),
            InlineKeyboardButton(text='➡️',
                                 callback_data=f'filters_right_{list_number + 1 if list_number < pages_number else 1}')
        ])
    inline_keyboard.append([
        InlineKeyboardButton(text='Назад', callback_data='back_to_menu')
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def filter_params_keyboard(filter_params: list, list_number: int = 1) -> InlineKeyboardMarkup:
    inline_keyboard = []
    starting_place = (list_number - 1) * 10
    last_place = list_number * 10
    for group in group_by_two(filter_params[starting_place:last_place]):
        row = []
        for filter_ in group:
            row.append(InlineKeyboardButton(text=filter_, callback_data=f'filters_set_{filter_}'))
        inline_keyboard.append(row)
    if len(filter_params) > 10:
        pages_number = ceil((len(filter_params)) / 10)
        inline_keyboard.append([
            InlineKeyboardButton(text='⬅️',
                                 callback_data=f'params_left_{list_number - 1 if list_number > 1 else pages_number}'),
            InlineKeyboardButton(text=f'{list_number}/{pages_number}', callback_data=f'params_counter_{list_number}'),
            InlineKeyboardButton(text='➡️',
                                 callback_data=f'params_right_{list_number + 1 if list_number < pages_number else 1}')
        ])
    inline_keyboard.append([
        InlineKeyboardButton(text='Назад', callback_data='back_to_filters')
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)