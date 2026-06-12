# Быстрый старт

## Установка

```bash
pip install vkmax
```

Зависимости: `msgpack`, `lz4`. Опционально: `zstandard` (`pip install
vkmax[zstd]`) для редких zstd-сжатых пакетов.

## Первый вход (SMS)

```python
import asyncio
from vkmax import MaxClient


async def main() -> None:
    client = MaxClient("main")
    await client.start(
        phone="+79991234567",
        code_callback=lambda: input("SMS код: "),
        password_callback=lambda: input("Пароль 2FA: "),
    )
    print("me =", client.account_id)
    await client.disconnect()


asyncio.run(main())
```

Сессия (`device_id`, `instance_id`, токен, телефон, account_id) сохраняется
в `~/.vkmax/main.json`. Следующие запуски используют токен — SMS
не нужен.

## Последующие входы

```python
client = MaxClient("main")
await client.start(token=client.device.token)
```

Или явно:

```python
await client.connect()
await client.login("<LOGIN_TOKEN>")
```

## Своё место для сессии

Передать путь к файлу:

```python
client = MaxClient("/tmp/bot.json")
```

Или использовать готовый `DeviceSession`:

```python
from vkmax import DeviceSession, create_device_session

device = create_device_session()
client = MaxClient(device)
```

## Переменные окружения

- `VKMAX_HOME` — переопределяет `~/.vkmax`.
- `TZ` — используется для `userAgent.timezone` по умолчанию.

## Что возвращает `start`

`MaxClient.start` возвращает одно из:

- `LoginResult` — полный успешный вход.
- `VerifyCodeResult` — потребовался 2FA, но `password_callback` не был
  передан. Поля: `requires_password`, `challenge_track_id`,
  `challenge_hint`. Доверши `check_password` вручную.
