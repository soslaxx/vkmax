from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING

from .enums import Opcode
from .exceptions import PacketError, UploadError
from .html_parse import parse_html
from .markdown import parse_markdown
from .models import FileUpload, Message, Packet
from .reactions import resolve_reaction
from .uploads import ProgressCallback, upload_binary, upload_multipart

if TYPE_CHECKING:
    from .client import MaxClient


async def send_message(
    client: "MaxClient",
    chat_id: int,
    text: str,
    *,
    notify: bool = True,
    reply_to: int | str | None = None,
    elements: list[dict[str, Any]] | None = None,
    markdown: bool = False,
    html: bool = False,
) -> str:
    if markdown and html:
        raise ValueError("choose either markdown or html, not both")
    final_text, final_elements = _apply_format(text, elements, markdown=markdown, html=html)
    message: dict[str, Any] = {
        "text": final_text,
        "cid": -int(time.time() * 1000),
        "elements": final_elements,
        "attaches": [],
    }
    payload: dict[str, Any] = {"chatId": chat_id, "message": message, "notify": notify}
    if reply_to is not None:
        payload["link"] = {"type": "REPLY", "messageId": str(reply_to)}
    packet = await client.invoke(Opcode.MSG_SEND, payload)
    return _extract_message_id(packet)


async def send_markdown(
    client: "MaxClient",
    chat_id: int,
    text: str,
    *,
    notify: bool = True,
    reply_to: int | str | None = None,
) -> str:
    return await send_message(
        client,
        chat_id,
        text,
        notify=notify,
        reply_to=reply_to,
        markdown=True,
    )


async def send_html(
    client: "MaxClient",
    chat_id: int,
    text: str,
    *,
    notify: bool = True,
    reply_to: int | str | None = None,
) -> str:
    return await send_message(
        client,
        chat_id,
        text,
        notify=notify,
        reply_to=reply_to,
        html=True,
    )


def _apply_format(
    text: str,
    elements: list[dict[str, Any]] | None,
    *,
    markdown: bool,
    html: bool,
) -> tuple[str, list[dict[str, Any]]]:
    final_text = text
    final_elements = list(elements) if elements else []
    if markdown:
        parsed_text, parsed_elements = parse_markdown(text)
        final_text = parsed_text
        final_elements = parsed_elements + final_elements
    elif html:
        parsed_text, parsed_elements = parse_html(text)
        final_text = parsed_text
        final_elements = parsed_elements + final_elements
    return final_text, final_elements


async def reply_message(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    text: str,
    *,
    notify: bool = True,
) -> str:
    return await send_message(client, chat_id, text, notify=notify, reply_to=message_id)


async def edit_message(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    text: str,
    *,
    notify: bool = True,
    elements: list[dict[str, Any]] | None = None,
    markdown: bool = False,
    html: bool = False,
) -> Packet:
    if markdown and html:
        raise ValueError("choose either markdown or html, not both")
    final_text, final_elements = _apply_format(text, elements, markdown=markdown, html=html)
    payload: dict[str, Any] = {
        "chatId": chat_id,
        "messageId": int(message_id),
        "text": final_text,
        "notify": notify,
    }
    if final_elements:
        payload["elements"] = final_elements
    return await client.invoke(Opcode.MSG_EDIT, payload)


async def edit_markdown(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    text: str,
    *,
    notify: bool = True,
) -> Packet:
    return await edit_message(
        client,
        chat_id,
        message_id,
        text,
        notify=notify,
        markdown=True,
    )


async def edit_html(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    text: str,
    *,
    notify: bool = True,
) -> Packet:
    return await edit_message(
        client,
        chat_id,
        message_id,
        text,
        notify=notify,
        html=True,
    )


async def delete_messages(
    client: "MaxClient",
    chat_id: int,
    message_ids: list[int | str],
    *,
    for_all: bool = False,
) -> Packet:
    payload: dict[str, Any] = {"chatId": chat_id, "messageIds": [int(mid) for mid in message_ids]}
    if for_all:
        payload["forAll"] = True
    return await client.invoke(Opcode.MSG_DELETE, payload)


