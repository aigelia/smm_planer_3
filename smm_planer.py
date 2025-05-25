import os

from dotenv import load_dotenv

#import post_on_ok
import post_on_vk
import post_on_tg
from google_sheet_tools import get_google_table_records, write_data_in_table_cell
from media_helper import extract_drive_url, download_file, get_image
from text_helper import extract_doc_id, fetch_google_doc_text, replace_quotes_and_dashes


def get_unpublished_vk_records(google_table_records):
    """Получает словарь с данными для vk из одной строки таблицы."""

    vk_fields = (
        'post_id',
        'google_doc',
        'media',
        'vk_pages',
        'vk_date',
        'vk_time',
        'vk_published',
    )

    if not google_table_records.get('vk_pages') and google_table_records.get('vk_published'):
        return {}

    return {vk_field: google_table_records[vk_field] for vk_field in vk_fields}


def get_unpublished_ok_records(google_table_records):
    """Получает словарь с данными для ok из одной строки таблицы."""

    ok_fields = (
        'post_id',
        'google_doc',
        'media',
        'ok_pages',
        'ok_date',
        'ok_time',
        'ok_published',
    )

    if not google_table_records.get('ok_pages') and google_table_records.get('ok_published'):
        return {}

    return {ok_field: google_table_records[ok_field] for ok_field in ok_fields}


def get_unpublished_tg_records(google_table_records):
    """Получает словарь с данными для tg из одной строки таблицы."""

    tg_fields = (
        'post_id',
        'google_doc',
        'media',
        'tg_pages',
        'tg_date',
        'tg_time',
        'tg_published',
    )

    if not google_table_records.get('tg_pages') and google_table_records.get('tg_published'):
        return {}

    return {tg_field: google_table_records[tg_field] for tg_field in tg_fields}


def main():
    vk_published_cell, tg_published_cell, ok_published_cell = 'G', 'K', 'O'

    load_dotenv()
    table_url = os.environ['GOOGLE_TABLE_LINK']
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    #ok_access_token = os.environ['OK_ACCESS_TOKEN']
    #tg_access_token = os.environ['TG_TOKEN']

    path_to_google_credentials_file = 'google_client.json' ## Норм или нет???

    all_google_table_records = get_google_table_records(
        path_to_google_credentials_file, table_url
    )

    all_unpublished_vk_records = []
    all_unpublished_ok_records = []
    all_unpublished_tg_records = []


    for google_table_records in all_google_table_records:
        unpublished_vk_records = get_unpublished_vk_records(google_table_records)
        #unpublished_ok_records = get_unpublished_ok_records(google_table_records)
        #unpublished_tg_records = get_unpublished_tg_records(google_table_records)

        if unpublished_vk_records:
            all_unpublished_vk_records.append(unpublished_vk_records)
        # if unpublished_ok_records:
        #     all_unpublished_ok_records.append(unpublished_ok_records)
        # if unpublished_tg_records:
        #     all_unpublished_tg_records.append(unpublished_tg_records)



if __name__ == '__main__':
    main()

# TODO: Скрипт запускается каждую минуту
# TODO: В случае ошибки скрипт запускается повторно не ломаясь