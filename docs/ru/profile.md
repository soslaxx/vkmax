# Профиль

Профиль хранится в `client.me` после `login`. Изменения идут через
опкод 16 (`PROFILE`) и 43 (`REMOVE_CONTACT_PHOTO`).

Мобильное API поддерживает **имя**, **фамилию** и **аватар**. Bio,
username, статус в протоколе отсутствуют — komet их не шлёт, сервер
отклоняет неизвестные поля.

## Сменить имя

```python
await client.set_profile_name("Егор")
await client.set_profile_name("Егор", "Иванов")
```

Возвращает обновлённый dict профиля (как `client.me`).

## Загрузить и поставить аватар

```python
await client.upload_and_set_avatar("/path/photo.jpg")
```

Это `upload_photo(profile=True)` + `set_profile_avatar(token)`.

Вручную:

```python
token = await client.upload_photo("/path/photo.jpg", profile=True)
await client.set_profile_avatar(token, avatar_type="USER_AVATAR")
```

## Preset-аватары

Сервер хранит каталог готовых аватарок («Антро», «Эмодзи»...). У
каждой числовой `id` и `url`.

```python
catalog = await client.get_preset_avatars()
await client.set_preset_avatar(3778498)
```

## Удалить фото профиля

```python
await client.remove_profile_photo(photo_id)
```

## Список своих фото профиля

```python
await client.get_profile_photos()
await client.get_profile_photos(contact_id=302677748)
```

## Пуш

`Opcode.NOTIF_PROFILE` (159) приходит при изменении профиля с другого
устройства.
