# Админы и права

MAX хранит права админа в одном целочисленном поле `permissions`.
Мобильный API принимает только девять заранее известных значений —
комбинации трёх независимых флагов поверх базового набора админа:

| Флаг | Что разрешает |
|---|---|
| `delete_messages` | удалять чужие сообщения |
| `control_participants` | добавлять / удалять участников |
| `control_admins` | назначать / снимать других админов |

**Базовые** права (закрепы, изменение названия/описания, mute и т.п.)
получает любой админ автоматически.

## Быстрый старт

```python
from vkmax import Client, AdminPermissions

app = Client("main")
await app.start_session()

# назначить со всеми правами
await app.promote_admin(chat_id, user_id,
    delete_messages=True,
    control_participants=True,
    control_admins=True,
)

# прочитать текущие права
perms = await app.get_admin_permissions(chat_id, user_id)
print(perms)            # AdminPermissions(delete_messages=True, ...)
print(perms.describe()) # "delete+participants+admins"

# изменить
await app.update_admin_permissions(chat_id, user_id, delete_messages=True)

# снять с админки
await app.demote_admin(chat_id, user_id)
```

## `AdminPermissions`

Dataclass-обёртка вокруг трёх флагов:

```python
from vkmax import AdminPermissions

p = AdminPermissions(delete_messages=True, control_participants=True)
print(p.to_value())       # 123
print(p.describe())       # "delete+participants"
print(p.is_full)          # False

p = AdminPermissions.from_value(255)  # распарсить число
```

Можно передать `AdminPermissions` сразу в `promote_admin`:

```python
await app.promote_admin(chat_id, user_id,
    permissions=AdminPermissions(control_admins=True))
```

### Допустимые значения

`vkmax.ADMIN_PERMISSION_VALUES` — кортеж девяти разрешённых сервером
чисел:

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

Любое другое значение в `AdminPermissions.to_value()` бросит
`ValueError`. Если нужно нестандартное число — передай
`permissions=<int>` в `promote_admin`, валидация пропускается.

## Список админов

```python
admins = await app.list_admins(chat_id)
# {user_id: AdminPermissions, ...}

for uid, p in admins.items():
    print(uid, p.describe())
```

## На типизированном `Chat`

```python
chat = await app.get_chat(chat_id)
await chat.promote_admin(user_id, control_participants=True)
await chat.demote_admin(user_id)
await chat.list_admins()
```

## Под капотом

Все три хелпера шлют `Opcode.CHAT_MEMBERS_UPDATE` (77):

```python
{
  "chatId": <int>,
  "userIds": [<int>],
  "type": "ADMIN",
  "operation": "add" | "remove",
  "permissions": <int>   # только на "add"
}
```

Сервер возвращает обновлённый `chat` (с новым `adminParticipants`).

## См. также

- [chats.md](chats.md) — общие опции (`ONLY_ADMIN_CAN_*`), участники,
  передача владельца.
- [low-level.md](low-level.md) — если MAX добавит новые флаги, шли
  свой payload через `app.invoke(...)`.
