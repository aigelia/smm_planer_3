from dotenv import load_dotenv
import os
import json
import requests


load_dotenv()

APPLICATION_ID = os.environ['OK_APP_ID']
APPLICATION_KEY = os.environ['OK_APP_KEY']
APPLICATION_SECRET_KEY = os.environ['OK_APP_SECRET']
ACCESS_TOKEN = os.environ['OK_ACCESS_TOKEN']
SESSION_SECRET_KEY = os.environ['ok_session_secret']


def get_upload_url(group_id):
    payload = {
        'method': 'photosV2.getUploadUrl',
        'application_id': APPLICATION_ID,
        'application_key': APPLICATION_KEY,
        'access_token': ACCESS_TOKEN,
        'gid': group_id,
    }
    response = requests.post('https://api.ok.ru/fb.do', params=payload)
    response.raise_for_status()
    return response.json()['upload_url']


def upload_photo_from_path(photo_path, group_id):
    if not photo_path or not os.path.isfile(photo_path):
        return None

    upload_url = get_upload_url(group_id)
    with open(photo_path, 'rb') as f:
        files = {'photo': ('photo.jpg', f)}
        upload_response = requests.post(upload_url, files=files)
        upload_response.raise_for_status()
        return upload_response.json()


def post_to_group(group_id, photo_tokens=None, text=None):
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
        'application_id': APPLICATION_ID,
        'application_key': APPLICATION_KEY,
        'access_token': ACCESS_TOKEN,
        'type': 'GROUP_THEME',
        'gid': group_id,
        'attachment': attachment_json,
    }

    response = requests.post("https://api.ok.ru/fb.do", params=payload)
    response.raise_for_status()
    return response.json()


def publish_post_to_ok(text=None, photo_path=None, group_ids=None):
    if group_ids is None:
        raise ValueError("Список групп не задан.")

    results = []

    for group_id in group_ids:
        photo_tokens = None

        if photo_path:
            upload_data = upload_photo_from_path(photo_path, group_id)
            if upload_data and 'photos' in upload_data:
                photo_tokens = [photo['token'] for photo in upload_data['photos'].values()]

        result = post_to_group(group_id, photo_tokens, text)
        results.append(result)

    return results[0] if len(results) == 1 else results
