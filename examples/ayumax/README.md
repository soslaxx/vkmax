# ayumax

Userbot that catches **edited** and **deleted** messages and shows you
what the other person was trying to hide. Inspired by AYUGRAM.

The bot stores every incoming message in a local SQLite database next
to `main.py` (`messages.db`). When the server fires an edit or delete
notification, the bot looks up the original text and reports it.

## Commands

- `.deleted` — last 20 deleted messages in the current chat.
- `.edited` — last 20 edited messages with before/after.

New incoming messages are stashed silently. Edits or deletions trigger
a visible report in the same chat:

- on edit: a reply quoting the old and the new text.
- on delete: a message with the original text.

The bot ignores its own edits / deletes — only **incoming** are
tracked.

## Setup

```bash
pip install vkmax
python login.py main      # create ~/.vkmax/main.json once
python main.py
```

`messages.db` is created automatically on first run with this schema:

```sql
CREATE TABLE messages (
    message_id  INTEGER PRIMARY KEY,
    chat_id     INTEGER NOT NULL,
    sender_id   INTEGER NOT NULL,
    text        TEXT,
    status      TEXT DEFAULT 'NEW',     -- NEW / EDITED / REMOVED
    edited_text TEXT,
    time        INTEGER NOT NULL
);
```

Safe to delete the file — the bot will just lose history of past
messages.

## How it works

```python
@app.on_message(filters.incoming, group=0)
async def stash_incoming(client, message):
    ...                                     # remember every dm/group msg

@app.on_edited_message(filters.incoming, group=10)
async def on_edited(client, message):
    ...                                     # compare old vs new text

@app.on_deleted_message(group=10)
async def on_deleted(client, message):
    ...                                     # look up the original
```

- `filters.incoming` skips your own messages.
- The catch-all stash handler is in `group=0` so it runs **before**
  the edit/delete reactions in `group=10`.
- All DB writes go through an `asyncio.Lock` because SQLite
  connections are not safe across coroutines.
