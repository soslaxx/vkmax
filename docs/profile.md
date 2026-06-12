# Profile

Your profile lives at `client.me` after `login`. Mutations go through
opcode 16 (`PROFILE`) and 43 (`REMOVE_CONTACT_PHOTO`).

The mobile API exposes **first name**, **last name**, and **avatar**.
Bio/username/status are not supported by the protocol — komet does
not send them and the server rejects unknown profile fields.

## Change name

```python
await client.set_profile_name("Егор")
await client.set_profile_name("Егор", "Иванов")
```

Returns the updated contact dict (same shape as `client.me`).

## Upload and set avatar

```python
await client.upload_and_set_avatar("/path/photo.jpg")
```

This is `upload_photo(profile=True)` + `set_profile_avatar(token)`.

Manual steps:

```python
token = await client.upload_photo("/path/photo.jpg", profile=True)
await client.set_profile_avatar(token, avatar_type="USER_AVATAR")
```

## Preset avatars

The server ships a catalog of pre-made avatars ("Антро", "Эмодзи",
...). Each has a numeric `id` and a `url`.

```python
catalog = await client.get_preset_avatars()
# { "presetAvatars": [
#     {"name": "Антро", "avatars": [{"id": 3778498, "url": ...}, ...]},
#     ...
#   ]
# }

await client.set_preset_avatar(3778498)
```

## Remove a profile photo

```python
await client.remove_profile_photo(photo_id)
```

## List my profile photos

```python
await client.get_profile_photos()              # me
await client.get_profile_photos(contact_id=302677748)
```

## Push events

`Opcode.NOTIF_PROFILE` (159) is fired when the profile changes from
another device.
