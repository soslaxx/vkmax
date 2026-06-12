# Getting started

## Install

```bash
pip install vkmax
```

Dependencies: `msgpack`, `lz4`. Optional: `zstandard` (`pip install
vkmax[zstd]`) for the rare zstd-compressed packets.

## First login (SMS)

```python
import asyncio
from vkmax import MaxClient


async def main() -> None:
    client = MaxClient("main")
    await client.start(
        phone="+79991234567",
        code_callback=lambda: input("SMS code: "),
        password_callback=lambda: input("2FA password: "),
    )
    print("me =", client.account_id)
    await client.disconnect()


asyncio.run(main())
```

The session (device id, instance id, auth token, phone, account id) is
persisted to `~/.vkmax/main.json`. Next runs reuse the token, no SMS
needed.

## Subsequent logins

```python
client = MaxClient("main")
await client.start(token=client.device.token)
```

Or explicitly:

```python
await client.connect()
await client.login("<LOGIN_TOKEN>")
```

## Custom session location

Pass a filesystem path:

```python
client = MaxClient("/tmp/bot.json")
```

Or provide a fully-formed `DeviceSession`:

```python
from vkmax import DeviceSession, create_device_session

device = create_device_session()
client = MaxClient(device)
```

## Environment variables

- `VKMAX_HOME` — overrides `~/.vkmax`.
- `TZ` — used when building the default `userAgent.timezone`.

## Reading the result of `start`

`MaxClient.start` returns one of:

- `LoginResult` — full successful login.
- `VerifyCodeResult` — 2FA was required but no `password_callback` was
  passed. Inspect `requires_password`, `challenge_track_id`,
  `challenge_hint`, and call `check_password` manually.
