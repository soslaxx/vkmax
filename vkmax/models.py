from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Packet:
    api: int = 10
    cmd: int = 0
    seq: int = 0
    opcode: int = 0
    payload: Any = None

    @property
    def is_ok(self) -> bool:
        return self.cmd == 1

    @property
    def is_error(self) -> bool:
        return self.cmd == 3

    @property
    def is_push(self) -> bool:
        return self.cmd == 0

    @property
    def is_not_found(self) -> bool:
        return self.cmd == 2


@dataclass(slots=True)
class VerifyCodeResult:
    payload: dict[str, Any]

    @property
    def login_token(self) -> str | None:
        return self._nested_token("LOGIN")

    @property
    def register_token(self) -> str | None:
        return self._nested_token("REGISTER")

    @property
    def requires_password(self) -> bool:
        return self.payload.get("passwordChallenge") is not None

    @property
    def is_new_user(self) -> bool:
        return self.register_token is not None and self.login_token is None

    @property
    def password_challenge(self) -> dict[str, Any] | None:
        challenge = self.payload.get("passwordChallenge")
        return challenge if isinstance(challenge, dict) else None

    @property
    def challenge_track_id(self) -> str | None:
        challenge = self.password_challenge
        return challenge.get("trackId") if challenge else None

    @property
    def challenge_hint(self) -> str | None:
        challenge = self.password_challenge
        return challenge.get("hint") if challenge else None

    @property
    def account_id(self) -> int | None:
        profile = self.payload.get("profile")
        contact = profile.get("contact") if isinstance(profile, dict) else None
        account_id = contact.get("id") if isinstance(contact, dict) else None
        return account_id if isinstance(account_id, int) else None

    def _nested_token(self, key: str) -> str | None:
        attrs = self.payload.get("tokenAttrs")
        entry = attrs.get(key) if isinstance(attrs, dict) else None
        token = entry.get("token") if isinstance(entry, dict) else None
        return token if isinstance(token, str) and token else None


@dataclass(slots=True)
class LoginResult:
    profile: dict[str, Any]
    raw: dict[str, Any]
    token: str | None = None
    server_time: int | None = None

    @property
    def account_id(self) -> int | None:
        value = self.profile.get("id")
        return value if isinstance(value, int) else None


@dataclass(slots=True)
class FileUpload:
    url: str
    file_id: int
    token: str


@dataclass(slots=True)
class UploadProgress:
    sent: int
    total: int

    @property
    def fraction(self) -> float:
        return self.sent / self.total if self.total else 0.0


@dataclass(slots=True)
class ReactionCounter:
    reaction: str
    count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReactionCounter:
        return cls(
            reaction=str(data.get("reaction", "")),
            count=int(data.get("count", 0)),
        )


@dataclass(slots=True)
class ReactionInfo:
    counters: list[ReactionCounter] = field(default_factory=list)
    total_count: int = 0
    your_reaction: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ReactionInfo | None:
        if not isinstance(data, dict):
            return None
        counters_raw = data.get("counters")
        counters: list[ReactionCounter] = []
        if isinstance(counters_raw, list):
            for item in counters_raw:
                if isinstance(item, dict):
                    counters.append(ReactionCounter.from_dict(item))
        total = data.get("totalCount")
        your = data.get("yourReaction")
        return cls(
            counters=counters,
            total_count=int(total) if isinstance(total, int) else sum(c.count for c in counters),
            your_reaction=str(your) if isinstance(your, str) and your else None,
        )

    @property
    def has_reactions(self) -> bool:
        return self.total_count > 0 or bool(self.counters)

    def get_count(self, emoji: str) -> int:
        for counter in self.counters:
            if counter.reaction == emoji:
                return counter.count
        return 0


