# Client

Pyrogram-style точка входа. `Client` наследует `MaxClient`, поэтому
все низкоуровневые методы остаются на месте; сверху добавлены
типизированный диспатч событий и удобные хелперы.

```python
from vkmax import Client

app = Client(
    session="main",                  # имя сессии → ~/.vkmax/main.json
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

## Три способа запуска

### 1. `app.run()` — блокирующий, до Ctrl+C

```python
app = Client("main")
app.run()
```

Внутри: `asyncio.run(connect() → login(token) → ждать вечно)`.
Используется для юзерботов.

### 2. `app.run(main_coroutine)` — async entry-point

```python
import asyncio

async def main():
    await app.send_message(307609904, "hi")

app.run(main())
```

### 3. Ручной жизненный цикл

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

Как контекст-менеджер (унаследовано от `MaxClient`):

```python
async with Client("main") as app:
    await app.login(app.device.token)
    ...
```

## Автореконнект

С `auto_reconnect=True` (по умолчанию) любой разрыв соединения —
ошибка валидации сервера, таймаут пингов, сбой сети — восстанавливается
в фоне:

1. Reconnect-таск ждёт `reconnect_delay` (удваивается на каждой
   неудаче, потолок `max_reconnect_delay`).
2. Открывает соединение заново, делает handshake и `login(token)`.
3. Следующий `invoke()` ждёт до 15 с восстановления и однократно
   ретраит запрос. Если не выходит — `NotConnected`.

**Ошибки валидации** (`proto.payload`) — отдельный случай: сервер
отвечает `cmd=ERROR` и сразу закрывает TCP-соединение. `vkmax`
переподключается прозрачно, следующий вызов работает.

## Пинги

Клиент шлёт `Opcode.PING` каждые `ping_interval` секунд (30 по
умолчанию). Без пингов сервер таймаутит соединение примерно через
2 минуты.

## Прокси

```python
Client("main", proxy="socks5://user:pass@127.0.0.1:1080")
Client("main", proxy="http://10.0.0.1:8080")
```

Поддержка: `http`, `https` (CONNECT), `socks5`, `socks5h` (remote DNS).
Подробности: [proxy.md](proxy.md).

## Атрибуты после login

| Атрибут | Что это |
|---|---|
| `app.account_id` | твой user id |
| `app.me` | dict из LOGIN |
| `app.token` | сохранённый login token |
| `app.config["user"]` | снапшот настроек приватности |
| `app.config["chats"]` | настройки уведомлений по чатам |
| `app.server_time` | время сервера (ms) на момент LOGIN |
| `app.handshake` | dict из SESSION_INIT |
| `app.transport` | `Transport` (`.is_connected`) |
| `app.device` | `DeviceSession` (меняй, потом `app.device.save(path)`) |

## Хелперы

```python
user = await app.get_me()              # User
user = await app.get_user(user_id)     # User | None
chat = await app.get_chat(chat_id)     # Chat | None  (pyrogram-style)
```

Все унаследованные методы `MaxClient` доступны как есть — см.
[messages.md](messages.md), [chats.md](chats.md),
[contacts.md](contacts.md), [profile.md](profile.md),
[privacy.md](privacy.md), и т.д.

## Низкоуровневый доступ

Для опкодов без обёртки:

```python
from vkmax import Opcode

packet = await app.invoke(Opcode.MSG_GET_STAT, {
    "chatId": chat_id, "messageId": int(message_id),
})
packet.cmd       # 1=OK, 3=ERROR
packet.payload   # dict от сервера
```

См. [low-level.md](low-level.md).
