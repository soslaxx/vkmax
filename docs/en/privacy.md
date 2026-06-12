# Privacy

All privacy settings live in `app.config["user"]`. The mobile
endpoint is opcode 22 (`CONFIG`) with
`payload = {"settings": {"user": {...}}}`.

## Read

```python
cfg = await app.get_privacy_config()
# {"SEARCH_BY_PHONE": "ALL",
#  "INCOMING_CALL": "ALL",
#  "CHATS_INVITE": "CONTACTS",
#  "PHONE_NUMBER_PRIVACY": "CONTACTS",
#  "INACTIVE_TTL": "6M",
#  "FAMILY_PROTECTION": "OFF",
#  ...
# }
```

The first call after `login` reads from the cached LOGIN reply. Pass
`refresh=True` to force a round trip to the server.

## Write

```python
await app.update_privacy_config({
    "SEARCH_BY_PHONE": "CONTACTS",
    "SHOW_READ_MARK": False,
})

await app.set_privacy("PUSH_DETAILS", True)
```

Server echoes back the full updated `user` dict.

## Typed helpers

Enum-style constants live in `vkmax`:

```python
from vkmax import PrivacyAudience, FamilyProtectionLevel, InactiveTtl

await app.set_search_by_phone(PrivacyAudience.CONTACTS)
await app.set_incoming_call(PrivacyAudience.CONTACTS)
await app.set_chats_invite(PrivacyAudience.ALL)
await app.set_phone_number_privacy(PrivacyAudience.NOBODY)
await app.set_family_protection(FamilyProtectionLevel.HIGH)
await app.set_inactive_ttl(InactiveTtl.ONE_YEAR)
```

An invalid value raises `ValueError` **before** the request is sent —
`vkmax` checks the whitelist locally to mirror the official UI.

## All keys

| Key | Type | Allowed values | Helper |
|---|---|---|---|
| `SEARCH_BY_PHONE` | enum | `ALL` `CONTACTS` | `set_search_by_phone` |
| `INCOMING_CALL` | enum | `ALL` `CONTACTS` | `set_incoming_call` |
| `CHATS_INVITE` | enum | `ALL` `CONTACTS` | `set_chats_invite` |
| `PHONE_NUMBER_PRIVACY` | enum | `ALL` `CONTACTS` `NOBODY` | `set_phone_number_privacy` |
| `INACTIVE_TTL` | enum | `3M` `6M` `1Y` | `set_inactive_ttl` |
| `FAMILY_PROTECTION` | enum | `OFF` `LOW` `MEDIUM` `HIGH` | `set_family_protection` |
| `STICKERS_SUGGEST` | enum | `ON` `OFF` | `set_stickers_suggest` |
| `HIDDEN` | bool | True = hide "online" from everyone, False = show to contacts | `set_hidden` |
| `SHOW_READ_MARK` | bool | | `set_show_read_mark` |
| `SAFE_MODE` | bool | | `set_safe_mode` |
| `SAFE_MODE_NO_PIN` | bool | | `set_safe_mode_no_pin` |
| `UNSAFE_FILES` | bool | | `set_unsafe_files` |
| `PUSH_DETAILS` | bool | | `set_push_details` |
| `PUSH_NEW_CONTACTS` | bool | | `set_push_new_contacts` |
| `ALT_KEYBOARD` | bool | | `set_alt_keyboard` |
| `CONTENT_LEVEL_ACCESS` | bool | | `set_content_level_access` |
| `AUDIO_TRANSCRIPTION_ENABLED` | bool | | `set_audio_transcription` |
| `DOUBLE_TAP_REACTION_DISABLED` | bool | | `set_double_tap_reaction(None)` |
| `DOUBLE_TAP_REACTION_VALUE` | str (emoji) | any | `set_double_tap_reaction("\U0001f44d")` |

String constants for the keys live in `vkmax.PrivacyKey`.

Runtime whitelist:

```python
from vkmax.privacy import allowed_values

allowed_values("SEARCH_BY_PHONE")   # ('ALL', 'CONTACTS')
allowed_values("HIDDEN")            # (True, False)
```

## Double-tap reaction

```python
await app.set_double_tap_reaction("\U0001f44d")   # 👍
await app.set_double_tap_reaction("fire")          # alias works
await app.set_double_tap_reaction(None)            # disable
```

## Push event

Server broadcasts `Opcode.NOTIF_CONFIG` (134) when settings change
from another device:

```python
from vkmax import Opcode


async def on_config(packet):
    print("config changed:", packet.payload)


app.transport.on(Opcode.NOTIF_CONFIG, on_config)
```
