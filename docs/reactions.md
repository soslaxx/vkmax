# Reactions

Reactions are emoji strings on the wire. The mobile API expects
`messageId` as **int**.

## Add

```python
await client.react_message(chat_id, message_id, "fire")
await client.react_message(chat_id, message_id, "\u2764\ufe0f")
```

The `reaction` argument accepts either an emoji or a short alias.

## Remove your reaction

```python
await client.cancel_reaction(chat_id, message_id)
```

## Read

```python
await client.get_reactions(chat_id, message_id)
# {'counters': [{'reaction': '🔥', 'count': 1}],
#  'yourReaction': '🔥',
#  'totalCount': 1}

await client.get_detailed_reactions(
    chat_id, message_id, reaction="fire", count=50, offset=0
)
```

`get_reactions` reads `reactionInfo` from the message (`MSG_GET`),
because `MSG_GET_REACTIONS` (180) on the mobile API expects an extra
shape we have not been able to confirm.

## Aliases

From `vkmax.REACTION_ALIASES`:

| alias | emoji |
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
| ... (see `vkmax.REACTION_ALIASES`) |

Unknown strings pass through unchanged, so any emoji works.

## Chat-level reaction settings

```python
await client.set_chat_reactions_settings(chat_id, {
    "enabledReactions": ["\U0001f44d", "\u2764\ufe0f"],
})
await client.get_chat_reactions_settings(chat_id)
```

## Default double-tap reaction (per user)

```python
await client.set_double_tap_reaction("\U0001f44d")  # set to 👍
await client.set_double_tap_reaction(None)          # disable
```

See also `docs/privacy.md`.
