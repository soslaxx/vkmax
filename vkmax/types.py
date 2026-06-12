from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .models import Attachment, ReactionInfo

if TYPE_CHECKING:
    from .pyromax import Client


@dataclass(slots=True)
class User:
    id: int
    first_name: str = ""
    last_name: str | None = None
    phone: int | None = None
    base_url: str | None = None
    photo_id: int | None = None
    options: set[str] = field(default_factory=set)
    raw: dict[str, Any] = field(default_factory=dict)
    client: "Client | None" = None

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def is_bot(self) -> bool:
        return "BOT" in self.options

    @property
    def is_official(self) -> bool:
        return "OFFICIAL" in self.options

    async def send_message(self, text: str, **kwargs: Any) -> "Message":
        if self.client is None:
            raise RuntimeError("User is detached from a client")
        return await self.client.send_message(self.dm_chat_id, text, **kwargs)

    @property
    def dm_chat_id(self) -> int:
        if self.client is None or self.client.account_id is None:
            raise RuntimeError("client account_id is unknown")
        return self.id ^ int(self.client.account_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, client: "Client | None" = None) -> "User":
        first_name = ""
        last_name: str | None = None
        names = data.get("names")
        if isinstance(names, list) and names:
            primary = None
            for entry in names:
                if not isinstance(entry, dict):
                    continue
                if entry.get("type") == "ONEME":
                    primary = entry
                    break
                if primary is None:
                    primary = entry
            if isinstance(primary, dict):
                first_name = str(primary.get("firstName", "") or "")
                ln = primary.get("lastName")
                last_name = str(ln) if isinstance(ln, str) and ln else None
        options_raw = data.get("options", [])
        options: set[str] = set()
        if isinstance(options_raw, list):
            options = {str(o) for o in options_raw if isinstance(o, str)}
        return cls(
            id=int(data.get("id", 0)),
            first_name=first_name,
            last_name=last_name,
            phone=data.get("phone") if isinstance(data.get("phone"), int) else None,
            base_url=data.get("baseUrl") if isinstance(data.get("baseUrl"), str) else None,
            photo_id=data.get("photoId") if isinstance(data.get("photoId"), int) else None,
            options=options,
            raw=data,
            client=client,
        )


@dataclass(slots=True)
class Chat:
    id: int
    type: str = "DIALOG"
    title: str | None = None
    owner: int | None = None
    admins: list[int] = field(default_factory=list)
    members_count: int | None = None
    base_icon_url: str | None = None
    last_event_time: int = 0
    new_messages: int = 0
    options: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    client: "Client | None" = None

    @property
    def is_private(self) -> bool:
        return self.id > 0 or self.type == "DIALOG"

    @property
    def is_group(self) -> bool:
        return self.type in ("CHAT", "GROUP")

    @property
    def is_channel(self) -> bool:
        return self.type == "CHANNEL"

    async def send(self, text: str, **kwargs: Any) -> "Message":
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.send_message(self.id, text, **kwargs)

    async def send_photo(self, path: str | Path, **kwargs: Any) -> Any:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.send_photo(self.id, path, **kwargs)

    async def send_video(self, path: str | Path, **kwargs: Any) -> Any:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.upload_video(self.id, path, **kwargs)

    async def send_file(self, path: str | Path, **kwargs: Any) -> Any:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.upload_file(self.id, path, **kwargs)

    async def send_poll(self, title: str, options: list[str], **kwargs: Any) -> Any:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.send_poll(self.id, title, options, **kwargs)

    async def leave(self) -> Any:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.leave_chat(self.id)

    async def mute(self, until: int = -1) -> Any:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.set_chat_mute(self.id, until)

    async def unmute(self) -> Any:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.unmute_chat(self.id)

    async def revoke_invite_link(self) -> str | None:
        if self.client is None:
            raise RuntimeError("Chat is detached from a client")
        return await self.client.revoke_invite_link(self.id)

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, client: "Client | None" = None) -> "Chat":
        admins_raw = data.get("admins", []) or data.get("adminParticipants", {})
        admins: list[int] = []
        if isinstance(admins_raw, list):
            for value in admins_raw:
                try:
                    admins.append(int(value))
                except (TypeError, ValueError):
                    continue
        elif isinstance(admins_raw, dict):
            for key in admins_raw:
                try:
                    admins.append(int(key))
                except (TypeError, ValueError):
                    continue
        options = data.get("options")
        if not isinstance(options, dict):
            options = {}
        owner = data.get("owner")
        return cls(
            id=int(data.get("id", 0)),
            type=str(data.get("type", "DIALOG")),
            title=data.get("title") if isinstance(data.get("title"), str) else None,
            owner=owner if isinstance(owner, int) else None,
            admins=admins,
            members_count=data.get("membersCount") if isinstance(data.get("membersCount"), int) else None,
            base_icon_url=data.get("baseIconUrl") if isinstance(data.get("baseIconUrl"), str) else None,
            last_event_time=int(data.get("lastEventTime", 0)),
            new_messages=int(data.get("newMessages", 0)),
            options=options,
            raw=data,
            client=client,
        )


