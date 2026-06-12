# MaxClient

The single entry point. All RPC helpers are methods on it.

```python
MaxClient(
    session: str | Path | DeviceSession = "main",
    *,
    host: str = "api.oneme.ru",
    port: int = 443,
    request_timeout: float = 30.0,
    ping_interval: float = 30.0,
    auto_reconnect: bool = True,
    reconnect_delay: float = 1.0,
    max_reconnect_delay: float = 30.0,
    save_session: bool = True,
)
```

## Lifecycle

```python
await client.connect()       # TLS + handshake
await client.login(token)    # opcode LOGIN (19)
await client.disconnect()    # cancel tasks, close socket
```

`connect()` is idempotent. `disconnect()` cancels the ping loop, the
reconnect loop, and closes the writer.

As a context manager:

```python
async with MaxClient("main") as client:
    await client.login(token)
    ...
```

## `start()`

Convenience wrapper around `connect` + `login` / `request_code` +
`sign_in`:

```python
await client.start(
    token=None,
    phone=None,
    code_callback=None,
    password_callback=None,
)
```

Logic:

1. If `token` (or `client.device.token`) is set, try `login`. If it is
   accepted, return `LoginResult`.
2. Otherwise call `request_code(phone)`, prompt via `code_callback`,
   then `sign_in`. If the response requires a password, prompt via
   `password_callback`, call `check_password`, then `login`.

## Auto-reconnect

Any server-side disconnect (timeout, validation error, network) is
caught by the transport. When `auto_reconnect=True` a background task
reconnects with exponential backoff (`reconnect_delay` →
`max_reconnect_delay`) and re-logs in using the cached token.

`invoke()` waits for the connection to come back (up to
`wait_for_reconnect`, default 15s) before retrying once. After that it
raises `NotConnected` / `TransportClosed`.

## Pings

While connected, `vkmax` sends `Opcode.PING` every `ping_interval`
seconds (default 30). On a timeout the connection is treated as broken
and auto-reconnect kicks in.

## Low level

```python
packet = await client.invoke(Opcode.MSG_GET_STAT, {
    "chatId": chat_id, "messageId": int(message_id),
})
packet.cmd      # 1 = ok, 3 = error
packet.payload  # dict from the server
```

All opcodes are in `vkmax.Opcode`.

## Attributes

- `client.device` — `DeviceSession`.
- `client.token`, `client.account_id`, `client.me` — set after login.
- `client.config` — `{user, chats, ...}` snapshot from the LOGIN reply.
- `client.handshake` — server response to opcode 6.
- `client.calls_seed`, `client.server_time` — convenience.
- `client.transport` — raw `Transport` (with `.is_connected`).
