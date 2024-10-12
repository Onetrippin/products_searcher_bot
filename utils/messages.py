from aiogram.types import Message

from utils.constants import LINES_PER_PAGE

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

def format_history_message(search_history: list, page_number: str = '1') -> str:
    return (
        'История поиска'
        '\n\n' +
        '\n'.join([
            f'{i + 1}. Поиск: {search_history[i]["input_string"]} искать снова'
            if search_history[i].get("input_string")
            else f'{i + 1}. Товар: {search_history[i]["product_name"]} Цена: {search_history[i]["price"]} Магазин: {search_history[i]["shop"]} посмотреть страницу товара'
            for i in range(((int(page_number) - 1) * LINES_PER_PAGE), min(int(page_number) * LINES_PER_PAGE, len(search_history)))
        ])
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