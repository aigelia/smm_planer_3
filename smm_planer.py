import os

from pprint import pprint

from dotenv import load_dotenv

from google_sheet_tools import get_google_table_records


def get_unpublished_vk_records(google_table_records):
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


def main():
    vk_published_cell, tg_published_cell, ok_published_cell = 'G', 'K', 'O'

    try:
        load_dotenv()
        table_url = os.environ['GOOGLE_TABLE_LINK']

        path_to_google_credentials_file = 'google_client.json'

        all_google_table_records = get_google_table_records(
            path_to_google_credentials_file, table_url
        )

        all_unpublished_vk_records = []
        all_unpublished_ok_records = []
        all_unpublished_tg_records = []


        for google_table_records in all_google_table_records:
            unpublished_vk_records = get_unpublished_vk_records(google_table_records)

            if unpublished_vk_records:
                all_unpublished_vk_records.append(unpublished_vk_records)


    except:
        print('ошибка')


if __name__ == '__main__':
    main()

# TODO: Скрипт запускается каждую минуту
# TODO: В случае ошибки скрипт запускается повторно не ломаясь