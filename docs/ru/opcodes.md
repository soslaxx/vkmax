# Опкоды

Все опкоды мобильного API MAX, сгруппированные по доменам.
Каноничный Python-enum — `vkmax.enums.Opcode`.

Поток пакетов:

- Клиент → сервер: `cmd=0`, `seq=N`, `opcode=X`, `payload=...`.
- Сервер → клиент (ответ): `cmd=1` (OK) / `2` (NOT_FOUND) / `3` (ERROR), тот же `seq`.
- Сервер → клиент (push): `cmd=0`, `seq` не совпадает ни с одним запросом, `opcode` — один из `NOTIF_*`.

## Системные

| # | Имя | Направление | Назначение |
|---|---|---|---|
| 1 | `PING` | C→S | Keep-alive. `vkmax` шлёт раз в 30 с. Ответ — пустой OK. |
| 2 | `DEBUG` | server-only | Серверный debug, клиентами не используется. |
| 3 | `RECONNECT` | S→C | Сервер просит клиента переподключиться. |
| 5 | `LOG` | C→S | Загрузка клиентских логов. `vkmax` не использует. |
| 6 | `SESSION_INIT` | C→S | Первый пакет соединения — `mt_instanceid`, `userAgent`, `deviceId`, `clientSessionId`. Сервер отвечает `callsSeed`, `location`, гео-конфигом. |

## Профиль и аккаунт

| # | Имя | Назначение |
|---|---|---|
| 16 | `PROFILE` | Обновить профиль: `firstName`, `lastName`, `photoToken`, `avatarType`, `photoId`. |
| 25 | `PRESET_AVATARS` | Получить каталог преднабранных аватарок. |
| 43 | `REMOVE_CONTACT_PHOTO` | Удалить фото из профиля по `photoId`. |
| 199 | `PROFILE_DELETE` | Удалить аккаунт. |
| 200 | `PROFILE_DELETE_TIME` | Запланировать / отменить отложенное удаление. |

## Аутентификация

| # | Имя | Назначение |
|---|---|---|
| 17 | `AUTH_REQUEST` | Старт SMS-аута: `{phone, type: START_AUTH, language}` → временный `token`. |
| 18 | `AUTH` | Отправить код: `{token, verifyCode, authTokenType: CHECK_CODE}` → `tokenAttrs.LOGIN.token` или `passwordChallenge`. |
| 19 | `LOGIN` | Логин по долгоживущему токену. Возвращает `profile`, `chats`, `contacts`, `config`. |
| 20 | `LOGOUT` | Завершить текущую сессию. |
| 23 | `AUTH_CONFIRM` | Завершить регистрацию нового аккаунта (`token` + `firstName` + опционально `lastName` / `photoId`). |
| 101 | `AUTH_LOGIN_RESTORE_PASSWORD` | Сброс пароля через email. |
| 104 | `AUTH_2FA_DETAILS` | Статус 2FA, подсказка, привязка email. |
| 107 | `AUTH_VALIDATE_PASSWORD` | Подтвердить текущий 2FA-пароль (`trackId` + `password`). |
| 108 | `AUTH_VALIDATE_HINT` | Установить / проверить подсказку пароля. |
| 109 | `AUTH_VERIFY_EMAIL` | Отправить код подтверждения на email. |
| 110 | `AUTH_CHECK_EMAIL` | Подтвердить email-код. |
| 111 | `AUTH_SET_2FA` | Включить / сменить / удалить 2FA. |
| 112 | `AUTH_CREATE_TRACK` | Создать `trackId` под следующую чувствительную операцию. |
| 113 | `AUTH_CHECK_PASSWORD` | Промежуточная проверка пароля в auth-flow. |
| 115 | `AUTH_LOGIN_CHECK_PASSWORD` | Шаг внутри SMS-логина при 2FA; меняет пароль на login-token. |
| 116 | `AUTH_LOGIN_PROFILE_DELETE` | Удалить профиль во время логина (когда аккаунт стоит на удаление). |
| 290 | `AUTH_QR_APPROVE` | Подтвердить QR-логин с другого устройства. |

## Привязка телефона

| # | Имя | Назначение |
|---|---|---|
| 98 | `PHONE_BIND_REQUEST` | Запрос SMS на новый номер. |
| 99 | `PHONE_BIND_CONFIRM` | Подтвердить код и привязать номер. |

