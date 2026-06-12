# Getting started

## Install

```bash
pip install vkmax
```

Runtime deps: `msgpack`, `lz4`. Optional: `zstandard` (`pip install
vkmax[zstd]`) only if the server ever sends you a zstd-compressed
packet.

## 1. Log in

Create a session file at `~/.vkmax/main.json`. Use the bundled
`login.py`:

```bash
python login.py main
```

It asks for the phone, the SMS code, and (if 2FA is on) the password.
For a brand-new number it also walks you through registration. The
session (device id, instance id, login token) is saved — next runs
won't need SMS.

You can also drive the flow from code:

```python
import asyncio
from vkmax import Client


async def main():
    app = Client("main")
    await app.start(
        phone="+79991234567",
        code_callback=lambda: input("SMS code: "),
        password_callback=lambda: input("2FA password: "),
    )
    print("me =", app.account_id)
    await app.disconnect()


asyncio.run(main())
```

## 2. Your first bot

```python
from vkmax import Client, MessageType, filters

app = Client("main")


@app.on_message(filters.outgoing & filters.command("ping"))
async def cmd_ping(app: Client, message: MessageType):
    await message.edit_markdown("**pong**")


@app.on_message(filters.incoming & filters.private & filters.text)
async def echo(app: Client, message: MessageType):
    await message.reply(message.text or "")


app.run()
```

That's a complete userbot:

- `filters.outgoing & filters.command("ping")` triggers only on your
  own `.ping` message.
- `message.edit_markdown(...)` rewrites the original message; MAX
  renders **pong** in bold.
- The second handler replies to every private message sent **to** you.
- `app.run()` connects, logs in with the cached token, then listens
  forever.

Run it with `python yourbot.py`.

## 3. Send something

```python
import asyncio
from vkmax import Client


async def main():
    app = Client("main")
    await app.start_session()
    await app.send_message(307609904, "hello!")
    await app.send_markdown(307609904, "**bold** *italic* `code`")
    await app.send_photo(307609904, "photo.jpg", caption="a photo")
    await app.upload_video(307609904, "clip.mp4")
    await app.disconnect()


asyncio.run(main())
```

## Custom session location

```python
Client("/tmp/bot.json")
```

Or build a `DeviceSession` yourself:

```python
from vkmax import DeviceSession, create_device_session, Client

device = create_device_session()
app = Client(device)
```

## Environment variables

- `VKMAX_HOME` — overrides `~/.vkmax`.
- `TZ` — used for the default `userAgent.timezone`.

## Next steps

- [client.md](client.md) — full `Client` constructor and lifecycle.
- [handlers.md](handlers.md) — event handlers and groups.
- [filters.md](filters.md) — everything you can filter on.
- [message.md](message.md) — what you can do with a `Message`.
