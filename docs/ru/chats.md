# Чаты

Идентификаторы чатов:

- **DIALOG** (личка): `user_a XOR user_b`. Удобно через `vkmax.dm_chat_id(a, b)`.
- **CHAT** / **GROUP**: отрицательное число от сервера.
- **CHANNEL**: тоже отрицательное.

## Список чатов

```python
chats = await client.list_chats()              # свежие первыми
chats = await client.iter_chats(limit=200)     # автопагинация
```

Внутри `list_chats` шлёт `{"marker": now_ms}` на опкод 53. Сервер
трактует `marker` как «вернуть чаты старше этого таймстампа». Передай
более ранний `marker` чтобы пролистать.

Сырой вариант:

```python
data = await client.get_chats_list(marker=None)
# {"chats": [...], "marker": <int>}
```

## Получить инфу

```python
chat = await client.get_chat(chat_id)          # Chat | None
raw  = await client.get_chat_info(chat_id)     # dict | None
raws = await client.get_chats_info([id1, id2]) # list[dict]
```

`Chat`: `id, type, title, owner, admins, members_count, base_icon_url,
last_event_time, new_messages, options, raw`.

## Создать

```python
chat = await client.create_group("Название", [user_id1, user_id2])
chat = await client.create_channel("Название", user_ids=[...])
```

Возвращает сырой dict чата.

## Участники

```python
await client.get_chat_members(chat_id, count=100, offset=0)
await client.add_members(chat_id, [user_id], show_history=True)
await client.remove_members(chat_id, [user_id], clean_msg_period=0)
```

`clean_msg_period` — сколько секунд истории стереть удалённому участнику
(0 — оставить всё).

## Админы / владелец

```python
await client.add_admin(chat_id, user_id)
await client.remove_admin(chat_id, user_id)
await client.transfer_ownership(chat_id, user_id)
```

## Заявки на вступление (каналы с модерацией)

```python
requests = await client.get_join_requests(chat_id, count=100)
await client.approve_join_requests(chat_id, [user_id])
await client.decline_join_requests(chat_id, [user_id])
```

## Вступление по ссылке

```python
info = await client.check_chat_link("https://max.ru/join/...")
await client.join_chat("https://max.ru/join/...")
await client.leave_chat(chat_id)
```

## Обновление чата

```python
await client.set_chat_title(chat_id, "новое название")
await client.set_chat_photo(chat_id, photo_token)
await client.set_chat_options(chat_id, {
    "ONLY_OWNER_CAN_CHANGE_ICON_TITLE": True,
    "ALL_CAN_PIN_MESSAGE": False,
    "ONLY_ADMIN_CAN_ADD_MEMBER": True,
    "ONLY_ADMIN_CAN_CALL": False,
    "MEMBERS_CAN_SEE_PRIVATE_LINK": True,
})
await client.update_chat(chat_id, theme="...", description="...")
```

## Закреплённое сообщение

```python
await client.pin_message(chat_id, message_id)
await client.unpin_message(chat_id)
await client.set_pin_visibility(chat_id, visible=True)
```

## Прочее

```python
await client.subscribe_chat(chat_id)
await client.clear_chat(chat_id)
await client.hide_chat(chat_id)
await client.delete_chat(chat_id, last_event_time, for_all=False)

await client.get_chat_media(chat_id, media_type="PHOTO", count=50)
await client.get_common_participants(chat_id)
await client.get_chat_suggestions()
await client.public_search("news", count=10)
await client.get_link_info("https://max.ru/...")
```

## Уведомления

См. [notifications.md](notifications.md) — `mute_chat`, `mute_chat_for`,
`unmute_chat`, `set_chat_mute(timestamp)`.
