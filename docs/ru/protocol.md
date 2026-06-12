# Протокол

`vkmax` говорит на бинарном мобильном протоколе официального
Android-приложения MAX. Это фреймированный TCP/TLS-стрим msgpack-пакетов,
опционально сжатых LZ4 block.

## Endpoint

- Хост: `api.oneme.ru`
- Порт: `443`
- TLS (любой современный контекст; сервер поддерживает TLS 1.3).

## Фрейм

Каждый пакет: 10-байтный заголовок + payload.

```
оффсет  байты  поле
0       1      api_version    (всегда 0x0A = 10)
1       1      cmd            (0=запрос, 1=ok, 2=not_found, 3=ошибка)
2       2      seq            (uint16 BE; запрос ↔ ответ по seq)
4       2      opcode         (uint16 BE; ID метода)
6       4      packed_len     (uint32 BE: flag<<24 | len)
10      N      payload        (msgpack, возможно LZ4)
```

- `flag = packed_len >> 24` — 0 если raw msgpack, >0 если LZ4 block.
- `len = packed_len & 0xFFFFFF` — длина payload в байтах.

Сервер использует тот же формат для ответов и push-событий.

## Сжатие

Если raw msgpack `>= 32` байт, клиент пробует LZ4 block. Если сжатый
короче — кладёт его, а в заголовок ставит флаг сжатия равный
`(raw_len // body_len) + 1`. Точное значение флага не ноль; любой
ненулевой флаг = «распаковать».

Входящие могут быть zstd (магия `28 b5 2f fd`) или LZ4 frame
(`04 22 4d 18`); все три варианта поддержаны.

## Кодирование payload

msgpack с `use_bin_type=True`. Карты могут иметь int- и str-ключи.
Библиотека читает с `strict_map_key=False`, чтобы поддерживать оба
варианта (важно для `settings.chats`, где ключ — chat_id как int).

## Handshake (опкод 6)

Первый пакет каждого соединения:

```python
{
    "mt_instanceid": "<uuid>",
    "userAgent": {
        "deviceType": "ANDROID",
        "appVersion": "26.17.1",
        "osVersion": "Android 11",
        "timezone": "Europe/Moscow",
        "screen": "420dpi 420dpi 1080x2340",
        "pushDeviceType": "GCM",
        "arch": "arm64-v8a",
        "locale": "ru",
        "buildNumber": 6712,
        "deviceName": "TECNO MOBILE LIMITED TECNO LE7n",
        "deviceLocale": "ru",
    },
    "clientSessionId": <int>,
    "deviceId": "<hex>",
}
```

Сервер отвечает `callsSeed`, `location`, гео-конфигом.

## Авторизация (по токену)

После handshake — login по токену (опкод 19):

```python
{
    "token": "<login_token>",
    "interactive": True,
    "presenceSync": 0,
    "exp": {"chatsCountGroups": b"\x0b\x32"},
    "chatCacheFingerprint": <bytes>,
}
```

`chatCacheFingerprint` считается из `callsSeed` сервера и `deviceId`
клиента. Хелпер: `vkmax.protocol.chat_cache_fingerprint`.

## Авторизация (SMS)

1. `AUTH_REQUEST` (17): `{phone, type: "START_AUTH", language: "ru"}`
   → временный `token`.
2. `AUTH` (18): `{token, verifyCode, authTokenType: "CHECK_CODE"}` →
   `tokenAttrs.LOGIN.token` (или `passwordChallenge` при 2FA).
3. Опционально `AUTH_LOGIN_CHECK_PASSWORD` (113) для 2FA.
4. `LOGIN` (19) как выше.

## Ответы и ошибки

- `cmd=1` (OK) — обычный ответ.
- `cmd=2` (NOT_FOUND) — мягкий промах (редко).
- `cmd=3` (ERROR) — `payload` содержит `{error, message, localizedMessage}`.
  Сервер **закрывает TCP-соединение** после ERROR. При
  `auto_reconnect=True` `vkmax` сам переподключается и логинится,
  следующий вызов проходит.

## Пинги

`vkmax` шлёт `PING` (1) каждые `ping_interval` секунд (30 по умолчанию).
Без пингов сервер таймаутит соединение примерно через две минуты.

## См. также

- `opcodes.md` — полный список опкодов.
- `vkmax.protocol` — Python-реализация pack/unpack и fingerprint.
