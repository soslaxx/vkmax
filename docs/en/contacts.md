# Contacts

The mobile API does **not** provide a way to list all contacts in
one call. Fetch them by id, by phone, or via search.

`Client` returns typed `User` objects (`vkmax.UserType`) — they
carry a back-reference to the client and expose helpers.
`MaxClient` returns raw dicts.

## Fetch by id

```python
user = await app.get_user(user_id)          # User | None  (pyrogram-style)
users = await app.resolve_users([id1, id2]) # list[Contact]

raw  = await app.get_contact(user_id)
raws = await app.get_contacts([id1, id2])
```

Fields on `User` / `Contact`:

```python
user.id
user.first_name
user.last_name
user.phone
user.base_url           # URL prefix for avatars
user.photo_id
user.options            # set[str]: 'BOT', 'OFFICIAL', 'ONEME', 'TT', ...
user.full_name
user.is_bot
user.is_official
user.raw                # full server dict
```

## Methods on `User`

```python
user = await app.get_user(user_id)
await user.send_message("hi")

# DM chat id:
user.dm_chat_id          # property
```

## Lookup by phone

```python
await app.contact_by_phone("+79991234567")
```

Returns the raw payload. Pyrogram-style usage:

```python
info = await app.contact_by_phone("+79991234567")
contact = info.get("contact") if isinstance(info, dict) else None
if contact:
    peer = await app.get_user(contact["id"])
    await peer.send_message("hi")
```

## Search

```python
await app.search_contact("name or username", count=20)
```

## Add / update / sort

```python
await app.add_contact(
    user_id, first_name="John", last_name=None, phone="+79991234567"
)
await app.update_contact(contact_id, status="NORMAL")
await app.sort_contacts([id1, id2, id3])
await app.verify_contact(contact_id)
```

## Block / unblock

```python
await app.block_contact(user_id)
await app.unblock_contact(user_id)
await app.get_blocked_contacts(count=100, offset=0)
```

## Mutual contacts and photos

```python
await app.get_mutual_contacts(contact_id)
await app.get_contact_photos(contact_id)
```

## Presence

```python
await app.get_contact_presence([user_id1, user_id2])
# {302677748: {"status": 1, "seen": 1781243040171}, ...}
```

`status=1` means online, `seen` is the last-seen timestamp in ms.

Push updates arrive as `Opcode.NOTIF_PRESENCE` (132). Subscribe at
transport level:

```python
from vkmax import Opcode
app.transport.on(Opcode.NOTIF_PRESENCE, lambda p: print(p.payload))
```

## DM chat id

```python
from vkmax import dm_chat_id

chat_id = dm_chat_id(my_id, other_id)  # int = a XOR b
await app.send_message(chat_id, "hi")
```

For a `User`:

```python
await user.send_message("hi")          # uses user.dm_chat_id internally
```

## Filters by user

```python
from vkmax import filters


@app.on_message(filters.user(123456, 789012))
async def from_friends(app, m):
    ...
```

See [filters.md](filters.md).
