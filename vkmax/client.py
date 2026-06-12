from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any

from .enums import Opcode
from .exceptions import AuthError, MaxError, NotConnected, PacketError, SessionExpired, TransportClosed
from .models import (
    Attachment,
    Chat,
    Contact,
    FileUpload,
    LoginResult,
    Message,
    Packet,
    ReactionInfo,
    UploadProgress,
    VerifyCodeResult,
)
from .protocol import chat_cache_fingerprint
from .reactions import resolve_reaction
from .session import DeviceSession, default_session_path, load_or_create_session
from .transport import Transport
from .uploads import ProgressCallback, download_url, upload_binary, upload_multipart

EventHandler = Callable[[Packet], Any]


class MaxClient:
    def __init__(
        self,
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
    ) -> None:
        self.host = host
        self.port = port
        self.request_timeout = request_timeout
        self.ping_interval = ping_interval
        self.auto_reconnect = auto_reconnect
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_delay = max_reconnect_delay
        self._save_session = save_session
        self._session_path: Path | None = None
        if isinstance(session, DeviceSession):
            self.device = session
        else:
            if isinstance(session, Path) or (isinstance(session, str) and session.endswith(".json")):
                self._session_path = Path(session)
            else:
                self._session_path = default_session_path(str(session))
            self.device = load_or_create_session(self._session_path)
        self.transport = Transport(host, port, request_timeout=request_timeout)
        self.transport.set_disconnect_handler(self._handle_disconnect)
        self.handshake: dict[str, Any] | None = None
        self.calls_seed: int | None = None
        self.server_time: int | None = None
        self.me: dict[str, Any] | None = None
        self.config: dict[str, Any] | None = None
        self.token: str | None = self.device.token
        self.account_id: int | None = self.device.account_id
        self._ping_task: asyncio.Task[None] | None = None
        self._reconnect_task: asyncio.Task[None] | None = None
        self._closing = False
        self._connect_lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        return self.transport.is_connected and self.handshake is not None

    @property
    def is_authorized(self) -> bool:
        return self.me is not None

    async def __aenter__(self) -> MaxClient:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        async with self._connect_lock:
            if self.transport.is_connected and self.handshake is not None:
                return
            self._closing = False
            await self.transport.connect()
            packet = await self.transport.request(Opcode.SESSION_INIT, self.device.handshake_payload)
            payload = packet.payload if isinstance(packet.payload, dict) else {}
            self.handshake = payload
            seed = payload.get("callsSeed")
            self.calls_seed = seed if isinstance(seed, int) else None
            srv_time = payload.get("time")
            self.server_time = srv_time if isinstance(srv_time, int) else None
            if self._ping_task is None or self._ping_task.done():
                from ._bind import ping_loop
                self._ping_task = asyncio.create_task(ping_loop(self), name="vkmax-ping")

    async def disconnect(self) -> None:
        self._closing = True
        if self._ping_task is not None:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except (asyncio.CancelledError, Exception):
                pass
            self._ping_task = None
        if self._reconnect_task is not None:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except (asyncio.CancelledError, Exception):
                pass
            self._reconnect_task = None
        await self.transport.close()
        self.handshake = None

    async def invoke(
        self,
        opcode: int | Opcode,
        payload: dict[Any, Any] | None = None,
        *,
        wait_for_reconnect: float | None = None,
    ) -> Packet:
        timeout = wait_for_reconnect if wait_for_reconnect is not None else (15.0 if self.auto_reconnect else 0.0)
        if not self.transport.is_connected:
            if not self.auto_reconnect or timeout <= 0:
                raise NotConnected("client is not connected")
            await self._wait_until_ready(timeout)
        try:
            return await self.transport.request(opcode, payload or {})
        except (TransportClosed, NotConnected) as exc:
            if not self.auto_reconnect or timeout <= 0:
                raise
            await self._wait_until_ready(timeout)
            return await self.transport.request(opcode, payload or {})

    async def _wait_until_ready(self, timeout: float) -> None:
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            if self.transport.is_connected and self.handshake is not None and (self.token is None or self.me is not None):
                return
            if self._closing:
                raise NotConnected("client is closed")
            await asyncio.sleep(0.1)
        if not self.transport.is_connected:
            raise NotConnected("client could not reconnect in time")

    async def ping(self) -> Packet:
        return await self.invoke(Opcode.PING, {"interactive": False})

    async def start(
        self,
        *,
        token: str | None = None,
        phone: str | None = None,
        code_callback: Callable[[], str | Awaitable[str]] | None = None,
        password_callback: Callable[[], str | Awaitable[str]] | None = None,
    ) -> LoginResult | VerifyCodeResult:
        await self.connect()
        effective_token = token or self.token
        if effective_token:
            try:
                return await self.login(effective_token)
            except SessionExpired:
                self.token = None
                self.device.token = None
                self._persist_session()
                if not phone or code_callback is None:
                    raise
        if not phone or code_callback is None:
            raise AuthError("token or phone + code_callback is required")
        auth_token = await self.request_code(phone)
        code = await _maybe_await(code_callback())
        result = await self.sign_in(code, auth_token)
        login_token = result.login_token
        if result.requires_password:
            if password_callback is None or result.challenge_track_id is None:
                return result
            password = await _maybe_await(password_callback())
            login_token = await self.check_password(result.challenge_track_id, password)
        if login_token:
            return await self.login(login_token)
        return result

    async def request_code(self, phone: str, *, language: str = "ru") -> str:
        packet = await self.invoke(
            Opcode.AUTH_REQUEST,
            {"phone": _normalize_phone(phone), "type": "START_AUTH", "language": language},
        )
        token = packet.payload.get("token") if isinstance(packet.payload, dict) else None
        if not isinstance(token, str) or not token:
            raise AuthError("auth token is missing in server response", payload=packet.payload)
        return token

    async def resend_code(self, phone: str, *, language: str = "ru") -> str:
        packet = await self.invoke(
            Opcode.AUTH_REQUEST,
            {"phone": _normalize_phone(phone), "type": "RESEND", "language": language},
        )
        token = packet.payload.get("token") if isinstance(packet.payload, dict) else None
        if not isinstance(token, str) or not token:
            raise AuthError("auth token is missing in server response", payload=packet.payload)
        return token

    async def sign_in(self, code: str, token: str) -> VerifyCodeResult:
        packet = await self.invoke(
            Opcode.AUTH,
            {"token": token, "verifyCode": str(code), "authTokenType": "CHECK_CODE"},
        )
        if not isinstance(packet.payload, dict):
            raise AuthError("unexpected auth response", payload=packet.payload)
        return VerifyCodeResult(packet.payload)

    async def check_password(self, track_id: str, password: str) -> str:
        packet = await self.invoke(
            Opcode.AUTH_LOGIN_CHECK_PASSWORD,
            {"trackId": track_id, "password": password},
        )
        data = packet.payload if isinstance(packet.payload, dict) else {}
        attrs = data.get("tokenAttrs")
        entry = attrs.get("LOGIN") if isinstance(attrs, dict) else None
        token = entry.get("token") if isinstance(entry, dict) else None
        if not isinstance(token, str) or not token:
            raise AuthError("login token is missing after password check", payload=packet.payload)
        return token

    async def complete_registration(
        self,
        token: str,
        first_name: str,
        *,
        last_name: str | None = None,
        photo_id: int | None = None,
    ) -> int:
        payload: dict[str, Any] = {"token": token, "tokenType": "REGISTER", "firstName": first_name}
        if last_name:
            payload["lastName"] = last_name
        if photo_id is not None:
            payload["photoId"] = photo_id
            payload["avatarType"] = "PRESET_AVATAR"
        packet = await self.invoke(Opcode.AUTH_CONFIRM, payload)
        contact = _contact_from_payload(packet.payload)
        account_id = contact.get("id")
        if not isinstance(account_id, int):
            raise AuthError("account id is missing in registration response", payload=packet.payload)
        return account_id

    async def login(self, token: str, **sync: Any) -> LoginResult:
        payload: dict[str, Any] = {
            "token": token,
            "interactive": True,
            "exp": {"chatsCountGroups": bytes([0x0B, 0x32])},
            "presenceSync": sync.pop("presence_sync", 0),
        }
        if self.calls_seed is not None:
            payload["chatCacheFingerprint"] = chat_cache_fingerprint(self.calls_seed, self.device.device_id)
        for key, value in sync.items():
            if value is not None:
                payload[_camel_key(key)] = value
        packet = await self.invoke(Opcode.LOGIN, payload)
        if not isinstance(packet.payload, dict):
            raise AuthError("unexpected login response", payload=packet.payload)
        contact = _contact_from_payload(packet.payload)
        self.me = contact
        config = packet.payload.get("config") if isinstance(packet.payload, dict) else None
        if isinstance(config, dict):
            self.config = config
        raw_token = packet.payload.get("token")
        self.token = raw_token if isinstance(raw_token, str) and raw_token else token
        self.account_id = contact.get("id") if isinstance(contact.get("id"), int) else None
        server_time = packet.payload.get("time")
        if isinstance(server_time, int):
            self.server_time = server_time
        self.device.token = self.token
        self.device.account_id = self.account_id
        phone = contact.get("phone")
        if isinstance(phone, (str, int)):
            self.device.phone = str(phone)
        self._persist_session()
        return LoginResult(
            profile=contact,
            raw=packet.payload,
            token=self.token,
            server_time=self.server_time,
        )

    async def logout(self, *, push_token: str | None = None) -> Packet:
        payload: dict[str, Any] = {}
        if self.token:
            payload["token"] = self.token
        if push_token:
            payload["pushToken"] = push_token
        packet = await self.invoke(Opcode.LOGOUT, payload)
        self.token = None
        self.me = None
        self.account_id = None
        self.device.token = None
        self.device.account_id = None
        self._persist_session()
        return packet

    async def get_sessions(self) -> list[dict[str, Any]]:
        packet = await self.invoke(Opcode.SESSIONS_INFO, {})
        sessions = packet.payload.get("sessions") if isinstance(packet.payload, dict) else None
        if isinstance(sessions, list):
            return [item for item in sessions if isinstance(item, dict)]
        return []

    async def terminate_other_sessions(self) -> Packet:
        return await self.invoke(Opcode.SESSIONS_CLOSE, {})

    async def sync(self, **params: Any) -> dict[str, Any]:
        payload = {_camel_key(k): v for k, v in params.items() if v is not None}
        packet = await self.invoke(Opcode.SYNC, payload)
        return packet.payload if isinstance(packet.payload, dict) else {}

    async def get_preset_avatars(self) -> dict[str, Any]:
        packet = await self.invoke(Opcode.PRESET_AVATARS, {})
        return packet.payload if isinstance(packet.payload, dict) else {}

    async def update_config(self, settings: dict[str, Any]) -> dict[str, Any]:
        packet = await self.invoke(Opcode.CONFIG, {"settings": settings})
        return packet.payload if isinstance(packet.payload, dict) else {}

    def _persist_session(self) -> None:
        if not self._save_session or self._session_path is None:
            return
        try:
            self.device.save(self._session_path)
        except Exception:
            pass

    def on(self, opcode: int | Opcode, handler: EventHandler) -> EventHandler:
        self.transport.on(opcode, handler)
        return handler

    def off(self, opcode: int | Opcode, handler: EventHandler | None = None) -> None:
        self.transport.off(opcode, handler)

    def on_message(self, handler: EventHandler) -> EventHandler:
        return self.on(Opcode.NOTIF_MESSAGE, handler)

    async def events(self) -> AsyncIterator[Packet]:
        async for packet in self.transport.pushes():
            yield packet

    async def download(self, url: str) -> bytes:
        return await download_url(url)

    def _handle_disconnect(self, exc: BaseException | None) -> None:
        self.handshake = None
        if self._closing or not self.auto_reconnect:
            return
        if self._reconnect_task is not None and not self._reconnect_task.done():
            return
        from ._bind import reconnect_loop
        self._reconnect_task = asyncio.create_task(reconnect_loop(self), name="vkmax-reconnect")


def _normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    return f"+{digits}"


def _camel_key(key: str) -> str:
    if "_" not in key:
        return key
    parts = key.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _contact_from_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PacketError("profile is missing in response", payload=payload)
    profile = payload.get("profile")
    contact = profile.get("contact") if isinstance(profile, dict) else None
    if not isinstance(contact, dict):
        raise PacketError("profile.contact is missing in response", payload=payload)
    return contact


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


from ._bind import bind_methods as _bind_methods

_bind_methods(MaxClient)
