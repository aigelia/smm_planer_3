from gspread import service_account
from pathlib import Path


def get_google_table_records(path_to_google_credentials_file, google_table_url):
        client_info = Path(path_to_google_credentials_file)
        client = service_account(filename=client_info)

        table = client.open_by_url(google_table_url)
        sheet = table.sheet1

        return sheet.get_all_records()


# TODO: Предоставить пользователю credentials?