from __future__ import annotations

import time
from typing import Any, TYPE_CHECKING

from .enums import Opcode
from .models import Chat, Packet

if TYPE_CHECKING:
    from .client import MaxClient


def _now_ms() -> int:
    return int(time.time() * 1000)


async def get_chats_list(
    client: "MaxClient",
    *,
    marker: int | None = None,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.CHATS_LIST,
        {"marker": marker if marker is not None else _now_ms()},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def list_chats(
    client: "MaxClient",
    *,
    marker: int | None = None,
) -> list[Chat]:
    data = await get_chats_list(client, marker=marker)
    chats = data.get("chats") if isinstance(data, dict) else None
    if not isinstance(chats, list):
        return []
    return [Chat.from_dict(item) for item in chats if isinstance(item, dict)]


async def iter_chats(
    client: "MaxClient",
    *,
    limit: int | None = None,
) -> list[Chat]:
    results: list[Chat] = []
    marker = _now_ms()
    seen: set[int] = set()
    while True:
        data = await get_chats_list(client, marker=marker)
        raw = data.get("chats") if isinstance(data, dict) else None
        if not isinstance(raw, list) or not raw:
            break
        next_marker: int | None = None
        for item in raw:
            if not isinstance(item, dict):
                continue
            chat = Chat.from_dict(item)
            if chat.id in seen:
                continue
            seen.add(chat.id)
            results.append(chat)
            if limit is not None and len(results) >= limit:
                return results
            if chat.last_event_time and (next_marker is None or chat.last_event_time < next_marker):
                next_marker = chat.last_event_time
        if next_marker is None or next_marker >= marker:
            break
        marker = next_marker
    return results


async def get_chat_info(client: "MaxClient", chat_id: int) -> dict[str, Any] | None:
    packet = await client.invoke(Opcode.CHAT_INFO, {"chatIds": [chat_id]})
    chats = packet.payload.get("chats") if isinstance(packet.payload, dict) else None
    if isinstance(chats, list) and chats and isinstance(chats[0], dict):
        return chats[0]
    return None


async def get_chats_info(client: "MaxClient", chat_ids: list[int]) -> list[dict[str, Any]]:
    packet = await client.invoke(Opcode.CHAT_INFO, {"chatIds": list(chat_ids)})
    chats = packet.payload.get("chats") if isinstance(packet.payload, dict) else None
    if isinstance(chats, list):
        return [item for item in chats if isinstance(item, dict)]
    return []


async def get_chat(client: "MaxClient", chat_id: int) -> Chat | None:
    data = await get_chat_info(client, chat_id)
    return Chat.from_dict(data) if isinstance(data, dict) else None


async def public_search(client: "MaxClient", query: str, *, count: int = 10, offset: int = 0) -> dict[str, Any]:
    packet = await client.invoke(Opcode.PUBLIC_SEARCH, {"query": query, "from": offset, "count": count})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_chat_members(
    client: "MaxClient",
    chat_id: int,
    *,
    count: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.CHAT_MEMBERS,
        {"chatId": chat_id, "count": count, "from": offset},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def add_members(
    client: "MaxClient",
    chat_id: int,
    user_ids: list[int],
    *,
    show_history: bool = True,
) -> Packet:
    return await client.invoke(
        Opcode.CHAT_MEMBERS_UPDATE,
        {
            "chatId": chat_id,
            "userIds": list(user_ids),
            "showHistory": show_history,
            "operation": "ADD",
        },
    )


async def remove_members(
    client: "MaxClient",
    chat_id: int,
    user_ids: list[int],
    *,
    clean_msg_period: int = 0,
) -> Packet:
    return await client.invoke(
        Opcode.CHAT_MEMBERS_UPDATE,
        {
            "chatId": chat_id,
            "userIds": list(user_ids),
            "operation": "REMOVE",
            "cleanMsgPeriod": clean_msg_period,
        },
    )


async def update_chat_members(
    client: "MaxClient",
    chat_id: int,
    user_ids: list[int],
    *,
    action: str = "ADD",
    show_history: bool = True,
    clean_msg_period: int = 0,
) -> Packet:
    op = action.upper()
    if op in ("ADD", "ADMIN"):
        return await add_members(client, chat_id, user_ids, show_history=show_history)
    return await remove_members(client, chat_id, user_ids, clean_msg_period=clean_msg_period)


async def add_admin(client: "MaxClient", chat_id: int, user_id: int) -> Packet:
    return await client.invoke(
        Opcode.CHAT_UPDATE,
        {"chatId": chat_id, "admin": user_id},
    )


async def remove_admin(client: "MaxClient", chat_id: int, user_id: int) -> Packet:
    return await client.invoke(
        Opcode.CHAT_UPDATE,
        {"chatId": chat_id, "removeAdmin": user_id},
    )


async def get_join_requests(
    client: "MaxClient",
    chat_id: int,
    *,
    count: int = 100,
) -> list[dict[str, Any]]:
    packet = await client.invoke(
        Opcode.CHAT_MEMBERS,
        {"chatId": chat_id, "type": "JOIN_REQUEST", "count": count},
    )
    data = packet.payload if isinstance(packet.payload, dict) else {}
    members = data.get("members")
    if isinstance(members, list):
        return [m for m in members if isinstance(m, dict)]
    return []


async def approve_join_requests(
    client: "MaxClient",
    chat_id: int,
    user_ids: list[int],
    *,
    show_history: bool = True,
) -> Packet:
    return await client.invoke(
        Opcode.CHAT_MEMBERS_UPDATE,
        {
            "chatId": chat_id,
            "userIds": list(user_ids),
            "type": "JOIN_REQUEST",
            "showHistory": show_history,
            "operation": "ADD",
        },
    )


async def decline_join_requests(
    client: "MaxClient",
    chat_id: int,
    user_ids: list[int],
) -> Packet:
    return await client.invoke(
        Opcode.CHAT_MEMBERS_UPDATE,
        {
            "chatId": chat_id,
            "userIds": list(user_ids),
            "type": "JOIN_REQUEST",
            "operation": "REMOVE",
        },
    )


async def transfer_ownership(client: "MaxClient", chat_id: int, user_id: int) -> Packet:
    return await client.invoke(
        Opcode.CHAT_UPDATE,
        {"chatId": chat_id, "owner": user_id},
    )


async def join_chat(client: "MaxClient", link: str) -> Packet:
    return await client.invoke(Opcode.CHAT_JOIN, {"link": link})


async def check_chat_link(client: "MaxClient", link: str) -> dict[str, Any]:
    packet = await client.invoke(Opcode.CHAT_CHECK_LINK, {"link": link})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def leave_chat(client: "MaxClient", chat_id: int) -> Packet:
    return await client.invoke(Opcode.CHAT_LEAVE, {"chatId": chat_id})


async def update_chat(client: "MaxClient", chat_id: int, **fields: Any) -> Packet:
    payload = {"chatId": chat_id}
    payload.update(fields)
    return await client.invoke(Opcode.CHAT_UPDATE, payload)


async def set_chat_title(client: "MaxClient", chat_id: int, title: str) -> Packet:
    return await update_chat(client, chat_id, theme=title)


async def set_chat_options(client: "MaxClient", chat_id: int, options: dict[str, Any]) -> Packet:
    return await update_chat(client, chat_id, options=options)


async def set_chat_photo(client: "MaxClient", chat_id: int, photo_token: str) -> Packet:
    return await update_chat(client, chat_id, photoToken=photo_token)


async def set_chat_mute(client: "MaxClient", chat_id: int, dont_disturb_until: int) -> Packet:
    return await client.invoke(
        Opcode.CONFIG,
        {"settings": {"chats": {chat_id: {"dontDisturbUntil": dont_disturb_until}}}},
    )


async def delete_chat(
    client: "MaxClient",
    chat_id: int,
    last_event_time: int,
    *,
    for_all: bool = False,
) -> Packet:
    return await client.invoke(
        Opcode.CHAT_DELETE,
        {"chatId": chat_id, "lastEventTime": last_event_time, "forAll": for_all},
    )


async def get_chat_media(
    client: "MaxClient",
    chat_id: int,
    *,
    media_type: str = "PHOTO",
    count: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.CHAT_MEDIA,
        {"chatId": chat_id, "type": media_type, "count": count, "from": offset},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def clear_chat(client: "MaxClient", chat_id: int) -> Packet:
    return await client.invoke(Opcode.CHAT_CLEAR, {"chatId": chat_id})


async def hide_chat(client: "MaxClient", chat_id: int) -> Packet:
    return await client.invoke(Opcode.CHAT_HIDE, {"chatId": chat_id})


async def subscribe_chat(client: "MaxClient", chat_id: int) -> Packet:
    return await client.invoke(Opcode.CHAT_SUBSCRIBE, {"chatId": chat_id})


async def set_pin_visibility(client: "MaxClient", chat_id: int, visible: bool = True) -> Packet:
    return await client.invoke(
        Opcode.CHAT_PIN_SET_VISIBILITY,
        {"chatId": chat_id, "visible": visible},
    )


async def get_link_info(client: "MaxClient", link: str) -> dict[str, Any]:
    packet = await client.invoke(Opcode.LINK_INFO, {"link": link})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_common_participants(
    client: "MaxClient",
    chat_id: int,
    *,
    count: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.CHAT_SEARCH_COMMON_PARTICIPANTS,
        {"chatId": chat_id, "count": count, "from": offset},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_chat_suggestions(client: "MaxClient") -> dict[str, Any]:
    packet = await client.invoke(Opcode.CHAT_SUGGEST, {})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def set_chat_personal_config(
    client: "MaxClient",
    chat_id: int,
    config: dict[str, Any],
) -> Packet:
    payload = {"chatId": chat_id}
    payload.update(config)
    return await client.invoke(Opcode.CHAT_PERSONAL_CONFIG, payload)


async def create_group(
    client: "MaxClient",
    title: str,
    user_ids: list[int],
    *,
    notify: bool = True,
) -> dict[str, Any] | None:
    packet = await client.invoke(
        Opcode.MSG_SEND,
        {
            "message": {
                "cid": -int(time.time() * 1000),
                "attaches": [
                    {
                        "_type": "CONTROL",
                        "event": "new",
                        "chatType": "CHAT",
                        "title": title,
                        "userIds": list(user_ids),
                    }
                ],
            },
            "notify": notify,
        },
    )
    chat = packet.payload.get("chat") if isinstance(packet.payload, dict) else None
    return chat if isinstance(chat, dict) else None


async def create_channel(
    client: "MaxClient",
    title: str,
    *,
    user_ids: list[int] | None = None,
    notify: bool = True,
) -> dict[str, Any] | None:
    packet = await client.invoke(
        Opcode.MSG_SEND,
        {
            "message": {
                "cid": -int(time.time() * 1000),
                "attaches": [
                    {
                        "_type": "CONTROL",
                        "event": "new",
                        "chatType": "CHANNEL",
                        "title": title,
                        "userIds": list(user_ids or []),
                    }
                ],
            },
            "notify": notify,
        },
    )
    chat = packet.payload.get("chat") if isinstance(packet.payload, dict) else None
    return chat if isinstance(chat, dict) else None


async def set_chat_reactions_settings(
    client: "MaxClient",
    chat_id: int,
    settings: dict[str, Any],
) -> Packet:
    payload = {"chatId": chat_id}
    payload.update(settings)
    return await client.invoke(Opcode.CHAT_REACTIONS_SETTINGS_SET, payload)


async def get_chat_reactions_settings(client: "MaxClient", chat_id: int) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.REACTIONS_SETTINGS_GET_BY_CHAT_ID,
        {"chatId": chat_id, "count": 50, "from": 0},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def complain_chat(client: "MaxClient", chat_id: int, *, reason: str = "") -> Packet:
    return await client.invoke(Opcode.CHAT_COMPLAIN, {"chatId": chat_id, "reason": reason})


async def complain(
    client: "MaxClient",
    chat_id: int,
    *,
    reason: str = "",
    message_id: int | str | None = None,
) -> Packet:
    payload: dict[str, Any] = {"chatId": chat_id, "reason": reason}
    if message_id is not None:
        payload["messageId"] = int(message_id)
    return await client.invoke(Opcode.COMPLAIN, payload)


async def get_complain_reasons(client: "MaxClient", *, chat_type: str = "DIALOG") -> dict[str, Any]:
    packet = await client.invoke(Opcode.COMPLAIN_REASONS_GET, {"chatType": chat_type})
    return packet.payload if isinstance(packet.payload, dict) else {}
