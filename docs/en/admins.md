# Admins and permissions

MAX uses a single integer field `permissions` to describe what an
admin can do. The mobile API doesn't accept arbitrary numbers — only
nine well-known combinations of three independent flags on top of the
base admin permission set:

| Flag | Action |
|---|---|
| `delete_messages` | delete anyone's messages |
| `control_participants` | add / remove members |
| `control_admins` | promote / demote other admins |

The **base admin** rights (pin messages, edit chat info, ban-and-mute
etc.) are always granted to anybody you mark as an admin.

## Quick start

```python
from vkmax import Client, AdminPermissions

app = Client("main")
await app.start_session()

# promote with all power
await app.promote_admin(chat_id, user_id,
    delete_messages=True,
    control_participants=True,
    control_admins=True,
)

# read current permissions
perms = await app.get_admin_permissions(chat_id, user_id)
print(perms)            # AdminPermissions(delete_messages=True, ...)
print(perms.describe()) # "delete+participants+admins"

# change them
await app.update_admin_permissions(chat_id, user_id, delete_messages=True)

# demote
await app.demote_admin(chat_id, user_id)
```

## `AdminPermissions`

Dataclass that wraps the three flags. Use it instead of raw numbers
for clarity:

```python
from vkmax import AdminPermissions

p = AdminPermissions(delete_messages=True, control_participants=True)
print(p.to_value())       # 123  (server-side number)
print(p.describe())       # "delete+participants"
print(p.is_full)          # False

p = AdminPermissions.from_value(255)  # parse a number back
print(p)                  # AdminPermissions(delete=True, parts=True, admins=True)
```

Expose `AdminPermissions` to `promote_admin` directly:

```python
await app.promote_admin(chat_id, user_id,
    permissions=AdminPermissions(control_admins=True))
```

### Allowed values

`vkmax.ADMIN_PERMISSION_VALUES` is the sorted tuple of nine
server-accepted numbers:

| permissions | delete | participants | admins |
|---:|:---:|:---:|:---:|
| 120 | × | × | × |
| 121 | ✓ | × | × |
| 123 | ✓ | ✓ | × |
| 124 | × | × | ✓ |
| 125 | ✓ | × | ✓ |
| 250 | × | ✓ | × |
| 251 | ✓ | ✓ | × |
| 254 | × | ✓ | ✓ |
| 255 | ✓ | ✓ | ✓ |

Anything else raises `ValueError` in `AdminPermissions.to_value()`.
If you need a non-standard number for some reason, pass
`permissions=<int>` to `promote_admin` — the helper will not validate.

## List all admins

```python
admins = await app.list_admins(chat_id)
# {user_id: AdminPermissions, ...}

for uid, p in admins.items():
    print(uid, p.describe())
```

## On a typed `Chat`

```python
chat = await app.get_chat(chat_id)
await chat.promote_admin(user_id, control_participants=True)
await chat.demote_admin(user_id)
await chat.list_admins()
```

## Under the hood

All three helpers send `Opcode.CHAT_MEMBERS_UPDATE` (77):

```python
{
  "chatId": <int>,
  "userIds": [<int>],
  "type": "ADMIN",
  "operation": "add" | "remove",
  "permissions": <int>   # only on "add"
}
```

Server responds with the updated chat dict (and the new
`adminParticipants` map).

## See also

- [chats.md](chats.md) — chat options (`ONLY_ADMIN_CAN_*`), members,
  ownership.
- [low-level.md](low-level.md) — sending custom payloads if MAX adds
  new flags.