@dataclass(slots=True)
class Message:
    id: str
    chat_id: int
    sender_id: int
    text: str | None
    time: int
    status: str | None
    reactions: ReactionInfo | None
    attachments: list[Attachment]
    forward: dict[str, Any] | None
    reply_to_message_id: str | None
    raw: dict[str, Any]
    client: "Client"
    chat: Chat | None = None
    from_user: User | None = None
    command: list[str] | None = None
    matches: Any = None

    @property
    def is_outgoing(self) -> bool:
        return self.sender_id == self.client.account_id

    @property
    def is_reply(self) -> bool:
        return self.reply_to_message_id is not None

    @property
    def is_edited(self) -> bool:
        return self.status == "EDITED"

    @property
    def is_removed(self) -> bool:
        return self.status == "REMOVED"

    @property
    def has_photo(self) -> bool:
        return any(a.type == "PHOTO" for a in self.attachments)

    @property
    def has_video(self) -> bool:
        return any(a.type == "VIDEO" for a in self.attachments)

    @property
    def has_file(self) -> bool:
        return any(a.type == "FILE" for a in self.attachments)

    @property
    def has_sticker(self) -> bool:
        return any(a.type == "STICKER" for a in self.attachments)

    async def reply(
        self,
        text: str,
        *,
        markdown: bool = False,
        html: bool = False,
        notify: bool = True,
    ) -> "Message":
        return await self.client.send_message(
            self.chat_id,
            text,
            reply_to=self.id,
            notify=notify,
            markdown=markdown,
            html=html,
        )

    async def reply_markdown(self, text: str, **kwargs: Any) -> "Message":
        return await self.reply(text, markdown=True, **kwargs)

    async def reply_html(self, text: str, **kwargs: Any) -> "Message":
        return await self.reply(text, html=True, **kwargs)

    async def edit(
        self,
        text: str,
        *,
        markdown: bool = False,
        html: bool = False,
    ) -> Any:
        return await self.client.edit_message(
            self.chat_id, self.id, text, markdown=markdown, html=html,
        )

    async def edit_markdown(self, text: str, **kwargs: Any) -> Any:
        return await self.edit(text, markdown=True, **kwargs)

    async def edit_html(self, text: str, **kwargs: Any) -> Any:
        return await self.edit(text, html=True, **kwargs)

    async def delete(self, *, for_all: bool = True) -> Any:
        return await self.client.delete_messages(self.chat_id, [self.id], for_all=for_all)

    async def react(self, reaction: str) -> Any:
        return await self.client.react_message(self.chat_id, self.id, reaction)

    async def unreact(self) -> Any:
        return await self.client.cancel_reaction(self.chat_id, self.id)

    async def forward_to(self, chat_id: int, *, notify: bool = True) -> Any:
        return await self.client.forward_message(self.chat_id, self.id, chat_id, notify=notify)

    async def pin(self, *, notify: bool = True) -> Any:
        return await self.client.pin_message(self.chat_id, self.id, notify=notify)

    @classmethod
    def from_payload(cls, payload: dict[str, Any], client: "Client") -> "Message | None":
        if not isinstance(payload, dict):
            return None
        message = payload.get("message")
        if not isinstance(message, dict):
            return None
        chat_id = int(payload.get("chatId", 0))
        reactions = None
        ri = message.get("reactionInfo")
        if isinstance(ri, dict):
            reactions = ReactionInfo.from_dict(ri)
        attaches_raw = message.get("attaches", [])
        attachments: list[Attachment] = []
        if isinstance(attaches_raw, list):
            for item in attaches_raw:
                if isinstance(item, dict):
                    attachments.append(Attachment.from_dict(item))
        link = message.get("link") if isinstance(message.get("link"), dict) else None
        forward = None
        reply_to = None
        if isinstance(link, dict):
            link_type = link.get("type")
            if link_type == "FORWARD":
                forward = link
            elif link_type == "REPLY":
                inner = link.get("message")
                if isinstance(inner, dict) and inner.get("id") is not None:
                    reply_to = str(inner["id"])
        msg = cls(
            id=str(message.get("id", "")),
            chat_id=chat_id,
            sender_id=int(message.get("sender", 0)),
            text=message.get("text"),
            time=int(message.get("time", 0)),
            status=message.get("status"),
            reactions=reactions,
            attachments=attachments,
            forward=forward,
            reply_to_message_id=reply_to,
            raw=message,
            client=client,
        )
        return msg
