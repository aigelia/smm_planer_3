import os
from dotenv import load_dotenv
import telegram


def publish_on_telegram(channel_id, post_text, media_path=None):
    load_dotenv()
    tg_token = os.environ['TG_TOKEN']
    bot = telegram.Bot(token=tg_token)

    if media_path:
        if media_path.endswith('.gif'):
            bot.send_animation(chat_id=channel_id, animation=media_path, caption=post_text)
        else:
            bot.send_photo(chat_id=channel_id, photo=media_path, caption=post_text)
    else:
        bot.send_message(chat_id=channel_id, text=post_text)
