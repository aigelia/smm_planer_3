import os
from dotenv import load_dotenv
import telegram


def publish_on_telegram():
    load_dotenv()
    tg_token = os.getenv('TG_TOKEN')
    channel_id = '@smm_planer_test_r1'
    bot = telegram.Bot(token=tg_token)

    post_text = 'Hello world'
    post_media_url = 'https://media.giphy.com/media/dzaUX7CAG0Ihi/giphy.gif'

    if post_media_url:
        try:
            if post_media_url.lower().endswith('.gif'):
                bot.send_animation(chat_id=channel_id, animation=post_media_url, caption=post_text)
            else:
                bot.send_photo(chat_id=channel_id, photo=post_media_url, caption=post_text)
        except telegram.error.TelegramError as e:
            print(f'Ошибка при отправке медиа: {e}')
            bot.send_message(chat_id=channel_id, text=post_text)
    else:
        bot.send_message(chat_id=channel_id, text=post_text)
