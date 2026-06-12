# Client

The pyrogram-style entry point. `Client` extends `MaxClient`, so
every low-level method is still available; on top it adds typed
event dispatch and helpers.

```python
from vkmax import Client

app = Client(
    session="main",                  # session name → ~/.vkmax/main.json
    host="api.oneme.ru",
    port=443,
    request_timeout=30.0,
    ping_interval=30.0,
    auto_reconnect=True,
    reconnect_delay=1.0,
    max_reconnect_delay=30.0,
    save_session=True,
    proxy=None,                      # str | ProxyConfig | None
)
```

## Three ways to start

### 1. `app.run()` — synchronous, blocks until Ctrl+C

```python
app = Client("main")
app.run()
```

Under the hood: `asyncio.run(connect() → login(token) → wait forever)`.
Use this for userbots.

### 2. `app.run(main_coroutine)` — run an async entry point

```python
import asyncio

async def main():
    await app.send_message(307609904, "hi")

app.run(main())
```

### 3. Manual lifecycle

```python
async def main():
    app = Client("main")
    await app.start_session()        # connect + login
    try:
        await app.send_message(307609904, "hi")
    finally:
        await app.disconnect()

asyncio.run(main())
```

Or as a context manager (inherited from `MaxClient`):

```python
async with Client("main") as app:
    await app.login(app.device.token)
    ...
```

## Auto-reconnect

With `auto_reconnect=True` (default) any disconnect — server
validation error, ping timeout, broken socket — is recovered in the
background:

1. A reconnect task waits `reconnect_delay` (doubling on each
   failure, capped at `max_reconnect_delay`).
2. It dials the host again, redoes the handshake and `login(token)`.
3. The next `invoke()` waits up to 15 s for the connection to come
   back and retries once. Failure raises `NotConnected`.

Server-side **validation errors** (`proto.payload`) are special: the
server returns `cmd=ERROR` and immediately drops the TCP socket.
`vkmax` reconnects transparently, so your *next* call works.

## Pings

While connected, `Client` sends `Opcode.PING` every `ping_interval`
seconds (30 by default). Without pings the server times out the
connection after ~2 minutes.

## Proxy

Pass a proxy URL or a `ProxyConfig`:

```python
Client("main", proxy="socks5://user:pass@127.0.0.1:1080")
Client("main", proxy="http://10.0.0.1:8080")
```

Supported schemes: `http`, `https` (CONNECT), `socks5`, `socks5h`
(remote DNS). Full details: [proxy.md](proxy.md).

## Attributes after login

| Attribute | Meaning |
|---|---|
| `app.account_id` | your user id |
| `app.me` | dict from the LOGIN response |
| `app.token` | cached login token |
| `app.config["user"]` | privacy settings snapshot |
| `app.config["chats"]` | per-chat notification settings |
| `app.server_time` | server time in ms at LOGIN |
| `app.handshake` | dict from the SESSION_INIT response |
| `app.transport` | raw `Transport` (`.is_connected`) |
| `app.device` | `DeviceSession` (mutate, then `app.device.save(path)`) |

## Helpers

```python
user = await app.get_me()              # User
user = await app.get_user(user_id)     # User | None
chat = await app.get_chat(chat_id)     # Chat | None  (pyrogram-style)
```

All inherited `MaxClient` methods stay available — see [messages.md](
messages.md), [chats.md](chats.md), [contacts.md](contacts.md),
[profile.md](profile.md), [privacy.md](privacy.md), etc.

## Low-level access

For opcodes without a wrapper:

```python
from vkmax import Opcode

packet = await app.invoke(Opcode.MSG_GET_STAT, {
    "chatId": chat_id, "messageId": int(message_id),
})
packet.cmd       # 1=OK, 3=ERROR
packet.payload   # dict from server
```

See [low-level.md](low-level.md).
