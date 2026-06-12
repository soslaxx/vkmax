# Formatting

MAX understands rich text via an `elements` array next to the
message text. Each element is
`{"type": "STRONG" | "EMPHASIZED" | "UNDERLINE" | "STRIKETHROUGH" |
"MONOSPACED" | "LINK" | "QUOTE", "from": <utf16>, "length": <utf16>}`.
The first element omits `from` when it equals zero.

`vkmax` ships two parsers that produce that array for you: Markdown
and HTML. **All offsets and lengths are computed in UTF-16 code
units**, which is what the server expects (otherwise an emoji shifts
the formatting).

## Markdown

Flavoured Markdown with the usual operators:

| Markdown | Element |
|---|---|
| `**bold**` | STRONG |
| `*italic*` | EMPHASIZED |
| `__underline__` | UNDERLINE |
| `~~strike~~` or `~strike~` | STRIKETHROUGH |
| `` `code` `` | MONOSPACED |
| `[label](https://example.com)` | LINK (`url` attribute) |
| `> quoted line` at line start | QUOTE |

```python
await app.send_markdown(chat_id,
    "**жирный** *курсив* `код` [vk](https://vk.com)")
await app.send_message(chat_id, "**bold**", markdown=True)
```

## HTML

```python
await app.send_html(chat_id,
    "<b>bold</b> <i>italic</i> <code>x = 1</code> "
    "<a href='https://vk.com'>link</a>")
await app.send_message(chat_id, "<b>bold</b>", html=True)
```

Supported tags:

- `<b>`, `<strong>` — STRONG
- `<i>`, `<em>` — EMPHASIZED
- `<u>`, `<ins>` — UNDERLINE
- `<s>`, `<strike>`, `<del>` — STRIKETHROUGH
- `<code>`, `<pre>`, `<tt>` — MONOSPACED
- `<a href="...">` — LINK
- `<blockquote>`, `<q>` — QUOTE
- `<br>` — newline
- `<p>...</p>` — adds a newline after the block
- HTML entities (`&amp;`, `&#39;`, `&lt;`, …) are decoded

Unknown tags are kept as-is in the text.

## On `Message`

The same `markdown=` / `html=` flags are also on the high-level
helpers exposed by a `Message`:

```python
await message.reply_markdown("**hi**")
await message.reply_html("<i>привет</i>")
await message.edit_markdown("**обновлено**")
await message.edit_html("<b>обновлено</b>")
```

## Manual `elements`

If you already have the array, pass it directly and skip parsers:

```python
await app.send_message(
    chat_id,
    "hello world",
    elements=[{"type": "STRONG", "length": 5}],   # bold "hello"
)
```

## Read back

If you want to read a message someone else sent and reconstruct the
formatting, use the raw payload from `Message.raw["elements"]` —
there's no built-in elements → markdown printer yet.

## Both at once?

Passing `markdown=True` and `html=True` to the same call raises
`ValueError`. Pick one.
