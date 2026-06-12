# Privacy

All privacy settings live in `client.config["user"]`. The mobile
endpoint is opcode 22 (`CONFIG`) with `payload = {"settings": {"user":
{...}}}`.

## Read

```python
cfg = await client.get_privacy_config()
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
`refresh=True` to force a round trip.

## Write

```python
await client.update_privacy_config({
    "SEARCH_BY_PHONE": "CONTACTS",
    "SHOW_READ_MARK": False,
})

await client.set_privacy("PUSH_DETAILS", True)
```

Server echoes back the full updated `user` dict.

## Typed helpers

Enum-style constants live in `vkmax`:

```python
from vkmax import PrivacyAudience, FamilyProtectionLevel, InactiveTtl

await client.set_search_by_phone(PrivacyAudience.CONTACTS)
await client.set_incoming_call(PrivacyAudience.NOBODY)
await client.set_chats_invite(PrivacyAudience.ALL)
await client.set_phone_number_privacy(PrivacyAudience.CONTACTS)
await client.set_family_protection(FamilyProtectionLevel.HIGH)
await client.set_inactive_ttl(InactiveTtl.ONE_YEAR)
```

## All keys

`vkmax` enforces the same value set the official UI offers; an invalid
value raises `ValueError` before the request is sent.

| Key | Type | Allowed values | Helper |
|---|---|---|---|
| `SEARCH_BY_PHONE` | enum | `ALL` `CONTACTS` | `set_search_by_phone` |
| `INCOMING_CALL` | enum | `ALL` `CONTACTS` | `set_incoming_call` |
| `CHATS_INVITE` | enum | `ALL` `CONTACTS` | `set_chats_invite` |
| `PHONE_NUMBER_PRIVACY` | enum | `ALL` `CONTACTS` `NOBODY` | `set_phone_number_privacy` |
| `INACTIVE_TTL` | enum | `3M` `6M` `1Y` | `set_inactive_ttl` |
| `FAMILY_PROTECTION` | enum | `OFF` `LOW` `MEDIUM` `HIGH` | `set_family_protection` |
| `STICKERS_SUGGEST` | enum | `ON` `OFF` | `set_stickers_suggest` |
| `HIDDEN` | bool | True = hide online status from everyone, False = show to contacts | `set_hidden` |
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

Use `vkmax.privacy.allowed_values(key)` to query the whitelist at
runtime.

String constants for the keys live in `vkmax.PrivacyKey`.

## Double-tap reaction

```python
await client.set_double_tap_reaction("\U0001f44d")   # 👍
await client.set_double_tap_reaction("fire")          # alias accepted
await client.set_double_tap_reaction(None)            # disable
```

## Push event

Server broadcasts `Opcode.NOTIF_CONFIG` (134) when settings change
elsewhere.
