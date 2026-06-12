# Messages

All message IDs are sent to the mobile API as **integers**, not
strings (unlike the legacy web API).

## Send

```python
message_id = await client.send_message(
    chat_id,
    "hello",
    notify=True,
    reply_to=None,
    elements=None,
)
```

Returns the new message id as a string. `elements` accepts the rich
text element list documented at the server.

## Reply

```python
await client.reply_message(chat_id, message_id, "text")
```

Shortcut for `send_message(..., reply_to=message_id)`.

## Edit

```python
await client.edit_message(chat_id, message_id, "new text")
```

## Delete

```python
await client.delete_messages(chat_id, [message_id], for_all=True)
await client.delete_message_range(chat_id, from_id, to_id)
```

`for_all=False` deletes only on the caller's side.

## Forward

```python
await client.forward_message(
    from_chat_id, message_id, to_chat_id, notify=True
)
```

## Pin

```python
await client.pin_message(chat_id, message_id, notify=True)
await client.unpin_message(chat_id)
```

## Typing indicator

```python
await client.send_typing(chat_id, kind="TEXT")
```

Kinds: `"TEXT"`, `"VOICE"`, `"VIDEO"`, `"PHOTO"`, `"FILE"`.

## History

```python
messages = await client.fetch_messages(chat_id, count=50, from_time=None)
raw = await client.fetch_history(chat_id, count=50, from_time=None)
```

`fetch_messages` returns typed `Message` objects, `fetch_history`
returns raw dicts. `from_time` defaults to "now + 1 day" which is how
the server signals "start from the latest message".

## Get one message

```python
raw = await client.get_message(chat_id, message_id)
```

## Mark as read

```python
await client.mark_read(chat_id, mark=message_id)
await client.mark_read(chat_id, set_as_unread=True)
```

## Search

```python
await client.search_messages("query", chat_id=chat_id, count=20)
await client.search_messages("query", count=20)
```

## Drafts

```python
await client.save_draft(chat_id, "unsent text")
await client.discard_draft(chat_id)
```

## Link preview

```python
await client.get_link_preview("https://example.com")
```

## Stats

```python
await client.get_message_stats(chat_id, message_id)
```

## Stickers

```python
await client.send_sticker(chat_id, sticker_id, pack_id=None)
```

## Polls

```python
await client.send_vote(chat_id, message_id, poll_id, [answer_id])
await client.get_poll_updates(chat_id, message_id, poll_id)
await client.get_voters_by_answer(chat_id, message_id, poll_id, answer_id)
```

## Audio transcription

```python
result = await client.transcribe_audio(chat_id, message_id, media_id)
# result = {transcriptionStatus: 1, transcription: "..."}
```

Globally enable/disable via `client.set_audio_transcription(True)`.

## The `Message` model

`Message.from_dict(raw, chat_id=chat_id)` parses a raw dict into a
slotted dataclass with helpers:

```python
msg.id            # str
msg.chat_id       # int
msg.sender_id     # int
msg.text          # str | None
msg.time          # int (ms)
msg.status        # 'EDITED' / 'REMOVED' / None
msg.reactions     # ReactionInfo | None
msg.attachments   # list[Attachment]
msg.forward       # dict | None (when forwarded)
msg.reply_to      # str | None

msg.has_reactions
msg.is_forwarded
msg.is_reply
msg.is_edited
msg.is_removed
msg.has_photos / has_files / has_video / has_audio / has_sticker / ...
msg.get_reaction_count(emoji)
```