## Сессии

| # | Имя | Назначение |
|---|---|---|
| 96 | `SESSIONS_INFO` | Список активных сессий. |
| 97 | `SESSIONS_CLOSE` | Закрыть все сессии кроме текущей. |

## Sync / config

| # | Имя | Назначение |
|---|---|---|
| 21 | `SYNC` | Ручной триггер синхронизации; нужен редко (LOGIN уже отдаёт снапшот). |
| 22 | `CONFIG` | Чтение/запись `settings.user` (приватность) и `settings.chats` (mute, звук, LED по чатам). |

## Стикерпаки / GIF

| # | Имя | Назначение |
|---|---|---|
| 26 | `ASSETS_GET` | Список твоих стикерпаков. |
| 27 | `ASSETS_UPDATE` | Обновить метаданные пака. |
| 28 | `ASSETS_GET_BY_IDS` | Получить паки по списку id. |
| 29 | `ASSETS_ADD` | Добавить стикерпак в библиотеку. |
| 259 | `ASSETS_REMOVE` | Удалить пак. |
| 260 | `ASSETS_MOVE` | Сменить позицию пака. |
| 261 | `ASSETS_LIST_MODIFY` | Массовый порядок. |

## Контакты

| # | Имя | Назначение |
|---|---|---|
| 32 | `CONTACT_INFO` | Получить пользователей по id. |
| 33 | `CONTACT_ADD` | Добавить в адресную книгу. |
| 34 | `CONTACT_UPDATE` | Переименовать, заблокировать, разблокировать. |
| 35 | `CONTACT_PRESENCE` | Онлайн / last seen для списка. |
| 36 | `CONTACT_LIST` | Список контактов по `status` (мобильное API отдаёт только `BLOCKED`). |
| 37 | `CONTACT_SEARCH` | Поиск по адресной книге. |
| 38 | `CONTACT_MUTUAL` | Общие контакты. |
| 39 | `CONTACT_PHOTOS` | Все фото контакта. |
| 40 | `CONTACT_SORT` | Сортировка контактов. |
| 42 | `CONTACT_VERIFY` | Отметить «верифицирован» (редко). |
| 46 | `CONTACT_INFO_BY_PHONE` | Найти контакт по номеру. |

## Чаты

| # | Имя | Назначение |
|---|---|---|
| 48 | `CHAT_INFO` | Получить чаты по `chatIds`. |
| 49 | `CHAT_HISTORY` | Страница истории (`from`, `forward`, `backward`). |
| 50 | `CHAT_MARK` | Сдвинуть маркер прочитанного / пометить непрочитанным. |
| 51 | `CHAT_MEDIA` | Медиа чата (`type`: PHOTO/VIDEO/FILE/AUDIO/LINK). |
| 52 | `CHAT_DELETE` | Удалить чат (опционально `forAll`). |
| 53 | `CHATS_LIST` | Список чатов с пагинацией (`marker = now_ms`, листаем назад во времени). |
| 54 | `CHAT_CLEAR` | Очистить локальную историю. |
| 55 | `CHAT_UPDATE` | Переименовать, описание, закреп, фото, опции, владелец. |
| 56 | `CHAT_CHECK_LINK` | Разрешить join-ссылку без вступления. |
| 57 | `CHAT_JOIN` | Вступить по ссылке. |
| 58 | `CHAT_LEAVE` | Выйти из чата. |
| 59 | `CHAT_MEMBERS` | Список участников (так же для заявок с `type: JOIN_REQUEST`). |
| 60 | `PUBLIC_SEARCH` | Поиск публичных чатов / каналов / пользователей. |
| 61 | `CHAT_PERSONAL_CONFIG` | Личные настройки пользователя в чате. |
| 63 | `CHAT_CREATE` | Создать чат. На практике используется `MSG_SEND` с CONTROL-вложением. |
| 75 | `CHAT_SUBSCRIBE` | Подписаться на канал. |
| 77 | `CHAT_MEMBERS_UPDATE` | Добавить / удалить / одобрить / отклонить участников. |
| 86 | `CHAT_PIN_SET_VISIBILITY` | Видимость закреплённого сообщения. |
| 117 | `CHAT_COMPLAIN` | Жалоба на чат. |
| 161 | `COMPLAIN` | Жалоба на сообщение / пользователя. |
| 162 | `COMPLAIN_REASONS_GET` | Готовые причины для COMPLAIN. |
| 196 | `CHAT_HIDE` | Скрыть чат из списка. |
| 198 | `CHAT_SEARCH_COMMON_PARTICIPANTS` | Общие участники с другим юзером. |
| 257 | `CHAT_REACTIONS_SETTINGS_SET` | Ограничить разрешённые реакции в чате. |
| 258 | `REACTIONS_SETTINGS_GET_BY_CHAT_ID` | Прочитать ограничения реакций чата. |
| 300 | `CHAT_SUGGEST` | Рекомендуемые чаты / каналы. |

