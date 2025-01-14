import logging

from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from . import router
from utils import (filter_message, filter_keyboard,
                   search_message, search_default_keyboard,
                   filter_set_message, filter_params_keyboard)
from utils.constants import FILTERS
from bot import user_queries
from data import DatabaseConnection, add_to_db


@router.callback_query(lambda call: call.data.startswith('filters_counter_'))
@add_to_db
async def filter_counter(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    await callback_query.answer(
        f'Это {callback_query.data.split("_")[2]} страница фильтров',
        show_alert=True
    )

@router.callback_query(lambda call: call.data.startswith('params_counter_'))
@add_to_db
async def params_counter(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    await callback_query.answer(
        f'Это {callback_query.data.split("_")[2]} страница параметров фильтра',
        show_alert=True
    )

@router.callback_query(lambda call: call.data == 'filters_add')
@add_to_db
async def filters_command_handler(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    filters = user_queries.setdefault(callback_query.from_user.id, {}).setdefault('filters', get_formatted_filter(FILTERS))
    any_selected = get_formatted_any_selected(filters)
    user_queries.setdefault(callback_query.from_user.id, {})['need_switch'] = None
    await callback_query.message.edit_text(
        filter_message(filters, any_selected),
        reply_markup=filter_keyboard(product_filters=filters, any_selected=any_selected)
    )

@router.callback_query(lambda call: call.data.startswith('filters_set_'))
@add_to_db
async def set_filter_page(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    params = callback_query.data.split('_')
    filter_name = params[2]
    try:
        filter_param = params[3]
        list_number = params[4]
        list_number = int(list_number)
    except IndexError:
        filter_param = None
        list_number = 1
    user_id = callback_query.from_user.id
    all_params = user_queries.setdefault(user_id, {}).setdefault('filters', get_formatted_filter(FILTERS)).get(
        filter_name).get('params')
    if filter_param:
        if filter_param == 'all':
            all_params.update({param: True for param in all_params})
        elif filter_param == 'clear':
            all_params.update({param: False for param in all_params})
        else:
            all_params[filter_param] = not(all_params.get(filter_param))
    user_queries[user_id]['filters'][filter_name]['any_selected'] = any(all_params.values())
    try:
        await callback_query.message.edit_text(
            filter_set_message(filter_name, all_params),
            reply_markup=filter_params_keyboard(filter_name, all_params, list_number)
        )
    except TelegramBadRequest:
        pass

@router.callback_query(lambda call: call.data.startswith('filters_'))
@add_to_db
async def filter_navigation(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    _, list_number = callback_query.data.split('_')
    list_number = int(list_number)
    filters = user_queries.get(callback_query.from_user.id, {}).get('filters')
    any_selected = get_formatted_any_selected(filters)
    await callback_query.message.edit_text(
        filter_message(filters, any_selected),
        reply_markup=filter_keyboard(list_number, filters, any_selected)
    )

@router.callback_query(lambda call: call.data.startswith('params_'))
@add_to_db
async def params_navigation(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    _, filter_name, list_number = callback_query.data.split('_')
    list_number = int(list_number)
    all_params = user_queries.get(callback_query.from_user.id, {}).get('filters', {}).get(filter_name, {}).get('params')
    await callback_query.message.edit_text(
        filter_set_message(filter_name, all_params),
        reply_markup=filter_params_keyboard(filter_name, all_params, list_number)
    )

@router.callback_query(lambda call: call.data.startswith('back_to_'))
@add_to_db
async def back_to(callback_query: types.CallbackQuery, logger: logging.Logger, db: DatabaseConnection) -> None:
    path = callback_query.data.split('_', maxsplit=2)[2]
    if path == 'menu':
        await callback_query.message.edit_text(
            search_message(),
            reply_markup=search_default_keyboard()
        )
    else: #elif path == 'filters':
        filters = user_queries.setdefault(callback_query.from_user.id, {}).setdefault('filters',
                                                                                      get_formatted_filter(FILTERS))
        any_selected = get_formatted_any_selected(filters)
        need_switch = user_queries.get(callback_query.from_user.id).get('need_switch', None)
        list_number = int(path.split('_')[1])
        await callback_query.message.edit_text(
            filter_message(filters, any_selected),
            reply_markup=filter_keyboard(list_number, filters, any_selected, need_switch, callback_query.from_user.id)
        )

def get_formatted_filter(filter_: dict) -> dict:
    formatted_filter = {}
    for key, value in filter_.items():
        formatted_filter[key] = {
            'params': {item: False for item in value},
            'any_selected': False
        }
    return formatted_filter

def get_formatted_any_selected(filters: dict) -> dict:
    return {filter_name: info.get('any_selected') for filter_name, info in filters.items()}