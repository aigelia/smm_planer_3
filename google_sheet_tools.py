from pathlib import Path

import requests
from gspread import service_account


def get_google_table_records(path_to_google_credentials_file, google_table_url):
        client_info = Path(path_to_google_credentials_file)
        client = service_account(filename=client_info)

        table = client.open_by_url(google_table_url)
        sheet = table.sheet1

        return sheet.get_all_records()


def write_data_in_table_cell(path_to_google_credentials_file, google_table_url, post_id, cell_letter):
        client_info = Path(path_to_google_credentials_file)
        client = service_account(filename=client_info)

        table = client.open_by_url(google_table_url)
        sheet = table.sheet1

        sheet.update(f'{cell_letter}{str(post_id)}', 'Опубликовано')


# # TODO: Предоставить пользователю credentials?
