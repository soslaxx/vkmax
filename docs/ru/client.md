# MaxClient

Единственная точка входа. Все RPC-хелперы — методы этого класса.

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

## Жизненный цикл

```python
await client.connect()       # TLS + handshake
await client.login(token)    # опкод LOGIN (19)
await client.disconnect()    # отменить таски, закрыть сокет
```

`connect()` идемпотентен. `disconnect()` останавливает ping-loop,
reconnect-loop, закрывает writer.

Как контекст-менеджер:

```python
async with MaxClient("main") as client:
    await client.login(token)
    ...
```

## `start()`

Обёртка над `connect` + `login` / `request_code` + `sign_in`:

```python
await client.start(
    token=None,
    phone=None,
    code_callback=None,
    password_callback=None,
)
```

Логика:

1. Если есть `token` (или `client.device.token`) — пробует `login`.
   При успехе возвращает `LoginResult`.
2. Иначе зовёт `request_code(phone)`, спрашивает код через
   `code_callback`, затем `sign_in`. Если требуется пароль 2FA —
   спрашивает через `password_callback`, делает `check_password`, потом
   `login`.

## Автореконнект

Любое серверное закрытие соединения (таймаут, ошибка валидации, сеть)
перехватывается транспортом. При `auto_reconnect=True` фоновый таск
переподключается с экспоненциальным backoff (`reconnect_delay` →
`max_reconnect_delay`) и логинится по сохранённому токену.

`invoke()` ждёт восстановления соединения (до `wait_for_reconnect`,
по умолчанию 15 с) и один раз повторяет запрос. После этого бросает
`NotConnected` / `TransportClosed`.

## Пинги

Пока соединение живо, `vkmax` шлёт `Opcode.PING` каждые
`ping_interval` секунд (по умолчанию 30). По таймауту соединение
считается умершим и срабатывает автореконнект.

## Низкоуровневые вызовы

```python
packet = await client.invoke(Opcode.MSG_GET_STAT, {
    "chatId": chat_id, "messageId": int(message_id),
})
packet.cmd      # 1 = ok, 3 = error
packet.payload  # dict от сервера
```

Все опкоды — в `vkmax.Opcode`.

## Атрибуты

- `client.device` — `DeviceSession`.
- `client.token`, `client.account_id`, `client.me` — после login.
- `client.config` — `{user, chats, ...}` снапшот из LOGIN.
- `client.handshake` — ответ сервера на опкод 6.
- `client.calls_seed`, `client.server_time` — служебные.
- `client.transport` — `Transport` (с `.is_connected`).
