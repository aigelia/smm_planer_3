import os
import mimetypes
import re

import requests


def extract_drive_url(media_url):
    """Извлекает ID файла из ссылки на Google Drive."""
    patterns = [
        r'drive\.google\.com\/file\/d\/([^\/\?]+)',
        r'drive\.google\.com\/open\?id=([^&]+)',
        r'drive\.google\.com\/uc\?id=([^&]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, media_url)
        if match:
            return match.group(1)
    raise ValueError("ID файла Google Drive не найдено. Проверьте настройки доступа.")


def download_file(download_link):
    """Скачивает файл по ссылке и сохраняет как временный файл в директорию проекта."""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(download_link, headers=headers)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").split(";")[0]
    extension = mimetypes.guess_extension(content_type)

    filename = f"temp_download{extension}"
    save_path = os.path.join(os.getcwd(), filename)

    with open(save_path, 'wb') as f:
        f.write(response.content)

    return save_path, content_type


def get_image(media_url):
    """Определяет источник изображения, сохраняет файл и возвращает его тип и путь"""
    if 'drive.google.com' in media_url:
        file_id = extract_drive_url(media_url)
        download_link = f'https://drive.google.com/uc?export=download&id={file_id}'
    else:
        download_link = media_url

    save_path, content_type = download_file(download_link)

    if content_type == 'image/gif':
        media_type = 'gif'
    elif content_type.startswith('image/'):
        media_type = 'image'
    else:
        media_type = 'unknown'

    return save_path, media_type
