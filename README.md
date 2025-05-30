# SMM Planer — сервис для автоматической публикации постов в Telegram, VK и "Одноклассники" #

SMM Planer — это автономный инструмент для автоматической публикации постов в социальные сети: Telegram, ВКонтакте и Одноклассники. Он считывает запланированные посты из Google-таблицы определенного формата, скачивает медиафайлы при необходимости, приводит текст в порядок и публикует контент точно в заданное время.

## Технические возможности ##

- Чтение плана публикации контента из Google-таблицы и публикация в заданное время для каждой соцсети;
- Поддержка публикации текста и медиафайлов (статичных изображений и .gif);
- Внесение в таблицу отметок об опубликованных постах;
- Мгновенная публикация постов, если дата не указана, и публикация ранее не вышедших постов;
- Автоматическая коррекция текста (кавычки, тире);
- Использование изображений по URL либо по ссылке на Google Drive;
- Запуск в фоновом режиме (проверка таблицы раз в 60 секунд и постинг материалов, готовых к публикации);
- Публикация в несколько каналов / групп в соцсетях.

## Ограничения ##

- Не более одного медиафайла в каждой публикации;
- Все материалы, размещенные на Google Drive (календарь публикаций, изображения и Google-документы с текстами постов) должны быть доступны по прямой ссылке;
- Для работы требуются токены API VK, Telegram (токен бота), OK, а также сервисов Google;
- Таблица с публикациями должна соответствовать образцу, описанному в документации.

## Установка ##

Для начала работы необходимо скачать репозиторий, установить виртуальное окружение (из-за технических особенностей потребуется Python версии 3.10 либо ниже) и зависимости. 

