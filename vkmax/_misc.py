from __future__ import annotations

import json
import uuid
from typing import Any, TYPE_CHECKING

from .enums import Opcode
from .models import Packet

if TYPE_CHECKING:
    from .client import MaxClient


async def get_sticker_packs(client: "MaxClient", *, sync: int = 0) -> dict[str, Any]:
    packet = await client.invoke(Opcode.ASSETS_GET, {"sync": sync})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_sticker_packs_by_ids(client: "MaxClient", pack_ids: list[int]) -> dict[str, Any]:
    packet = await client.invoke(Opcode.ASSETS_GET_BY_IDS, {"stickerPackIds": list(pack_ids)})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def add_sticker_pack(client: "MaxClient", pack_id: int) -> Packet:
    return await client.invoke(Opcode.ASSETS_ADD, {"stickerPackId": pack_id})


async def remove_sticker_pack(client: "MaxClient", pack_id: int) -> Packet:
    return await client.invoke(Opcode.ASSETS_REMOVE, {"stickerPackId": pack_id})


async def suggest_sticker(client: "MaxClient", query: str) -> dict[str, Any]:
    packet = await client.invoke(Opcode.STICKER_SUGGEST, {"query": query})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_bot_info(client: "MaxClient", bot_id: int) -> dict[str, Any]:
    packet = await client.invoke(Opcode.BOT_INFO, {"botId": bot_id})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_bot_commands(client: "MaxClient", chat_id: int, bot_id: int) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.CHAT_BOT_COMMANDS,
        {"chatId": chat_id, "botId": bot_id},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def send_bot_callback(
    client: "MaxClient",
    chat_id: int,
    message_id: int | str,
    callback_data: str,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.MSG_SEND_CALLBACK,
        {"chatId": chat_id, "messageId": int(message_id), "callbackData": callback_data},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def suspend_bot(client: "MaxClient", bot_id: int) -> Packet:
    return await client.invoke(Opcode.SUSPEND_BOT, {"botId": bot_id})


async def get_last_mentions(
    client: "MaxClient",
    *,
    count: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.GET_LAST_MENTIONS,
        {"count": count, "from": offset},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_folders(client: "MaxClient", *, folder_sync: int = 0) -> dict[str, Any]:
    packet = await client.invoke(Opcode.FOLDERS_GET, {"folderSync": folder_sync})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_folder(client: "MaxClient", folder_id: str) -> dict[str, Any]:
    packet = await client.invoke(Opcode.FOLDERS_GET_BY_ID, {"id": folder_id})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def update_folder(
    client: "MaxClient",
    *,
    folder_id: str,
    title: str,
    include: list[int] | None = None,
    favorites: list[int] | None = None,
    filters: list[Any] | None = None,
    options: list[Any] | None = None,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.FOLDERS_UPDATE,
        {
            "id": folder_id,
            "title": title,
            "include": include or [],
            "favorites": favorites or [],
            "filters": filters or [],
            "options": options or [],
        },
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def reorder_folders(client: "MaxClient", folder_ids: list[str]) -> Packet:
    return await client.invoke(Opcode.FOLDERS_REORDER, {"foldersOrder": list(folder_ids)})


async def delete_folder(client: "MaxClient", folder_id: str) -> Packet:
    return await client.invoke(Opcode.FOLDERS_DELETE, {"id": folder_id})


async def get_call_history(client: "MaxClient") -> dict[str, Any]:
    packet = await client.invoke(Opcode.VIDEO_CHAT_HISTORY, {})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_inbound_calls(client: "MaxClient") -> dict[str, Any]:
    packet = await client.invoke(Opcode.GET_INBOUND_CALLS, {})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def initiate_call(
    client: "MaxClient",
    callee_id: int,
    *,
    is_video: bool = False,
) -> dict[str, Any]:
    internal_params = {
        "deviceId": client.device.device_id,
        "sdkVersion": "2.8.9",
        "clientAppKey": "VKMAXCLIENTKEYAAAA",
        "platform": "ANDROID",
        "protocolVersion": 5,
        "domainId": "",
        "capabilities": "3c03f",
    }
    packet = await client.invoke(
        Opcode.VIDEO_CHAT_START_ACTIVE,
        {
            "conversationId": str(uuid.uuid4()),
            "calleeIds": [callee_id],
            "internalParams": json.dumps(internal_params),
            "isVideo": is_video,
        },
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def create_video_chat_join_link(client: "MaxClient", chat_id: int) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.VIDEO_CHAT_CREATE_JOIN_LINK,
        {"chatId": chat_id},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_video_chat_members(client: "MaxClient", chat_id: int) -> dict[str, Any]:
    packet = await client.invoke(Opcode.VIDEO_CHAT_MEMBERS, {"chatId": chat_id})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def stop_location(client: "MaxClient", chat_id: int) -> Packet:
    return await client.invoke(Opcode.LOCATION_STOP, {"chatId": chat_id})


async def approve_qr_login(client: "MaxClient", qr_link: str) -> Packet:
    return await client.invoke(Opcode.AUTH_QR_APPROVE, {"qrLink": qr_link})


async def get_ok_token(client: "MaxClient") -> dict[str, Any]:
    packet = await client.invoke(Opcode.OK_TOKEN, {})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def request_phone_bind(client: "MaxClient", phone: str) -> dict[str, Any]:
    from ._contacts import _normalize_phone
    packet = await client.invoke(
        Opcode.PHONE_BIND_REQUEST,
        {"phone": _normalize_phone(phone)},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def confirm_phone_bind(client: "MaxClient", code: str, token: str) -> Packet:
    return await client.invoke(
        Opcode.PHONE_BIND_CONFIRM,
        {"verifyCode": str(code), "token": token},
    )


async def get_webapp_init_data(client: "MaxClient", app_id: int) -> dict[str, Any]:
    packet = await client.invoke(Opcode.WEB_APP_INIT_DATA, {"appId": app_id})
    return packet.payload if isinstance(packet.payload, dict) else {}
