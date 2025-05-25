from dotenv import load_dotenv
from text_helper import replace_quotes_and_dashes
from media_helper import get_image
import os
import requests
import json


load_dotenv()

application_id = os.environ['OK_APP_ID']
application_key = os.environ['OK_APP_KEY']
application_secret_key = os.environ['OK_APP_SECRET']
access_token = os.environ['OK_ACCESS_TOKEN']
session_secret_key = os.environ['ok_session_secret']
group_ids = ['70000035422780', '70000035460156']


def get_upload_url(group_id):
    payload = {
        'method': 'photosV2.getUploadUrl',
        'application_id': application_id,
        'application_key': application_key,
        'access_token': access_token,
        'gid': group_id,
    }
    response = requests.post('https://api.ok.ru/fb.do', params=payload)
    response.raise_for_status()
    upload_link = response.json()['upload_url']
    return upload_link


def fetch_image_to_memory(file_path, group_id):
    if not file_path or not os.path.exists(file_path):
        return None

    upload_url = get_upload_url(group_id)

    with open(file_path, 'rb') as f:
        files = {
            'photo': (os.path.basename(file_path), f)
        }
        upload_response = requests.post(upload_url, files=files)
        upload_response.raise_for_status()

    return upload_response.json()


def post_to_group(group_id, photo_tokens=None, text=None,):
    media = []

    if text:
        cleaned_text = replace_quotes_and_dashes(text)
        media.append({"type": "text", "text": cleaned_text})

    if photo_tokens:
        media.append({
            "type": "photo",
            "list": [{"id": token} for token in photo_tokens]
        })

    if not media:
        return None

    attachment = {"media": media}
    attachment_json = json.dumps(attachment, ensure_ascii=False)

    payload = {
        'method': 'mediatopic.post',
        'application_id': application_id,
        'application_key': application_key,
        'access_token': access_token,
        'type': 'GROUP_THEME',
        'gid': group_id,
        'attachment': attachment_json,
    }

    response = requests.post("https://api.ok.ru/fb.do", params=payload)
    response.raise_for_status()
    return response.json()


def main():
    image_input = input("Введите ссылку на изображение или путь к файлу (оставьте пустым если без фото): ").strip()
    text = input("Введите текст поста: ").strip()

    file_path = None
    temp_downloaded = False

    if image_input:
        file_path, _ = get_image(image_input)
        if not os.path.samefile(os.path.dirname(file_path), os.getcwd()):
            temp_downloaded = True
        elif file_path.startswith(os.getcwd()) and "temp_download" in file_path:
            temp_downloaded = True

    for group_id in group_ids:
        photo_tokens = None
        if file_path:
            upload_data = fetch_image_to_memory(file_path, group_id)
            if upload_data and 'photos' in upload_data:
                photo_tokens = [photo['token'] for photo in upload_data['photos'].values()]

        post_to_group(group_id, photo_tokens, text if text else None)

    if temp_downloaded and os.path.exists(file_path):
        os.remove(file_path)

if __name__ in "__main__":
    main()
