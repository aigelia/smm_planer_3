import os

from dotenv import load_dotenv
from gspread import service_account


load_dotenv()
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
GOOGLE_TABLE_LINK = os.getenv('GOOGLE_TABLE_LINK')
if not GOOGLE_CREDENTIALS or not GOOGLE_TABLE_LINK:
    raise EnvironmentError(
        "Переменные окружения GOOGLE_CREDENTIALS и GOOGLE_TABLE_LINK должны быть заданы в .env"
    )


def get_google_table_records():
    """Получает все записи Google таблицы в виде списка словарей."""
    client = service_account(filename=GOOGLE_CREDENTIALS)
    table = client.open_by_url(GOOGLE_TABLE_LINK)
    sheet = table.sheet1
    return sheet.get_all_records()


def write_data_in_table_cell(post_id: int, cell_letter: str, value: str = 'Опубликовано'):
    """Добавляет отметку о публикации."""
    client = service_account(filename=GOOGLE_CREDENTIALS)
    sheet = client.open_by_url(GOOGLE_TABLE_LINK).sheet1
    target_cell = f"{cell_letter}{post_id + 1}"
    sheet.update_acell(target_cell, value)
