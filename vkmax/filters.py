from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .types import Message

FilterFunc = Callable[["Message"], bool | Awaitable[bool]]


class Filter:
    __slots__ = ("func", "name")

    def __init__(self, func: FilterFunc, name: str = "") -> None:
        self.func = func
        self.name = name or func.__name__ if hasattr(func, "__name__") else "<filter>"

    async def __call__(self, message: "Message") -> bool:
        result = self.func(message)
        if hasattr(result, "__await__"):
            result = await result  # type: ignore[misc]
        return bool(result)

    def __and__(self, other: "Filter") -> "Filter":
        async def combined(message: "Message") -> bool:
            return await self(message) and await other(message)
        return Filter(combined, f"({self.name} & {other.name})")

    def __or__(self, other: "Filter") -> "Filter":
        async def combined(message: "Message") -> bool:
            return await self(message) or await other(message)
        return Filter(combined, f"({self.name} | {other.name})")

    def __invert__(self) -> "Filter":
        async def negated(message: "Message") -> bool:
            return not await self(message)
        return Filter(negated, f"~{self.name}")

    def __repr__(self) -> str:
        return f"Filter({self.name})"


def create(func: FilterFunc, name: str = "") -> Filter:
    return Filter(func, name)


all_ = Filter(lambda _m: True, "all")
me = Filter(lambda m: m.sender_id == m.client.account_id, "me")
outgoing = me
incoming = Filter(lambda m: m.sender_id != m.client.account_id, "incoming")
private = Filter(lambda m: m.chat_id > 0, "private")
group = Filter(lambda m: m.chat_id < 0 and (m.chat.type == "CHAT" if m.chat else True), "group")
channel = Filter(lambda m: m.chat_id < 0 and (m.chat.type == "CHANNEL" if m.chat else False), "channel")
reply = Filter(lambda m: m.reply_to_message_id is not None, "reply")
forward = Filter(lambda m: m.forward is not None, "forward")
edited = Filter(lambda m: m.status == "EDITED", "edited")
removed = Filter(lambda m: m.status == "REMOVED", "removed")
photo = Filter(lambda m: any(a.type == "PHOTO" for a in m.attachments), "photo")
video = Filter(lambda m: any(a.type == "VIDEO" for a in m.attachments), "video")
file = Filter(lambda m: any(a.type == "FILE" for a in m.attachments), "file")
sticker = Filter(lambda m: any(a.type == "STICKER" for a in m.attachments), "sticker")
audio = Filter(lambda m: any(a.type in ("AUDIO", "VOICE") for a in m.attachments), "audio")
poll = Filter(lambda m: any(a.type == "POLL" for a in m.attachments), "poll")
location = Filter(lambda m: any(a.type == "LOCATION" for a in m.attachments), "location")
control = Filter(lambda m: any(a.type == "CONTROL" for a in m.attachments), "control")
media = photo | video | file | sticker | audio
text = Filter(lambda m: isinstance(m.text, str) and bool(m.text), "text")


def chat(*chat_ids: int) -> Filter:
    targets = {int(c) for c in chat_ids}
    return Filter(lambda m: m.chat_id in targets, f"chat({sorted(targets)})")


def user(*user_ids: int) -> Filter:
    targets = {int(u) for u in user_ids}
    return Filter(lambda m: m.sender_id in targets, f"user({sorted(targets)})")


def regex(pattern: str, *, flags: int = 0) -> Filter:
    compiled = re.compile(pattern, flags)

    def matcher(m: "Message") -> bool:
        if not isinstance(m.text, str):
            return False
        match = compiled.search(m.text)
        if match is None:
            return False
        m.matches = match  # type: ignore[attr-defined]
        return True

    return Filter(matcher, f"regex({pattern!r})")


def command(
    commands: str | list[str],
    *,
    prefixes: str | list[str] = ".",
    case_sensitive: bool = False,
) -> Filter:
    cmd_list = [commands] if isinstance(commands, str) else list(commands)
    prefix_list = [prefixes] if isinstance(prefixes, str) else list(prefixes)
    if not case_sensitive:
        cmd_list = [c.lower() for c in cmd_list]

    def matcher(m: "Message") -> bool:
        text = m.text or ""
        for prefix in prefix_list:
            if not text.startswith(prefix):
                continue
            body = text[len(prefix):]
            if not body:
                continue
            head, _, tail = body.partition(" ")
            head_cmp = head if case_sensitive else head.lower()
            if head_cmp in cmd_list:
                m.command = [head] + (tail.split() if tail else [])  # type: ignore[attr-defined]
                return True
        return False

    return Filter(matcher, f"command({cmd_list})")


def text_equals(value: str, *, case_sensitive: bool = False) -> Filter:
    target = value if case_sensitive else value.lower()

    def matcher(m: "Message") -> bool:
        if not isinstance(m.text, str):
            return False
        candidate = m.text if case_sensitive else m.text.lower()
        return candidate == target

    return Filter(matcher, f"text_equals({value!r})")


def text_contains(value: str, *, case_sensitive: bool = False) -> Filter:
    target = value if case_sensitive else value.lower()

    def matcher(m: "Message") -> bool:
        if not isinstance(m.text, str):
            return False
        candidate = m.text if case_sensitive else m.text.lower()
        return target in candidate

    return Filter(matcher, f"text_contains({value!r})")
