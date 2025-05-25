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

        # 1) нет даты или времени → публикуем сразу
        if not d or not t:
            ready.append(row)
            continue

        # 2+3) разбираем "DD.MM.YYYY HH:MM"
        try:
            scheduled = datetime.strptime(f"{d} {t}", "%d.%m.%Y %H:%M")
        except ValueError:
            continue

        # если время настало или уже прошло
        if scheduled <= now:
            ready.append(row)

    return ready


def run_cycle():
    load_dotenv()
    table_url = os.environ['GOOGLE_TABLE_LINK']
    creds = os.environ.get('GOOGLE_CREDENTIALS', 'google_client.json')

    # Столбцы для отметок
    tg_published_cell = 'K'  # tg_published
    vk_published_cell = 'L'  # vk_published
    ok_published_cell = 'M'  # ok_published

    # Читаем все записи из таблицы
    records = get_google_table_records(creds, table_url)

    # --- Telegram ---
    tg_posts = need_publish_or_not(
        get_unpublished_records(records, 'tg'), 'tg'
    )
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
    vk_posts = need_publish_or_not(
        get_unpublished_records(records, 'vk'), 'vk'
    )
    for post in vk_posts:
        try:
            raw = fetch_google_doc_text(post['google_doc'])
            clean = replace_quotes_and_dashes(raw)

            media_path = None
            if post['media']:
                try:
                    media_path, _ = get_image(post['media'])
                except Exception as e:
                    print(f"[VK] Не удалось скачать медиа для поста {post['post_id']}: {e}")

            groups = {grp.strip() for grp in post['vk_pages'].split(',') if grp.strip()}
            for group in groups:
                post_on_vk.publish_on_vk(
                    owner_id=group,
                    post_text=clean,
                    media_path=media_path
                )

            write_data_in_table_cell(post['post_id'], vk_published_cell, 'TRUE')
        except Exception as e:
            print(f"[VK] Ошибка при публикации поста {post['post_id']}: {e}")

    # --- Odnoklassniki ---
    ok_posts = need_publish_or_not(
        get_unpublished_records(records, 'ok'), 'ok'
    )
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
                post_on_ok.publish_on_ok(
                    page_id=page,
                    post_text=clean,
                    media_path=media_path
                )

            write_data_in_table_cell(post['post_id'], ok_published_cell, 'TRUE')
        except Exception as e:
            print(f"[OK] Ошибка при публикации поста {post['post_id']}: {e}")


def main():
    print("SMM Planer запущен. Проверяю каждые 60 секунд...")
    while True:
        run_cycle()
        time.sleep(60)


if __name__ == '__main__':
    main()