## Сообщения

| # | Имя | Назначение |
|---|---|---|
| 64 | `MSG_SEND` | Отправить сообщение (текст, attaches, стикер, reply, forward, CONTROL для создания чата). |
| 65 | `MSG_TYPING` | Индикатор печати (TEXT / VOICE / VIDEO / PHOTO / FILE). |
| 66 | `MSG_DELETE` | Удалить одно или несколько сообщений. |
| 67 | `MSG_EDIT` | Редактировать текст и/или `elements`. |
| 68 | `CHAT_SEARCH` | Поиск внутри одного чата. |
| 70 | `MSG_SHARE_PREVIEW` | Превью для ссылки. |
| 71 | `MSG_GET` | Сообщения по id внутри чата. |
| 72 | `MSG_SEARCH_TOUCH` | UI-подсказки поиска. |
| 73 | `MSG_SEARCH` | Глобальный поиск сообщений. |
| 74 | `MSG_GET_STAT` | Статистика поста в канале. |
| 92 | `MSG_DELETE_RANGE` | Удалить диапазон сообщений. |
| 127 | `GET_LAST_MENTIONS` | Последние упоминания по всем чатам. (Точная форма payload не подтверждена.) |
| 176 | `DRAFT_SAVE` | Сохранить черновик чата. |
| 177 | `DRAFT_DISCARD` | Удалить черновик. |
| 178 | `MSG_REACTION` | Поставить реакцию (`{chatId, messageId(int), reaction: {reactionType: EMOJI, id: "<emoji>"}}`). |
| 179 | `MSG_CANCEL_REACTION` | Убрать свою реакцию. |
| 180 | `MSG_GET_REACTIONS` | Получить реакции. (`vkmax` берёт `reactionInfo` из `MSG_GET`.) |
| 181 | `MSG_GET_DETAILED_REACTIONS` | Список юзеров по реакции с пагинацией. |

## Медиа и файлы

| # | Имя | Назначение |
|---|---|---|
| 80 | `PHOTO_UPLOAD` | URL для загрузки фото. |
| 81 | `STICKER_UPLOAD` | URL для стикера. |
| 82 | `VIDEO_UPLOAD` | URL для видео. |
| 83 | `VIDEO_PLAY` | URL стриминга (`MP4_1080`, `MP4_720`, `HLS`, ...). |
| 87 | `FILE_UPLOAD` | URL для произвольного файла. |
| 88 | `FILE_DOWNLOAD` | URL для скачивания файла / фото. |
| 89 | `LINK_INFO` | Разрешить публичную ссылку (`max.ru/...`). |
| 193 | `STICKER_CREATE` | Создать стикер из загруженной картинки. |
| 194 | `STICKER_SUGGEST` | Подсказки стикеров под запрос. |
| 202 | `AUDIO_TRANSCRIPTION` | Запрос распознавания голосового (`chatId`, `messageId`, `mediaId`). |
| 301 | `AUDIO_PLAY` | URL аудио (`MP3`, `OGG`, `HLS`). |
| 293 | `TRANSCRIPTION_RESULT` | Push с готовым текстом распознавания. |

## Звонки

| # | Имя | Назначение |
|---|---|---|
| 76 | `VIDEO_CHAT_START` | Запустить пассивный видеочат. |
| 78 | `VIDEO_CHAT_START_ACTIVE` | Начать 1-к-1 / групповой звонок (с `internalParams`). |
| 79 | `VIDEO_CHAT_HISTORY` | История звонков. |
| 84 | `VIDEO_CHAT_CREATE_JOIN_LINK` | Ссылка для входа в активный звонок. |
| 103 | `GET_INBOUND_CALLS` | Текущие входящие. |
| 124 | `LOCATION_STOP` | Остановить шаринг геолокации. |
| 195 | `VIDEO_CHAT_MEMBERS` | Участники звонка. |