async def delete_message_range(
    client: "MaxClient",
    chat_id: int,
    from_id: int | str,
    to_id: int | str,
) -> Packet:
    return await client.invoke(
        Opcode.MSG_DELETE_RANGE,
        {"chatId": chat_id, "fromMessageId": int(from_id), "toMessageId": int(to_id)},
    )


async def forward_message(
    client: "MaxClient",
    from_chat_id: int,
    message_id: int | str,
    to_chat_id: int,
    *,
    notify: bool = True,
) -> str:
    packet = await client.invoke(
        Opcode.MSG_SEND,
        {
            "chatId": to_chat_id,
            "message": {
                "cid": -int(time.time() * 1000),
                "elements": [],
                "attaches": [],
            },
            "link": {
                "type": "FORWARD",
                "chatId": from_chat_id,
                "messageId": int(message_id),
            },
            "notify": notify,
        },
    )
    return _extract_message_id(packet)


async def pin_message(client: "MaxClient", chat_id: int, message_id: int | str, *, notify: bool = True) -> Packet:
    return await client.invoke(
        Opcode.CHAT_UPDATE,
        {"chatId": chat_id, "pin": int(message_id), "notify": notify},
    )


async def unpin_message(client: "MaxClient", chat_id: int) -> Packet:
    return await client.invoke(Opcode.CHAT_UPDATE, {"chatId": chat_id, "pin": 0})


async def send_typing(client: "MaxClient", chat_id: int, *, kind: str = "TEXT") -> Packet:
    return await client.invoke(Opcode.MSG_TYPING, {"chatId": chat_id, "type": kind})


async def fetch_history(
    client: "MaxClient",
    chat_id: int,
    *,
    count: int = 50,
    from_time: int | None = None,
) -> list[dict[str, Any]]:
    packet = await client.invoke(
        Opcode.CHAT_HISTORY,
        {
            "chatId": chat_id,
            "from": from_time if from_time is not None else int(time.time() * 1000) + 86_400_000,
            "forward": 0,
            "backward": count,
            "getMessages": True,
        },
    )
    messages = packet.payload.get("messages") if isinstance(packet.payload, dict) else None
    if isinstance(messages, list):
        return [item for item in messages if isinstance(item, dict)]
    return []


async def fetch_messages(
    client: "MaxClient",
    chat_id: int,
    *,
    count: int = 50,
    from_time: int | None = None,
) -> list[Message]:
    raw = await fetch_history(client, chat_id, count=count, from_time=from_time)
    return [Message.from_dict(item, chat_id=chat_id) for item in raw]


async def get_message(client: "MaxClient", chat_id: int, message_id: int | str) -> dict[str, Any] | None:
    packet = await client.invoke(
        Opcode.MSG_GET,
        {"chatId": chat_id, "messageIds": [int(message_id)]},
    )
    messages = packet.payload.get("messages") if isinstance(packet.payload, dict) else None
    if isinstance(messages, list) and messages and isinstance(messages[0], dict):
        return messages[0]
    return None


async def mark_read(
    client: "MaxClient",
    chat_id: int,
    mark: int | None = None,
    *,
    set_as_unread: bool = False,
) -> Packet:
    payload: dict[str, Any] = {"chatId": chat_id}
    if mark is not None:
        payload["mark"] = mark
    if set_as_unread:
        payload["setAsUnread"] = True
    return await client.invoke(Opcode.CHAT_MARK, payload)


async def react_message(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    reaction: str,
) -> Packet:
    emoji = resolve_reaction(reaction)
    return await client.invoke(
        Opcode.MSG_REACTION,
        {"chatId": chat_id, "messageId": int(message_id), "reaction": {"reactionType": "EMOJI", "id": emoji}},
    )


async def cancel_reaction(client: "MaxClient", chat_id: int, message_id: int | str) -> Packet:
    return await client.invoke(
        Opcode.MSG_CANCEL_REACTION,
        {"chatId": chat_id, "messageId": int(message_id)},
    )


