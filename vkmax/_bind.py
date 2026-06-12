from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from . import _chats, _contacts, _messages, _misc, _notify, _profile, privacy
from .exceptions import SessionExpired, TransportClosed

if TYPE_CHECKING:
    from .client import MaxClient

_MESSAGES = [
    "send_message", "send_markdown", "send_html", "reply_message",
    "edit_message", "edit_markdown", "edit_html",
    "delete_messages", "delete_message_range",
    "forward_message", "pin_message", "unpin_message", "send_typing", "fetch_history",
    "fetch_messages", "get_message", "mark_read", "react_message", "cancel_reaction",
    "get_reactions", "get_detailed_reactions", "search_messages", "get_link_preview",
    "get_message_stats", "save_draft", "discard_draft", "send_vote", "get_poll_updates",
    "get_voters_by_answer", "send_poll", "send_sticker", "request_upload_url", "request_photo_upload_url",
    "upload_file", "send_file", "upload_photo", "send_photos", "send_photo",
    "upload_video", "send_video", "request_video_upload_url",
    "get_file_url", "get_photo_url", "get_video_url", "get_audio_url", "transcribe_audio",
]

_CHATS = [
    "get_chats_list", "list_chats", "iter_chats", "get_chat_info", "get_chats_info", "get_chat",
    "public_search", "get_chat_members", "update_chat_members", "add_members", "remove_members",
    "add_admin", "remove_admin", "get_join_requests", "approve_join_requests", "decline_join_requests",
    "transfer_ownership", "join_chat", "check_chat_link",
    "leave_chat", "update_chat", "set_chat_title", "set_chat_options", "set_chat_photo",
    "set_chat_mute", "revoke_invite_link", "delete_chat", "get_chat_media", "clear_chat", "hide_chat",
    "subscribe_chat", "set_pin_visibility", "get_link_info", "get_common_participants",
    "get_chat_suggestions", "set_chat_personal_config", "create_group", "create_channel",
    "set_chat_reactions_settings", "get_chat_reactions_settings", "complain_chat",
    "complain", "get_complain_reasons",
]

_CONTACTS = [
    "get_contact", "get_contacts", "resolve_user", "resolve_users",
    "get_blocked_contacts", "search_contact", "contact_by_phone", "get_contact_presence",
    "add_contact", "update_contact", "block_contact", "unblock_contact", "get_mutual_contacts",
    "get_contact_photos", "verify_contact", "sort_contacts",
]

_MISC = [
    "get_sticker_packs", "get_sticker_packs_by_ids", "add_sticker_pack", "remove_sticker_pack",
    "suggest_sticker", "get_bot_info", "get_bot_commands", "send_bot_callback", "suspend_bot",
    "get_last_mentions", "get_folders", "get_folder", "update_folder", "reorder_folders",
    "delete_folder", "get_call_history", "get_inbound_calls", "initiate_call",
    "create_video_chat_join_link", "get_video_chat_members", "stop_location",
    "approve_qr_login", "get_ok_token", "request_phone_bind", "confirm_phone_bind",
    "get_webapp_init_data",
]

_PROFILE = [
    "set_profile_name", "set_profile_avatar", "set_preset_avatar", "upload_and_set_avatar",
    "remove_profile_photo", "get_profile_photos",
    "delete_account", "set_account_delete_timer", "cancel_account_delete_timer",
    "request_email_verify", "check_email_code",
    "validate_password", "validate_password_hint", "create_auth_track",
    "set_2fa", "remove_2fa", "get_2fa_details",
    "request_phone_change", "confirm_phone_change",
]

_NOTIFY = [
    "get_chat_notification_settings", "set_chat_mute", "mute_chat", "unmute_chat",
    "mute_chat_for", "set_chats_mute",
]

_PRIVACY = [
    "get_privacy_config", "update_privacy_config", "set_privacy",
    "set_search_by_phone", "set_incoming_call", "set_chats_invite",
    "set_phone_number_privacy", "set_inactive_ttl", "set_family_protection",
    "set_show_read_mark", "set_hidden", "set_safe_mode", "set_safe_mode_no_pin",
    "set_unsafe_files", "set_push_details", "set_push_new_contacts",
    "set_alt_keyboard", "set_content_level_access", "set_stickers_suggest",
    "set_double_tap_reaction", "set_audio_transcription",
]


def _wrap(module, name: str):
    fn = getattr(module, name)

    async def method(self, *args, **kwargs):
        return await fn(self, *args, **kwargs)

    method.__name__ = name
    method.__qualname__ = f"MaxClient.{name}"
    method.__doc__ = fn.__doc__
    return method


def bind_methods(cls) -> None:
    for name in _MESSAGES:
        setattr(cls, name, _wrap(_messages, name))
    for name in _CHATS:
        setattr(cls, name, _wrap(_chats, name))
    for name in _CONTACTS:
        setattr(cls, name, _wrap(_contacts, name))
    for name in _MISC:
        setattr(cls, name, _wrap(_misc, name))
    for name in _PROFILE:
        setattr(cls, name, _wrap(_profile, name))
    for name in _NOTIFY:
        setattr(cls, name, _wrap(_notify, name))
    for name in _PRIVACY:
        setattr(cls, name, _wrap(privacy, name))


async def ping_loop(client: "MaxClient") -> None:
    try:
        while True:
            await asyncio.sleep(client.ping_interval)
            if not client.transport.is_connected:
                return
            try:
                await asyncio.wait_for(client.ping(), timeout=15.0)
            except (TransportClosed, asyncio.TimeoutError):
                return
            except Exception:
                continue
    except asyncio.CancelledError:
        return


async def reconnect_loop(client: "MaxClient") -> None:
    delay = client.reconnect_delay
    max_delay = client.max_reconnect_delay
    current = delay
    while not client._closing:
        try:
            await asyncio.sleep(current)
            if client._closing:
                return
            try:
                client.handshake = None
                await client.connect()
            except Exception:
                current = min(current * 2, max_delay)
                continue
            if client.token:
                try:
                    await client.login(client.token)
                except SessionExpired:
                    return
                except Exception:
                    current = min(current * 2, max_delay)
                    continue
            return
        except asyncio.CancelledError:
            return
