from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import filters as filters_module
from .client import MaxClient
from .enums import Opcode
from .filters import Filter
from .models import Packet
from .proxy import ProxyConfig
from .session import DeviceSession
from .types import Chat, Message, User

Handler = Callable[["Client", Message], Awaitable[Any] | Any]


@dataclass(slots=True)
class _Subscription:
    opcode: int
    filter: Filter | None
    callback: Handler
    group: int


class Client(MaxClient):
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
        proxy: str | ProxyConfig | None = None,
    ) -> None:
        super().__init__(
            session,
            host=host,
            port=port,
            request_timeout=request_timeout,
            ping_interval=ping_interval,
            auto_reconnect=auto_reconnect,
            reconnect_delay=reconnect_delay,
            max_reconnect_delay=max_reconnect_delay,
            save_session=save_session,
            proxy=proxy,
        )
        self._subscriptions: dict[int, list[_Subscription]] = {}
        self._installed_opcodes: set[int] = set()

    def on_message(
        self,
        filter: Filter | None = None,
        *,
        group: int = 0,
    ) -> Callable[[Handler], Handler]:
        return self._subscribe(Opcode.NOTIF_MESSAGE, filter, group)

    def on_edited_message(
        self,
        filter: Filter | None = None,
        *,
        group: int = 0,
    ) -> Callable[[Handler], Handler]:
        return self._subscribe(Opcode.NOTIF_MESSAGE, filter & filters_module.edited if filter else filters_module.edited, group)

    def on_deleted_message(
        self,
        filter: Filter | None = None,
        *,
        group: int = 0,
    ) -> Callable[[Handler], Handler]:
        return self._subscribe(Opcode.NOTIF_MSG_DELETE, filter, group)

    def on_reaction(
        self,
        filter: Filter | None = None,
        *,
        group: int = 0,
    ) -> Callable[[Handler], Handler]:
        return self._subscribe(Opcode.NOTIF_MSG_REACTIONS_CHANGED, filter, group)

    def on_typing(
        self,
        filter: Filter | None = None,
        *,
        group: int = 0,
    ) -> Callable[[Handler], Handler]:
        return self._subscribe(Opcode.NOTIF_TYPING, filter, group)

    def on_event(
        self,
        opcode: int | Opcode,
        filter: Filter | None = None,
        *,
        group: int = 0,
    ) -> Callable[[Handler], Handler]:
        return self._subscribe(int(opcode), filter, group)

    def add_handler(
        self,
        opcode: int | Opcode,
        callback: Handler,
        *,
        filter: Filter | None = None,
        group: int = 0,
    ) -> None:
        self._register(int(opcode), filter, callback, group)

    def _subscribe(
        self,
        opcode: int,
        filter: Filter | None,
        group: int,
    ) -> Callable[[Handler], Handler]:
        def decorator(func: Handler) -> Handler:
            self._register(opcode, filter, func, group)
            return func
        return decorator

    def _register(
        self,
        opcode: int,
        filter: Filter | None,
        callback: Handler,
        group: int,
    ) -> None:
        bucket = self._subscriptions.setdefault(opcode, [])
        bucket.append(_Subscription(opcode, filter, callback, group))
        bucket.sort(key=lambda s: s.group)
        if opcode not in self._installed_opcodes:
            self._installed_opcodes.add(opcode)
            self.transport.on(opcode, self._make_router(opcode))

    def _make_router(self, opcode: int) -> Callable[[Packet], Any]:
        def router(packet: Packet) -> Any:
            asyncio.create_task(self._dispatch_event(opcode, packet))
        return router

    async def _dispatch_event(self, opcode: int, packet: Packet) -> None:
        subs = self._subscriptions.get(opcode)
        if not subs:
            return
        message = Message.from_payload(packet.payload, self) if isinstance(packet.payload, dict) else None
        if message is None:
            return
        for sub in subs:
            try:
                if sub.filter is not None and not await sub.filter(message):
                    continue
                result = sub.callback(self, message)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:
                print(f"[vkmax] handler error in {sub.callback.__name__}: {exc}")

    async def get_me(self) -> User:
        if self.me is None:
            raise RuntimeError("client is not logged in")
        return User.from_dict(self.me, client=self)

    async def get_user(self, user_id: int) -> User | None:
        data = await super().get_contact(user_id)
        return User.from_dict(data, client=self) if isinstance(data, dict) else None

    async def get_chat(self, chat_id: int) -> Chat | None:  # type: ignore[override]
        data = await super().get_chat_info(chat_id)
        return Chat.from_dict(data, client=self) if isinstance(data, dict) else None

    async def send_message(  # type: ignore[override]
        self,
        chat_id: int,
        text: str,
        *,
        notify: bool = True,
        reply_to: int | str | None = None,
        elements: list[dict[str, Any]] | None = None,
        markdown: bool = False,
        html: bool = False,
    ) -> Message:
        message_id = await super().send_message(
            chat_id,
            text,
            notify=notify,
            reply_to=reply_to,
            elements=elements,
            markdown=markdown,
            html=html,
        )
        raw = await super().get_message(chat_id, message_id) if message_id else None
        payload = {"chatId": chat_id, "message": raw or {"id": message_id, "text": text, "sender": self.account_id, "attaches": []}}
        msg = Message.from_payload(payload, self)
        if msg is None:
            raise RuntimeError("failed to materialise sent message")
        return msg

    def run(self, main: Awaitable[Any] | None = None) -> None:
        async def runner() -> None:
            await self.start_session()
            try:
                if main is not None:
                    await main
                else:
                    await asyncio.Event().wait()
            finally:
                await self.disconnect()
        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            pass

    async def start_session(self) -> None:
        await self.connect()
        if self.device.token:
            await self.login(self.device.token)
        else:
            raise RuntimeError("no token in session; run login.py first")
