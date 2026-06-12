# Приватность

Все настройки приватности живут в `client.config["user"]`. Мобильный
endpoint — опкод 22 (`CONFIG`), `payload = {"settings": {"user": {...}}}`.

## Прочитать

```python
cfg = await client.get_privacy_config()
# {"SEARCH_BY_PHONE": "ALL",
#  "INCOMING_CALL": "ALL",
#  "CHATS_INVITE": "CONTACTS",
#  "PHONE_NUMBER_PRIVACY": "CONTACTS",
#  "INACTIVE_TTL": "6M",
#  ...
# }
```

Первый вызов после `login` берёт из кэша LOGIN. `refresh=True` —
припринудительный поход к серверу.

## Записать

```python
await client.update_privacy_config({
    "SEARCH_BY_PHONE": "CONTACTS",
    "SHOW_READ_MARK": False,
})

await client.set_privacy("PUSH_DETAILS", True)
```

Сервер возвращает полный обновлённый `user` dict.

## Хелперы

```python
from vkmax import PrivacyAudience, FamilyProtectionLevel, InactiveTtl

await client.set_search_by_phone(PrivacyAudience.CONTACTS)
await client.set_incoming_call(PrivacyAudience.NOBODY)  # ValueError: NOBODY не разрешён
await client.set_chats_invite(PrivacyAudience.ALL)
await client.set_phone_number_privacy(PrivacyAudience.NOBODY)
await client.set_family_protection(FamilyProtectionLevel.HIGH)
await client.set_inactive_ttl(InactiveTtl.ONE_YEAR)
```

## Все ключи

`vkmax` валидирует значения локально — невалидное падает с `ValueError`
до отправки на сервер.

| Ключ | Тип | Допустимые значения | Хелпер |
|---|---|---|---|
| `SEARCH_BY_PHONE` | enum | `ALL` `CONTACTS` | `set_search_by_phone` |
| `INCOMING_CALL` | enum | `ALL` `CONTACTS` | `set_incoming_call` |
| `CHATS_INVITE` | enum | `ALL` `CONTACTS` | `set_chats_invite` |
| `PHONE_NUMBER_PRIVACY` | enum | `ALL` `CONTACTS` `NOBODY` | `set_phone_number_privacy` |
| `INACTIVE_TTL` | enum | `3M` `6M` `1Y` | `set_inactive_ttl` |
| `FAMILY_PROTECTION` | enum | `OFF` `LOW` `MEDIUM` `HIGH` | `set_family_protection` |
| `STICKERS_SUGGEST` | enum | `ON` `OFF` | `set_stickers_suggest` |
| `HIDDEN` | bool | True — скрыть «онлайн» от всех | `set_hidden` |
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
| `DOUBLE_TAP_REACTION_VALUE` | str (emoji) | любой | `set_double_tap_reaction("\U0001f44d")` |

Константы — в `vkmax.PrivacyKey`. Whitelist в рантайме:
`vkmax.privacy.allowed_values(key)`.

## Двойной тап → реакция

```python
await client.set_double_tap_reaction("\U0001f44d")   # 👍
await client.set_double_tap_reaction("fire")         # алиас ок
await client.set_double_tap_reaction(None)           # выключить
```

## Пуш

`Opcode.NOTIF_CONFIG` (134) приходит при изменении настроек с другого
устройства.
