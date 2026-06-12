# vkmax

Async Python client for the MAX messenger (max.ru / OneMe) **mobile API**.

Unlike the older WebSocket-based web API, this version speaks the binary
mobile protocol (`api.oneme.ru:443`, TLS + msgpack + LZ4) used by the
official Android app. That gives access to a much larger set of methods
and to data the web protocol does not expose.

## What is MAX?

MAX (internal code name OneMe) is a Russian messenger developed by VK
Group, integrated with Gosuslugi/ESIA. This library lets you build
userbots and custom clients on top of it.

## Installation

```bash
pip install vkmax
```

Dependencies: `msgpack`, `lz4` (and optionally `zstandard` for the
`zstd` extra).

## Quick start

```python
import asyncio
from vkmax import MaxClient, Packet


async def get_code() -> str:
    return input("SMS code: ").strip()


async def main() -> None:
    client = MaxClient("main")

    if client.device.token:
        await client.start(token=client.device.token)
    else:
        phone = input("Phone (+7...): ").strip()
        await client.start(phone=phone, code_callback=get_code)

    print(f"Logged in as {client.account_id}")

    @client.on_message
    async def on_message(packet: Packet) -> None:
        payload = packet.payload or {}
        message = payload.get("message") or {}
        if message.get("sender") == client.account_id:
            return
        text = message.get("text") or ""
        if text.startswith(".ping"):
            await client.send_message(
                payload["chatId"], "pong", reply_to=message["id"]
            )

    await asyncio.Event().wait()


asyncio.run(main())
```

The session (device id, instance id, auth token) is cached at
`~/.vkmax/main.json`, so subsequent runs reuse the token automatically.

## Highlights

- Async, single-class API (`MaxClient`) with 140+ methods.
- Binary mobile protocol with transparent LZ4 compression.
- Automatic reconnect + re-login after server-side disconnects.
- Event handlers per opcode: `client.on(Opcode.NOTIF_MESSAGE, handler)`
  or the shortcut `@client.on_message`.
- Typed result models (`Message`, `Chat`, `Contact`, `ReactionInfo`,
  `Attachment`) plus raw `Packet` access for advanced use.
- File and photo uploads, sticker packs, reactions, message search,
  groups, folders, polls, call history.

## Common operations

```python
await client.send_message(chat_id, "hello")
await client.reply_message(chat_id, message_id, "reply")
await client.edit_message(chat_id, message_id, "edited")
await client.delete_messages(chat_id, [message_id], for_all=True)

await client.react_message(chat_id, message_id, "fire")  # or any emoji
await client.cancel_reaction(chat_id, message_id)
reactions = await client.get_reactions(chat_id, message_id)

chats = await client.list_chats()
group = await client.get_chat(chat_id)
members = await client.get_chat_members(chat_id)

await client.upload_photo("image.jpg")
await client.upload_file(chat_id, "doc.pdf")

results = await client.public_search("news")
folders = await client.get_folders()
```

## Low-level

For opcodes the wrappers don't cover yet:

```python
from vkmax import Opcode
packet = await client.invoke(Opcode.MSG_GET_STAT, {
    "chatId": chat_id, "messageId": message_id,
})
print(packet.payload)
```

Full list of opcodes: see `vkmax.enums.Opcode`.

## Notes

- The server enforces strict payload validation and will close the
  TCP connection on any rejected payload. `vkmax` reconnects and
  re-authenticates automatically; your next call just works.
- Reaction IDs accept either an emoji (`"\u2764\ufe0f"`) or an alias
  (`"heart"`, `"fire"`, `"like"`, ...). See `vkmax.REACTION_ALIASES`.
- `messageId` fields are sent as **integers** on the mobile API
  (unlike the web API which used strings).
- Account deletion and privacy settings are intentionally not
  implemented.

## License

MIT.
