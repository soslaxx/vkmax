# Notifications

Per-chat notification preferences are stored on the server inside the
user's CONFIG (opcode 22), under `settings.chats[chatId]`.

## Constants

```python
from vkmax import MUTE_OFF, MUTE_FOREVER
# MUTE_OFF     = 0      → notifications on
# MUTE_FOREVER = -1     → muted indefinitely
# any positive int      → muted until that ms-timestamp
```

## Mute / unmute

```python
await app.mute_chat(chat_id)              # forever
await app.unmute_chat(chat_id)            # off
await app.mute_chat_for(chat_id, 3600)    # next hour

import time
await app.set_chat_mute(chat_id, int(time.time() * 1000) + 86_400_000)
```

Or through a typed `Chat`:

```python
chat = await app.get_chat(chat_id)
await chat.mute()
await chat.mute(until=int(time.time()*1000) + 3600_000)
await chat.unmute()
```

## Batch update

```python
await app.set_chats_mute({
    chat_a: MUTE_FOREVER,
    chat_b: MUTE_OFF,
    chat_c: int(time.time() * 1000) + 3600 * 1000,
})
```

## Read current settings

```python
settings = await app.get_chat_notification_settings()
# {
#   -75800508459204: {
#     "dontDisturbUntil": 0,
#     "vibr": True,
#     "sound": True,
#     "led": True,
#     "favIndex": 0,
#   },
#   ...
# }
```

The initial value comes from the LOGIN cache; after any change
(yours or another device) it is refreshed via `Opcode.NOTIF_CONFIG`.

## Global push / sound preferences

These live in the user config (see [privacy.md](privacy.md)):

- `PUSH_DETAILS` — include chat title / preview in push.
- `PUSH_NEW_CONTACTS` — notify on first message from a new contact.
- `CHATS_PUSH_NOTIFICATION` — master switch (set via
  `update_privacy_config({"CHATS_PUSH_NOTIFICATION": "ON"})`).
- `CHATS_PUSH_SOUND`, `CHATS_VIBR`, `CHATS_LED` — defaults for chats
  that don't override them.

## Audio transcription

Transcription must be enabled in your privacy config before
`transcribe_audio` will succeed:

```python
await app.set_audio_transcription(True)
result = await app.transcribe_audio(chat_id, message_id, media_id)
```
