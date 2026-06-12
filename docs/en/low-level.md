# Low level

Below the pyrogram-style `Client` lives `MaxClient`: the same class,
minus typed events and decorators. Use it directly when you need raw
access to the protocol.

## `invoke()`

Any opcode + payload, returns a `Packet`:

```python
from vkmax import Client, Opcode

app = Client("main")
await app.start_session()

packet = await app.invoke(Opcode.MSG_GET_STAT, {
    "chatId": 307609904,
    "messageId": 116735543880668877,
})
print(packet.cmd)      # 1 = OK, 2 = NOT_FOUND, 3 = ERROR
print(packet.payload)  # dict from the server
```

A `cmd=3` reply is converted to `PacketError`. Catch and inspect:

```python
from vkmax import PacketError

try:
    await app.invoke(Opcode.MSG_REACTION, {"chatId": 1, "messageId": 0})
except PacketError as e:
    print(e.error_key)   # e.g. "proto.payload"
    print(e.message)     # localised text
    print(e.payload)     # full server dict
```

Full opcode catalogue: [opcodes.md](opcodes.md).

## Transport hooks

Server push events that don't carry a `Message` (presence updates,
folders, config changes, …) can be handled at the transport level:

```python
from vkmax import Opcode


async def on_presence(packet):
    print(packet.payload)


app.transport.on(Opcode.NOTIF_PRESENCE, on_presence)
```

Remove a handler:

```python
app.transport.off(Opcode.NOTIF_PRESENCE, on_presence)
app.transport.off(Opcode.NOTIF_PRESENCE)            # all handlers
```

Or iterate every push packet:

```python
async for packet in app.transport.pushes():
    print(packet.opcode)
```

## `Packet`

```python
@dataclass
class Packet:
    api: int        # protocol version, always 10
    cmd: int        # 0 request / push, 1 OK, 2 NOT_FOUND, 3 ERROR
    seq: int        # request/response pairing id
    opcode: int     # one of vkmax.Opcode
    payload: Any    # decoded msgpack body (usually a dict)
```

Helpers: `packet.is_ok`, `packet.is_error`, `packet.is_push`,
`packet.is_not_found`.

## Wait for a specific response

Most flows are request/response and don't need this; but for events
you can wait for from a push opcode:

```python
import asyncio
from vkmax import Opcode

waiter = asyncio.get_event_loop().create_future()

def capture(packet):
    if not waiter.done():
        waiter.set_result(packet)

app.transport.on(Opcode.NOTIF_PROFILE, capture)
profile_change = await asyncio.wait_for(waiter, timeout=30)
app.transport.off(Opcode.NOTIF_PROFILE, capture)
```

## Manual `MaxClient`

If you don't need event dispatch at all, drop the `Client`:

```python
from vkmax import MaxClient, Opcode

client = MaxClient("main")
await client.connect()
await client.login(client.device.token)
packet = await client.invoke(Opcode.SESSIONS_INFO, {})
print(packet.payload["sessions"])
await client.disconnect()
```

Everything from this doc applies to both `MaxClient` and `Client`.
