# Filters

Filters are predicates over a `Message`. They are combined with `&`,
`|`, `~` and passed to event decorators:

```python
from vkmax import filters


@app.on_message(filters.incoming & filters.private & filters.text)
async def on_dm(app, m):
    ...
```

All filters live in `vkmax.filters`.

## Direction

| Filter | True when |
|---|---|
| `filters.incoming` | sender ≠ you |
| `filters.outgoing` | sender == you |
| `filters.me` | alias for `outgoing` |

## Chat type

| Filter | True when |
|---|---|
| `filters.private` | DM (`chat_id > 0`) |
| `filters.group` | group chat |
| `filters.channel` | channel |

## Content type

| Filter | True when message has |
|---|---|
| `filters.text` | non-empty text |
| `filters.photo` | photo attachment |
| `filters.video` | video attachment |
| `filters.file` | file attachment |
| `filters.audio` | audio or voice |
| `filters.sticker` | sticker |
| `filters.poll` | poll |
| `filters.location` | location |
| `filters.control` | control / system attach |
| `filters.media` | any of: photo, video, file, sticker, audio |

## Status

| Filter | True when |
|---|---|
| `filters.edited` | message status is `EDITED` |
| `filters.removed` | message status is `REMOVED` |
| `filters.reply` | replies to another message |
| `filters.forward` | forwarded message |

## Targeted

```python
filters.chat(307609904)             # one chat
filters.chat(307609904, -75800508459204)  # several
filters.user(123, 456)              # by sender id
```

## Text matching

```python
filters.text_equals("hi", case_sensitive=False)
filters.text_contains("weather")
filters.regex(r"^\d+$")
```

`regex` saves the `re.Match` to `message.matches` for later use:

```python
@app.on_message(filters.regex(r"^count (\d+)$"))
async def count(app, m):
    n = int(m.matches.group(1))
    await m.reply("got " + str(n))
```

## Commands

```python
filters.command("start")
filters.command(["start", "hi"])
filters.command("start", prefixes=["/", "."])
filters.command("start", case_sensitive=True)
```

When the filter matches, it stores the parsed parts in
`message.command`:

```python
@app.on_message(filters.outgoing & filters.command("weather"))
async def cmd(app, m):
    args = m.command[1:]   # everything after .weather
    city = " ".join(args) or "Moscow"
```

## Combining

```python
filter = (
    filters.outgoing
    & filters.command("ban")
    & (filters.group | filters.channel)
)
```

`&` is AND, `|` is OR, `~` is NOT, parentheses control precedence.

## Custom filters

```python
from vkmax.filters import create


def is_long(message) -> bool:
    return isinstance(message.text, str) and len(message.text) > 100


long_messages = create(is_long, name="long")


@app.on_message(long_messages)
async def warn(app, m):
    await m.reply("тише, тише")
```

The predicate may be sync or async, and it receives the `Message`.

## Lower-level (no filter)

Pass `None` to receive every event of that type:

```python
@app.on_message()                # every NOTIF_MESSAGE
async def log_all(app, m):
    ...
```
