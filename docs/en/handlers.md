# Event handlers

Every push event from the server (`cmd=0`, opcode in the
`NOTIF_*` range) is dispatched to the handlers you register with
decorators on the `Client`.

## Decorators

| Decorator | What | Opcode |
|---|---|---|
| `@app.on_message(filter)` | new / received message | 128 `NOTIF_MESSAGE` |
| `@app.on_edited_message(filter)` | message was edited | 128 + `filters.edited` |
| `@app.on_deleted_message(filter)` | one message deleted | 142 `NOTIF_MSG_DELETE` |
| `@app.on_reaction(filter)` | reactions changed | 155 `NOTIF_MSG_REACTIONS_CHANGED` |
| `@app.on_typing(filter)` | typing indicator | 129 `NOTIF_TYPING` |
| `@app.on_event(opcode, filter)` | any opcode | custom |

All decorators accept a `Filter` (single or combined) and an optional
`group` argument for ordering.

## Handler signature

```python
async def handler(client: Client, message: MessageType) -> None: ...
```

- `client` — the same `Client` instance you decorated on.
- `message` — a typed `Message` (see [message.md](message.md)).
- Synchronous functions also work; the dispatcher schedules them in
  the loop.

Returning anything is ignored.

## Filters

Filters are imported from `vkmax.filters` and combined with `&`,
`|`, `~`:

```python
from vkmax import filters as f

filter = (f.incoming & f.private & f.text) | f.command("start")
```

Full catalogue: [filters.md](filters.md).

## Groups (order)

Handlers run in ascending `group` order. Inside the same group,
registration order is preserved.

```python
@app.on_message(filters.outgoing, group=0)
async def log(app, m):
    print("sent:", m.text)


@app.on_message(filters.outgoing & filters.command("ping"), group=10)
async def ping(app, m):
    await m.edit_markdown("**pong**")
```

## Adding handlers programmatically

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

## Raw events

If you need raw packets — for example for an opcode that doesn't
carry a `Message` — subscribe at the transport level:

```python
from vkmax import Opcode


def on_presence(packet):
    print(packet.payload)


app.transport.on(Opcode.NOTIF_PRESENCE, on_presence)
```

Or iterate all pushes:

```python
async for packet in app.transport.pushes():
    print(packet.opcode, packet.payload)
```

## Errors inside handlers

Exception raised inside your handler is caught, logged to stdout
(`[vkmax] handler error in <name>: ...`) and the dispatcher moves on
to the next handler. The connection is not affected.

## Lifecycle hooks

There are no hard-coded `on_start`/`on_stop` decorators. Pass a
coroutine to `app.run()` for startup logic, do cleanup in a `finally`
block around `app.run()` itself, or use the explicit lifecycle:

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
