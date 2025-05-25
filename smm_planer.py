import os
import time
from datetime import datetime

from dotenv import load_dotenv

import post_on_vk
import post_on_tg
# import post_on_ok  # модуль для ОК подключим, когда он будет готов
from google_sheets_helper import get_google_table_records, write_data_in_table_cell
from media_helper import get_image
from text_helper import fetch_google_doc_text, replace_quotes_and_dashes


def get_unpublished_records(records, platform):
    base = ['post_id', 'google_doc', 'media']
    pages  = f"{platform}_pages"
    date   = f"{platform}_date"
    field  = f"{platform}_published"

    fields = base + [pages, date, f"{platform}_time", field]
    return [
        {f: row.get(f) for f in fields}
        for row in records
        if row.get(pages) and not row.get(field)
    ]


def need_publish_or_not(records, platform):
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
    # загрузка конфига
    load_dotenv()
    table_url = os.environ['GOOGLE_TABLE_LINK']
    creds     = os.environ.get('GOOGLE_CREDENTIALS', 'google_client.json')
    vk_token  = os.environ['VK_ACCESS_TOKEN']
    tg_token  = os.environ.get('TG_TOKEN')

    # считываем все записи
    records = get_google_table_records(creds, table_url)

    # фильтруем по платформам
    vk_posts = need_publish_or_not(
        get_unpublished_records(records, 'vk'), 'vk'
    )
    tg_posts = need_publish_or_not(
        get_unpublished_records(records, 'tg'), 'tg'
    )
    ok_posts = need_publish_or_not(
        get_unpublished_records(records, 'ok'), 'ok'
    )

    # публикация в VK
    for post in vk_posts:
        try:
            text = fetch_google_doc_text(post['google_doc'])
            clean_text = replace_quotes_and_dashes(text)
            media_path, _ = get_image(post['media']) if post['media'] else (None, None)
            post_on_vk.publish_on_vk(
                token=vk_token,
                pages=post['vk_pages'],
                text=clean_text,
                media_path=media_path
            )
            write_data_in_table_cell(post['post_id'], 'vk_published', 'TRUE')
        except Exception as e:
            print(f"[VK] Ошибка публикации поста {post['post_id']}: {e}")

    # публикация в Telegram
    for post in tg_posts:
        try:
            text = fetch_google_doc_text(post['google_doc'])
            clean_text = replace_quotes_and_dashes(text)
            media_path, _ = get_image(post['media']) if post['media'] else (None, None)
            post_on_tg.publish_on_telegram(
                channel_id=post['tg_pages'],
                post_text=clean_text,
                media_path=media_path
            )
            write_data_in_table_cell(post['post_id'], 'tg_published', 'TRUE')
        except Exception as e:
            print(f"[TG] Ошибка публикации поста {post['post_id']}: {e}")

    # публикация в OK (когда модуль будет готов)
    # for post in ok_posts:
    #     ...

def main():
    print("SMM Planer запущен. Каждую минуту проверяю таблицу...")
    while True:
        run_cycle()
        time.sleep(60)


if __name__ == '__main__':
    main()

# TODO: В случае ошибки скрипт запускается повторно не ломаясь