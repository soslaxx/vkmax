# Реакции

Реакции — это эмодзи-строки. Сервер ждёт `messageId` как **int**.

## Поставить

```python
await client.react_message(chat_id, message_id, "fire")
await client.react_message(chat_id, message_id, "\u2764\ufe0f")
```

Аргумент `reaction` принимает эмодзи или короткий алиас.

## Убрать свою реакцию

```python
await client.cancel_reaction(chat_id, message_id)
```

## Прочитать

```python
await client.get_reactions(chat_id, message_id)
# {'counters': [{'reaction': '🔥', 'count': 1}],
#  'yourReaction': '🔥',
#  'totalCount': 1}

await client.get_detailed_reactions(
    chat_id, message_id, reaction="fire", count=50, offset=0
)
```

`get_reactions` берёт `reactionInfo` из `MSG_GET`, потому что для
`MSG_GET_REACTIONS` (180) точный payload на мобильном API нам неизвестен.

## Алиасы

Из `vkmax.REACTION_ALIASES`:

| алиас | эмодзи |
|---|---|
| `like` / `thumbs_up` | 👍 |
| `dislike` / `thumbsdown` | 👎 |
| `heart` / `love` | ❤️ |
| `fire` | 🔥 |
| `laugh` / `joy` | 🤣 / 😂 |
| `cry` | 😭 |
| `party` / `tada` | 🎉 |
| `clap` | 👏 |
| `ok` | 👌 |
| `100` | 💯 |
| `skull` | 💀 |
| `rocket` | 🚀 |
| `angry` | 😡 |
| `cool` | 😎 |
| `eyes` | 👀 |
| ... (полный список в `vkmax.REACTION_ALIASES`) |

Неизвестные строки проходят насквозь, так что любой эмодзи работает.

## Настройки реакций в чате

```python
await client.set_chat_reactions_settings(chat_id, {
    "enabledReactions": ["\U0001f44d", "\u2764\ufe0f"],
})
await client.get_chat_reactions_settings(chat_id)
```

## Реакция по двойному тапу (для аккаунта)

```python
await client.set_double_tap_reaction("\U0001f44d")   # 👍
await client.set_double_tap_reaction("fire")          # алиас тоже ок
await client.set_double_tap_reaction(None)            # выключить
```

См. также `docs/ru/privacy.md`.
