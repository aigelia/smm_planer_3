import re

import requests


def extract_doc_id(doc_url):
    """Извлекает ID Google-документа из URL."""
    match = re.search(r'document/d/([a-zA-Z0-9_-]+)', doc_url)
    return match.group(1)


def fetch_google_doc_text(doc_url):
    """Возвращает текст Google-документа, экспортируя его как .txt."""
    doc_id = extract_doc_id(doc_url)
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"

    response = requests.get(export_url)
    response.raise_for_status()
    return response.text


def replace_quotes_and_dashes(text):
    """Исправляет кавычки на "ёлочки" и дефисы на тире."""
    text = text.replace(' - ', ' — ')
    quotes = ['"', '„', '“', '”']
    result = []
    temp = 0

    for symbol in text:
        if symbol in quotes and temp == 0:
            symbol = '«'
            temp = 1
        elif symbol in quotes and temp == 1:
            symbol = '»'
            temp = 0
        result.append(symbol)
    return ''.join(result)
