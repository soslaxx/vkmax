from __future__ import annotations

import time
from typing import Any, TYPE_CHECKING

from .enums import Opcode
from .models import Packet

if TYPE_CHECKING:
    from .client import MaxClient

MUTE_OFF = 0
MUTE_FOREVER = -1


async def get_chat_notification_settings(client: "MaxClient") -> dict[str, Any]:
    if isinstance(client.config, dict):
        chats = client.config.get("chats")
        if isinstance(chats, dict):
            return chats
    packet = await client.invoke(Opcode.CONFIG, {"settings": {"chats": {}}})
    payload = packet.payload if isinstance(packet.payload, dict) else {}
    settings = payload.get("settings")
    container = settings if isinstance(settings, dict) else payload
    chats = container.get("chats") if isinstance(container, dict) else None
    if isinstance(chats, dict):
        if isinstance(client.config, dict):
            client.config["chats"] = chats
        else:
            client.config = {"chats": chats}
        return chats
    return {}


async def set_chat_mute(
    client: "MaxClient",
    chat_id: int,
    dont_disturb_until: int = MUTE_FOREVER,
) -> Packet:
    return await client.invoke(
        Opcode.CONFIG,
        {"settings": {"chats": {int(chat_id): {"dontDisturbUntil": int(dont_disturb_until)}}}},
    )


async def mute_chat(client: "MaxClient", chat_id: int) -> Packet:
    return await set_chat_mute(client, chat_id, MUTE_FOREVER)


async def unmute_chat(client: "MaxClient", chat_id: int) -> Packet:
    return await set_chat_mute(client, chat_id, MUTE_OFF)


async def mute_chat_for(client: "MaxClient", chat_id: int, seconds: int) -> Packet:
    until = int(time.time() * 1000) + int(seconds) * 1000
    return await set_chat_mute(client, chat_id, until)


async def set_chats_mute(
    client: "MaxClient",
    states: dict[int, int],
) -> Packet:
    chats_payload = {int(cid): {"dontDisturbUntil": int(value)} for cid, value in states.items()}
    return await client.invoke(Opcode.CONFIG, {"settings": {"chats": chats_payload}})
