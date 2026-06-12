# Messages

All message IDs are sent to the mobile API as **integers**. The
client takes care of conversion when you pass a string id.

## Send

```python
message_id = await app.send_message(
    chat_id,
    "hello",
    notify=True,
    reply_to=None,
    elements=None,        # raw element list (advanced)
    markdown=False,       # parse text as Markdown
    html=False,           # parse text as HTML
)
```

Returns the id of the new message as a string. With pyrogram-style
`Client`, `send_message` returns a typed `Message` object instead.

Shortcuts:

```python
await app.send_markdown(chat_id, "**bold**")
await app.send_html(chat_id, "<b>bold</b>")
```

See [formatting.md](formatting.md) for the supported markup.

## Reply

```python
await app.reply_message(chat_id, message_id, "text")
```

Or, when you already have a `Message`:

```python
await message.reply("text")
await message.reply_markdown("**text**")
await message.reply_html("<b>text</b>")
```

## Edit

```python
await app.edit_message(chat_id, message_id, "new text")
await app.edit_markdown(chat_id, message_id, "**new text**")
await app.edit_html(chat_id, message_id, "<b>new text</b>")

await message.edit("new text")
await message.edit_markdown("**new text**")
await message.edit_html("<b>new text</b>")
```

## Delete

```python
await app.delete_messages(chat_id, [message_id], for_all=True)
await app.delete_message_range(chat_id, from_id, to_id)
await message.delete()                # for everyone
await message.delete(for_all=False)    # only for you
```

## Forward

```python
await app.forward_message(
    from_chat_id, message_id, to_chat_id, notify=True
)
await message.forward_to(other_chat_id)
```

## Pin

```python
await app.pin_message(chat_id, message_id, notify=True)
await app.unpin_message(chat_id)
await message.pin()
```

## Typing indicator

```python
await app.send_typing(chat_id, kind="TEXT")
```

Kinds: `"TEXT"`, `"VOICE"`, `"VIDEO"`, `"PHOTO"`, `"FILE"`.

## History

```python
messages = await app.fetch_messages(chat_id, count=50, from_time=None)
raw = await app.fetch_history(chat_id, count=50, from_time=None)
```

`fetch_messages` returns typed `Message` objects;
`fetch_history` returns raw dicts. `from_time` defaults to
"now + 1 day" — the server interprets that as "start from the latest
message".

## Get one message

```python
raw = await app.get_message(chat_id, message_id)
```

## Mark as read

```python
await app.mark_read(chat_id, mark=message_id)
await app.mark_read(chat_id, set_as_unread=True)
```

## Search

```python
await app.search_messages("query", chat_id=chat_id, count=20)
await app.search_messages("query", count=20)
```

## Drafts

```python
await app.save_draft(chat_id, "unsent text")
await app.discard_draft(chat_id)
```

## Link preview

```python
await app.get_link_preview("https://example.com")
```

## Stats

```python
await app.get_message_stats(chat_id, message_id)
```

## Stickers

```python
await app.send_sticker(chat_id, sticker_id, pack_id=None)
```

## Polls

### Create

```python
await app.send_poll(chat_id, "Title", ["option A", "option B"])
```

Full signature:

```python
await app.send_poll(
    chat_id,
    title,
    options,                # list[str], at least 2 non-empty entries
    *,
    anonymous=False,        # voters are not visible
    multiple=False,         # voter can pick more than one answer
    quiz=True,              # show results only after voting
    settings=None,          # raw bitmask, overrides the three flags above
    notify=True,
)
```

Returns the message id of the poll. The server assigns:

- `pollId` — used by all the methods below.
- `answerId` for each option (1, 2, 3, …).

React to the typed `Chat` helper if you already have one:

```python
chat = await app.get_chat(chat_id)
await chat.send_poll("Title", ["a", "b"], anonymous=True)
```

### Flags

`settings` is a bitmask. Constants live on the package:

```python
from vkmax import POLL_ANONYMOUS, POLL_MULTIPLE, POLL_QUIZ

await app.send_poll(
    chat_id, "?", ["yes", "no"],
    settings=POLL_ANONYMOUS | POLL_QUIZ,
)
```

| Constant | Bit | Meaning |
|---|---|---|
| `POLL_ANONYMOUS` | 1 | voters are not visible |
| `POLL_MULTIPLE` | 2 | voter can pick more than one answer |
| `POLL_QUIZ` | 4 | results are visible only after the user votes |

The keyword arguments (`anonymous=`, `multiple=`, `quiz=`) are
shortcuts over the same bitmask.

### Vote

```python
await app.send_vote(chat_id, message_id, poll_id, [answer_id])
```

- `message_id` — id of the message that contains the poll.
- `poll_id` — value of `pollId` returned in the poll attachment.
- `answer_ids` — list of `answerId` to submit. If the poll is not
  `POLL_MULTIPLE`, pass exactly one id.

### Read state

```python
state = await app.get_poll_updates(chat_id, message_id, poll_id)
# {"polls": [{"pollId": ..., "answers": [...], "state": {...}}]}

voters = await app.get_voters_by_answer(
    chat_id, message_id, poll_id, answer_id, count=50, offset=0
)
```

`state.result[i].voteCount` and `state.result[i].rate` show the live
tally; `state.total` is the total number of voters; `state.voterPreviewIds`
lists the first few participants (only when the poll is not anonymous).

### Inspect from a message

Poll attachments arrive as `attachment.type == "POLL"`. Useful fields
in `attachment.raw`:

```python
for a in message.attachments:
    if a.type == "POLL":
        raw = a.raw
        print(raw["title"], raw["pollId"], raw["settings"])
        for answer in raw["answers"]:
            print(" ", answer["answerId"], answer["text"])
        state = raw.get("state") or {}
        print("total:", state.get("total"))
```

## Audio transcription

```python
result = await app.transcribe_audio(chat_id, message_id, media_id)
# result = {"transcriptionStatus": 1, "transcription": "..."}
```

Must be enabled in your privacy config:
`app.set_audio_transcription(True)`.

## The `Message` object

When you use `Client`, every handler receives a typed `Message`
(see [message.md](message.md)). The fields are:

```python
message.id            # str
message.chat_id       # int
message.sender_id     # int
message.text          # str | None
message.time          # int (ms)
message.status        # 'EDITED' / 'REMOVED' / None
message.reactions     # ReactionInfo | None
message.attachments   # list[Attachment]
message.forward       # dict | None (when forwarded)
message.reply_to_message_id  # str | None
message.raw           # raw payload from server
message.command       # set by filters.command
message.matches       # set by filters.regex
```

Low-level `Message.from_dict(raw, chat_id=chat_id)` is also available
from `vkmax.models`.
