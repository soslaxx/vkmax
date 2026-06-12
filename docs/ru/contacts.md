# Контакты

Мобильное API **не отдаёт** все контакты одним запросом. Можно
получить по id, по номеру или через поиск.

## По id

```python
user  = await client.resolve_user(user_id)   # Contact | None
users = await client.resolve_users([id1, id2])

raw  = await client.get_contact(user_id)
raws = await client.get_contacts([id1, id2])
```

`Contact`: `id, first_name, last_name, phone, base_url, photo_id,
options, full_name, is_official, is_bot, raw`.

## По телефону

```python
await client.contact_by_phone("+79991234567")
```

## Поиск

```python
await client.search_contact("имя или ник", count=20)
```

## Добавить / обновить / отсортировать

```python
await client.add_contact(
    user_id, first_name="Иван", last_name=None, phone="+79991234567"
)
await client.update_contact(contact_id, status="NORMAL")
await client.sort_contacts([id1, id2, id3])
await client.verify_contact(contact_id)
```

## Блок / разблок

```python
await client.block_contact(user_id)
await client.unblock_contact(user_id)
await client.get_blocked_contacts(count=100, offset=0)
```

## Общие контакты и фотки

```python
await client.get_mutual_contacts(contact_id)
await client.get_contact_photos(contact_id)
```

## Онлайн / last seen

```python
await client.get_contact_presence([user_id1, user_id2])
# {302677748: {"status": 1, "seen": 1781243040171}, ...}
```

`status=1` — онлайн, `seen` — last seen в миллисекундах.

## ID DM-чата

```python
from vkmax import dm_chat_id
chat_id = dm_chat_id(my_id, other_id)  # int (a XOR b)
```
