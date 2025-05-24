import io
import os

import requests
from dotenv import load_dotenv


def get_server_upload_url(vk_access_token, vk_page_id):
    vk_api_url = 'https://api.vk.com/method/photos.getWallUploadServer'

    query_parameters = {
        'group_id': vk_page_id,
        'access_token': vk_access_token,
        'v': '5.199'
    }

    server_upload_url = requests.post(vk_api_url, data=query_parameters)
    server_upload_url.raise_for_status()

    return server_upload_url.json()['response']['upload_url']


def send_image_to_server(vk_image_url, server_upload_url):
    image_response = requests.get(vk_image_url)
    image_response.raise_for_status()
    image_response = image_response.content

    image_bytes = io.BytesIO(image_response)

    image_bytes.name = "photo.jpg"

    image_params = {
        "photo": (image_bytes.name, image_bytes, "image/jpeg")
    }

    uploaded_image = requests.post(server_upload_url, files=image_params)
    uploaded_image.raise_for_status()

    return uploaded_image.json()


def save_image_on_wall(vk_access_token, vk_page_id, uploaded_image):
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


def publish_post_in_vk(vk_access_token, vk_page_id, saved_image, text, date_time):
    owner_id = saved_image['response'][0]['owner_id']
    photo_id = saved_image['response'][0]['id']

    vk_api_url = 'https://api.vk.com/method/wall.post'

    query_parameters = {
        'owner_id': f'-{vk_page_id}',
        'message': text,
        'attachments': f'photo{owner_id}_{photo_id}',
        'publish_date': date_time,
        'access_token': vk_access_token,
        'v': '5.199'
    }

    post_response = requests.post(vk_api_url, params=query_parameters)
    post_response.raise_for_status()

    return post_response.json()


def main():
    load_dotenv()
    vk_access_token = os.environ['VK_ACCESS_TOKEN']

    vk_post_ids = ''
    vk_page_ids = ['230572126', '230578699']
    vk_publication_dates = ''
    vk_publication_times = ''
    vk_google_doc_urls = ''
    vk_image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    vk_successful_publications = ''

    server_upload_url = get_server_upload_url(vk_access_token, vk_page_ids[0])
    uploaded_image = send_image_to_server(vk_image_url, server_upload_url)
    saved_image = save_image_on_wall(vk_access_token, vk_page_ids[0], uploaded_image)
    print(publish_post_in_vk(vk_access_token, vk_page_ids[0], saved_image, '', 1747929439))


if __name__ == '__main__':
    main()


# TODO: Сделать проверку подключения к серверу и если проблемы,
#  через какое то время попробовать еще раз

# TODO: Учесть формат картинки, она может быть гифкой