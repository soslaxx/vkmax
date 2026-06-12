# Message

Что получает обработчик. Типизированный dataclass с методами, которые
ходят через тот же `Client`, что и диспатчил событие.

```python
from vkmax import MessageType
```

## Поля

| Поле | Тип | Описание |
|---|---|---|
| `id` | `str` | id сообщения на сервере |
| `chat_id` | `int` | id чата (DM — положительный, группа/канал — отрицательный) |
| `sender_id` | `int` | id автора |
| `text` | `str \| None` | текст без `elements`-форматирования |
| `time` | `int` | timestamp в ms |
| `status` | `str \| None` | `EDITED` / `REMOVED` / `None` |
| `reactions` | `ReactionInfo \| None` | счётчики и твоя реакция |
| `attachments` | `list[Attachment]` | photo/video/file/sticker/audio/poll/… |
| `forward` | `dict \| None` | данные пересылки |
| `reply_to_message_id` | `str \| None` | id того, на что ответ |
| `raw` | `dict` | исходный payload |
| `client` | `Client` | клиент-получатель |
| `command` | `list[str] \| None` | заполняется `filters.command` |
| `matches` | `re.Match` | заполняется `filters.regex` |

## Свойства

- `is_outgoing` — отправитель == ты.
- `is_reply`, `is_edited`, `is_removed`.
- `has_photo`, `has_video`, `has_file`, `has_sticker`.

## Ответы

```python
await message.reply("обычный текст")
await message.reply_markdown("**жирный**")
await message.reply_html("<b>жирный</b>")
```

Все три зовут `Client.send_message` с `reply_to=message.id`.

## Редактирование

```python
await message.edit("новый текст")
await message.edit_markdown("**новый**")
await message.edit_html("<b>новый</b>")
```

## Удаление

```python
await message.delete()              # у всех
await message.delete(for_all=False) # только у себя
```

## Реакции

```python
await message.react("fire")
await message.react("\U0001f44d")
await message.unreact()
```

Алиасы — в [reactions.md](reactions.md).

## Пересылка

```python
await message.forward_to(other_chat_id)
await message.forward_to(other_chat_id, notify=False)
```

## Закрепить

```python
await message.pin()
await message.pin(notify=False)
```

## Вложения

```python
for a in message.attachments:
    print(a.type, a.token, a.url, a.width, a.height, a.duration)
```

`Attachment.type`: `"PHOTO"`, `"VIDEO"`, `"FILE"`, `"AUDIO"`,
`"VOICE"`, `"STICKER"`, `"POLL"`, `"LOCATION"`, `"CONTROL"`.
Исходный dict — в `a.raw`.

## Работа с чатом / отправителем

```python
await message.client.send_message(message.chat_id, "...")
await message.client.get_user(message.sender_id)
await message.client.get_chat(message.chat_id)
```

или через типизированные хелперы:

```python
chat = await message.client.get_chat(message.chat_id)
await chat.mute()
await chat.send_photo("photo.jpg")
```
