from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .enums import Opcode
from .models import Packet

if TYPE_CHECKING:
    from .client import MaxClient


@dataclass(frozen=True, slots=True)
class AdminPermissions:
    delete_messages: bool = False
    control_participants: bool = False
    control_admins: bool = False

    def to_value(self) -> int:
        key = (self.delete_messages, self.control_participants, self.control_admins)
        try:
            return _COMBO_TO_VALUE[key]
        except KeyError as exc:
            raise ValueError(
                f"unsupported permission combination: {key}; pass raw int instead"
            ) from exc

    @classmethod
    def from_value(cls, value: int) -> "AdminPermissions":
        combo = _VALUE_TO_COMBO.get(int(value))
        if combo is None:
            return cls()
        return cls(*combo)

    @property
    def is_full(self) -> bool:
        return self.delete_messages and self.control_participants and self.control_admins

    def describe(self) -> str:
        bits = []
        if self.delete_messages:
            bits.append("delete")
        if self.control_participants:
            bits.append("participants")
        if self.control_admins:
            bits.append("admins")
        return "+".join(bits) if bits else "basic"


_COMBO_TO_VALUE: dict[tuple[bool, bool, bool], int] = {
    (False, False, False): 120,
    (True, False, False): 121,
    (True, True, False): 123,
    (False, False, True): 124,
    (True, False, True): 125,
    (False, True, False): 250,
    (True, True, False): 251,
    (False, True, True): 254,
    (True, True, True): 255,
}
_COMBO_TO_VALUE[(True, True, False)] = 251
_VALUE_TO_COMBO: dict[int, tuple[bool, bool, bool]] = {
    120: (False, False, False),
    121: (True, False, False),
    123: (True, True, False),
    124: (False, False, True),
    125: (True, False, True),
    250: (False, True, False),
    251: (True, True, False),
    254: (False, True, True),
    255: (True, True, True),
}

ADMIN_PERMISSION_VALUES = tuple(sorted(_VALUE_TO_COMBO))


def _resolve_permissions(
    permissions: int | AdminPermissions | None,
    *,
    delete_messages: bool,
    control_participants: bool,
    control_admins: bool,
) -> int:
    if isinstance(permissions, AdminPermissions):
        return permissions.to_value()
    if permissions is None:
        return AdminPermissions(
            delete_messages=delete_messages,
            control_participants=control_participants,
            control_admins=control_admins,
        ).to_value()
    return int(permissions)


async def promote_admin(
    client: "MaxClient",
    chat_id: int,
    user_id: int,
    *,
    permissions: int | AdminPermissions | None = None,
    delete_messages: bool = False,
    control_participants: bool = False,
    control_admins: bool = False,
) -> Packet:
    value = _resolve_permissions(
        permissions,
        delete_messages=delete_messages,
        control_participants=control_participants,
        control_admins=control_admins,
    )
    return await client.invoke(
        Opcode.CHAT_MEMBERS_UPDATE,
        {
            "chatId": chat_id,
            "userIds": [int(user_id)],
            "type": "ADMIN",
            "operation": "add",
            "permissions": value,
        },
    )


async def update_admin_permissions(
    client: "MaxClient",
    chat_id: int,
    user_id: int,
    *,
    permissions: int | AdminPermissions | None = None,
    delete_messages: bool = False,
    control_participants: bool = False,
    control_admins: bool = False,
) -> Packet:
    return await promote_admin(
        client,
        chat_id,
        user_id,
        permissions=permissions,
        delete_messages=delete_messages,
        control_participants=control_participants,
        control_admins=control_admins,
    )


async def demote_admin(
    client: "MaxClient",
    chat_id: int,
    user_id: int,
) -> Packet:
    return await client.invoke(
        Opcode.CHAT_MEMBERS_UPDATE,
        {
            "chatId": chat_id,
            "userIds": [int(user_id)],
            "type": "ADMIN",
            "operation": "remove",
        },
    )


async def get_admin_permissions(
    client: "MaxClient",
    chat_id: int,
    user_id: int,
) -> AdminPermissions | None:
    info = await client.get_chat_info(chat_id)
    if not isinstance(info, dict):
        return None
    admins = info.get("adminParticipants")
    if not isinstance(admins, dict):
        return None
    entry = admins.get(int(user_id)) or admins.get(str(user_id))
    if not isinstance(entry, dict):
        return None
    raw = entry.get("permissions")
    if not isinstance(raw, int):
        return None
    return AdminPermissions.from_value(raw)


async def list_admins(
    client: "MaxClient",
    chat_id: int,
) -> dict[int, AdminPermissions]:
    info = await client.get_chat_info(chat_id)
    if not isinstance(info, dict):
        return {}
    admins = info.get("adminParticipants")
    out: dict[int, AdminPermissions] = {}
    if not isinstance(admins, dict):
        return out
    for key, value in admins.items():
        try:
            uid = int(key)
        except (TypeError, ValueError):
            continue
        raw = value.get("permissions") if isinstance(value, dict) else None
        if not isinstance(raw, int):
            continue
        out[uid] = AdminPermissions.from_value(raw)
    return out
