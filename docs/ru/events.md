# События

Сервер пушит уведомления как пакеты с `cmd=0` и известным опкодом
(см. `Opcode.NOTIF_*`). Два способа их слушать.

## Хендлеры по опкоду

```python
from vkmax import Opcode


@client.on(Opcode.NOTIF_MESSAGE)
async def on_msg(packet):
    print(packet.payload)
```

`client.on(opcode, handler)` регистрирует sync или async коллбек.
`client.off(opcode, handler)` снимает конкретный хендлер, без аргумента
`handler` — все на этот опкод.

## Шорткат `on_message`

```python
@client.on_message
async def on_msg(packet):
    payload = packet.payload
    message = payload["message"]
    if message["sender"] == client.account_id:
        return
    await client.send_message(payload["chatId"], "echo: " + message["text"])
```

Эквивалент `client.on(Opcode.NOTIF_MESSAGE, ...)`.

## Асинхронный итератор

Для любых push-пакетов:

```python
async for packet in client.events():
    print(packet.opcode, packet.payload)
```

## Полезные опкоды

| Опкод | Имя | Что |
|---|---|---|
| 128 | `NOTIF_MESSAGE` | новое / обновлённое сообщение |
| 129 | `NOTIF_TYPING` | индикатор печати |
| 130 | `NOTIF_MARK` | сдвиг маркера прочитанного |
| 131 | `NOTIF_CONTACT` | контакт обновился |
| 132 | `NOTIF_PRESENCE` | онлайн / last seen |
| 134 | `NOTIF_CONFIG` | сменились настройки |
| 135 | `NOTIF_CHAT` | сменились данные чата |
| 136 | `NOTIF_ATTACH` | аплоад завершён |
| 140 | `NOTIF_MSG_DELETE_RANGE` | массовое удаление |
| 142 | `NOTIF_MSG_DELETE` | удалили сообщение |
| 152 | `NOTIF_DRAFT` | сменился черновик |
| 155 | `NOTIF_MSG_REACTIONS_CHANGED` | изменились реакции |
| 156 | `NOTIF_MSG_YOU_REACTED` | твоя реакция подтверждена |
| 159 | `NOTIF_PROFILE` | обновился твой профиль |

Полный список — в `vkmax.Opcode`.

## Форма payload

Большинство `NOTIF_*` выглядят так:

```python
{
    "chatId": -75800508459204,
    "message": { "id": 116..., "sender": ..., "text": ..., "attaches": [...] },
    # опкод-специфичные поля
}
```

Используй `Message.from_dict(message, chat_id=chat_id)` чтобы получить
типизированный объект.
