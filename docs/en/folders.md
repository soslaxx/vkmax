# Chat folders

Folders group chats in the sidebar. The server stores the canonical
list; the client maintains a sync counter.

## Read

```python
result = await client.get_folders(folder_sync=0)
# {"folderSync": 1781243858452, "folders": [...]}

folder = await client.get_folder("<folder_id>")
```

Each folder has `id, title, include, favorites, filters, options,
updateTime, sourceId`. The system folder `all.chat.folder` is
pre-created and lists every chat.

## Create / update

There is no separate "create" RPC: send an `update` for a non-existent
`id` and the server creates it.

```python
await client.update_folder(
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
await client.reorder_folders(["all.chat.folder", "my.folder"])
```

## Delete

```python
await client.delete_folder("my.folder")
```

## Push event

Updates arrive as `Opcode.NOTIF_FOLDERS` (277) — register a handler
to react to changes from other devices.
