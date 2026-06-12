from __future__ import annotations

import html as html_lib
import re
from dataclasses import dataclass
from typing import Any

_TAG_MAP: dict[str, tuple[str, dict[str, Any] | None]] = {
    "b": ("STRONG", None),
    "strong": ("STRONG", None),
    "i": ("EMPHASIZED", None),
    "em": ("EMPHASIZED", None),
    "u": ("UNDERLINE", None),
    "ins": ("UNDERLINE", None),
    "s": ("STRIKETHROUGH", None),
    "strike": ("STRIKETHROUGH", None),
    "del": ("STRIKETHROUGH", None),
    "code": ("MONOSPACED", None),
    "pre": ("MONOSPACED", None),
    "tt": ("MONOSPACED", None),
    "blockquote": ("QUOTE", None),
    "q": ("QUOTE", None),
}

_TOKEN_RE = re.compile(r"<\s*(/?)\s*([A-Za-z][A-Za-z0-9]*)\b([^>]*)>")
_ATTR_RE = re.compile(r"([A-Za-z_:][\w:.-]*)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))")


def _utf16_len(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


@dataclass(slots=True)
class _Element:
    type: str
    start: int
    length: int
    attributes: dict[str, Any] | None = None

    def to_dict(self, *, omit_zero: bool) -> dict[str, Any]:
        data: dict[str, Any] = {"type": self.type, "length": self.length}
        if not omit_zero or self.start:
            data["from"] = self.start
        if self.attributes:
            data.update(self.attributes)
        return data


@dataclass(slots=True)
class _OpenTag:
    tag: str
    element_type: str
    start: int
    attributes: dict[str, Any] | None


def parse_html(text: str) -> tuple[str, list[dict[str, Any]]]:
    text = text or ""
    out_chars: list[str] = []
    elements: list[_Element] = []
    stack: list[_OpenTag] = []
    cursor = 0
    current_len = 0

    for match in _TOKEN_RE.finditer(text):
        if match.start() > cursor:
            chunk = _unescape(_replace_br(text[cursor:match.start()]))
            out_chars.append(chunk)
            current_len = _utf16_len("".join(out_chars))
        closing = match.group(1) == "/"
        name = match.group(2).lower()
        attrs_text = match.group(3) or ""

        if name == "br":
            out_chars.append("\n")
            current_len = _utf16_len("".join(out_chars))
            cursor = match.end()
            continue

        if name == "p":
            if closing:
                out_chars.append("\n")
            current_len = _utf16_len("".join(out_chars))
            cursor = match.end()
            continue

        if name == "a":
            if closing:
                _close_tag(stack, elements, "a", current_len)
            else:
                href = _extract_href(attrs_text)
                attrs = {"url": href} if href else None
                stack.append(_OpenTag("a", "LINK", current_len, attrs))
            cursor = match.end()
            continue

        mapped = _TAG_MAP.get(name)
        if mapped is None:
            out_chars.append(match.group(0))
            current_len = _utf16_len("".join(out_chars))
            cursor = match.end()
            continue

        element_type, default_attrs = mapped
        if closing:
            _close_tag(stack, elements, name, current_len)
        else:
            stack.append(_OpenTag(name, element_type, current_len, default_attrs))
        cursor = match.end()

    if cursor < len(text):
        chunk = _unescape(_replace_br(text[cursor:]))
        out_chars.append(chunk)
        current_len = _utf16_len("".join(out_chars))

    while stack:
        opener = stack.pop()
        length = current_len - opener.start
        if length > 0:
            elements.append(
                _Element(opener.element_type, opener.start, length, opener.attributes)
            )

    plain = "".join(out_chars)
    if not elements:
        return plain, []

    elements.sort(key=lambda e: (e.start, e.length))
    payload: list[dict[str, Any]] = []
    for index, element in enumerate(elements):
        payload.append(element.to_dict(omit_zero=index == 0))
    return plain, payload


def _close_tag(
    stack: list[_OpenTag],
    elements: list[_Element],
    tag: str,
    current_len: int,
) -> None:
    for index in range(len(stack) - 1, -1, -1):
        if stack[index].tag == tag:
            opener = stack.pop(index)
            length = current_len - opener.start
            if length > 0:
                elements.append(
                    _Element(opener.element_type, opener.start, length, opener.attributes)
                )
            return


def _extract_href(attrs_text: str) -> str | None:
    for match in _ATTR_RE.finditer(attrs_text):
        name = match.group(1).lower()
        if name != "href":
            continue
        value = match.group(2) or match.group(3) or match.group(4) or ""
        return html_lib.unescape(value)
    return None


def _replace_br(text: str) -> str:
    return text


def _unescape(text: str) -> str:
    return html_lib.unescape(text)
