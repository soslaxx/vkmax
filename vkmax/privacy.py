from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .enums import Opcode

if TYPE_CHECKING:
    from .client import MaxClient


class PrivacyKey:
    SEARCH_BY_PHONE = "SEARCH_BY_PHONE"
    INCOMING_CALL = "INCOMING_CALL"
    CHATS_INVITE = "CHATS_INVITE"
    PHONE_NUMBER_PRIVACY = "PHONE_NUMBER_PRIVACY"
    INACTIVE_TTL = "INACTIVE_TTL"
    FAMILY_PROTECTION = "FAMILY_PROTECTION"
    STICKERS_SUGGEST = "STICKERS_SUGGEST"
    HIDDEN = "HIDDEN"
    SHOW_READ_MARK = "SHOW_READ_MARK"
    SAFE_MODE = "SAFE_MODE"
    SAFE_MODE_NO_PIN = "SAFE_MODE_NO_PIN"
    UNSAFE_FILES = "UNSAFE_FILES"
    ALT_KEYBOARD = "ALT_KEYBOARD"
    PUSH_DETAILS = "PUSH_DETAILS"
    PUSH_NEW_CONTACTS = "PUSH_NEW_CONTACTS"
    CONTENT_LEVEL_ACCESS = "CONTENT_LEVEL_ACCESS"
    DOUBLE_TAP_REACTION_DISABLED = "DOUBLE_TAP_REACTION_DISABLED"
    DOUBLE_TAP_REACTION_VALUE = "DOUBLE_TAP_REACTION_VALUE"
    AUDIO_TRANSCRIPTION_ENABLED = "AUDIO_TRANSCRIPTION_ENABLED"


class PrivacyAudience:
    ALL = "ALL"
    CONTACTS = "CONTACTS"
    NOBODY = "NOBODY"


class FamilyProtectionLevel:
    OFF = "OFF"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InactiveTtl:
    THREE_MONTHS = "3M"
    SIX_MONTHS = "6M"
    ONE_YEAR = "1Y"


_AUDIENCE_AC = frozenset({"ALL", "CONTACTS"})
_AUDIENCE_ACN = frozenset({"ALL", "CONTACTS", "NOBODY"})
_FAMILY_LEVELS = frozenset({"OFF", "LOW", "MEDIUM", "HIGH"})
_INACTIVE_TTLS = frozenset({"3M", "6M", "1Y"})
_ON_OFF = frozenset({"ON", "OFF"})

_ALLOWED_VALUES: dict[str, frozenset[str]] = {
    PrivacyKey.SEARCH_BY_PHONE: _AUDIENCE_AC,
    PrivacyKey.INCOMING_CALL: _AUDIENCE_AC,
    PrivacyKey.CHATS_INVITE: _AUDIENCE_AC,
    PrivacyKey.PHONE_NUMBER_PRIVACY: _AUDIENCE_ACN,
    PrivacyKey.FAMILY_PROTECTION: _FAMILY_LEVELS,
    PrivacyKey.INACTIVE_TTL: _INACTIVE_TTLS,
    PrivacyKey.STICKERS_SUGGEST: _ON_OFF,
}

_BOOL_KEYS: frozenset[str] = frozenset({
    PrivacyKey.HIDDEN,
    PrivacyKey.SHOW_READ_MARK,
    PrivacyKey.SAFE_MODE,
    PrivacyKey.SAFE_MODE_NO_PIN,
    PrivacyKey.UNSAFE_FILES,
    PrivacyKey.PUSH_DETAILS,
    PrivacyKey.PUSH_NEW_CONTACTS,
    PrivacyKey.ALT_KEYBOARD,
    PrivacyKey.CONTENT_LEVEL_ACCESS,
    PrivacyKey.AUDIO_TRANSCRIPTION_ENABLED,
    PrivacyKey.DOUBLE_TAP_REACTION_DISABLED,
})


def allowed_values(key: str) -> tuple[Any, ...]:
    if key in _ALLOWED_VALUES:
        return tuple(sorted(_ALLOWED_VALUES[key]))
    if key in _BOOL_KEYS:
        return (True, False)
    return ()


