import os
import time
from datetime import datetime

from dotenv import load_dotenv

import post_on_tg
import post_on_vk
import post_on_ok
from google_sheets_helper import get_google_table_records, write_data_in_table_cell
from media_helper import get_image
from text_helper import fetch_google_doc_text, replace_quotes_and_dashes


def get_unpublished_records(records, platform):
    """
    Возвращает список словарей для постов, которые ещё не опубликованы
    на платформе platform: 'vk', 'tg' или 'ok'.
    """
    base_fields = ['post_id', 'google_doc', 'media']
    pages_field = f"{platform}_pages"
    date_field = f"{platform}_date"
    time_field = f"{platform}_time"
    published_field = f"{platform}_published"

    fields = base_fields + [pages_field, date_field, time_field, published_field]
    return [
        {fld: row.get(fld) for fld in fields}
        for row in records
        if row.get(pages_field) and not row.get(published_field)
    ]


def need_publish_or_not(records, platform):
    """
    Фильтрует записи, оставляя только те, что пора публиковать:
      1) нет даты или нет времени — мгновенная публикация
      2) время в прошлом — «догоняем» пропущенные
      3) указанное время <= сейчас
    """
    date_field = f"{platform}_date"
    time_field = f"{platform}_time"
    now = datetime.now()
    ready = []

    for row in records:
        d = row.get(date_field) or ''
        t = row.get(time_field) or ''

        if not d or not t:
            ready.append(row)
            continue

        try:
            scheduled = datetime.strptime(f"{d} {t}", "%d.%m.%Y %H:%M")
        except ValueError:
            continue

        if scheduled <= now:
            ready.append(row)

    return ready


def run_cycle():
    load_dotenv()
    table_url = os.environ['GOOGLE_TABLE_LINK']
    creds = os.environ.get('GOOGLE_CREDENTIALS', 'google_client.json')

    # Токены и столбцы
    tg_published_cell = 'K'
    vk_published_cell = 'L'
    ok_published_cell = 'M'
    vk_token = os.environ['VK_ACCESS_TOKEN']

    records = get_google_table_records(creds, table_url)

    # --- Telegram ---
    tg_posts = need_publish_or_not(get_unpublished_records(records, 'tg'), 'tg')
    for post in tg_posts:
        try:
            raw = fetch_google_doc_text(post['google_doc'])
            clean = replace_quotes_and_dashes(raw)

            media_path = None
            if post['media']:
                try:
                    media_path, _ = get_image(post['media'])
                except Exception as e:
                    print(f"[TG] Не удалось скачать медиа для поста {post['post_id']}: {e}")

            channels = {chan.strip() for chan in post['tg_pages'].split(',') if chan.strip()}
            for channel in channels:
                post_on_tg.publish_on_telegram(
                    channel_id=channel,
                    post_text=clean,
                    media_path=media_path
                )

            write_data_in_table_cell(post['post_id'], tg_published_cell, 'TRUE')
        except Exception as e:
            print(f"[TG] Ошибка при публикации поста {post['post_id']}: {e}")

    # --- VKontakte ---
    vk_posts = need_publish_or_not(get_unpublished_records(records, 'vk'), 'vk')
    for post in vk_posts:
        try:
            raw = fetch_google_doc_text(post['google_doc'])
            clean = replace_quotes_and_dashes(raw)

            media_path = None
            media_type = None
            if post['media']:
                try:
                    media_path, _ = get_image(post['media'])
                    if media_path.lower().endswith('.gif'):
                        media_type = 'gif'
                    else:
                        media_type = 'image'
                except Exception as e:
                    print(f"[VK] Не удалось скачать медиа для поста {post['post_id']}: {e}")

            groups = {grp.strip() for grp in post['vk_pages'].split(',') if grp.strip()}
            for group in groups:
                # Передаем токен, ID группы, тип медиа и путь к файлу как saved_file
                post_on_vk.publish_post_in_vk(
                    vk_access_token=vk_token,
                    vk_page_id=group,
                    media_type=media_type,
                    saved_file=media_path,
                    text=clean
                )

            write_data_in_table_cell(post['post_id'], vk_published_cell, 'TRUE')
        except Exception as e:
            print(f"[VK] Ошибка при публикации поста {post['post_id']}: {e}")

    # --- Odnoklassniki ---
    ok_posts = need_publish_or_not(get_unpublished_records(records, 'ok'), 'ok')
    for post in ok_posts:
        try:
            raw = fetch_google_doc_text(post['google_doc'])
            clean = replace_quotes_and_dashes(raw)

            media_path = None
            if post['media']:
                try:
                    media_path, _ = get_image(post['media'])
                except Exception as e:
                    print(f"[OK] Не удалось скачать медиа для поста {post['post_id']}: {e}")

            pages = {pg.strip() for pg in post['ok_pages'].split(',') if pg.strip()}
            for page in pages:
                post_on_ok.publish_post_to_ok(
                    text=clean,
                    photo_path=media_path,
                    group_ids=[int(page)]
                )

            write_data_in_table_cell(post['post_id'], ok_published_cell, 'TRUE')
        except Exception as e:
            print(f"[OK] Ошибка при публикации поста {post['post_id']}: {e}")


def main():
    print("SMM Planer запущен. Проверяю каждую минуту...")
    while True:
        run_cycle()
        time.sleep(60)


if __name__ == '__main__':
    main()
