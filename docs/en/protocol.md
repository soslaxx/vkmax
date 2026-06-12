# Protocol

`vkmax` speaks the binary mobile protocol that the official Android app
uses. It is a framed TCP/TLS stream of msgpack-encoded packets,
optionally compressed with LZ4 block.

## Endpoint

- Host: `api.oneme.ru`
- Port: `443`
- TLS (any modern context; the server supports TLS 1.3).

## Frame

Every packet is a 10-byte header followed by a payload:

```
offset  bytes  field
0       1      api_version    (always 0x0A = 10)
1       1      cmd            (0=request, 1=ok, 2=not_found, 3=error)
2       2      seq            (uint16 big-endian, request-response match)
4       2      opcode         (uint16 big-endian, RPC method id)
6       4      packed_len     (uint32 big-endian: flag<<24 | len)
10      N      payload        (msgpack, optionally LZ4-compressed)
```

- `flag = packed_len >> 24` — 0 if payload is raw msgpack, >0 if it is
  LZ4 block-compressed.
- `len = packed_len & 0xFFFFFF` — number of payload bytes that follow.

The server uses the same format for replies and push events.

## Compression

When the raw msgpack payload is `>= 32` bytes the client tries to
LZ4-block-compress it. If the compressed body is smaller, the body is
replaced with the compressed bytes and the header's compression flag is
set to `(raw_len // body_len) + 1`. The exact value of the flag is not
zero; any non-zero flag means "decompress".

Incoming compressed payloads may also be zstd (magic `28 b5 2f fd`) or
LZ4 frame (`04 22 4d 18`); the library handles all three.

## Payload encoding

msgpack with `use_bin_type=True`. Maps may contain integer or string
keys. The library decodes with `strict_map_key=False` to support
both styles (notably for `settings.chats`, where the key is the chat
id as an integer).

## Handshake (opcode 6)

The first packet on every connection sets the device parameters:

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

The server replies with `callsSeed`, `location`, registration country
filters and other static config.

## Auth flow (token)

After the handshake, log in by token (opcode 19):

```python
{
    "token": "<login_token>",
    "interactive": True,
    "presenceSync": 0,
    "exp": {"chatsCountGroups": b"\x0b\x32"},
    "chatCacheFingerprint": <bytes>,
}
```

`chatCacheFingerprint` is derived from the server's `callsSeed` and the
client's `deviceId`. `vkmax.protocol.chat_cache_fingerprint` builds it.

## Auth flow (SMS)

1. `AUTH_REQUEST` (17): `{phone, type: "START_AUTH", language: "ru"}` →
   returns a temporary `token`.
2. `AUTH` (18): `{token, verifyCode, authTokenType: "CHECK_CODE"}` →
   returns `tokenAttrs.LOGIN.token` (or `passwordChallenge` if 2FA is
   enabled).
3. Optional `AUTH_LOGIN_CHECK_PASSWORD` (113) for 2FA.
4. `LOGIN` (19) as above.

## Replies and errors

- `cmd=1` (OK) → normal response.
- `cmd=2` (NOT_FOUND) → soft miss (rare, opcode dependent).
- `cmd=3` (ERROR) → `payload` carries `{error, message, localizedMessage}`.
  The server **closes the TCP connection** after sending the error.
  `vkmax` auto-reconnects and re-logs in transparently when
  `auto_reconnect=True`.

## Pings

`vkmax` sends `PING` (1) every `ping_interval` seconds (30 by default).
Without pings the server times out the connection after roughly two
minutes.

## See also

- `opcodes.md` — full opcode list.
- `vkmax.protocol` — Python implementation of pack/unpack and the
  fingerprint helper.
