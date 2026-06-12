from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .enums import Opcode
from .models import Contact, Packet

if TYPE_CHECKING:
    from .client import MaxClient


def _normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    return f"+{digits}"


async def get_contact(client: "MaxClient", contact_id: int) -> dict[str, Any] | None:
    contacts = await get_contacts(client, [contact_id])
    return contacts[0] if contacts else None


async def get_contacts(client: "MaxClient", contact_ids: list[int]) -> list[dict[str, Any]]:
    packet = await client.invoke(Opcode.CONTACT_INFO, {"contactIds": list(contact_ids)})
    contacts = packet.payload.get("contacts") if isinstance(packet.payload, dict) else None
    if isinstance(contacts, list):
        return [item for item in contacts if isinstance(item, dict)]
    return []


async def resolve_user(client: "MaxClient", user_id: int) -> Contact | None:
    data = await get_contact(client, user_id)
    return Contact.from_dict(data) if isinstance(data, dict) else None


async def resolve_users(client: "MaxClient", user_ids: list[int]) -> list[Contact]:
    raw = await get_contacts(client, user_ids)
    return [Contact.from_dict(item) for item in raw]


async def get_blocked_contacts(
    client: "MaxClient",
    *,
    count: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    packet = await client.invoke(
        Opcode.CONTACT_LIST,
        {"status": "BLOCKED", "count": count, "from": offset},
    )
    contacts = packet.payload.get("contacts") if isinstance(packet.payload, dict) else None
    if isinstance(contacts, list):
        return [item for item in contacts if isinstance(item, dict)]
    return []


def dm_chat_id(user_a: int, user_b: int) -> int:
    return int(user_a) ^ int(user_b)


async def search_contact(
    client: "MaxClient",
    query: str,
    *,
    count: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.CONTACT_SEARCH,
        {"query": query, "count": count, "from": offset},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def contact_by_phone(client: "MaxClient", phone: str) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.CONTACT_INFO_BY_PHONE,
        {"phone": _normalize_phone(phone)},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_contact_presence(client: "MaxClient", contact_ids: list[int]) -> dict[str, Any]:
    packet = await client.invoke(Opcode.CONTACT_PRESENCE, {"contactIds": list(contact_ids)})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def add_contact(
    client: "MaxClient",
    user_id: int,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
) -> Packet:
    payload: dict[str, Any] = {"userId": user_id}
    if first_name:
        payload["firstName"] = first_name
    if last_name:
        payload["lastName"] = last_name
    if phone:
        payload["phone"] = _normalize_phone(phone)
    return await client.invoke(Opcode.CONTACT_ADD, payload)


async def update_contact(client: "MaxClient", contact_id: int, *, status: str = "NORMAL") -> Packet:
    return await client.invoke(
        Opcode.CONTACT_UPDATE,
        {"contactId": contact_id, "status": status},
    )


async def block_contact(client: "MaxClient", contact_id: int) -> Packet:
    return await update_contact(client, contact_id, status="BLOCKED")


async def unblock_contact(client: "MaxClient", contact_id: int) -> Packet:
    return await update_contact(client, contact_id, status="NORMAL")


async def get_mutual_contacts(client: "MaxClient", contact_id: int) -> dict[str, Any]:
    packet = await client.invoke(Opcode.CONTACT_MUTUAL, {"contactId": contact_id})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def get_contact_photos(client: "MaxClient", contact_id: int) -> dict[str, Any]:
    packet = await client.invoke(Opcode.CONTACT_PHOTOS, {"contactId": contact_id})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def verify_contact(client: "MaxClient", contact_id: int) -> Packet:
    return await client.invoke(Opcode.CONTACT_VERIFY, {"contactId": contact_id})


async def sort_contacts(client: "MaxClient", contact_ids: list[int]) -> Packet:
    return await client.invoke(Opcode.CONTACT_SORT, {"contactIds": list(contact_ids)})
