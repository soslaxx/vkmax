# Chats

Chat IDs follow these conventions:

- **DIALOG** (one-to-one): `user_a ^ user_b` (XOR). Use
  `vkmax.dm_chat_id(a, b)` to compute it.
- **CHAT** / **GROUP**: negative integer assigned by the server.
- **CHANNEL**: also negative.

`Client.get_chat()` returns a typed `Chat` with methods bound to the
current client; `MaxClient.get_chat_info()` returns the raw dict.

## List your chats

```python
chats = await app.list_chats()              # latest first
chats = await app.iter_chats(limit=200)     # auto paginate
```

Both return `list[Chat]`. Internally `list_chats` sends
`{"marker": now_ms}` on opcode 53 — the server treats `marker` as a
"go back from this timestamp" cursor. Pass an older `marker` to fetch
older pages.

Raw form:

```python
data = await app.get_chats_list(marker=None)
# {"chats": [...], "marker": <int>}
```

## Get info

```python
chat = await app.get_chat(chat_id)            # Chat | None
raw  = await app.get_chat_info(chat_id)       # dict | None
raws = await app.get_chats_info([id1, id2])   # list[dict]
```

`Chat` exposes `id, type, title, owner, admins, members_count,
base_icon_url, last_event_time, new_messages, options, raw, client`
and the helpers below.

## Methods on `Chat`

For `Chat` returned by the pyrogram-style `Client`:

```python
chat = await app.get_chat(chat_id)

await chat.send("hello")
await chat.send_photo("photo.jpg")
await chat.send_video("clip.mp4")
await chat.send_file("doc.pdf")
await chat.leave()
await chat.mute()                    # MUTE_FOREVER
await chat.mute(until=int(time.time()*1000) + 3600_000)
await chat.unmute()
```

Also: `chat.is_private`, `chat.is_group`, `chat.is_channel`.

## Create

```python
chat = await app.create_group("Title", [user_id1, user_id2])
chat = await app.create_channel("Title", user_ids=[...])
```

Both return the raw chat dict from the server.

## Members

```python
await app.get_chat_members(chat_id, count=100, offset=0)
await app.add_members(chat_id, [user_id], show_history=True)
await app.remove_members(chat_id, [user_id], clean_msg_period=0)
```

`clean_msg_period` is the number of seconds of recent history to wipe
for the removed user (0 = keep everything).

## Admins / ownership

```python
await app.add_admin(chat_id, user_id)
await app.remove_admin(chat_id, user_id)
await app.transfer_ownership(chat_id, user_id)
```

## Join requests (channels with approval)

```python
requests = await app.get_join_requests(chat_id, count=100)
await app.approve_join_requests(chat_id, [user_id])
await app.decline_join_requests(chat_id, [user_id])
```

## Join by link

```python
info = await app.check_chat_link("https://max.ru/join/...")
await app.join_chat("https://max.ru/join/...")
await app.leave_chat(chat_id)
```

## Update chat profile

```python
await app.set_chat_title(chat_id, "new title")
await app.set_chat_photo(chat_id, photo_token)
await app.set_chat_options(chat_id, {
    "ONLY_OWNER_CAN_CHANGE_ICON_TITLE": True,
    "ALL_CAN_PIN_MESSAGE": False,
    "ONLY_ADMIN_CAN_ADD_MEMBER": True,
    "ONLY_ADMIN_CAN_CALL": False,
    "MEMBERS_CAN_SEE_PRIVATE_LINK": True,
})
await app.update_chat(chat_id, theme="...", description="...")
```

## Pinned messages

```python
await app.pin_message(chat_id, message_id)
await app.unpin_message(chat_id)
await app.set_pin_visibility(chat_id, visible=True)
```

## Other

```python
await app.subscribe_chat(chat_id)         # subscribe to a channel
await app.clear_chat(chat_id)             # clear local history
await app.hide_chat(chat_id)              # hide from list
await app.delete_chat(chat_id, last_event_time, for_all=False)

await app.get_chat_media(chat_id, media_type="PHOTO", count=50)
await app.get_common_participants(chat_id)
await app.get_chat_suggestions()
await app.public_search("news", count=10)
await app.get_link_info("https://max.ru/...")
```

## Filters in handlers

You can route messages by chat:

```python
from vkmax import filters


@app.on_message(filters.chat(-75800508459204))
async def in_one_group(app, m):
    ...


@app.on_message(filters.group & filters.command("kick"))
async def kick(app, m):
    ...
```

See [filters.md](filters.md) and [notifications.md](notifications.md).
