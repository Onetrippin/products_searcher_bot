from aiogram import types

from . import router
from utils import filter_message, filter_keyboard, search_message, search_default_keyboard
from utils.constants import FILTERS
from bot import selected_filters, current_index

@router.callback_query(lambda call: call.data == 'filters_add')
async def filters_command_handler(callback_query: types.CallbackQuery) -> None:
    selected_filters[callback_query.from_user.id] = {} if not selected_filters.get(callback_query.from_user.id)\
        else selected_filters[callback_query.from_user.id]
    filter_index = 0
    current_index[callback_query.from_user.id] = filter_index
    await callback_query.message.edit_text(
        filter_message(),
        reply_markup=filter_keyboard()
    )

async def send_filter_page(callback_query: types.CallbackQuery, filter_index: int) -> None:
    current_index[callback_query.from_user.id] = filter_index
    message_text = filter_message()
    keyboard = filter_keyboard(filter_index, selected_filters[callback_query.from_user.id])
    await callback_query.message.edit_text(message_text, reply_markup=keyboard)

@router.callback_query(lambda call: call.data.startswith('filter_'))
async def filter_navigation(callback_query: types.CallbackQuery) -> None:
    _, direction, filter_index = callback_query.data.split('_')
    filter_index = int(filter_index)
    if direction == 'left':
        new_filter_index = len(FILTERS) - 1 if filter_index == 0 else filter_index - 1
    else: # elif direction == "right":
        new_filter_index = 0 if filter_index == len(FILTERS) - 1 else filter_index + 1
    await send_filter_page(callback_query, new_filter_index)

@router.callback_query(lambda call: call.data == 'select_all')
async def select_all_filters(callback_query: types.CallbackQuery) -> None:
    filter_name = list(FILTERS.keys())[current_index[callback_query.from_user.id]]
    selected_filters[callback_query.from_user.id][filter_name] = FILTERS[filter_name].copy()
    await send_filter_page(callback_query, current_index[callback_query.from_user.id])

@router.callback_query(lambda call: call.data.startswith('select_'))
async def select_filter_option(callback_query: types.CallbackQuery) -> None:
    _, filter_name, option = callback_query.data.split('_')
    if filter_name not in selected_filters[callback_query.from_user.id]:
        selected_filters[callback_query.from_user.id][filter_name] = []
    if option in selected_filters[callback_query.from_user.id][filter_name]:
        selected_filters[callback_query.from_user.id][filter_name].remove(option)
    else:
        selected_filters[callback_query.from_user.id][filter_name].append(option)
    await send_filter_page(callback_query, current_index[callback_query.from_user.id])

@router.callback_query(lambda call: call.data == 'clear_selection')
async def clear_filters(callback_query: types.CallbackQuery) -> None:
    filter_name = list(FILTERS.keys())[current_index[callback_query.from_user.id]]
    selected_filters[callback_query.from_user.id][filter_name] = []
    await send_filter_page(callback_query, current_index[callback_query.from_user.id])

@router.callback_query(lambda call: call.data == 'back_to_menu')
async def back_to_menu(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.edit_text(
        search_message(),
        reply_markup=search_default_keyboard()
    )

@router.callback_query(lambda call: call.data.startswith('filters_counter_'))
async def filter_counter(callback_query: types.CallbackQuery) -> None:
    await callback_query.answer(
        f'Это {callback_query.data.split("_")[2]} страница параметров данного фильтра',
        show_alert=True
    )