async def get_reactions(client: "MaxClient", chat_id: int, message_id: int | str) -> dict[str, Any]:
    message = await get_message(client, chat_id, message_id)
    if isinstance(message, dict):
        info = message.get("reactionInfo")
        if isinstance(info, dict):
            return info
    return {}


async def get_detailed_reactions(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    *,
    reaction: str | None = None,
    count: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "chatId": chat_id,
        "messageId": int(message_id),
        "count": count,
        "from": offset,
    }
    if reaction:
        payload["reaction"] = resolve_reaction(reaction)
    packet = await client.invoke(Opcode.MSG_GET_DETAILED_REACTIONS, payload)
    return packet.payload if isinstance(packet.payload, dict) else {}


async def search_messages(
    client: "MaxClient",
    query: str,
    *,
    chat_id: int | None = None,
    count: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    if chat_id is not None:
        packet = await client.invoke(
            Opcode.CHAT_SEARCH,
            {"chatId": chat_id, "query": query, "count": count, "from": offset},
        )
    else:
        packet = await client.invoke(
            Opcode.MSG_SEARCH,
            {"query": query, "count": count, "from": offset},
        )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_link_preview(client: "MaxClient", url: str) -> dict[str, Any]:
    packet = await client.invoke(Opcode.MSG_SHARE_PREVIEW, {"url": url})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_message_stats(client: "MaxClient", chat_id: int, message_id: int | str) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.MSG_GET_STAT,
        {"chatId": chat_id, "messageId": int(message_id)},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def save_draft(client: "MaxClient", chat_id: int, text: str) -> Packet:
    return await client.invoke(Opcode.DRAFT_SAVE, {"chatId": chat_id, "text": text})


async def discard_draft(client: "MaxClient", chat_id: int) -> Packet:
    return await client.invoke(Opcode.DRAFT_DISCARD, {"chatId": chat_id})


async def send_vote(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    poll_id: int,
    answer_ids: list[int],
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.SEND_VOTE,
        {"chatId": chat_id, "messageId": int(message_id), "pollId": poll_id, "answerIds": answer_ids},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_poll_updates(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    poll_id: int,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.GET_POLL_UPDATES,
        {"chatId": chat_id, "polls": [{"messageId": int(message_id), "pollId": poll_id}]},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_voters_by_answer(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    poll_id: int,
    answer_id: int,
    *,
    count: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.VOTERS_LIST_BY_ANSWER,
        {
            "chatId": chat_id,
            "messageId": int(message_id),
            "pollId": poll_id,
            "answerId": answer_id,
            "count": count,
            "from": offset,
        },
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def send_sticker(
    client: "MaxClient",
    chat_id: int,
    sticker_id: str,
    *,
    pack_id: int | None = None,
    notify: bool = True,
) -> str:
    attach: dict[str, Any] = {"_type": "STICKER", "stickerId": sticker_id}
    if pack_id is not None:
        attach["stickerPackId"] = pack_id
    packet = await client.invoke(
        Opcode.MSG_SEND,
        {
            "chatId": chat_id,
            "message": {
                "cid": -int(time.time() * 1000),
                "elements": [],
                "attaches": [attach],
            },
            "notify": notify,
        },
    )
    return _extract_message_id(packet)


async def request_upload_url(client: "MaxClient", *, count: int = 1) -> FileUpload:
    packet = await client.invoke(Opcode.FILE_UPLOAD, {"count": count})
    info = packet.payload.get("info") if isinstance(packet.payload, dict) else None
    first = info[0] if isinstance(info, list) and info else None
    if not isinstance(first, dict):
        raise UploadError("upload info is missing in server response")
    return FileUpload(
        url=str(first.get("url") or ""),
        file_id=int(first.get("fileId") or 0),
        token=str(first.get("token") or ""),
    )


async def request_photo_upload_url(client: "MaxClient", *, count: int = 1, profile: bool = False) -> str:
    payload: dict[str, Any] = {"count": count}
    if profile:
        payload["profile"] = True
    packet = await client.invoke(Opcode.PHOTO_UPLOAD, payload)
    url = packet.payload.get("url") if isinstance(packet.payload, dict) else None
    if not isinstance(url, str) or not url:
        raise UploadError("photo upload url is missing in server response")
    return url


async def request_video_upload_url(client: "MaxClient", *, count: int = 1) -> FileUpload:
    packet = await client.invoke(Opcode.VIDEO_UPLOAD, {"count": count})
    payload = packet.payload if isinstance(packet.payload, dict) else {}
    info = payload.get("info")
    first: dict[str, Any] | None = None
    if isinstance(info, list) and info and isinstance(info[0], dict):
        first = info[0]
    elif isinstance(payload.get("url"), str):
        first = payload
    if not isinstance(first, dict) or not first.get("url"):
        raise UploadError("video upload info is missing in server response")
    return FileUpload(
        url=str(first.get("url") or ""),
        file_id=int(first.get("videoId") or first.get("fileId") or 0),
        token=str(first.get("token") or ""),
    )


async def upload_file(
    client: "MaxClient",
    chat_id: int,
    path: str | Path,
    *,
    filename: str | None = None,
    notify: bool = True,
    progress: ProgressCallback | None = None,
) -> FileUpload:
    info = await request_upload_url(client)
    await send_typing(client, chat_id, kind="FILE")
    status = await upload_binary(info.url, path, filename=filename, progress=progress)
    if status not in (0, 200, 201, 204):
        raise UploadError(f"file upload failed with HTTP {status}")
    await send_file(client, chat_id, info.file_id, token=info.token, notify=notify)
    return info


async def send_file(
    client: "MaxClient",
    chat_id: int,
    file_id: int,
    *,
    token: str | None = None,
    notify: bool = True,
    attempts: int = 20,
    retry_delay: float = 1.0,
) -> bool:
    attach: dict[str, Any] = {"_type": "FILE"}
    if token:
        attach["token"] = token
    else:
        attach["fileId"] = file_id
    return await _send_attach(
        client,
        chat_id,
        attach,
        notify=notify,
        attempts=attempts,
        retry_delay=retry_delay,
        extra_message={"isLive": False, "detectShare": False, "elements": []},
    )


async def upload_video(
    client: "MaxClient",
    chat_id: int,
    path: str | Path,
    *,
    filename: str | None = None,
    notify: bool = True,
    progress: ProgressCallback | None = None,
    attempts: int = 30,
    retry_delay: float = 1.0,
) -> FileUpload:
    info = await request_video_upload_url(client)
    await send_typing(client, chat_id, kind="VIDEO")
    status = await upload_binary(info.url, path, filename=filename, progress=progress)
    if status not in (0, 200, 201, 204):
        raise UploadError(f"video upload failed with HTTP {status}")
    await send_video(
        client,
        chat_id,
        token=info.token,
        notify=notify,
        attempts=attempts,
        retry_delay=retry_delay,
    )
    return info


async def send_video(
    client: "MaxClient",
    chat_id: int,
    *,
    token: str | None = None,
    video_id: int | None = None,
    notify: bool = True,
    attempts: int = 30,
    retry_delay: float = 1.0,
) -> bool:
    if not token and not video_id:
        raise ValueError("send_video requires token or video_id")
    attach: dict[str, Any] = {"_type": "VIDEO"}
    if video_id is not None:
        attach["videoId"] = int(video_id)
    if token:
        attach["token"] = token
    return await _send_attach(
        client,
        chat_id,
        attach,
        notify=notify,
        attempts=attempts,
        retry_delay=retry_delay,
    )


async def _send_attach(
    client: "MaxClient",
    chat_id: int,
    attach: dict[str, Any],
    *,
    notify: bool,
    attempts: int,
    retry_delay: float,
    extra_message: dict[str, Any] | None = None,
) -> bool:
    message: dict[str, Any] = {
        "cid": -int(time.time() * 1000),
        "attaches": [attach],
    }
    if extra_message:
        message.update(extra_message)
    payload = {"chatId": chat_id, "message": message, "notify": notify}
    for attempt in range(attempts):
        try:
            packet = await client.invoke(Opcode.MSG_SEND, payload)
            return packet.is_ok
        except PacketError as exc:
            if exc.error_key != "attachment.not.ready" or attempt == attempts - 1:
                raise
            await asyncio.sleep(retry_delay)
    return False


async def upload_photo(
    client: "MaxClient",
    path: str | Path,
    *,
    filename: str | None = None,
    profile: bool = False,
    progress: ProgressCallback | None = None,
) -> str:
    url = await request_photo_upload_url(client, profile=profile)
    token = await upload_multipart(url, path, filename=filename, progress=progress)
    if not token:
        raise UploadError("photo upload did not return a token")
    return token


async def send_photos(
    client: "MaxClient",
    chat_id: int,
    photo_tokens: list[str],
    *,
    caption: str | None = None,
    notify: bool = True,
    attempts: int = 20,
    retry_delay: float = 1.0,
) -> dict[str, Any] | None:
    message: dict[str, Any] = {
        "cid": -int(time.time() * 1000),
        "attaches": [{"_type": "PHOTO", "photoToken": token} for token in photo_tokens],
    }
    if caption:
        message["text"] = caption
    payload = {"chatId": chat_id, "message": message, "notify": notify}
    for attempt in range(attempts):
        try:
            packet = await client.invoke(Opcode.MSG_SEND, payload)
            result = packet.payload.get("message") if isinstance(packet.payload, dict) else None
            return result if isinstance(result, dict) else None
        except PacketError as exc:
            if exc.error_key != "attachment.not.ready" or attempt == attempts - 1:
                raise
            await asyncio.sleep(retry_delay)
    return None


async def send_photo(
    client: "MaxClient",
    chat_id: int,
    path: str | Path,
    *,
    caption: str | None = None,
    notify: bool = True,
    progress: ProgressCallback | None = None,
) -> dict[str, Any] | None:
    token = await upload_photo(client, path, progress=progress)
    return await send_photos(client, chat_id, [token], caption=caption, notify=notify)


async def get_file_url(client: "MaxClient", *, chat_id: int, message_id: int | str, file_id: int) -> str | None:
    packet = await client.invoke(
        Opcode.FILE_DOWNLOAD,
        {"messageId": int(message_id), "chatId": chat_id, "fileId": file_id},
    )
    url = packet.payload.get("url") if isinstance(packet.payload, dict) else None
    return url if isinstance(url, str) else None


async def get_photo_url(client: "MaxClient", base_url: str, token: str) -> str | None:
    packet = await client.invoke(Opcode.FILE_DOWNLOAD, {"url": base_url, "token": token})
    content = packet.payload.get("content") if isinstance(packet.payload, dict) else None
    return content if isinstance(content, str) else None


async def get_video_url(
    client: "MaxClient",
    *,
    chat_id: int,
    message_id: int | str,
    token: str,
    video_id: int,
) -> str | None:
    packet = await client.invoke(
        Opcode.VIDEO_PLAY,
        {"messageId": int(message_id), "chatId": chat_id, "token": token, "videoId": video_id},
    )
    if not isinstance(packet.payload, dict):
        return None
    for key in ("MP4_1080", "MP4_720", "MP4_480", "MP4_360", "MP4_240", "HLS", "EXTERNAL"):
        value = packet.payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


async def get_audio_url(
    client: "MaxClient",
    *,
    chat_id: int,
    message_id: int | str,
    token: str,
    audio_id: int,
) -> str | None:
    packet = await client.invoke(
        Opcode.AUDIO_PLAY,
        {"chatId": chat_id, "messageId": int(message_id), "token": token, "audioId": audio_id},
    )
    if not isinstance(packet.payload, dict):
        return None
    for key in ("MP3", "OGG", "HLS", "EXTERNAL"):
        value = packet.payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


async def transcribe_audio(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    media_id: int,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.AUDIO_TRANSCRIPTION,
        {"chatId": chat_id, "messageId": int(message_id), "mediaId": media_id},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


def _extract_message_id(packet: Packet) -> str:
    message = packet.payload.get("message") if isinstance(packet.payload, dict) else None
    msg_id = message.get("id") if isinstance(message, dict) else None
    return str(msg_id) if msg_id is not None else ""