```Shell
git clone https://github.com/yourusername/smm-planer.git
cd smm-planer

python3.10 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

После этого переименуйте файл `.env.example` в `.env` и добавьте в него все необходимые токены, процесс получения которых описан ниже.

### Получение токенов соцсетей ###

#### Telegram ####

Для получения токена бота в Telegram необходимо обратиться к боту [BotFather](https://telegram.me/BotFather). Введите /start, следуйте простым инструкциям по регистрации бота, а после получения токена добавить его в .env (`TG_TOKEN=`). Далее следует добавить созданного бота в качестве администратора во все каналы, в которых планируется осуществлять автоматическую публикацию постов из таблицы Google.

#### Одноклассники ####

Чтобы публиковать фотографии и текст в группы на [OK.ru](https://apiok.ru/) с помощью официального API Одноклассников.
Создайте рядом со скриптом файл .env, в который вы добавите конфиденциальные ключи и токены. Они не хранятся в коде напрямую, что удобно и безопасно.
```text
OK_APP_ID=ваш_APPLICATION_ID
OK_APP_KEY=ваш_PUBLIC_APP_KEY
OK_APP_SECRET=ваш_SECRET_KEY
OK_ACCESS_TOKEN=ваш_ACCESS_TOKEN
ok_session_secret=ваш_SESSION_SECRET_KEY
```
Чтобы использовать API Одноклассников, необходимо зарегистрировать приложение и получить ряд ключей доступа. Это делается один раз, после чего вы можете использовать полученные значения сколько угодно.
Перейдите на страницу [OK.ru](https://ok.ru/app/setup), авторизуйтесь и создайте новое приложение. В процессе вам будет предложено указать:
* Название приложения
* Тип: Web
* IP-адрес сервера, с которого будут идти запросы (можно узнать на [2ip.ru](https://2ip.ru/))
  
После создания вы получите:

`application_id` — используется для идентификации приложения

`application_key` — публичный ключ, обязательный параметр в запросах

`application_secret_key` — приватный ключ для формирования подписи

#### Получение `access_token` и `session_secret_key` ####
Для получения этих двух параметров выполните авторизацию через браузер. Перейдите по следующей ссылке, подставив свои `application_id` и `application_key`:
```text
https://connect.ok.ru/oauth/authorize?client_id=OK_APP_ID&scope=VALUABLE_ACCESS;PHOTO_CONTENT;GROUP_CONTENT&response_type=token&redirect_uri=https://api.ok.ru/blank.html
```
После разрешения доступа вы будете перенаправлены на страницу, в адресной строке которой будет содержаться `access_token` и `session_secret_key`. Их нужно скопировать и сохранить в .env.

#### VK ####

Для того чтобы программа работала с API VK необходимо создать и настроить приложение, перейдите по ссылке [Создание приложения VK](https://id.vk.com/about/business/go/docs/ru/vkid/latest/vk-id/connection/create-application#Sozdanie-prilozheniya)
и следуйте инструкции. При регистрации приложения укажите:
- Тип приложения - Web;
- Базовый домен - example.com;
- Доверенный Redirect URL - https://example.com.

В разделе 'Доступы' вашего приложения, активируйте:
- Стена;
- Сообщества;
- Документы;
- Фотографии.

Так же в настройках, во вкладке 'Разделы' в группах ВКонтакте, активируйте доступ:
- Файлы;
- Фото;
- Посты.

Для того чтобы получить VK_ACCESS_TOKEN, перейдите по ссылке ниже, подставив в параметр client_id вместо `...`
ID своего приложения VK: 
```text
oauth.vk.com/oauth/authorize?client_id=...&display=page&scope=wall,groups,photos,docs&response_type=token&v=5.199&state=123456
```
В окне 'Вход с помощью VK ID' выберите продолжить. После разрешения доступа вы будете перенаправлены на страницу
в адресной строке которой будет содержаться `access_token=` вида `vk.1.axTHGNkdjfls533bacf01e1165b57531ad114461ae8736d6506a3`
скопируйте его до символа `&`, сохраните в .env файл под именем VK_ACCESS_TOKEN.

### Получение токена Google ###

Для этой части настройки вам необходимо авторизоваться и войти в [Google Cloud Console](https://console.cloud.google.com/), нажать кнопку **«Выбрать проект» → «Новый проект»**. Введите любое название.

После создания проекта выберите в левом меню **API и сервисы → Библиотека**. Найдите и включите два API — Google Sheets и Google Drive. Далее нужно в меню слева выбрать **API и сервисы → Учётные данные** и создать сервисный аккаунт.

Последний этап — найдите в списке сервисный аккаунт, кликните по его имени и во вкладке **«Ключи»** нажмите **«Добавить ключ» → «Создать новый ключ».** Выберите формат JSON. После чего на ваш компьютер будет скачен файл. Откройте его в текстовом редакторе и скопируйте из него email. Строка с ним будет выглядеть подобным образом:

`"client_email": "testtest@smm-planer-3.iam.gserviceaccount.com"`

Переместите .json-файл в директорию с кодом. Скопированный вам email нужно указать в Google-таблице, где хранится календарь публикаций, выдав ему права редактора файла.

С подробной иллюстрированной инструкцией по получению необходимых доступов для Google API можно ознакомиться [по ссылке](https://habr.com/ru/articles/825404/).

## Создание календаря публикаций ##

Для использования скрипта потребуется календарь-таблица публикаций определенного образца. Вы можете скопировать таблицу [по ссылке](https://docs.google.com/spreadsheets/d/1-YrbMs7EHixx-j75aRIipwDNHG7FE5XrZEgjdG25F1c/edit?gid=0#gid=0), либо создать ее самостоятельно, следуя образцу:

| post_id | google_doc | media | vk_pages | vk_date | vk_time | vk_published | tg_pages | tg_date | tg_time | tg_published | ok_pages | ok_date | ok_time | ok_published |
| ------- | ---------- | ----- | -------- | ------- | ------- | ------------ | -------- | ------- | ------- | ------------ | -------- | ------- | ------- | ------------ |
|         |            |       |          |         |         |              |          |         |         |              |          |         |         |              |
|         |            |       |          |         |         |              |          |         |         |              |          |         |         |              |
|         |            |       |          |         |         |              |          |         |         |              |          |         |         |              |

Обратите внимание, что в настройках доступа следует указать, чтобы таблица была доступна по ссылке для всех

### Как следует пользоваться календарем ###

Каждая строка таблицы — это один пост, который может быть запланирован для трех социальных сетей; для каждой из соцсетей может быть указано более одного ресурса (указываются в соответствующем поле через запятую), также для каждой из соцсетей могут быть выбраны свои дата и время публикации.

**Поля для заполнения**:

- post_id — любой уникальный идентификатор (можно просто 1, 2, 3...);
- google_doc — ссылка на Google-документ с текстом поста (должен быть открыт для чтения);
- media — ссылка на изображение или gif (прямой URL или Google Drive-файл с доступом "по ссылке");
- *_pages — список страниц/групп (например, `@mychannel` для Telegram, `230572126` для VK, `70000035422780` для OK), указываются через запятую;
- *_date и *_time — дата и время публикации. Если не указаны — пост будет опубликован немедленно. Дата указывается в формате ДД.ММ.ГГГГ, время в 24-часовом формате. Скрипт использует системное время;
- *_published — заполняется автоматически скриптом после успешной публикации ("Опубликовано").

**Что важно учитывать**:

- Если дата и время в прошлом, а *_published не отмечено, пост будет опубликован при следующей проверке.
- Если дата/время не указаны, пост считается "без отложки" и публикуется сразу.
- Если ни один из блоков vk_, tg_ или ok_ не заполнен — пост будет пропущен.

## Запуск скрипта ##

Перед запуском программы убедитесь, что все необходимые зависимости установленны, в .env файле присутствуют все необходимые токены.

```shell

> python smm_planer.py
> SMM Planer запущен. Проверяю каждую минуту...
```

## Цель проекта ##

Код написан в учебных целях — это задание в курсе по Python и веб-разработке на [Devman.org](https://dvmn.org).
