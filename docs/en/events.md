# Events

The server pushes notifications as packets with `cmd=0` and a known
opcode (see `Opcode.NOTIF_*`). Two ways to consume them.

## Handlers per opcode

```python
from vkmax import Opcode


@client.on(Opcode.NOTIF_MESSAGE)
async def on_msg(packet):
    print(packet.payload)
```

`client.on(opcode, handler)` registers an async (or sync) callable.
`client.off(opcode, handler)` removes a specific handler, or all
handlers for that opcode if `handler` is omitted.

## Shortcut: `on_message`

```python
@client.on_message
async def on_msg(packet):
    payload = packet.payload
    message = payload["message"]
    if message["sender"] == client.account_id:
        return
    await client.send_message(payload["chatId"], "echo: " + message["text"])
```

Equivalent to `client.on(Opcode.NOTIF_MESSAGE, ...)`.

## Async iterator

For every push packet, regardless of opcode:

```python
async for packet in client.events():
    print(packet.opcode, packet.payload)
```

## Useful opcodes

| Opcode | Name | What |
|---|---|---|
| 128 | `NOTIF_MESSAGE` | new / received message |
| 129 | `NOTIF_TYPING` | typing indicator |
| 130 | `NOTIF_MARK` | read marker moved |
| 131 | `NOTIF_CONTACT` | contact updated |
| 132 | `NOTIF_PRESENCE` | online / last seen |
| 134 | `NOTIF_CONFIG` | config changed |
| 135 | `NOTIF_CHAT` | chat metadata changed |
| 136 | `NOTIF_ATTACH` | upload finalized |
| 140 | `NOTIF_MSG_DELETE_RANGE` | bulk delete |
| 142 | `NOTIF_MSG_DELETE` | message deleted |
| 152 | `NOTIF_DRAFT` | draft changed |
| 155 | `NOTIF_MSG_REACTIONS_CHANGED` | reactions changed |
| 156 | `NOTIF_MSG_YOU_REACTED` | your reaction confirmed |
| 159 | `NOTIF_PROFILE` | profile updated |

Full list in `vkmax.Opcode`.

## Payload shape

Most `NOTIF_*` payloads look like:

```python
{
    "chatId": -75800508459204,
    "message": { "id": 116..., "sender": ..., "text": ..., "attaches": [...] },
    # opcode-specific extras
}
```

Use `Message.from_dict(message, chat_id=chat_id)` to get a typed object.
