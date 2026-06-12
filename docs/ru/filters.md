# Фильтры

Фильтры — предикаты над `Message`. Комбинируются `&`, `|`, `~` и
передаются декораторам событий:

```python
from vkmax import filters


@app.on_message(filters.incoming & filters.private & filters.text)
async def on_dm(app, m):
    ...
```

Все фильтры — в `vkmax.filters`.

## Направление

| Фильтр | True когда |
|---|---|
| `filters.incoming` | отправитель ≠ ты |
| `filters.outgoing` | отправитель == ты |
| `filters.me` | синоним `outgoing` |

## Тип чата

| Фильтр | True когда |
|---|---|
| `filters.private` | личка (`chat_id > 0`) |
| `filters.group` | группа |
| `filters.channel` | канал |

## Контент

| Фильтр | Что в сообщении |
|---|---|
| `filters.text` | непустой текст |
| `filters.photo` | фото |
| `filters.video` | видео |
| `filters.file` | файл |
| `filters.audio` | аудио или голосовое |
| `filters.sticker` | стикер |
| `filters.poll` | опрос |
| `filters.location` | геолокация |
| `filters.control` | системное вложение |
| `filters.media` | любое из: photo, video, file, sticker, audio |

## Статус

| Фильтр | True когда |
|---|---|
| `filters.edited` | статус `EDITED` |
| `filters.removed` | статус `REMOVED` |
| `filters.reply` | это ответ на другое сообщение |
| `filters.forward` | пересланное сообщение |

## Точечный таргет

```python
filters.chat(307609904)
filters.chat(307609904, -75800508459204)
filters.user(123, 456)
```

## Совпадение по тексту

```python
filters.text_equals("hi", case_sensitive=False)
filters.text_contains("weather")
filters.regex(r"^\d+$")
```

`regex` сохраняет `re.Match` в `message.matches`:

```python
@app.on_message(filters.regex(r"^count (\d+)$"))
async def count(app, m):
    n = int(m.matches.group(1))
    await m.reply("got " + str(n))
```

## Команды

```python
filters.command("start")
filters.command(["start", "hi"])
filters.command("start", prefixes=["/", "."])
filters.command("start", case_sensitive=True)
```

Когда фильтр сработал, в `message.command` лежит разобранный список:

```python
@app.on_message(filters.outgoing & filters.command("weather"))
async def cmd(app, m):
    args = m.command[1:]   # всё после .weather
    city = " ".join(args) or "Moscow"
```

## Комбинирование

```python
filter = (
    filters.outgoing
    & filters.command("ban")
    & (filters.group | filters.channel)
)
```

`&` — AND, `|` — OR, `~` — NOT.

## Кастомные фильтры

```python
from vkmax.filters import create


def is_long(message) -> bool:
    return isinstance(message.text, str) and len(message.text) > 100


long_messages = create(is_long, name="long")


@app.on_message(long_messages)
async def warn(app, m):
    await m.reply("тише, тише")
```

Предикат может быть sync или async, принимает `Message`.

## Без фильтра

Передай `None` (или ничего) — получишь все события этого типа:

```python
@app.on_message()                # каждое NOTIF_MESSAGE
async def log_all(app, m):
    ...
```
