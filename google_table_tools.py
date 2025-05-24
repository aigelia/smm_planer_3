from pathlib import Path

import requests
from gspread import service_account


def get_google_table_records(path_to_google_credentials_file, google_table_url):
        client_info = Path(path_to_google_credentials_file)
        client = service_account(filename=client_info)

        table = client.open_by_url(google_table_url)
        sheet = table.sheet1

        return sheet.get_all_records()


def get_text_from_google_doc(google_doc_url):
        google_doc = requests.get(google_doc_url)
        google_doc.raise_for_status()
        return google_doc.text



# TODO: Предоставить пользователю credentials?

print(get_text_from_google_doc('https://docs.google.com/document/d/16Jhi7SWlCa2Ptpl6NCVy8YFRFOz3zMFPclh3Gcjq9iI/export?format=txt'))