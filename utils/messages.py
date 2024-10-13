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

def format_saved_message(saved_products: list, page_number: str = '1') -> str:
    return (
        '<b>Избранное</b>'
        '\n\n' +
        '\n\n'.join([
            f'⭐ <code>{saved_products[i]["product_name"]}</code> | '
            f'<b>Последняя цена</b>: <code>{saved_products[i]["price"]}</code> | '
            f'<b>Магазин</b>: <code>{saved_products[i]["shop"]}</code> '
            f'<b>(<a href="t.me/pavel">страница товара</a>)</b>'
            for i in range(((int(page_number) - 1) * LINES_PER_PAGE),
                           min(int(page_number) * LINES_PER_PAGE, len(saved_products)))
        ])
    )

def format_history_message(search_history: list, page_number: str = '1') -> str:
    return (
        '<b>История поиска</b>'
        '\n\n' +
        '\n\n'.join([
            f'🔎 <i><b><u>Поиск</u></b> ➜ '
            f'<code>{search_history[i]["input_string"]}</code> '
            f'<b>(<a href="t.me/pavel">искать снова</a>)</b></i>'
            if search_history[i].get("input_string")
            else
            f'🛒 <b><u>Товар</u></b> ➜ '
            f'<code>{search_history[i]["product_name"]}</code> | '
            f'<b>Цена</b>: <code>{search_history[i]["price"]}</code> | '
            f'<b>Магазин</b>: <code>{search_history[i]["shop"]}</code> '
            f'<b>(<a href="t.me/pavel">страница товара</a>)</b>'
            for i in range(((int(page_number) - 1) * LINES_PER_PAGE),
                           min(int(page_number) * LINES_PER_PAGE, len(search_history)))
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