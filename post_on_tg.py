import os
from dotenv import load_dotenv
import telegram

def publish_on_telegram(channel_id, post_text, media_path=None):
    load_dotenv()
    tg_token = os.environ['TG_TOKEN']
    bot = telegram.Bot(token=tg_token)

    if media_path and os.path.exists(media_path):
        mode = 'animation' if media_path.lower().endswith('.gif') else 'photo'
        with open(media_path, 'rb') as f:
            if mode == 'animation':
                bot.send_animation(chat_id=channel_id, animation=f, caption=post_text)
            else:
                bot.send_photo(chat_id=channel_id, photo=f, caption=post_text)
    else:
        bot.send_message(chat_id=channel_id, text=post_text)
