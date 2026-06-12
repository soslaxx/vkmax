# Reactions

Reactions are emoji strings on the wire. The mobile API expects
`messageId` as **int** (the helpers cast automatically).

## Add

The pyrogram-style way — on the `Message` itself:

```python
@app.on_message(filters.incoming & filters.text)
async def handler(app, message):
    await message.react("fire")
    await message.react("\U0001f525")
```

Low-level:

```python
await app.react_message(chat_id, message_id, "fire")
await app.react_message(chat_id, message_id, "\u2764\ufe0f")
```

The `reaction` argument accepts either an emoji or a short alias.

## Remove your reaction

```python
await message.unreact()
await app.cancel_reaction(chat_id, message_id)
```

## Read

```python
info = await app.get_reactions(chat_id, message_id)
# {'counters': [{'reaction': '🔥', 'count': 1}],
#  'yourReaction': '🔥',
#  'totalCount': 1}

await app.get_detailed_reactions(
    chat_id, message_id, reaction="fire", count=50, offset=0
)
```

`get_reactions` reads `reactionInfo` from the message (`MSG_GET`);
`MSG_GET_REACTIONS` (180) on the mobile API expects an extra shape
we haven't confirmed yet.

From a typed `Message` you can use `message.reactions` (a parsed
`ReactionInfo`) without a network call:

```python
if message.reactions and message.reactions.has_reactions:
    print(message.reactions.total_count,
          message.reactions.your_reaction)
```

## React handler

React to reaction-change events:

```python
@app.on_reaction()
async def on_react(app, message):
    print("reactions changed on", message.id,
          "->", message.reactions and message.reactions.counters)
```

This fires on opcode 155 (`NOTIF_MSG_REACTIONS_CHANGED`).

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
| … | see `vkmax.REACTION_ALIASES` for the full list |

Unknown strings pass through unchanged, so any emoji works:

```python
await message.react("\U0001f47b")  # 👻
```

## Chat-level reaction settings

```python
await app.set_chat_reactions_settings(chat_id, {
    "enabledReactions": ["\U0001f44d", "\u2764\ufe0f"],
})
await app.get_chat_reactions_settings(chat_id)
```

## Default double-tap reaction (per user)

```python
await app.set_double_tap_reaction("\U0001f44d")  # 👍
await app.set_double_tap_reaction("fire")        # alias is fine
await app.set_double_tap_reaction(None)          # disable
```

See also [privacy.md](privacy.md).
