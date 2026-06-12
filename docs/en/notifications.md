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
await client.mute_chat(chat_id)              # forever
await client.unmute_chat(chat_id)            # off
await client.mute_chat_for(chat_id, 3600)    # next hour

# Explicit timestamp:
import time
await client.set_chat_mute(chat_id, int(time.time() * 1000) + 86_400_000)
```

## Batch update

```python
await client.set_chats_mute({
    chat_a: MUTE_FOREVER,
    chat_b: MUTE_OFF,
    chat_c: int(time.time() * 1000) + 3600 * 1000,
})
```

## Read current settings

```python
settings = await client.get_chat_notification_settings()
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
(yours or another device) it is updated through `Opcode.NOTIF_CONFIG`.

## Global push / sound preferences

These live in the user config (see [privacy.md](privacy.md)):

- `PUSH_DETAILS` — include chat title / preview in push.
- `PUSH_NEW_CONTACTS` — notify on first message from a new contact.
- `CHATS_PUSH_NOTIFICATION` — master switch (read-only here; set via
  `update_privacy_config({"CHATS_PUSH_NOTIFICATION": "ON"})`).
- `CHATS_PUSH_SOUND`, `CHATS_VIBR`, `CHATS_LED` — defaults for chats
  that don't override them.

## Audio transcription

Transcription must be enabled before `transcribe_audio` will succeed:

```python
await client.set_audio_transcription(True)
result = await client.transcribe_audio(chat_id, message_id, media_id)
```
