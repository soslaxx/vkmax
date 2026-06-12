# Proxy support

`vkmax` can tunnel its TLS connection to `api.oneme.ru:443` through
an HTTP CONNECT proxy or a SOCKS5 proxy. Useful for hosting bots in
networks where the MAX endpoint is blocked.

## Quick start

Pass a URL when constructing the client:

```python
from vkmax import Client

app = Client("main", proxy="socks5://user:pass@127.0.0.1:1080")
```

Supported schemes:

- `http://` and `https://` — HTTP CONNECT.
- `socks5://` — SOCKS5, the proxy resolves the hostname **locally**.
- `socks5h://` — SOCKS5, the proxy resolves the hostname **remotely**
  (preferred for blocked DNS).

Username and password are optional and read from the URL itself.

## Programmatic config

If you prefer not to embed credentials in a string:

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

## What happens under the hood

`Transport.connect()` checks `Client.proxy`. If set:

1. Opens a TCP socket to the proxy.
2. Performs CONNECT or the SOCKS5 handshake, asking it to connect to
   `api.oneme.ru:443`.
3. Wraps the resulting socket into TLS using
   `ssl.create_default_context()`.
4. Hands the TLS pipe to the existing reader/writer code.

Auto-reconnect, ping loop, and validation-error recovery all keep
working — every reconnect re-runs the same flow.

## Uploads through proxy

Currently the photo / video / file upload HTTPS connections **do
not** route through the proxy — they hit the upload host directly
(`iu.oneme.ru`, `iv.oneme.ru`). If you need full proxying, open an
issue: the upload helpers need a small refactor to take a
`ProxyConfig` too.

## Troubleshooting

- `ConnectionError: proxy CONNECT failed: 407 Proxy Authentication
  Required` — bad credentials.
- `ConnectionError: SOCKS5: auth rejected` — same, but for SOCKS5.
- `ConnectionError: SOCKS5: server replied 4` — host unreachable
  from the proxy.
- `TransportClosed: connection lost: 0 bytes ...` — proxy works but
  `api.oneme.ru` refused the TLS handshake (e.g. proxy strips SNI).
