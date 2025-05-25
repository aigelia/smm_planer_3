import requests


def get_image_upload_url(vk_access_token, vk_page_id):
    """Получает url для загрузки изображения на сервер."""

    vk_api_url = 'https://api.vk.com/method/photos.getWallUploadServer'

    query_parameters = {
        'group_id': vk_page_id,
        'access_token': vk_access_token,
        'v': '5.199'
    }

    image_upload_url = requests.post(vk_api_url, data=query_parameters)
    image_upload_url.raise_for_status()

    return image_upload_url.json()['response']['upload_url']


def upload_image(vk_image_path, image_upload_url):
    """Загружает изображение на сервер."""

    with open(vk_image_path, 'rb') as image:
        image_params = {
            'photo': image
        }

        uploaded_image = requests.post(image_upload_url, files=image_params)
        uploaded_image.raise_for_status()

        return uploaded_image.json()


def save_image_on_wall(vk_access_token, vk_page_id, uploaded_image):
    """Сохраняет изображение на стене."""

    vk_api_url = 'https://api.vk.com/method/photos.saveWallPhoto'

    query_params = {
        'group_id': vk_page_id,
        'access_token': vk_access_token,
        'v': '5.199',
        'server': uploaded_image['server'],
        'photo': uploaded_image['photo'],
        'hash': uploaded_image['hash']
    }

    saved_image = requests.post(vk_api_url, query_params)
    saved_image.raise_for_status()

    return saved_image.json()


def get_gif_upload_url(vk_access_token, vk_page_id):
    """Получает url для загрузки гифки на сервер."""

    vk_api_url = 'https://api.vk.com/method/docs.getWallUploadServer'

    query_params = {
        'group_id': vk_page_id,
        'access_token': vk_access_token,
        'v': '5.199'
    }

    gif_upload_url = requests.get(vk_api_url, params=query_params)
    gif_upload_url.raise_for_status()
    print(gif_upload_url.json())

    return gif_upload_url.json()['response']['upload_url']


def upload_gif(gif_upload_url, vk_gif_path):
    """Загружает гифку на сервер."""

    with open(vk_gif_path, 'rb') as gif:
        query_params = {'file': gif}

        uploaded_gif = requests.post(gif_upload_url, files=query_params)
        uploaded_gif.raise_for_status()

        return uploaded_gif.json()['file']


def save_doc(vk_access_token, uploaded_gif):
    """Сохраняет гифку для последующего постинга."""

    query_params = {
        'file': uploaded_gif,
        'access_token': vk_access_token,
        'v': '5.199'
    }

    saved_doc = requests.post('https://api.vk.com/method/docs.save', data=query_params)
    saved_doc.raise_for_status()

    return saved_doc.json()['response']['doc']


def publish_post_in_vk(vk_access_token, vk_page_id, media_type, saved_file=None, text=''):
    """Публикует контент на стене."""

    vk_api_url = 'https://api.vk.com/method/wall.post'

    if saved_file:
        if media_type == 'gif':
            owner_id = saved_file["owner_id"]
            photo_id = saved_file['id']
            attachments = f'doc{owner_id}_{photo_id}'
        if media_type == 'image':
            owner_id = saved_file['response'][0]['owner_id']
            photo_id = saved_file['response'][0]['id']
            attachments = f'photo{owner_id}_{photo_id}'

        query_parameters = {
            'owner_id': f'-{vk_page_id}',
            'message': text,
            'attachments': attachments,
            'access_token': vk_access_token,
            'v': '5.199'
        }
    else:
        query_parameters = {
            'owner_id': f'-{vk_page_id}',
            'message': text,
            'access_token': vk_access_token,
            'v': '5.199'
        }

    post_response = requests.post(vk_api_url, params=query_parameters)
    post_response.raise_for_status()

    return post_response.json()