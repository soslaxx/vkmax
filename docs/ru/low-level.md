# Низкий уровень

Под pyrogram-style `Client` лежит `MaxClient`: тот же класс, но без
типизированных событий и декораторов. Используется когда нужен сырой
доступ.

## `invoke()`

Любой опкод + payload, возвращает `Packet`:

```python
from vkmax import Client, Opcode

app = Client("main")
await app.start_session()

packet = await app.invoke(Opcode.MSG_GET_STAT, {
    "chatId": 307609904,
    "messageId": 116735543880668877,
})
print(packet.cmd)      # 1 = OK, 2 = NOT_FOUND, 3 = ERROR
print(packet.payload)  # dict от сервера
```

Ответ `cmd=3` превращается в `PacketError`:

```python
from vkmax import PacketError

try:
    await app.invoke(Opcode.MSG_REACTION, {"chatId": 1, "messageId": 0})
except PacketError as e:
    print(e.error_key)   # например "proto.payload"
    print(e.message)     # локализованный текст
    print(e.payload)     # полный dict
```

Полный каталог опкодов: [opcodes.md](opcodes.md).

## Хуки транспорта

Для push-событий, не несущих `Message` (presence, folders, config
change…) — слушай на уровне транспорта:

```python
from vkmax import Opcode


async def on_presence(packet):
    print(packet.payload)


app.transport.on(Opcode.NOTIF_PRESENCE, on_presence)
```

Снять:

```python
app.transport.off(Opcode.NOTIF_PRESENCE, on_presence)
app.transport.off(Opcode.NOTIF_PRESENCE)            # все обработчики
```

Или итерировать все пуши:

```python
async for packet in app.transport.pushes():
    print(packet.opcode)
```

## `Packet`

```python
@dataclass
class Packet:
    api: int        # версия протокола, всегда 10
    cmd: int        # 0 запрос/push, 1 OK, 2 NOT_FOUND, 3 ERROR
    seq: int        # пара запрос↔ответ
    opcode: int     # из vkmax.Opcode
    payload: Any    # msgpack body (обычно dict)
```

Хелперы: `packet.is_ok`, `packet.is_error`, `packet.is_push`,
`packet.is_not_found`.

## Ждать конкретное событие

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

## Чистый `MaxClient`

Если диспатч событий вообще не нужен, бери `MaxClient`:

```python
from vkmax import MaxClient, Opcode

client = MaxClient("main")
await client.connect()
await client.login(client.device.token)
packet = await client.invoke(Opcode.SESSIONS_INFO, {})
print(packet.payload["sessions"])
await client.disconnect()
```

Всё что выше применимо и к `MaxClient`, и к `Client`.
