from __future__ import annotations

import asyncio
import base64
import socket
import ssl
import struct
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

ProxyScheme = Literal["http", "https", "socks5", "socks5h"]


@dataclass(slots=True)
class ProxyConfig:
    scheme: ProxyScheme
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    rdns: bool = True

    @classmethod
    def from_url(cls, url: str) -> "ProxyConfig":
        parsed = urlparse(url)
        scheme = (parsed.scheme or "http").lower()
        if scheme not in {"http", "https", "socks5", "socks5h"}:
            raise ValueError(f"unsupported proxy scheme: {scheme!r}")
        if not parsed.hostname:
            raise ValueError("proxy url has no host")
        return cls(
            scheme=scheme,  # type: ignore[arg-type]
            host=parsed.hostname,
            port=parsed.port or (1080 if scheme.startswith("socks") else 8080),
            username=parsed.username,
            password=parsed.password,
            rdns=scheme != "socks5",
        )

    @property
    def is_socks(self) -> bool:
        return self.scheme.startswith("socks")


async def open_proxied_connection(
    proxy: ProxyConfig,
    host: str,
    port: int,
    *,
    ssl_context: ssl.SSLContext | None = None,
    server_hostname: str | None = None,
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    if proxy.is_socks:
        sock = await _socks5_connect(proxy, host, port)
    else:
        sock = await _http_connect(proxy, host, port)
    if ssl_context is not None:
        return await asyncio.open_connection(
            sock=sock,
            ssl=ssl_context,
            server_hostname=server_hostname or host,
        )
    return await asyncio.open_connection(sock=sock)


async def _http_connect(proxy: ProxyConfig, host: str, port: int) -> socket.socket:
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        await loop.sock_connect(sock, (proxy.host, proxy.port))
        request = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}:{port}\r\n"
        if proxy.username:
            creds = f"{proxy.username}:{proxy.password or ''}".encode()
            request += f"Proxy-Authorization: Basic {base64.b64encode(creds).decode()}\r\n"
        request += "Connection: keep-alive\r\n\r\n"
        await loop.sock_sendall(sock, request.encode())
        response = await _read_http_response(sock, loop)
        status_line = response.split(b"\r\n", 1)[0].decode(errors="replace")
        parts = status_line.split(" ", 2)
        if len(parts) < 2 or not parts[1].startswith("2"):
            raise ConnectionError(f"proxy CONNECT failed: {status_line!r}")
    except Exception:
        sock.close()
        raise
    return sock


async def _read_http_response(sock: socket.socket, loop: asyncio.AbstractEventLoop) -> bytes:
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        chunk = await loop.sock_recv(sock, 4096)
        if not chunk:
            raise ConnectionError("proxy closed connection during CONNECT")
        buffer += chunk
        if len(buffer) > 65536:
            raise ConnectionError("proxy response too large")
    return buffer


async def _socks5_connect(proxy: ProxyConfig, host: str, port: int) -> socket.socket:
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        await loop.sock_connect(sock, (proxy.host, proxy.port))
        await _socks5_handshake(sock, loop, proxy)
        await _socks5_request(sock, loop, proxy, host, port)
    except Exception:
        sock.close()
        raise
    return sock


async def _socks5_handshake(
    sock: socket.socket,
    loop: asyncio.AbstractEventLoop,
    proxy: ProxyConfig,
) -> None:
    methods = b"\x00\x02" if proxy.username else b"\x00"
    await loop.sock_sendall(sock, b"\x05" + bytes([len(methods)]) + methods)
    reply = await _recv_exact(sock, loop, 2)
    if reply[0] != 0x05:
        raise ConnectionError("SOCKS5: invalid version in greeting")
    method = reply[1]
    if method == 0xFF:
        raise ConnectionError("SOCKS5: no acceptable methods")
    if method == 0x02:
        if not proxy.username:
            raise ConnectionError("SOCKS5: server requires auth but no credentials provided")
        user = proxy.username.encode()
        password = (proxy.password or "").encode()
        await loop.sock_sendall(
            sock,
            b"\x01" + bytes([len(user)]) + user + bytes([len(password)]) + password,
        )
        auth_reply = await _recv_exact(sock, loop, 2)
        if auth_reply[1] != 0x00:
            raise ConnectionError("SOCKS5: auth rejected")


async def _socks5_request(
    sock: socket.socket,
    loop: asyncio.AbstractEventLoop,
    proxy: ProxyConfig,
    host: str,
    port: int,
) -> None:
    if proxy.rdns:
        encoded_host = host.encode("idna")
        atype = bytes([0x03, len(encoded_host)]) + encoded_host
    else:
        try:
            packed = socket.inet_aton(host)
            atype = b"\x01" + packed
        except OSError:
            try:
                packed = socket.inet_pton(socket.AF_INET6, host)
                atype = b"\x04" + packed
            except OSError:
                encoded_host = host.encode("idna")
                atype = bytes([0x03, len(encoded_host)]) + encoded_host
    request = b"\x05\x01\x00" + atype + struct.pack(">H", port)
    await loop.sock_sendall(sock, request)
    head = await _recv_exact(sock, loop, 4)
    if head[0] != 0x05:
        raise ConnectionError("SOCKS5: invalid response version")
    if head[1] != 0x00:
        raise ConnectionError(f"SOCKS5: server replied {head[1]}")
    rtype = head[3]
    if rtype == 0x01:
        await _recv_exact(sock, loop, 4 + 2)
    elif rtype == 0x04:
        await _recv_exact(sock, loop, 16 + 2)
    elif rtype == 0x03:
        length = (await _recv_exact(sock, loop, 1))[0]
        await _recv_exact(sock, loop, length + 2)
    else:
        raise ConnectionError(f"SOCKS5: unknown address type {rtype}")


async def _recv_exact(
    sock: socket.socket,
    loop: asyncio.AbstractEventLoop,
    size: int,
) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = await loop.sock_recv(sock, remaining)
        if not chunk:
            raise ConnectionError("proxy closed connection unexpectedly")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)
