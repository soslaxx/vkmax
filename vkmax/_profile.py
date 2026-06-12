from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

from .enums import Opcode
from .exceptions import AuthError, PacketError
from .models import Packet

if TYPE_CHECKING:
    from .client import MaxClient


async def set_profile_name(
    client: "MaxClient",
    first_name: str,
    last_name: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"firstName": first_name}
    if last_name is not None:
        payload["lastName"] = last_name
    packet = await client.invoke(Opcode.PROFILE, payload)
    return _contact_from_payload(packet.payload)


async def set_profile_avatar(
    client: "MaxClient",
    photo_token: str,
    *,
    avatar_type: str = "USER_AVATAR",
) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.PROFILE,
        {"photoToken": photo_token, "avatarType": avatar_type},
    )
    return _contact_from_payload(packet.payload)


async def set_preset_avatar(client: "MaxClient", photo_id: int) -> dict[str, Any]:
    packet = await client.invoke(
        Opcode.PROFILE,
        {"photoId": photo_id, "avatarType": "PRESET_AVATAR"},
    )
    return _contact_from_payload(packet.payload)


async def upload_and_set_avatar(
    client: "MaxClient",
    path: str | Path,
    *,
    avatar_type: str = "USER_AVATAR",
) -> dict[str, Any]:
    token = await client.upload_photo(path, profile=True)
    return await set_profile_avatar(client, token, avatar_type=avatar_type)


async def remove_profile_photo(client: "MaxClient", photo_id: int) -> dict[str, Any]:
    packet = await client.invoke(Opcode.REMOVE_CONTACT_PHOTO, {"photoId": photo_id})
    return _contact_from_payload(packet.payload)


async def get_profile_photos(client: "MaxClient", contact_id: int | None = None) -> dict[str, Any]:
    target = contact_id if contact_id is not None else client.account_id
    if target is None:
        raise AuthError("account id is unknown; call login first")
    packet = await client.invoke(Opcode.CONTACT_PHOTOS, {"contactId": int(target)})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def delete_account(
    client: "MaxClient",
    *,
    password: str | None = None,
    track_id: str | None = None,
    reason: str | None = None,
) -> Packet:
    payload: dict[str, Any] = {}
    if password is not None:
        payload["password"] = password
    if track_id is not None:
        payload["trackId"] = track_id
    if reason is not None:
        payload["reason"] = reason
    return await client.invoke(Opcode.PROFILE_DELETE, payload)


async def set_account_delete_timer(
    client: "MaxClient",
    *,
    days: int | None = None,
    delete_time: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if delete_time is not None:
        payload["deleteTime"] = int(delete_time)
    elif days is not None:
        payload["days"] = int(days)
    packet = await client.invoke(Opcode.PROFILE_DELETE_TIME, payload)
    return packet.payload if isinstance(packet.payload, dict) else {}


async def cancel_account_delete_timer(client: "MaxClient") -> dict[str, Any]:
    packet = await client.invoke(Opcode.PROFILE_DELETE_TIME, {"cancel": True})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def request_email_verify(client: "MaxClient", track_id: str, email: str) -> Packet:
    return await client.invoke(
        Opcode.AUTH_VERIFY_EMAIL,
        {"trackId": track_id, "email": email},
    )


async def check_email_code(client: "MaxClient", track_id: str, code: str) -> Packet:
    return await client.invoke(
        Opcode.AUTH_CHECK_EMAIL,
        {"trackId": track_id, "verifyCode": str(code)},
    )


async def validate_password(client: "MaxClient", track_id: str, password: str) -> Packet:
    return await client.invoke(
        Opcode.AUTH_VALIDATE_PASSWORD,
        {"trackId": track_id, "password": password},
    )


async def validate_password_hint(client: "MaxClient", track_id: str, hint: str) -> Packet:
    return await client.invoke(
        Opcode.AUTH_VALIDATE_HINT,
        {"trackId": track_id, "hint": hint},
    )


async def create_auth_track(client: "MaxClient") -> str:
    packet = await client.invoke(Opcode.AUTH_CREATE_TRACK, {})
    data = packet.payload if isinstance(packet.payload, dict) else {}
    track_id = data.get("trackId") or data.get("track_id")
    if not isinstance(track_id, str) or not track_id:
        raise AuthError("trackId is missing in response", payload=packet.payload)
    return track_id


async def set_2fa(
    client: "MaxClient",
    track_id: str,
    password: str,
    *,
    hint: str | None = None,
    expected_capabilities: list[int] | None = None,
) -> Packet:
    payload: dict[str, Any] = {
        "trackId": track_id,
        "password": password,
    }
    if hint is not None:
        payload["hint"] = hint
    if expected_capabilities is not None:
        payload["expectedCapabilities"] = list(expected_capabilities)
    return await client.invoke(Opcode.AUTH_SET_2FA, payload)


async def remove_2fa(
    client: "MaxClient",
    track_id: str,
    password: str,
) -> Packet:
    return await client.invoke(
        Opcode.AUTH_SET_2FA,
        {"trackId": track_id, "password": password, "remove2fa": True},
    )


async def get_2fa_details(client: "MaxClient") -> dict[str, Any]:
    packet = await client.invoke(Opcode.AUTH_2FA_DETAILS, {})
    return packet.payload if isinstance(packet.payload, dict) else {}


async def request_phone_change(client: "MaxClient", phone: str) -> dict[str, Any]:
    from ._contacts import _normalize_phone
    packet = await client.invoke(
        Opcode.PHONE_BIND_REQUEST,
        {"phone": _normalize_phone(phone)},
    )
    return packet.payload if isinstance(packet.payload, dict) else {}


async def confirm_phone_change(client: "MaxClient", token: str, code: str) -> Packet:
    return await client.invoke(
        Opcode.PHONE_BIND_CONFIRM,
        {"token": token, "verifyCode": str(code)},
    )


def _contact_from_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise PacketError("profile is missing in response", payload=payload)
    profile = payload.get("profile")
    contact = profile.get("contact") if isinstance(profile, dict) else None
    if not isinstance(contact, dict):
        if isinstance(payload.get("contact"), dict):
            return payload["contact"]
        raise PacketError("profile.contact is missing in response", payload=payload)
    return contact
