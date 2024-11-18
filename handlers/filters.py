from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from . import router
from utils import (filter_message, filter_keyboard,
                   search_message, search_default_keyboard,
                   filter_set_message, filter_params_keyboard)
from utils.constants import FILTERS
from bot import user_queries


@router.callback_query(lambda call: call.data.startswith('filters_counter_'))
async def filter_counter(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(
        f'Это {callback_query.data.split("_")[2]} страница фильтров',
        show_alert=True
    )

@router.callback_query(lambda call: call.data.startswith('params_counter_'))
async def params_counter(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(
        f'Это {callback_query.data.split("_")[2]} страница параметров фильтра',
        show_alert=True
    )

@router.callback_query(lambda call: call.data == 'filters_add')
async def filters_command_handler(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_text(
        filter_message(),
        reply_markup=filter_keyboard()
    )

@router.callback_query(lambda call: call.data.startswith('filters_set_'))
async def set_filter_page(callback_query: types.CallbackQuery) -> None:
    params = callback_query.data.split('_')
    filter_name = params[2]
    try:
        filter_param = params[3]
        list_number = params[4]
        list_number = int(list_number)
    except IndexError:
        filter_param = None
        list_number = 1
    if filter_param:
        user_id = callback_query.from_user.id
        user_queries[user_id] = user_queries.setdefault(user_id, {})
        user_queries[user_id]['filters'] = user_queries[user_id].setdefault('filters', {})
        user_queries[user_id]['filters'][filter_name] = user_queries[user_id]['filters'].setdefault(filter_name, [])
        if filter_param == 'all':
            user_queries[user_id]['filters'][filter_name] = FILTERS[filter_name].copy()
        elif filter_param == 'clear':
            user_queries[user_id]['filters'][filter_name].clear()
        elif filter_param in user_queries.get(user_id, {}).get('filters', {}).get(filter_name, []):
            user_queries[user_id]['filters'][filter_name].remove(filter_param)
        else:
            user_queries[user_id]['filters'][filter_name].append(filter_param)
    selected_parameters = user_queries.get(callback_query.from_user.id, {}).get('filters', {}).get(filter_name)
    try:
        await callback_query.message.edit_text(
            filter_set_message(filter_name, selected_parameters),
            reply_markup=filter_params_keyboard(filter_name, FILTERS[filter_name], selected_parameters, list_number)
        )
    except TelegramBadRequest:
        pass

@router.callback_query(lambda call: call.data.startswith('filters_'))
async def filter_navigation(callback_query: types.CallbackQuery) -> None:
    _, direction, filter_index = callback_query.data.split('_')
    filter_index = int(filter_index)
    if direction == 'left':
        new_filter_index = len(FILTERS) - 1 if filter_index == 0 else filter_index - 1
    else: # elif direction == "right":
        new_filter_index = 0 if filter_index == len(FILTERS) - 1 else filter_index + 1
    await send_filter_page(callback_query, new_filter_index)

@router.callback_query(lambda call: call.data.startswith('params_'))
async def params_navigation(callback_query: types.CallbackQuery) -> None:
    _, filter_name, list_number = callback_query.data.split('_')
    list_number = int(list_number)
    selected_parameters = user_queries.get(callback_query.from_user.id, {}).get('filters', {}).get(filter_name)
    await callback_query.message.edit_text(
        filter_set_message(filter_name, selected_parameters),
        reply_markup=filter_params_keyboard(filter_name, FILTERS[filter_name], selected_parameters, list_number)
    )

@router.callback_query(lambda call: call.data.startswith('back_to_'))
async def back_to(callback_query: types.CallbackQuery) -> None:
    path = callback_query.data.split('_')[2]
    if path == 'menu':
        await callback_query.message.edit_text(
            search_message(),
            reply_markup=search_default_keyboard()
        )
    else: #elif path == 'filters':
        await callback_query.message.edit_text(
            filter_message(),
            reply_markup=filter_keyboard()
        )