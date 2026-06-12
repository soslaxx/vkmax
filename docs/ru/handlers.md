# Обработчики событий

Каждый push-пакет с сервера (`cmd=0`, опкод из диапазона `NOTIF_*`)
диспатчится в обработчики, зарегистрированные декораторами на
`Client`.

## Декораторы

| Декоратор | Что | Опкод |
|---|---|---|
| `@app.on_message(filter)` | новое / полученное сообщение | 128 `NOTIF_MESSAGE` |
| `@app.on_edited_message(filter)` | сообщение отредактировано | 128 + `filters.edited` |
| `@app.on_deleted_message(filter)` | удалили сообщение | 142 `NOTIF_MSG_DELETE` |
| `@app.on_reaction(filter)` | реакции изменились | 155 `NOTIF_MSG_REACTIONS_CHANGED` |
| `@app.on_typing(filter)` | индикатор печати | 129 `NOTIF_TYPING` |
| `@app.on_event(opcode, filter)` | любой опкод | свой |

Каждый декоратор принимает `Filter` (один или собранный из других) и
опциональный `group` (порядок).

## Сигнатура обработчика

```python
async def handler(client: Client, message: MessageType) -> None: ...
```

- `client` — тот же `Client` на котором повешен декоратор.
- `message` — типизированный `Message` (см. [message.md](message.md)).
- Синхронные функции тоже работают; диспатчер вызывает их в loop.

Возвращаемое значение игнорируется.

## Фильтры

```python
from vkmax import filters as f

filter = (f.incoming & f.private & f.text) | f.command("start")
```

Полный каталог: [filters.md](filters.md).

## Группы (порядок)

Обработчики запускаются в порядке возрастания `group`. Внутри одной
группы — в порядке регистрации.

```python
@app.on_message(filters.outgoing, group=0)
async def log(app, m):
    print("sent:", m.text)


@app.on_message(filters.outgoing & filters.command("ping"), group=10)
async def ping(app, m):
    await m.edit_markdown("**pong**")
```

## Программная регистрация

```python
async def my_callback(app, message):
    ...

app.add_handler(
    Opcode.NOTIF_MESSAGE,
    my_callback,
    filter=filters.command("start"),
    group=5,
)
```

## Raw-события

Для опкодов, которые **не** несут `Message`, подписывайся на уровне
транспорта:

```python
from vkmax import Opcode


def on_presence(packet):
    print(packet.payload)


app.transport.on(Opcode.NOTIF_PRESENCE, on_presence)
```

Или итерируй все push-пакеты:

```python
async for packet in app.transport.pushes():
    print(packet.opcode, packet.payload)
```

## Ошибки внутри обработчика

Исключение ловится, печатается в stdout
(`[vkmax] handler error in <name>: ...`), и диспатчер переходит к
следующему обработчику. На соединение не влияет.

## Lifecycle hooks

Специальных `on_start`/`on_stop` нет. Передай корутину в `app.run()`
для startup-логики, делай cleanup в `finally` вокруг `app.run()`,
или используй ручной цикл:

```python
async def main():
    app = Client("main")
    await app.start_session()
    print("online as", app.account_id)
    try:
        await asyncio.Event().wait()
    finally:
        await app.disconnect()
```
