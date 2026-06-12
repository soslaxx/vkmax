# Uploads and downloads

The protocol has three upload pipelines, one per content category.
Each starts with an RPC asking the server for an upload URL, then
streams the bytes over HTTPS, then references the result by token in
a `MSG_SEND` attachment.

| Pipeline | Opcode | Helper |
|---|---|---|
| Photo | 80 `PHOTO_UPLOAD` | `upload_photo`, `send_photo`, `send_photos` |
| Video | 82 `VIDEO_UPLOAD` | `upload_video`, `send_video` |
| File (anything else) | 87 `FILE_UPLOAD` | `upload_file`, `send_file` |

## Photo

```python
token = await app.upload_photo("/path/to/image.jpg", profile=False)
```

`profile=True` is required by `set_profile_avatar` and tells the
server to return a URL that allows profile-photo binding.

### Send a photo message

```python
await app.send_photo(
    chat_id, "/path/to/image.jpg", caption="hi", notify=True
)
```

Or from an already-uploaded token:

```python
await app.send_photos(
    chat_id, [token1, token2], caption=None, notify=True
)
```

## Video

```python
info = await app.upload_video(
    chat_id,
    "/path/to/clip.mp4",
    filename=None,                # default = path.name
    notify=True,
    progress=lambda p: print(p.fraction),
)
# info.file_id, info.token, info.url
```

Under the hood:

1. `request_video_upload_url()` asks opcode 82 for a URL.
2. The bytes are streamed (`upload_binary`) with `Content-Range`.
3. `send_video(chat_id, token=info.token)` sends a `MSG_SEND`
   with `_type: VIDEO`. The server fills in `videoId`,
   `previewData`, `width/height`, `duration`.

MAX needs a few seconds to ingest the video and you'll see
`attachment.not.ready` errors meanwhile — `vkmax` retries
automatically (up to 30 attempts, 1 s apart by default).

Low-level pieces (if you want to do the steps yourself):

```python
upload = await app.request_video_upload_url()
status = await vkmax.uploads.upload_binary(upload.url, path)
await app.send_video(chat_id, token=upload.token)
```

## File (everything else)

```python
info = await app.upload_file(
    chat_id,
    "/path/to/doc.pdf",
    filename=None,
    notify=True,
    progress=lambda p: print(p.fraction),
)
```

Same retry semantics as video.

Low-level:

```python
upload = await app.request_upload_url()
status = await vkmax.uploads.upload_binary(upload.url, path)
await app.send_file(chat_id, upload.file_id, token=upload.token)
```

## Progress callback

Accepts sync or async callables of `UploadProgress(sent: int, total: int)`:

```python
async def on_progress(p):
    print(f"{p.sent}/{p.total} ({p.fraction:.0%})")

await app.upload_video(chat_id, path, progress=on_progress)
```

The callback is invoked after every 128 KB chunk, plus once with the
final value of `sent == total`.

## Download

```python
url = await app.get_file_url(
    chat_id=chat_id, message_id=message_id, file_id=file_id
)
url = await app.get_photo_url(base_url, token)
url = await app.get_video_url(
    chat_id=chat_id, message_id=message_id, token=token, video_id=vid
)
url = await app.get_audio_url(
    chat_id=chat_id, message_id=message_id, token=token, audio_id=aid
)
```

Then fetch the bytes:

```python
data = await app.download(url)
```

## Avatar shortcut

```python
await app.upload_and_set_avatar("photo.jpg")
```

Wraps `upload_photo(profile=True)` + `set_profile_avatar(token)`.
See [profile.md](profile.md).

## On `Chat`

Typed `Chat` instances (from `get_chat`) carry their own shortcuts:

```python
chat = await app.get_chat(chat_id)
await chat.send_photo("image.jpg")
await chat.send_video("clip.mp4")
await chat.send_file("doc.pdf")
```

## Notes

- Photo upload uses **multipart/form-data**, file/video use a
  **raw binary** body with `Content-Range`.
- Uploads do not currently route through the SOCKS/HTTP proxy that
  the main TLS connection uses — they hit the upload host directly.
  Open an issue if you need that.
- Maximum size is enforced by the server, not by `vkmax`. Don't try
  to push a 4 GB file.
