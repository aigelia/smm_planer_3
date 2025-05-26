import time
from datetime import datetime

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
    """Фильтрует записи, оставляя только те, что пора публиковать."""
    date_field = f"{platform}_date"
    time_field = f"{platform}_time"
    now = datetime.now()
    ready = []
    dt_format = "%d.%m.%Y %H:%M"

    for row in records:
        d = row.get(date_field) or ''
        t = row.get(time_field) or ''

        if not d and not t:
            ready.append(row)
            continue

        if d and t:
            dt_str = f"{d} {t}"
        elif d and not t:
            dt_str = f"{d} 00:00"
        elif not d and t:
            today_str = datetime.now().strftime("%d.%m.%Y")
            dt_str = f"{today_str} {t}"
        else:
            ready.append(row)
            continue

        try:
            scheduled = datetime.strptime(dt_str, dt_format)
        except ValueError:
            print('Некорректно указана дата или время.')
            continue

        if scheduled <= now:
            ready.append(row)

    return ready


def run_cycle():
    tg_published_cell = 'K'
    vk_published_cell = 'G'
    ok_published_cell = 'O'

    records = get_google_table_records()

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

            write_data_in_table_cell(post['post_id'], tg_published_cell, 'Опубликовано')
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

            post['vk_pages'] = str(post['vk_pages'])
            groups = [group.strip() for group in post['vk_pages'].split(',')]

            for group in groups:
                if media_type == 'gif':
                    upload_url = post_on_vk.get_gif_upload_url(group)
                    uploaded_gif = post_on_vk.upload_gif(media_path, upload_url)
                    saved_gif = post_on_vk.save_doc(uploaded_gif)
                    post_on_vk.publish_post_in_vk(
                        vk_page_id=group,
                        media_type=media_type,
                        saved_file=saved_gif,
                        text=clean
                    )

                if media_type == 'image':
                    upload_url = post_on_vk.get_image_upload_url(group)
                    uploaded_image = post_on_vk.upload_image(media_path, upload_url)
                    saved_image = post_on_vk.save_image_on_wall(group, uploaded_image)
                    post_on_vk.publish_post_in_vk(
                        vk_page_id=group,
                        media_type=media_type,
                        saved_file=saved_image,
                        text=clean
                    )

                if not media_type:
                    post_on_vk.publish_post_in_vk(
                        vk_page_id=group,
                        text=clean
                    )

            write_data_in_table_cell(post['post_id'], vk_published_cell, 'Опубликовано')
        except Exception as e:
            print(f"[VK] Ошибка при публикации поста {post['post_id']}: {e}")

    # --- Odnoklassniki ---
    ok_posts = need_publish_or_not(get_unpublished_records(records, 'ok'), 'ok')
    for post in ok_posts:
        try:
            raw = fetch_google_doc_text(post['google_doc'])
            clean = replace_quotes_and_dashes(raw)

            media_path = None
            if post['media'] and str(post['media']).startswith("http"):
                try:
                    media_path, _ = get_image(post['media'])
                except Exception as e:
                    print(f"[OK] Не удалось скачать медиа для поста {post['post_id']}: {e}")

            pages = {pg.strip() for pg in str(post['ok_pages']).split(',') if pg.strip()}
            for page in pages:
                post_on_ok.publish_post_to_ok(
                    text=clean,
                    photo_path=media_path,
                    group_ids=[int(page)]
                )

            write_data_in_table_cell(post['post_id'], ok_published_cell, 'Опубликовано')
        except Exception as e:
            print(f"[OK] Ошибка при публикации поста {post['post_id']}: {e}")


def main():
    print("SMM Planer запущен. Проверяю каждую минуту...")
    while True:
        run_cycle()
        time.sleep(60)


if __name__ == '__main__':
    main()