## Боты / мини-приложения

| # | Имя | Назначение |
|---|---|---|
| 105 | `EXTERNAL_CALLBACK` | Зарезервировано под внешние интеграции. |
| 118 | `MSG_SEND_CALLBACK` | Нажать inline-кнопку (`callbackData`). |
| 119 | `SUSPEND_BOT` | Запретить боту писать тебе. |
| 144 | `CHAT_BOT_COMMANDS` | Команды бота в чате. |
| 145 | `BOT_INFO` | Публичная инфа о боте. |
| 158 | `OK_TOKEN` | Короткоживущий OK SSO токен. |
| 160 | `WEB_APP_INIT_DATA` | `initData` для запуска мини-приложения. |

## Опросы

| # | Имя | Назначение |
|---|---|---|
| 304 | `SEND_VOTE` | Проголосовать. |
| 305 | `VOTERS_LIST_BY_ANSWER` | Список проголосовавших за ответ. |
| 306 | `GET_POLL_UPDATES` | Обновления по набору опросов. |

## Папки

| # | Имя | Назначение |
|---|---|---|
| 272 | `FOLDERS_GET` | Список папок (`folderSync` курсор). |
| 273 | `FOLDERS_GET_BY_ID` | Одна папка. |
| 274 | `FOLDERS_UPDATE` | Создать / обновить (`id, title, include, favorites, filters, options`). |
| 275 | `FOLDERS_REORDER` | Порядок (`foldersOrder: [id, id]`). |
| 276 | `FOLDERS_DELETE` | Удалить. |

## Push-события (server → client)

| # | Имя | Что приходит |
|---|---|---|
| 128 | `NOTIF_MESSAGE` | Новое / обновлённое сообщение. |
| 129 | `NOTIF_TYPING` | Чужой индикатор печати. |
| 130 | `NOTIF_MARK` | Маркер прочитанного сдвинут (твой или чужой). |
| 131 | `NOTIF_CONTACT` | Изменился контакт. |
| 132 | `NOTIF_PRESENCE` | Онлайн / last seen. |
| 134 | `NOTIF_CONFIG` | Настройки изменились с другого устройства. |
| 135 | `NOTIF_CHAT` | Изменились данные чата. |
| 136 | `NOTIF_ATTACH` | Аплоад завершён. |
| 137 | `NOTIF_CALL_START` | Входящий / стартующий звонок. |
| 139 | `NOTIF_CONTACT_SORT` | Сменился порядок контактов. |
| 140 | `NOTIF_MSG_DELETE_RANGE` | Массовое удаление. |
| 142 | `NOTIF_MSG_DELETE` | Удалили сообщение. |
| 143 | `NOTIF_CALLBACK_ANSWER` | Бот ответил на callback. |
| 147 | `NOTIF_LOCATION` | Обновление live-локации. |
| 148 | `NOTIF_LOCATION_REQUEST` | У тебя запросили live-локацию. |
| 150 | `NOTIF_ASSETS_UPDATE` | Стикерпак обновлён. |
| 152 | `NOTIF_DRAFT` | Черновик изменился. |
| 153 | `NOTIF_DRAFT_DISCARD` | Черновик удалён. |
| 154 | `NOTIF_MSG_DELAYED` | Отложенная отправка сработала. |
| 155 | `NOTIF_MSG_REACTIONS_CHANGED` | Реакции изменились. |
| 156 | `NOTIF_MSG_YOU_REACTED` | Подтверждение твоей реакции. |
| 159 | `NOTIF_PROFILE` | Твой профиль обновлён с другого устройства. |
| 277 | `NOTIF_FOLDERS` | Список папок изменился. |
| 292 | `NOTIF_BANNERS` | UI-баннеры (анонсы). |

## Status / command codes

Значение байта `cmd` в каждом пакете:

| Значение | Имя | Смысл |
|---|---|---|
| 0 | `CMD_REQUEST` | Запрос клиента или push сервера. |
| 1 | `CMD_OK` | Успешный ответ. |
| 2 | `CMD_NOT_FOUND` | Не найдено (редко). |
| 3 | `CMD_ERROR` | Ошибка. Payload содержит `error`, `message`, `localizedMessage`. После ERROR сервер обычно закрывает TCP-соединение. |
