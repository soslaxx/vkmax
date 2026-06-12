# Форматирование

MAX понимает форматированный текст через массив `elements` рядом с
текстом сообщения. Каждый элемент:
`{"type": "STRONG" | "EMPHASIZED" | "UNDERLINE" | "STRIKETHROUGH" |
"MONOSPACED" | "LINK" | "QUOTE", "from": <utf16>, "length": <utf16>}`.
У первого элемента `from` опускается, если равно нулю.

`vkmax` идёт с двумя парсерами: Markdown и HTML. **Все смещения и
длины считаются в UTF-16 code units** — именно так ожидает сервер
(иначе эмодзи сбивает позиции).

## Markdown

| Markdown | Элемент |
|---|---|
| `**жирный**` | STRONG |
| `*курсив*` | EMPHASIZED |
| `__подчёркнутый__` | UNDERLINE |
| `~~зачёркнутый~~` или `~зачёркнутый~` | STRIKETHROUGH |
| `` `код` `` | MONOSPACED |
| `[надпись](https://example.com)` | LINK (атрибут `url`) |
| `> цитата` в начале строки | QUOTE |

```python
await app.send_markdown(chat_id,
    "**жирный** *курсив* `код` [vk](https://vk.com)")
await app.send_message(chat_id, "**жирный**", markdown=True)
```

## HTML

```python
await app.send_html(chat_id,
    "<b>жирный</b> <i>курсив</i> <code>x = 1</code> "
    "<a href='https://vk.com'>ссылка</a>")
await app.send_message(chat_id, "<b>жирный</b>", html=True)
```

Поддержанные теги:

- `<b>`, `<strong>` — STRONG
- `<i>`, `<em>` — EMPHASIZED
- `<u>`, `<ins>` — UNDERLINE
- `<s>`, `<strike>`, `<del>` — STRIKETHROUGH
- `<code>`, `<pre>`, `<tt>` — MONOSPACED
- `<a href="...">` — LINK
- `<blockquote>`, `<q>` — QUOTE
- `<br>` — перенос строки
- `<p>...</p>` — добавляет перенос после блока
- HTML-сущности (`&amp;`, `&#39;`, `&lt;`, …) — декодируются

Неизвестные теги остаются в тексте как есть.

## На `Message`

Те же `markdown=` / `html=` доступны через хелперы `Message`:

```python
await message.reply_markdown("**hi**")
await message.reply_html("<i>привет</i>")
await message.edit_markdown("**обновлено**")
await message.edit_html("<b>обновлено</b>")
```

## Свой `elements`

Если массив уже собран — передай напрямую, парсер не понадобится:

```python
await app.send_message(
    chat_id,
    "hello world",
    elements=[{"type": "STRONG", "length": 5}],   # bold "hello"
)
```

## Чтение чужого форматирования

Если хочется прочитать чужое сообщение и восстановить markdown,
бери `message.raw["elements"]` — встроенного обратного принтера нет.

## Оба сразу нельзя

`markdown=True` + `html=True` в одном вызове → `ValueError`.
Выбери одно.
