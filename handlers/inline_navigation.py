from aiogram import types

from utils import saved_message, page_navigation_keyboard, format_history_message
from data import get_search_history
from . import router

@router.callback_query(lambda call: call.data.startswith('page_saved'))
async def saved_page_changer(callback_query: types.CallbackQuery) -> None:
    _, page_type, current_page, _ = callback_query.data.split('_')
    await callback_query.message.edit_text(
        saved_message(callback_query.message, current_page),
        reply_markup=page_navigation_keyboard(page_type, 100, int(current_page))
    )

@router.callback_query(lambda call: call.data.startswith('page_history'))
async def history_page_changer(callback_query: types.CallbackQuery) -> None:
    search_history = await get_search_history(callback_query.message.chat.id)
    _, page_type, current_page, _ = callback_query.data.split('_')
    await callback_query.message.edit_text(
        format_history_message(search_history, current_page),
        reply_markup=page_navigation_keyboard(page_type, len(search_history), int(current_page))
    )

@router.callback_query(lambda call: call.data.startswith('counter_'))
async def page_counter(callback_query: types.CallbackQuery) -> None:
    current_page, total_page = callback_query.data.split('_')[1].split('/')
    await callback_query.answer(
        f'Ты смотришь {current_page} страницу из {total_page}',
        show_alert=True
    )