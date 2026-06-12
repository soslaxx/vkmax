# Уведомления

По-чатовые настройки уведомлений лежат на сервере в CONFIG (опкод 22),
в `settings.chats[chatId]`.

## Константы

```python
from vkmax import MUTE_OFF, MUTE_FOREVER
# MUTE_OFF     = 0      → уведомления включены
# MUTE_FOREVER = -1     → выключены навсегда
# положительный int     → выключены до этого ms-таймстампа
```

## Mute / unmute

```python
await client.mute_chat(chat_id)              # навсегда
await client.unmute_chat(chat_id)
await client.mute_chat_for(chat_id, 3600)    # на час

import time
await client.set_chat_mute(chat_id, int(time.time() * 1000) + 86_400_000)
```

## Пачкой

```python
await client.set_chats_mute({
    chat_a: MUTE_FOREVER,
    chat_b: MUTE_OFF,
    chat_c: int(time.time() * 1000) + 3600 * 1000,
})
```

## Прочитать

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

Первый вызов берёт из LOGIN-кэша; дальше обновляется через
`Opcode.NOTIF_CONFIG`.

## Глобальные пуши

Живут в user config (см. [privacy.md](privacy.md)):

- `PUSH_DETAILS` — показывать заголовок/превью в пуше.
- `PUSH_NEW_CONTACTS` — пушить первое сообщение от нового контакта.
- `CHATS_PUSH_NOTIFICATION` — мастер-свитч.
- `CHATS_PUSH_SOUND`, `CHATS_VIBR`, `CHATS_LED` — дефолты для чатов
  без своих настроек.

## Транскрипция голосовых

Включить, потом вызывать `transcribe_audio`:

```python
await client.set_audio_transcription(True)
result = await client.transcribe_audio(chat_id, message_id, media_id)
```
