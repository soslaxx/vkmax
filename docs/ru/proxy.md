# Прокси

`vkmax` умеет туннелировать TLS-соединение к `api.oneme.ru:443`
через HTTP CONNECT или SOCKS5. Полезно где MAX заблокирован.

## Быстро

Передай URL в конструктор:

```python
from vkmax import Client

app = Client("main", proxy="socks5://user:pass@127.0.0.1:1080")
```

Поддерживаются схемы:

- `http://` и `https://` — HTTP CONNECT.
- `socks5://` — SOCKS5, прокси резолвит хост **локально**.
- `socks5h://` — SOCKS5, прокси резолвит хост **удалённо**
  (предпочтительно при заблокированном DNS).

Логин/пароль читаются из URL.

## Программно

```python
from vkmax import Client
from vkmax.proxy import ProxyConfig

proxy = ProxyConfig(
    scheme="socks5h",
    host="proxy.example.com",
    port=1080,
    username="alice",
    password="secret",
)
app = Client("main", proxy=proxy)
```

## Как это работает

`Transport.connect()` смотрит на `Client.proxy`. Если задан:

1. Открывает TCP до прокси.
2. Делает CONNECT или SOCKS5-handshake, просит соединить с
   `api.oneme.ru:443`.
3. Поверх этого сокета поднимает TLS
   (`ssl.create_default_context()`).
4. Передаёт пайп в обычный reader/writer.

Автореконнект, ping-loop, восстановление после `proto.payload` —
всё это работает; каждый реконнект повторяет тот же путь.

## Аплоады через прокси

Пока что HTTPS-соединения для аплоада фото/видео/файлов **не** идут
через прокси — они уходят напрямую на upload-хост (`iu.oneme.ru`,
`iv.oneme.ru`). Если нужно полное проксирование, открой issue —
uploads-хелперам нужен небольшой рефактор под `ProxyConfig`.

## Траблшутинг

- `ConnectionError: proxy CONNECT failed: 407 ...` — неправильные
  креды HTTP-прокси.
- `ConnectionError: SOCKS5: auth rejected` — то же для SOCKS5.
- `ConnectionError: SOCKS5: server replied 4` — хост недоступен с
  прокси.
- `TransportClosed: connection lost: 0 bytes ...` — прокси работает,
  но `api.oneme.ru` отверг TLS (например, прокси режет SNI).
