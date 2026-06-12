# Сообщения

В мобильном API `messageId` отправляется как **integer**, а не строка
(в отличие от старого web API).

## Отправить

```python
message_id = await client.send_message(
    chat_id,
    "привет",
    notify=True,
    reply_to=None,
    elements=None,
)
```

Возвращает id нового сообщения строкой. `elements` принимает список
элементов форматирования (см. ниже).

## Markdown / HTML

```python
await client.send_markdown(chat_id, "**жирный** *курсив* `код`")
await client.send_message(chat_id, "**жирный**", markdown=True)

await client.send_html(chat_id, "<b>жирный</b> <i>курсив</i>")
await client.send_message(chat_id, "<b>жирный</b>", html=True)
```

Парсер сам считает позиции в UTF-16 единицах (как ожидает сервер MAX).
Подробности — `vkmax.parse_markdown(text)` и `vkmax.parse_html(text)`.

## Ответ

```python
await client.reply_message(chat_id, message_id, "текст")
```

Короткая форма `send_message(..., reply_to=message_id)`.

## Редактировать

```python
await client.edit_message(chat_id, message_id, "новый текст")
await client.edit_markdown(chat_id, message_id, "**обновлено**")
await client.edit_html(chat_id, message_id, "<b>обновлено</b>")
```

## Удалить

```python
await client.delete_messages(chat_id, [message_id], for_all=True)
await client.delete_message_range(chat_id, from_id, to_id)
```

`for_all=False` — удалить только у себя.

## Переслать

```python
await client.forward_message(
    from_chat_id, message_id, to_chat_id, notify=True
)
```

## Закрепить

```python
await client.pin_message(chat_id, message_id, notify=True)
await client.unpin_message(chat_id)
```

## Индикатор печати

```python
await client.send_typing(chat_id, kind="TEXT")
```

Виды: `"TEXT"`, `"VOICE"`, `"VIDEO"`, `"PHOTO"`, `"FILE"`.

## История

```python
messages = await client.fetch_messages(chat_id, count=50, from_time=None)
raw = await client.fetch_history(chat_id, count=50, from_time=None)
```

`fetch_messages` возвращает `Message`, `fetch_history` — сырые dict.
`from_time` по умолчанию = «сейчас + 1 день» (так сервер понимает
«начать с самого свежего»).

## Получить одно сообщение

```python
raw = await client.get_message(chat_id, message_id)
```

## Пометить прочитанным

```python
await client.mark_read(chat_id, mark=message_id)
await client.mark_read(chat_id, set_as_unread=True)
```

## Поиск

```python
await client.search_messages("запрос", chat_id=chat_id, count=20)
await client.search_messages("запрос", count=20)
```

## Черновики

```python
await client.save_draft(chat_id, "неотправленный текст")
await client.discard_draft(chat_id)
```

## Превью ссылки

```python
await client.get_link_preview("https://example.com")
```

## Статистика

```python
await client.get_message_stats(chat_id, message_id)
```

## Стикеры

```python
await client.send_sticker(chat_id, sticker_id, pack_id=None)
```

## Опросы

```python
await client.send_vote(chat_id, message_id, poll_id, [answer_id])
await client.get_poll_updates(chat_id, message_id, poll_id)
await client.get_voters_by_answer(chat_id, message_id, poll_id, answer_id)
```

## Распознавание голосовых

```python
result = await client.transcribe_audio(chat_id, message_id, media_id)
# result = {transcriptionStatus: 1, transcription: "..."}
```

Глобально включается через `client.set_audio_transcription(True)`.

## Модель `Message`

`Message.from_dict(raw, chat_id=chat_id)` парсит dict в slot-dataclass:

```python
msg.id            # str
msg.chat_id       # int
msg.sender_id     # int
msg.text          # str | None
msg.time          # int (ms)
msg.status        # 'EDITED' / 'REMOVED' / None
msg.reactions     # ReactionInfo | None
msg.attachments   # list[Attachment]
msg.forward       # dict | None
msg.reply_to      # str | None

msg.has_reactions
msg.is_forwarded
msg.is_reply
msg.is_edited
msg.is_removed
msg.has_photos / has_files / has_video / has_audio / has_sticker / ...
msg.get_reaction_count(emoji)
```