def _validate(key: str, value: Any) -> None:
    allowed = _ALLOWED_VALUES.get(key)
    if allowed is not None:
        if value not in allowed:
            raise ValueError(
                f"{key} does not accept {value!r}; allowed: {sorted(allowed)}"
            )
        return
    if key in _BOOL_KEYS and not isinstance(value, bool):
        raise ValueError(f"{key} must be bool, got {type(value).__name__}")


async def get_privacy_config(client: "MaxClient", *, refresh: bool = False) -> dict[str, Any]:
    if not refresh:
        cached = client.config.get("user") if isinstance(client.config, dict) else None
        if isinstance(cached, dict) and cached:
            return cached
    packet = await client.invoke(Opcode.CONFIG, {"settings": {"user": {}}})
    user = _extract_user_config(packet.payload)
    if user and isinstance(client.config, dict):
        client.config["user"] = user
    elif user:
        client.config = {"user": user}
    return user


async def update_privacy_config(client: "MaxClient", settings: dict[str, Any]) -> dict[str, Any]:
    for key, value in settings.items():
        _validate(key, value)
    packet = await client.invoke(Opcode.CONFIG, {"settings": {"user": dict(settings)}})
    return _extract_user_config(packet.payload)


def _extract_user_config(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    settings = payload.get("settings")
    if isinstance(settings, dict):
        user = settings.get("user")
        if isinstance(user, dict):
            return user
    user = payload.get("user")
    if isinstance(user, dict):
        return user
    return {}


async def set_privacy(client: "MaxClient", key: str, value: Any) -> dict[str, Any]:
    _validate(key, value)
    return await update_privacy_config(client, {key: value})


async def set_search_by_phone(client: "MaxClient", audience: str) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.SEARCH_BY_PHONE, audience)


async def set_incoming_call(client: "MaxClient", audience: str) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.INCOMING_CALL, audience)


async def set_chats_invite(client: "MaxClient", audience: str) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.CHATS_INVITE, audience)


async def set_phone_number_privacy(client: "MaxClient", audience: str) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.PHONE_NUMBER_PRIVACY, audience)


async def set_inactive_ttl(client: "MaxClient", ttl: str) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.INACTIVE_TTL, ttl)


async def set_family_protection(client: "MaxClient", level: str) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.FAMILY_PROTECTION, level)


async def set_show_read_mark(client: "MaxClient", enabled: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.SHOW_READ_MARK, bool(enabled))


async def set_hidden(client: "MaxClient", hidden: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.HIDDEN, bool(hidden))


async def set_safe_mode(client: "MaxClient", enabled: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.SAFE_MODE, bool(enabled))


async def set_safe_mode_no_pin(client: "MaxClient", enabled: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.SAFE_MODE_NO_PIN, bool(enabled))


async def set_unsafe_files(client: "MaxClient", allow: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.UNSAFE_FILES, bool(allow))


async def set_push_details(client: "MaxClient", show: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.PUSH_DETAILS, bool(show))


async def set_push_new_contacts(client: "MaxClient", enabled: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.PUSH_NEW_CONTACTS, bool(enabled))


async def set_alt_keyboard(client: "MaxClient", enabled: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.ALT_KEYBOARD, bool(enabled))


async def set_content_level_access(client: "MaxClient", enabled: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.CONTENT_LEVEL_ACCESS, bool(enabled))


async def set_stickers_suggest(client: "MaxClient", state: str) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.STICKERS_SUGGEST, state)


async def set_double_tap_reaction(client: "MaxClient", emoji: str | None) -> dict[str, Any]:
    if emoji is None:
        return await update_privacy_config(
            client,
            {
                PrivacyKey.DOUBLE_TAP_REACTION_DISABLED: True,
                PrivacyKey.DOUBLE_TAP_REACTION_VALUE: None,
            },
        )
    return await update_privacy_config(
        client,
        {
            PrivacyKey.DOUBLE_TAP_REACTION_DISABLED: False,
            PrivacyKey.DOUBLE_TAP_REACTION_VALUE: emoji,
        },
    )


async def set_audio_transcription(client: "MaxClient", enabled: bool) -> dict[str, Any]:
    return await set_privacy(client, PrivacyKey.AUDIO_TRANSCRIPTION_ENABLED, bool(enabled))
