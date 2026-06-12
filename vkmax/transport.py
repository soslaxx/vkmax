from __future__ import annotations

import asyncio
import ssl
from collections.abc import AsyncIterator, Callable
from typing import Any

from .enums import CMD_ERROR, CMD_NOT_FOUND, CMD_OK, Opcode
from .exceptions import PacketError, SessionExpired, TransportClosed
from .models import Packet
from .protocol import HEADER_SIZE, pack_packet, packet_size_from_header, unpack_packet
from .proxy import ProxyConfig, open_proxied_connection

HandlerType = Callable[[Packet], Any]


class Transport:
    def __init__(
        self,
        host: str,
        port: int,
        *,
        request_timeout: float = 30.0,
        ssl_context: ssl.SSLContext | None = None,
        use_tls: bool = True,
        proxy: ProxyConfig | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.request_timeout = request_timeout
        self.use_tls = use_tls
        self.ssl_context = ssl_context
        self.proxy = proxy
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._seq = 0
        self._pending: dict[int, asyncio.Future[Packet]] = {}
        self._push_queue: asyncio.Queue[Packet] = asyncio.Queue()
        self._handlers: dict[int, list[HandlerType]] = {}
        self._send_lock = asyncio.Lock()
        self._on_disconnect: Callable[[BaseException | None], Any] | None = None

    @property
    def is_connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    def set_disconnect_handler(self, handler: Callable[[BaseException | None], Any] | None) -> None:
        self._on_disconnect = handler

    async def connect(self) -> None:
        if self.is_connected:
            return
        context = self.ssl_context or ssl.create_default_context() if self.use_tls else None
        if self.proxy is not None:
            self._reader, self._writer = await open_proxied_connection(
                self.proxy,
                self.host,
                self.port,
                ssl_context=context,
                server_hostname=self.host if context else None,
            )
        elif context is not None:
            self._reader, self._writer = await asyncio.open_connection(
                self.host,
                self.port,
                ssl=context,
                server_hostname=self.host,
            )
        else:
            self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
        self._reader_task = asyncio.create_task(self._read_loop(), name="vkmax-reader")

    async def close(self) -> None:
        task = self._reader_task
        self._reader_task = None
        if task:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        writer = self._writer
        self._writer = None
        self._reader = None
        if writer is not None:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        self._fail_pending(TransportClosed("transport closed"))

    async def request(self, opcode: int | Opcode, payload: dict[Any, Any] | None = None) -> Packet:
        if not self.is_connected or self._writer is None:
            raise TransportClosed("transport is not connected")
        async with self._send_lock:
            self._seq = (self._seq + 1) % 65536
            if self._seq == 0:
                self._seq = 1
            seq = self._seq
            loop = asyncio.get_running_loop()
            future: asyncio.Future[Packet] = loop.create_future()
            self._pending[seq] = future
            try:
                self._writer.write(pack_packet(int(opcode), payload or {}, seq=seq))
                await self._writer.drain()
            except Exception as exc:
                self._pending.pop(seq, None)
                raise TransportClosed(f"write failed: {exc}") from exc
        try:
            return await asyncio.wait_for(future, timeout=self.request_timeout)
        except asyncio.TimeoutError as exc:
            self._pending.pop(seq, None)
            raise TransportClosed(f"request {int(opcode)} timed out") from exc
        finally:
            self._pending.pop(seq, None)

    async def pushes(self) -> AsyncIterator[Packet]:
        while True:
            yield await self._push_queue.get()

    def on(self, opcode: int | Opcode, handler: HandlerType) -> None:
        self._handlers.setdefault(int(opcode), []).append(handler)

    def off(self, opcode: int | Opcode, handler: HandlerType | None = None) -> None:
        if handler is None:
            self._handlers.pop(int(opcode), None)
            return
        handlers = self._handlers.get(int(opcode), [])
        remaining = [item for item in handlers if item is not handler]
        if remaining:
            self._handlers[int(opcode)] = remaining
        else:
            self._handlers.pop(int(opcode), None)

    async def _read_loop(self) -> None:
        reader = self._reader
        if reader is None:
            return
        cause: BaseException | None = None
        try:
            while True:
                header = await reader.readexactly(HEADER_SIZE)
                total = packet_size_from_header(header)
                body = await reader.readexactly(total - HEADER_SIZE) if total > HEADER_SIZE else b""
                try:
                    packet = unpack_packet(header + body)
                except Exception:
                    continue
                self._dispatch(packet)
        except asyncio.CancelledError:
            raise
        except (asyncio.IncompleteReadError, ConnectionError) as exc:
            cause = TransportClosed(f"connection lost: {exc}")
        except Exception as exc:
            cause = exc
        finally:
            if cause is None:
                cause = TransportClosed("reader stopped")
            self._fail_pending(cause)
            handler = self._on_disconnect
            if handler is not None:
                try:
                    result = handler(cause)
                    if hasattr(result, "__await__"):
                        asyncio.create_task(result)
                except Exception:
                    pass

    def _dispatch(self, packet: Packet) -> None:
        if packet.cmd in (CMD_OK, CMD_ERROR, CMD_NOT_FOUND):
            future = self._pending.pop(packet.seq, None)
            if future is None or future.done():
                return
            if packet.is_error:
                future.set_exception(_packet_error(packet))
            else:
                future.set_result(packet)
            return
        try:
            self._push_queue.put_nowait(packet)
        except asyncio.QueueFull:
            pass
        for handler in list(self._handlers.get(packet.opcode, [])):
            try:
                result = handler(packet)
            except Exception:
                continue
            if hasattr(result, "__await__"):
                asyncio.create_task(result)

    def _fail_pending(self, exc: BaseException) -> None:
        for future in self._pending.values():
            if not future.done():
                future.set_exception(exc)
        self._pending.clear()


def _packet_error(packet: Packet) -> PacketError:
    payload = packet.payload
    message = "Unknown server error"
    error_key: str | None = None
    if isinstance(payload, dict):
        raw_error = payload.get("error")
        if raw_error is not None:
            error_key = str(raw_error)
        for key in ("localizedMessage", "message", "title"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                message = value.strip()
                break
        if payload.get("message") in {"FAIL_LOGIN_TOKEN", "FAIL_WRONG_PASSWORD"}:
            return SessionExpired(message, error_key=error_key, payload=payload)
    elif payload is not None:
        message = str(payload)
    return PacketError(message, error_key=error_key, payload=payload)
