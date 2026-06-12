# Uploads and downloads

The protocol has two upload pipelines: photos go through one HTTP
endpoint, everything else (files, voice, video, stickers) goes through
another. Both endpoints are returned by an RPC call before the upload.

## Photo (avatar, chat photo, message photo)

```python
token = await client.upload_photo("/path/to/image.jpg", profile=False)
```

`profile=True` requests an upload URL with the profile flag set,
required by `set_profile_avatar`.

## Send a photo message

```python
await client.send_photo(
    chat_id, "/path/to/image.jpg", caption="hi", notify=True
)
```

Or from an already-uploaded token:

```python
await client.send_photos(
    chat_id, [token1, token2], caption=None, notify=True
)
```

## File

```python
info = await client.upload_file(
    chat_id,
    "/path/to/doc.pdf",
    filename=None,                   # default = path.name
    notify=True,
    progress=lambda p: print(p.fraction),
)
# info.file_id, info.token, info.url
```

`upload_file` requests an upload URL, streams the bytes, then sends a
message with a `FILE` attachment. It transparently retries the
`MSG_SEND` while the server reports `attachment.not.ready`.

Low-level pieces:

```python
upload = await client.request_upload_url()
status = await vkmax.uploads.upload_binary(upload.url, path, ...)
await client.send_file(chat_id, upload.file_id, token=upload.token)
```

## Download

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

Then fetch the bytes through `client.download(url)`.

## Progress callback

Accepts both sync and async callables of
`UploadProgress(sent: int, total: int)`:

```python
async def on_progress(p):
    print(f"{p.sent}/{p.total} ({p.fraction:.0%})")

await client.upload_file(chat_id, path, progress=on_progress)
```
