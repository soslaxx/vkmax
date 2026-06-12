# Загрузка и скачивание

В протоколе два аплоад-пайплайна: фото идёт через один HTTP-endpoint,
остальное (файлы, голос, видео, стикеры) — через другой. Оба URL
получаются предварительным RPC-вызовом.

## Фото (аватар, фото чата, фото в сообщении)

```python
token = await client.upload_photo("/path/to/image.jpg", profile=False)
```

`profile=True` нужен, если потом ставишь как аватар через
`set_profile_avatar`.

## Отправить фото-сообщение

```python
await client.send_photo(
    chat_id, "/path/to/image.jpg", caption="привет", notify=True
)
```

Или из готового токена:

```python
await client.send_photos(
    chat_id, [token1, token2], caption=None, notify=True
)
```

## Файл

```python
info = await client.upload_file(
    chat_id,
    "/path/to/doc.pdf",
    filename=None,
    notify=True,
    progress=lambda p: print(p.fraction),
)
# info.file_id, info.token, info.url
```

`upload_file` запрашивает URL, стримит байты, потом шлёт сообщение с
FILE-вложением. Автоматически ретраит `MSG_SEND` пока сервер отвечает
`attachment.not.ready`.

Низкоуровневые куски:

```python
upload = await client.request_upload_url()
status = await vkmax.uploads.upload_binary(upload.url, path, ...)
await client.send_file(chat_id, upload.file_id, token=upload.token)
```

## Скачать

```python
url = await client.get_file_url(
    chat_id=chat_id, message_id=message_id, file_id=file_id
)
url = await client.get_photo_url(base_url, token)
url = await client.get_video_url(
    chat_id=chat_id, message_id=message_id, token=token, video_id=vid
)
url = await client.get_audio_url(
    chat_id=chat_id, message_id=message_id, token=token, audio_id=aid
)
```

Затем — `client.download(url)`.

## Прогресс

Принимает sync или async коллбек с `UploadProgress(sent, total)`:

```python
async def on_progress(p):
    print(f"{p.sent}/{p.total} ({p.fraction:.0%})")

await client.upload_file(chat_id, path, progress=on_progress)
```
