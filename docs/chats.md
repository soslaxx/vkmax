# Chats

Chat IDs follow these conventions:

- **DIALOG** (one-to-one): `user_a ^ user_b` (XOR). Use
  `vkmax.dm_chat_id(a, b)` to compute it.
- **CHAT** / **GROUP**: negative integer assigned by the server.
- **CHANNEL**: also negative.

## List your chats

```python
chats = await client.list_chats()              # latest first
chats = await client.iter_chats(limit=200)     # auto paginate
```

Both return `list[Chat]`. Internally `list_chats` sends
`{"marker": now_ms}` on opcode 53 — the server treats `marker` as a
"go back from this timestamp" cursor. Pass an older `marker` to fetch
older pages.

Raw form:

```python
data = await client.get_chats_list(marker=None)
# {"chats": [...], "marker": <int>}
```

## Get info

```python
chat = await client.get_chat(chat_id)          # Chat | None
raw  = await client.get_chat_info(chat_id)     # dict | None
raws = await client.get_chats_info([id1, id2]) # list[dict]
```

`Chat` exposes `id, type, title, owner, admins, members_count,
base_icon_url, last_event_time, new_messages, options, raw`.

## Create

```python
chat = await client.create_group("Title", [user_id1, user_id2])
chat = await client.create_channel("Title", user_ids=[...])
```

Both return the raw chat dict from the server.

## Members

```python
await client.get_chat_members(chat_id, count=100, offset=0)
await client.add_members(chat_id, [user_id], show_history=True)
await client.remove_members(chat_id, [user_id], clean_msg_period=0)
```

`clean_msg_period` is the number of seconds of recent history to wipe
for the removed user (0 = keep everything).

## Admins / ownership

```python
await client.add_admin(chat_id, user_id)
await client.remove_admin(chat_id, user_id)
await client.transfer_ownership(chat_id, user_id)
```

## Join requests (channels with approval)

```python
requests = await client.get_join_requests(chat_id, count=100)
await client.approve_join_requests(chat_id, [user_id])
await client.decline_join_requests(chat_id, [user_id])
```

## Join by link

```python
info = await client.check_chat_link("https://max.ru/join/...")
await client.join_chat("https://max.ru/join/...")
await client.leave_chat(chat_id)
```

## Update chat profile

```python
await client.set_chat_title(chat_id, "new title")
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

## Pinned messages

```python
await client.pin_message(chat_id, message_id)
await client.unpin_message(chat_id)
await client.set_pin_visibility(chat_id, visible=True)
```

## Other

```python
await client.subscribe_chat(chat_id)         # subscribe to a channel
await client.clear_chat(chat_id)             # clear local history
await client.hide_chat(chat_id)              # hide from list
await client.delete_chat(chat_id, last_event_time, for_all=False)

await client.get_chat_media(chat_id, media_type="PHOTO", count=50)
await client.get_common_participants(chat_id)
await client.get_chat_suggestions()
await client.public_search("news", count=10)
await client.get_link_info("https://max.ru/...")
```

## Notification settings

See [notifications.md](notifications.md) — `mute_chat`,
`mute_chat_for`, `unmute_chat`, `set_chat_mute(timestamp)`.
