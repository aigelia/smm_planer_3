from io import BytesIO
from dotenv import load_dotenv
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


def fetch_image_to_memory(photo_url, group_id):
    if not photo_url:
        return None

    upload_url = get_upload_url(group_id)
    response = requests.get(photo_url)
    response.raise_for_status()
    photo = response.content
    file_like = BytesIO(photo)
    files = {
        'photo': ('photo.jpg', file_like)
    }
    upload_response = requests.post(upload_url, files=files)
    media_id = upload_response.json()
    return media_id


def post_to_group(group_id, photo_tokens=None, text=None,):
    media = []

    if text:
        media.append({"type": "text", "text": text})

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
    return response.json()


def main():
    photo_url = input("Введите ссылку на фото (оставьте пустым если без фото): ").strip()
    text = input("Введите текст поста (оставьте пустым если без текста): ").strip()

    results = []
    for group_id in group_ids:
        photo_tokens = None
        if photo_url:
            upload_data = fetch_image_to_memory(photo_url, group_id)
            if upload_data and 'photos' in upload_data:
                photo_tokens = [photo['token'] for photo in upload_data['photos'].values()]

        result = post_to_group(group_id, photo_tokens, text if text else None)
        results.append(result)

    return results[0] if len(results) == 1 else results

if __name__ in "__main__":
    main()
