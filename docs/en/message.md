# Message

What your handler receives. A typed dataclass with helper methods
bound to the same `Client` that dispatched the event.

```python
from vkmax import MessageType
```

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | `str` | server-side message id |
| `chat_id` | `int` | chat id (DM = positive, group/channel = negative) |
| `sender_id` | `int` | author user id |
| `text` | `str \| None` | plain text without `elements` formatting |
| `time` | `int` | timestamp in ms |
| `status` | `str \| None` | `EDITED` / `REMOVED` / `None` |
| `reactions` | `ReactionInfo \| None` | counters + your reaction |
| `attachments` | `list[Attachment]` | photo/video/file/sticker/audio/poll/etc |
| `forward` | `dict \| None` | original forward link (when forwarded) |
| `reply_to_message_id` | `str \| None` | id of replied-to message |
| `raw` | `dict` | original payload from the server |
| `client` | `Client` | the client that received the event |
| `command` | `list[str] \| None` | filled by `filters.command` |
| `matches` | `re.Match` | filled by `filters.regex` |

## Properties

- `is_outgoing` — sender == you.
- `is_reply`, `is_edited`, `is_removed`.
- `has_photo`, `has_video`, `has_file`, `has_sticker`.

## Replies

```python
await message.reply("plain text")
await message.reply_markdown("**bold**")
await message.reply_html("<b>bold</b>")
```

All three call `Client.send_message` with `reply_to=message.id`.

## Edit

```python
await message.edit("new text")
await message.edit_markdown("**new**")
await message.edit_html("<b>new</b>")
```

## Delete

```python
await message.delete()              # for everyone
await message.delete(for_all=False) # only for you
```

## Reactions

```python
await message.react("fire")         # alias
await message.react("\U0001f44d")   # explicit emoji
await message.unreact()
```

Alias table: [reactions.md](reactions.md).

## Forward

```python
await message.forward_to(other_chat_id)
await message.forward_to(other_chat_id, notify=False)
```

## Pin

```python
await message.pin()
await message.pin(notify=False)
```

## Accessing attachments

```python
for a in message.attachments:
    print(a.type, a.token, a.url, a.width, a.height, a.duration)
```

`Attachment.type` is one of `"PHOTO"`, `"VIDEO"`, `"FILE"`,
`"AUDIO"`, `"VOICE"`, `"STICKER"`, `"POLL"`, `"LOCATION"`,
`"CONTROL"`. Raw dict is in `a.raw`.

## Working with the chat / sender

```python
await message.client.send_message(message.chat_id, "...")
await message.client.get_user(message.sender_id)
await message.client.get_chat(message.chat_id)
```

or through the typed helpers:

```python
chat = await message.client.get_chat(message.chat_id)
await chat.mute()
await chat.send_photo("photo.jpg")
```
