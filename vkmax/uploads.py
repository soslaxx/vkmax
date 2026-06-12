from __future__ import annotations

import asyncio
import json
import mimetypes
import ssl
from collections.abc import Awaitable, Callable
from pathlib import Path
from urllib.parse import urlsplit

from .exceptions import UploadError
from .models import UploadProgress

ProgressCallback = Callable[[UploadProgress], None | Awaitable[None]]

DEFAULT_USER_AGENT = (
    "OKMessages/26.17.1%20(Android%2011;%20TECNO%20MOBILE%20LIMITED%20TECNO%20LE7n;%20xxhdpi%20480dpi%201080x2208)"
)
CHUNK_SIZE = 128 * 1024


async def upload_binary(
    url: str,
    path: str | Path,
    *,
    filename: str | None = None,
    progress: ProgressCallback | None = None,
    response_timeout: float = 30.0,
) -> int:
    path = Path(path)
    if not path.is_file():
        raise UploadError(f"file not found: {path}")
    total = path.stat().st_size
    name = filename or path.name
    parsed = urlsplit(url)
    reader, writer = await _open_http(parsed)
    headers = (
        f"POST {_target(parsed)} HTTP/1.1\r\n"
        f"Host: {parsed.hostname}\r\n"
        "Content-Type: application/x-binary; charset=x-user-defined\r\n"
        f"Content-Disposition: attachment; filename={name}\r\n"
        "Connection: close\r\n"
        f"User-Agent: {DEFAULT_USER_AGENT}\r\n"
        f"Content-Range: bytes 0-{max(total - 1, 0)}/{total}\r\n"
        f"Content-Length: {total}\r\n"
        "\r\n"
    )
    try:
        writer.write(headers.encode())
        await writer.drain()
        sent = 0
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(CHUNK_SIZE)
                if not chunk:
                    break
                writer.write(chunk)
                await writer.drain()
                sent += len(chunk)
                if progress is not None:
                    await _maybe_call(progress, UploadProgress(sent=sent, total=total))
        status, _ = await asyncio.wait_for(_read_response(reader), timeout=response_timeout)
        return status
    finally:
        await _close_writer(writer)


async def upload_multipart(
    url: str,
    path: str | Path,
    *,
    filename: str | None = None,
    progress: ProgressCallback | None = None,
    response_timeout: float = 60.0,
) -> str | None:
    path = Path(path)
    if not path.is_file():
        raise UploadError(f"file not found: {path}")
    total_file = path.stat().st_size
    name = filename or path.name
    content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
    boundary = f"----vkmaxBoundary{id(path):x}"
    preamble = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
        f"Content-Type: {content_type}\r\n"
        "\r\n"
    ).encode()
    epilogue = f"\r\n--{boundary}--\r\n".encode()
    total = len(preamble) + total_file + len(epilogue)
    parsed = urlsplit(url)
    reader, writer = await _open_http(parsed)
    headers = (
        f"POST {_target(parsed)} HTTP/1.1\r\n"
        f"Host: {parsed.hostname}\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
        f"Content-Length: {total}\r\n"
        "Connection: close\r\n"
        f"User-Agent: {DEFAULT_USER_AGENT}\r\n"
        "\r\n"
    )
    try:
        writer.write(headers.encode() + preamble)
        await writer.drain()
        sent = 0
        with path.open("rb") as fh:
            while True:
                chunk = fh.read(CHUNK_SIZE)
                if not chunk:
                    break
                writer.write(chunk)
                await writer.drain()
                sent += len(chunk)
                if progress is not None:
                    await _maybe_call(progress, UploadProgress(sent=sent, total=total_file))
        writer.write(epilogue)
        await writer.drain()
        status, body = await asyncio.wait_for(_read_response(reader), timeout=response_timeout)
        if status != 200:
            return None
        return _parse_photo_token(body)
    finally:
        await _close_writer(writer)


async def download_url(url: str, *, chunk_size: int = CHUNK_SIZE, timeout: float = 60.0) -> bytes:
    parsed = urlsplit(url)
    reader, writer = await _open_http(parsed)
    request = (
        f"GET {_target(parsed)} HTTP/1.1\r\n"
        f"Host: {parsed.hostname}\r\n"
        "Connection: close\r\n"
        f"User-Agent: {DEFAULT_USER_AGENT}\r\n"
        "\r\n"
    )
    try:
        writer.write(request.encode())
        await writer.drain()
        _status, body = await asyncio.wait_for(_read_response(reader, chunk_size=chunk_size), timeout=timeout)
        return body
    finally:
        await _close_writer(writer)


async def _open_http(parsed):
    if not parsed.hostname:
        raise UploadError("upload url has no host")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    ssl_context = ssl.create_default_context() if parsed.scheme == "https" else None
    return await asyncio.open_connection(
        parsed.hostname,
        port,
        ssl=ssl_context,
        server_hostname=parsed.hostname if ssl_context else None,
    )


def _target(parsed) -> str:
    path = parsed.path or "/"
    return f"{path}?{parsed.query}" if parsed.query else path


async def _read_response(reader: asyncio.StreamReader, *, chunk_size: int = CHUNK_SIZE) -> tuple[int, bytes]:
    head = await reader.readuntil(b"\r\n\r\n")
    header_text = head.decode(errors="replace")
    first = header_text.split("\r\n", 1)[0]
    parts = first.split()
    status = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
    headers: dict[str, str] = {}
    for line in header_text.split("\r\n")[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.lower()] = value.strip()
    if headers.get("transfer-encoding", "").lower() == "chunked":
        return status, await _read_chunked(reader)
    length_raw = headers.get("content-length")
    if length_raw is not None:
        length = int(length_raw or 0)
        body = await reader.readexactly(length) if length else b""
        return status, body
    body = bytearray()
    while True:
        chunk = await reader.read(chunk_size)
        if not chunk:
            break
        body.extend(chunk)
    return status, bytes(body)


async def _read_chunked(reader: asyncio.StreamReader) -> bytes:
    out = bytearray()
    while True:
        line = await reader.readline()
        size_text = line.split(b";", 1)[0].strip()
        size = int(size_text, 16) if size_text else 0
        if size == 0:
            await reader.readuntil(b"\r\n")
            break
        out.extend(await reader.readexactly(size))
        await reader.readexactly(2)
    return bytes(out)


def _parse_photo_token(body: bytes) -> str | None:
    try:
        data = json.loads(body.decode(errors="replace"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    photos = data.get("photos")
    if isinstance(photos, dict):
        for value in photos.values():
            if isinstance(value, dict) and isinstance(value.get("token"), str):
                return value["token"]
    token = data.get("photoToken")
    if isinstance(token, str):
        return token
    return None


async def _maybe_call(progress: ProgressCallback, info: UploadProgress) -> None:
    result = progress(info)
    if hasattr(result, "__await__"):
        await result


async def _close_writer(writer: asyncio.StreamWriter) -> None:
    try:
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass
