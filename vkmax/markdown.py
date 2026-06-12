from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

ELEMENT_TYPES = (
    "STRONG",
    "EMPHASIZED",
    "UNDERLINE",
    "STRIKETHROUGH",
    "MONOSPACED",
    "LINK",
    "QUOTE",
)

_INLINE_PATTERN = re.compile(
    r"(?P<bold>\*\*(?P<bold_text>.+?)\*\*)"
    r"|(?P<under>__(?P<under_text>.+?)__)"
    r"|(?P<italic>\*(?P<italic_text>[^*\n]+?)\*)"
    r"|(?P<strike>~~(?P<strike_text>.+?)~~)"
    r"|(?P<strike1>~(?P<strike1_text>[^~\n]+?)~)"
    r"|(?P<code>`(?P<code_text>[^`\n]+?)`)"
    r"|(?P<link>\[(?P<link_text>[^\]\n]+?)\]\((?P<link_url>[^)\s]+)\))",
    re.DOTALL,
)


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


def parse_markdown(text: str) -> tuple[str, list[dict[str, Any]]]:
    plain_parts: list[str] = []
    elements: list[_Element] = []
    cursor = 0
    text = text or ""

    for line in _split_lines(text):
        line_text, line_elements = _parse_line(line, len("".join(plain_parts)))
        plain_parts.append(line_text)
        elements.extend(line_elements)

    plain = "".join(plain_parts)
    if not elements:
        return plain, []

    elements.sort(key=lambda e: (e.start, e.length))
    payload: list[dict[str, Any]] = []
    for index, element in enumerate(elements):
        payload.append(element.to_dict(omit_zero=index == 0))
    return plain, payload


def _split_lines(text: str) -> list[str]:
    lines = text.splitlines(keepends=True)
    if not lines:
        return [text]
    return lines


def _parse_line(line: str, base_offset: int) -> tuple[str, list[_Element]]:
    quote_active = False
    if line.lstrip().startswith("> "):
        stripped = line.lstrip()[2:]
        leading = line[: len(line) - len(line.lstrip())]
        line_for_inline = leading + stripped
        quote_active = True
    else:
        line_for_inline = line

    plain, inline = _parse_inline(line_for_inline, base_offset)
    if quote_active and plain.strip():
        start = base_offset + (len(plain) - len(plain.lstrip("\r\n")))
        quote_text = plain.rstrip("\r\n")
        inline.append(_Element("QUOTE", base_offset, len(quote_text)))
    return plain, inline


def _parse_inline(text: str, base_offset: int) -> tuple[str, list[_Element]]:
    out_chars: list[str] = []
    elements: list[_Element] = []
    cursor = 0
    for match in _INLINE_PATTERN.finditer(text):
        if match.start() > cursor:
            out_chars.append(text[cursor:match.start()])
        kind, inner, attrs = _classify(match)
        start_index = base_offset + sum(len(s) for s in out_chars)
        if inner is None:
            out_chars.append(match.group(0))
        else:
            inner_plain, inner_elements = _parse_inline(inner, start_index)
            out_chars.append(inner_plain)
            elements.append(
                _Element(kind, start_index, len(inner_plain), attributes=attrs)
            )
            elements.extend(inner_elements)
        cursor = match.end()
    if cursor < len(text):
        out_chars.append(text[cursor:])
    return "".join(out_chars), elements


def _classify(match: re.Match[str]) -> tuple[str, str | None, dict[str, Any] | None]:
    if match.group("bold") is not None:
        return "STRONG", match.group("bold_text"), None
    if match.group("under") is not None:
        return "UNDERLINE", match.group("under_text"), None
    if match.group("italic") is not None:
        return "EMPHASIZED", match.group("italic_text"), None
    if match.group("strike") is not None:
        return "STRIKETHROUGH", match.group("strike_text"), None
    if match.group("strike1") is not None:
        return "STRIKETHROUGH", match.group("strike1_text"), None
    if match.group("code") is not None:
        return "MONOSPACED", match.group("code_text"), None
    if match.group("link") is not None:
        url = match.group("link_url")
        return "LINK", match.group("link_text"), {"url": url}
    return "", None, None
