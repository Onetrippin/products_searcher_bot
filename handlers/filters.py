import logging

from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from services import form_filters, actualize_filters
from utils.constants import FILTERS
from . import router
from utils import (filter_message, filter_keyboard,
                   search_message, search_default_keyboard,
                   filter_set_message, filter_params_keyboard)
from bot import user_queries
from data import DatabaseConnection, add_to_db, log_filters


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
    filters = user_queries.setdefault(callback_query.from_user.id, {}).setdefault('filters',
                                                                                  await form_filters(
                                                                                      db, callback_query.from_user.id))
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
        list_number = prev_list_number = int(list_number)
    except IndexError:
        filter_param = None
        list_number = 1
        prev_list_number = int(params[3])
    user_id = callback_query.from_user.id
    all_params = (user_queries.setdefault(user_id, {}).setdefault('filters',
                                                                 await form_filters(
                                                                     db,
                                                                     callback_query.from_user.id)).
                  get(filter_name).get('params'))
    if len(all_params) == 1:
        param_value = next(iter(all_params.keys()))
        user_queries[user_id]['filters'][filter_name]['params'][param_value] = not all_params.get(param_value)
        user_queries[user_id]['filters'][filter_name]['any_selected'] = not user_queries[user_id]['filters'][filter_name]['any_selected']
        filters = user_queries.get(user_id, {}).get('filters')
        any_selected = get_formatted_any_selected(filters)
        await callback_query.message.edit_text(
            filter_message(filters, any_selected),
            reply_markup=filter_keyboard(prev_list_number, filters, any_selected)
        )
        return
    if filter_param:
        if filter_name == 'Тип' and filter_param != 'clear':
            prev_type = next((param for param, value in all_params.items() if value), None)
            if filter_param == 'all':
                await callback_query.answer(
                    'Можно указать только один тип товара!',
                    show_alert=True
                )
                return
            if prev_type and prev_type != filter_param:
                all_params[prev_type] = not all_params.get(prev_type)
            all_params[filter_param] = not (all_params.get(filter_param))
        elif filter_param == 'all':
            all_params.update({param: True for param in all_params})
        elif filter_param == 'clear':
            all_params.update({param: False for param in all_params})
        else:
            all_params[filter_param] = not(all_params.get(filter_param))
        user_queries[user_id]['filters'][filter_name]['any_selected'] = any(all_params.values())
    filters_list_number = (list(user_queries.get(callback_query.from_user.id).get('filters').keys()).index(filter_name) // 10) + 1
    try:
        await callback_query.message.edit_text(
            filter_set_message(filter_name, all_params),
            reply_markup=filter_params_keyboard(filter_name, all_params, list_number, filters_list_number)
        )
    except TelegramBadRequest:
        pass
    else:
        await actualize_filters(db,
                                user_id,
                                True if filter_param and filter_name == 'Тип' else False)
        await log_filters(db, user_id, user_queries.get(user_id).get('filters'))

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
    filters_list_number = (list(user_queries.get(callback_query.from_user.id).get('filters').keys()).index(filter_name) // 10) + 1
    await callback_query.message.edit_text(
        filter_set_message(filter_name, all_params),
        reply_markup=filter_params_keyboard(filter_name, all_params, list_number, filters_list_number)
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
                                                                                      await form_filters(
                                                                                          db,
                                                                                          callback_query.from_user.id))
        any_selected = get_formatted_any_selected(filters)
        need_switch = user_queries.get(callback_query.from_user.id).get('need_switch', None)
        list_number = int(path.split('_')[1])
        await callback_query.message.edit_text(
            filter_message(filters, any_selected),
            reply_markup=filter_keyboard(list_number, filters, any_selected, need_switch, callback_query.from_user.id)
        )

def get_formatted_any_selected(filters: dict) -> dict:
    return {filter_name: info.get('any_selected') for filter_name, info in filters.items()}