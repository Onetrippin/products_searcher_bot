from typing import Tuple
import logging

from data import DatabaseConnection


def get_data_info(data: dict) -> Tuple[logging.Logger, DatabaseConnection]:
    return data.get('logger'), data.get('db')