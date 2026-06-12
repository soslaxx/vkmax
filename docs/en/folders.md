# Chat folders

Folders group chats in the sidebar. The server stores the canonical
list; the client maintains a `folderSync` cursor.

## Read

```python
result = await app.get_folders(folder_sync=0)
# {"folderSync": 1781243858452, "folders": [...]}

folder = await app.get_folder("<folder_id>")
```

Each folder has `id, title, include, favorites, filters, options,
updateTime, sourceId`. The system folder `all.chat.folder` is
pre-created and lists every chat.

## Create / update

There is no separate "create" RPC: send an `update` for a non-existent
`id` and the server creates it.

```python
await app.update_folder(
    folder_id="my.folder",
    title="Friends",
    include=[-75800508459204, 307609904],
    favorites=[307609904],
    filters=[],
    options=[],
)
```

Fields:

- `include` — list of chat ids that always belong to the folder.
- `favorites` — pinned subset of `include`.
- `filters` — server-side filter rules (advanced).
- `options` — server-side option flags (advanced).

## Reorder

```python
await app.reorder_folders(["all.chat.folder", "my.folder"])
```

## Delete

```python
await app.delete_folder("my.folder")
```

## Push event

Updates arrive as `Opcode.NOTIF_FOLDERS` (277):

```python
from vkmax import Opcode


async def on_folders(packet):
    print(packet.payload)


app.transport.on(Opcode.NOTIF_FOLDERS, on_folders)
```
