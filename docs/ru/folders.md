# Папки чатов

Папки — это группировка чатов в боковой панели. Канонический список
живёт на сервере; клиент держит sync-счётчик.

## Чтение

```python
result = await client.get_folders(folder_sync=0)
# {"folderSync": 1781243858452, "folders": [...]}

folder = await client.get_folder("<folder_id>")
```

Каждая папка: `id, title, include, favorites, filters, options,
updateTime, sourceId`. Системная папка `all.chat.folder` существует
всегда и содержит все чаты.

## Создание / обновление

Отдельного «create» нет — отправь `update` с несуществующим `id`,
сервер создаст.

```python
await client.update_folder(
    folder_id="my.folder",
    title="Друзья",
    include=[-75800508459204, 307609904],
    favorites=[307609904],
    filters=[],
    options=[],
)
```

Поля:

- `include` — список чатов в папке.
- `favorites` — закреплённые внутри `include`.
- `filters` — серверные правила фильтрации (продвинуто).
- `options` — серверные флаги (продвинуто).

## Порядок

```python
await client.reorder_folders(["all.chat.folder", "my.folder"])
```

## Удаление

```python
await client.delete_folder("my.folder")
```

## Пуш

Изменения с других устройств приходят как `Opcode.NOTIF_FOLDERS` (277).