@dataclass(slots=True)
class Attachment:
    type: str
    raw: dict[str, Any]
    file_id: int | None = None
    token: str | None = None
    url: str | None = None
    filename: str | None = None
    size: int | None = None
    photo_token: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    mime_type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Attachment:
        return cls(
            type=str(data.get("_type", data.get("type", "UNKNOWN"))),
            raw=data,
            file_id=data.get("fileId"),
            token=data.get("token"),
            url=data.get("url") or data.get("baseUrl"),
            filename=data.get("filename") or data.get("name"),
            size=data.get("size"),
            photo_token=data.get("photoToken"),
            width=data.get("width"),
            height=data.get("height"),
            duration=data.get("duration"),
            mime_type=data.get("mime") or data.get("contentType"),
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
    reply_to: str | None
    raw: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, chat_id: int = 0) -> Message:
        reaction_info = ReactionInfo.from_dict(data.get("reactionInfo"))
        attaches_raw = data.get("attaches", [])
        attachments: list[Attachment] = []
        if isinstance(attaches_raw, list):
            for item in attaches_raw:
                if isinstance(item, dict):
                    attachments.append(Attachment.from_dict(item))
        link = data.get("link")
        forward = None
        reply_to = None
        if isinstance(link, dict):
            link_type = link.get("type")
            if link_type == "FORWARD":
                forward = link
            elif link_type == "REPLY":
                msg = link.get("message")
                if isinstance(msg, dict):
                    reply_to = str(msg.get("id")) if msg.get("id") is not None else None
        return cls(
            id=str(data.get("id", "")),
            chat_id=chat_id or int(data.get("chatId", 0)),
            sender_id=int(data.get("sender", 0)),
            text=data.get("text"),
            time=int(data.get("time", 0)),
            status=data.get("status"),
            reactions=reaction_info,
            attachments=attachments,
            forward=forward,
            reply_to=reply_to,
            raw=data,
        )

    @property
    def has_reactions(self) -> bool:
        return self.reactions is not None and self.reactions.has_reactions

    @property
    def is_forwarded(self) -> bool:
        return self.forward is not None

    @property
    def is_reply(self) -> bool:
        return self.reply_to is not None

    @property
    def is_edited(self) -> bool:
        return self.status == "EDITED"

    @property
    def is_removed(self) -> bool:
        return self.status == "REMOVED"

    @property
    def is_control(self) -> bool:
        return any(a.type == "CONTROL" for a in self.attachments)

    @property
    def has_files(self) -> bool:
        return any(a.type == "FILE" for a in self.attachments)

    @property
    def has_photos(self) -> bool:
        return any(a.type == "PHOTO" for a in self.attachments)

    @property
    def has_sticker(self) -> bool:
        return any(a.type == "STICKER" for a in self.attachments)

    @property
    def has_video(self) -> bool:
        return any(a.type == "VIDEO" for a in self.attachments)

    @property
    def has_audio(self) -> bool:
        return any(a.type in ("AUDIO", "VOICE") for a in self.attachments)

    @property
    def has_poll(self) -> bool:
        return any(a.type == "POLL" for a in self.attachments)

    @property
    def has_location(self) -> bool:
        return any(a.type == "LOCATION" for a in self.attachments)

    def get_reaction_count(self, emoji: str) -> int:
        return self.reactions.get_count(emoji) if self.reactions else 0


@dataclass(slots=True)
class Contact:
    id: int
    first_name: str
    last_name: str | None
    phone: int | None
    base_url: str | None
    photo_id: int | None
    options: set[str]
    raw: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Contact:
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
        )

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def is_official(self) -> bool:
        return "OFFICIAL" in self.options

    @property
    def is_bot(self) -> bool:
        return "BOT" in self.options


@dataclass(slots=True)
class Chat:
    id: int
    type: str
    title: str | None
    owner: int | None
    admins: list[int]
    members_count: int | None
    base_icon_url: str | None
    last_event_time: int
    new_messages: int
    options: dict[str, Any]
    raw: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chat:
        admins_raw = data.get("admins", [])
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
        admin_participants = data.get("adminParticipants")
        if isinstance(admin_participants, dict) and not admins:
            for key in admin_participants:
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
        )

    @property
    def is_group(self) -> bool:
        return self.type in ("CHAT", "GROUP")

    @property
    def is_channel(self) -> bool:
        return self.type == "CHANNEL"

    @property
    def is_dialog(self) -> bool:
        return self.type == "DIALOG"
