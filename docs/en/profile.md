# Profile

Your profile lives at `app.me` after `login`. Mutations go through
opcode 16 (`PROFILE`) and 43 (`REMOVE_CONTACT_PHOTO`).

The mobile API exposes **first name**, **last name**, and **avatar**.
Bio / username / status are not supported by the protocol — komet
does not send them and the server rejects unknown profile fields.

## Change name

```python
await app.set_profile_name("Егор")
await app.set_profile_name("Егор", "Иванов")
```

Returns the updated contact dict (same shape as `app.me`).

## Upload and set avatar

```python
await app.upload_and_set_avatar("/path/photo.jpg")
```

This is `upload_photo(profile=True)` + `set_profile_avatar(token)`.

Manual steps:

```python
token = await app.upload_photo("/path/photo.jpg", profile=True)
await app.set_profile_avatar(token, avatar_type="USER_AVATAR")
```

## Preset avatars

The server ships a catalog of pre-made avatars ("Антро", "Эмодзи",
…). Each has a numeric `id` and a `url`.

```python
catalog = await app.get_preset_avatars()
# {"presetAvatars": [
#     {"name": "Антро", "avatars": [{"id": 3778498, "url": ...}, ...]},
#     ...
#   ]
# }

await app.set_preset_avatar(3778498)
```

## Remove a profile photo

```python
await app.remove_profile_photo(photo_id)
```

## List my profile photos

```python
await app.get_profile_photos()                       # me
await app.get_profile_photos(contact_id=302677748)
```

## Push events

`Opcode.NOTIF_PROFILE` (159) is fired when the profile changes from
another device.

```python
from vkmax import Opcode


async def on_profile(packet):
    print(packet.payload)


app.transport.on(Opcode.NOTIF_PROFILE, on_profile)
```

## See also

- [account.md](account.md) — delete account, change phone, bind email.
- [security.md](security.md) — 2FA, sessions.
- [privacy.md](privacy.md) — privacy settings (`HIDDEN`,
  `SEARCH_BY_PHONE`, …).
