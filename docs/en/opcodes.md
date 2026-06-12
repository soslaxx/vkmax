# Opcodes

All opcodes the MAX mobile API speaks, grouped by domain.
The canonical Python enum lives in `vkmax.enums.Opcode`.

Packet flow:

- Client → server: `cmd=0`, `seq=N`, `opcode=X`, `payload=...`.
- Server → client (reply): `cmd=1` (OK) / `2` (NOT_FOUND) / `3` (ERROR), same `seq`.
- Server → client (push): `cmd=0`, no matching `seq`, `opcode=128..` notifications.

## System

| # | Name | Direction | Purpose |
|---|---|---|---|
| 1 | `PING` | C→S | Keep-alive ping. `vkmax` sends one every 30 s. Reply is an empty OK. |
| 2 | `DEBUG` | server-only | Server debug channel; not used by clients. |
| 3 | `RECONNECT` | S→C | Server politely asks the client to reconnect. |
| 5 | `LOG` | C→S | Client log upload. Not used by `vkmax`. |
| 6 | `SESSION_INIT` | C→S | First packet on every connection — sends `mt_instanceid`, `userAgent`, `deviceId`, `clientSessionId`. Server replies with `callsSeed`, `location`, geo config. |

## Profile and account

| # | Name | Purpose |
|---|---|---|
| 16 | `PROFILE` | Update own profile: `firstName`, `lastName`, `photoToken`, `avatarType`, `photoId`. |
| 25 | `PRESET_AVATARS` | Get the catalog of server-side preset avatars. |
| 43 | `REMOVE_CONTACT_PHOTO` | Remove a specific photo from your profile (`photoId`). |
| 199 | `PROFILE_DELETE` | Wipe the account. |
| 200 | `PROFILE_DELETE_TIME` | Schedule / cancel delayed account deletion. |

## Authentication

| # | Name | Purpose |
|---|---|---|
| 17 | `AUTH_REQUEST` | Start SMS auth: `{phone, type: START_AUTH, language}` → temp `token`. |
| 18 | `AUTH` | Submit code: `{token, verifyCode, authTokenType: CHECK_CODE}` → `tokenAttrs.LOGIN.token` or `passwordChallenge`. |
| 19 | `LOGIN` | Log in by long-lived token. Returns `profile`, `chats`, `contacts`, `config`. |
| 20 | `LOGOUT` | Drop current session. |
| 23 | `AUTH_CONFIRM` | Finish registration of a new account (`token` + `firstName` + optional `lastName` / `photoId`). |
| 101 | `AUTH_LOGIN_RESTORE_PASSWORD` | Reset password via email. |
| 104 | `AUTH_2FA_DETAILS` | Get 2FA status, hint, email-binding flag. |
| 107 | `AUTH_VALIDATE_PASSWORD` | Confirm the current 2FA password (`trackId` + `password`). |
| 108 | `AUTH_VALIDATE_HINT` | Set / check the password hint. |
| 109 | `AUTH_VERIFY_EMAIL` | Send a confirmation code to an email. |
| 110 | `AUTH_CHECK_EMAIL` | Confirm the email code. |
| 111 | `AUTH_SET_2FA` | Enable / change / remove 2FA. |
| 112 | `AUTH_CREATE_TRACK` | Create a server-side `trackId` for the next sensitive operation. |
| 113 | `AUTH_CHECK_PASSWORD` | Misc password check during the auth flow. |
| 115 | `AUTH_LOGIN_CHECK_PASSWORD` | Step inside SMS-login when 2FA is on; trades password for the login token. |
| 116 | `AUTH_LOGIN_PROFILE_DELETE` | Delete a profile during the login flow (only seen when the account is scheduled for deletion). |
| 290 | `AUTH_QR_APPROVE` | Approve a QR-login request shown on another device. |

## Phone binding

| # | Name | Purpose |
|---|---|---|
| 98 | `PHONE_BIND_REQUEST` | Request SMS to a new phone number. |
| 99 | `PHONE_BIND_CONFIRM` | Confirm the SMS code and bind the number to the account. |

## Sessions

| # | Name | Purpose |
|---|---|---|
| 96 | `SESSIONS_INFO` | List active login sessions. |
| 97 | `SESSIONS_CLOSE` | Terminate every session except the current one. |

## Sync / config

| # | Name | Purpose |
|---|---|---|
| 21 | `SYNC` | Manual sync trigger; rarely needed because LOGIN already returns a snapshot. |
| 22 | `CONFIG` | Read/write `settings.user` (privacy) and `settings.chats` (per-chat mute, sound, led). |

## Assets (sticker packs, gifs)

| # | Name | Purpose |
|---|---|---|
| 26 | `ASSETS_GET` | List your sticker packs. |
| 27 | `ASSETS_UPDATE` | Update pack metadata. |
| 28 | `ASSETS_GET_BY_IDS` | Bulk fetch packs by id. |
| 29 | `ASSETS_ADD` | Add a sticker pack to the library. |
| 259 | `ASSETS_REMOVE` | Remove a sticker pack. |
| 260 | `ASSETS_MOVE` | Change pack position. |
| 261 | `ASSETS_LIST_MODIFY` | Bulk reorder. |

## Contacts

| # | Name | Purpose |
|---|---|---|
| 32 | `CONTACT_INFO` | Fetch users by ids. |
| 33 | `CONTACT_ADD` | Add to address book. |
| 34 | `CONTACT_UPDATE` | Rename, block, unblock. |
| 35 | `CONTACT_PRESENCE` | Online / last-seen for a list of users. |
| 36 | `CONTACT_LIST` | Listing of contacts by `status` (the mobile API only exposes `BLOCKED`). |
| 37 | `CONTACT_SEARCH` | Search address book by query. |
| 38 | `CONTACT_MUTUAL` | Mutual contacts. |
| 39 | `CONTACT_PHOTOS` | All photos of a contact. |
| 40 | `CONTACT_SORT` | Reorder contacts. |
| 42 | `CONTACT_VERIFY` | Mark verified (rare). |
| 46 | `CONTACT_INFO_BY_PHONE` | Look up a contact by phone number. |

## Chats

| # | Name | Purpose |
|---|---|---|
| 48 | `CHAT_INFO` | Fetch chats by `chatIds`. |
| 49 | `CHAT_HISTORY` | Read history page (`from`, `forward`, `backward`). |
| 50 | `CHAT_MARK` | Move read marker / mark as unread. |
| 51 | `CHAT_MEDIA` | List chat media (`type`: PHOTO/VIDEO/FILE/AUDIO/LINK). |
| 52 | `CHAT_DELETE` | Delete chat (optionally `forAll`). |
| 53 | `CHATS_LIST` | Paginated chat list (`marker = now_ms`, go back in time). |
| 54 | `CHAT_CLEAR` | Clear local history. |
| 55 | `CHAT_UPDATE` | Rename, change description, pin a message, set photo, set options, change owner. |
| 56 | `CHAT_CHECK_LINK` | Resolve a join link without joining. |
| 57 | `CHAT_JOIN` | Join by link. |
| 58 | `CHAT_LEAVE` | Leave chat. |
| 59 | `CHAT_MEMBERS` | List members (also used for join requests with `type: JOIN_REQUEST`). |
| 60 | `PUBLIC_SEARCH` | Search public chats / users / channels. |
| 61 | `CHAT_PERSONAL_CONFIG` | Per-user-per-chat preferences. |
| 63 | `CHAT_CREATE` | Create chat. In practice `MSG_SEND` with a `CONTROL` attach is used. |
| 75 | `CHAT_SUBSCRIBE` | Subscribe to a channel. |
| 77 | `CHAT_MEMBERS_UPDATE` | Add / remove / approve / decline members. |
| 86 | `CHAT_PIN_SET_VISIBILITY` | Toggle pinned-message visibility. |
| 117 | `CHAT_COMPLAIN` | Report a chat. |
| 161 | `COMPLAIN` | Report a message / user. |
| 162 | `COMPLAIN_REASONS_GET` | Predefined reasons for `COMPLAIN`. |
| 196 | `CHAT_HIDE` | Hide chat from the list. |
| 198 | `CHAT_SEARCH_COMMON_PARTICIPANTS` | Common participants between you and another user. |
| 257 | `CHAT_REACTIONS_SETTINGS_SET` | Restrict allowed reactions in a chat. |
| 258 | `REACTIONS_SETTINGS_GET_BY_CHAT_ID` | Read reaction restrictions for a chat. |
| 300 | `CHAT_SUGGEST` | Suggested chats / channels. |

## Messages

| # | Name | Purpose |
|---|---|---|
| 64 | `MSG_SEND` | Send a message (text, attaches, sticker, reply, forward, create-chat control). |
| 65 | `MSG_TYPING` | Send typing indicator (TEXT / VOICE / VIDEO / PHOTO / FILE). |
| 66 | `MSG_DELETE` | Delete one or more messages. |
| 67 | `MSG_EDIT` | Edit message text and/or `elements`. |
| 68 | `CHAT_SEARCH` | Search inside a single chat. |
| 70 | `MSG_SHARE_PREVIEW` | Build a link preview. |
| 71 | `MSG_GET` | Fetch messages by ids inside a chat. |
| 72 | `MSG_SEARCH_TOUCH` | Touch search (used by UI suggestion). |
| 73 | `MSG_SEARCH` | Global message search. |
| 74 | `MSG_GET_STAT` | Channel post statistics. |
| 92 | `MSG_DELETE_RANGE` | Delete a range of messages by ids. |
| 127 | `GET_LAST_MENTIONS` | Latest mentions across all chats. (Exact payload not yet known.) |
| 176 | `DRAFT_SAVE` | Save a draft for a chat. |
| 177 | `DRAFT_DISCARD` | Drop the draft. |
| 178 | `MSG_REACTION` | Add reaction (`{chatId, messageId(int), reaction: {reactionType: EMOJI, id: "<emoji>"}}`). |
| 179 | `MSG_CANCEL_REACTION` | Remove your reaction. |
| 180 | `MSG_GET_REACTIONS` | Read reactions. (`vkmax` derives them from `MSG_GET.reactionInfo` instead.) |
| 181 | `MSG_GET_DETAILED_REACTIONS` | Paginated list of users who reacted. |

## Media and files

| # | Name | Purpose |
|---|---|---|
| 80 | `PHOTO_UPLOAD` | Request upload URL for a photo. |
| 81 | `STICKER_UPLOAD` | Request upload URL for a sticker. |
| 82 | `VIDEO_UPLOAD` | Request upload URL for a video. |
| 83 | `VIDEO_PLAY` | Get streaming URLs (`MP4_1080`, `MP4_720`, `HLS`, ...). |
| 87 | `FILE_UPLOAD` | Request upload URL for an arbitrary file. |
| 88 | `FILE_DOWNLOAD` | Get a download URL for a file / photo (different payload shape). |
| 89 | `LINK_INFO` | Resolve a public link (`max.ru/...`). |
| 193 | `STICKER_CREATE` | Create a sticker from an uploaded image. |
| 194 | `STICKER_SUGGEST` | Stickers that match a search query. |
| 202 | `AUDIO_TRANSCRIPTION` | Request voice-note transcription (`chatId`, `messageId`, `mediaId`). |
| 301 | `AUDIO_PLAY` | Audio streaming URLs (`MP3`, `OGG`, `HLS`). |
| 293 | `TRANSCRIPTION_RESULT` | Server push with the finished transcription text. |

## Calls (video / voice)

| # | Name | Purpose |
|---|---|---|
| 76 | `VIDEO_CHAT_START` | Start a passive video chat. |
| 78 | `VIDEO_CHAT_START_ACTIVE` | Start a 1-on-1 / group call (sends `internalParams`). |
| 79 | `VIDEO_CHAT_HISTORY` | Call history. |
| 84 | `VIDEO_CHAT_CREATE_JOIN_LINK` | Create a link to join an ongoing call. |
| 103 | `GET_INBOUND_CALLS` | Currently-ringing incoming calls. |
| 124 | `LOCATION_STOP` | Stop sharing live location. |
| 195 | `VIDEO_CHAT_MEMBERS` | Members in the call. |

## Bots / mini-apps

| # | Name | Purpose |
|---|---|---|
| 105 | `EXTERNAL_CALLBACK` | Reserved external integration callback. |
| 118 | `MSG_SEND_CALLBACK` | Press an inline button (`callbackData`). |
| 119 | `SUSPEND_BOT` | Stop a bot from messaging you. |
| 144 | `CHAT_BOT_COMMANDS` | Get bot commands available in a chat. |
| 145 | `BOT_INFO` | Public bot info. |
| 158 | `OK_TOKEN` | OK SSO short-lived token. |
| 160 | `WEB_APP_INIT_DATA` | Build `initData` for a mini-app launch. |

## Polls

| # | Name | Purpose |
|---|---|---|
| 304 | `SEND_VOTE` | Submit a vote in a poll. |
| 305 | `VOTERS_LIST_BY_ANSWER` | Paginated voter list for an answer. |
| 306 | `GET_POLL_UPDATES` | Live updates for a set of polls. |

## Folders

| # | Name | Purpose |
|---|---|---|
| 272 | `FOLDERS_GET` | List folders (`folderSync` cursor). |
| 273 | `FOLDERS_GET_BY_ID` | Single folder. |
| 274 | `FOLDERS_UPDATE` | Create or update (`id, title, include, favorites, filters, options`). |
| 275 | `FOLDERS_REORDER` | Reorder folder list (`foldersOrder: [id, id]`). |
| 276 | `FOLDERS_DELETE` | Delete a folder. |

## Push notifications (server → client)

| # | Name | What it pushes |
|---|---|---|
| 128 | `NOTIF_MESSAGE` | New or updated message. |
| 129 | `NOTIF_TYPING` | Typing indicator from someone else. |
| 130 | `NOTIF_MARK` | Read marker moved (yours or theirs). |
| 131 | `NOTIF_CONTACT` | Contact metadata changed. |
| 132 | `NOTIF_PRESENCE` | Online status / last-seen tick. |
| 134 | `NOTIF_CONFIG` | Privacy or notification settings changed elsewhere. |
| 135 | `NOTIF_CHAT` | Chat metadata changed. |
| 136 | `NOTIF_ATTACH` | Upload finalized. |
| 137 | `NOTIF_CALL_START` | Incoming / starting call. |
| 139 | `NOTIF_CONTACT_SORT` | Contact order changed. |
| 140 | `NOTIF_MSG_DELETE_RANGE` | Bulk delete. |
| 142 | `NOTIF_MSG_DELETE` | One message deleted. |
| 143 | `NOTIF_CALLBACK_ANSWER` | Bot callback answered. |
| 147 | `NOTIF_LOCATION` | Live-location update. |
| 148 | `NOTIF_LOCATION_REQUEST` | Someone requested live location. |
| 150 | `NOTIF_ASSETS_UPDATE` | Sticker pack updated. |
| 152 | `NOTIF_DRAFT` | Draft changed elsewhere. |
| 153 | `NOTIF_DRAFT_DISCARD` | Draft removed. |
| 154 | `NOTIF_MSG_DELAYED` | Scheduled-send happened. |
| 155 | `NOTIF_MSG_REACTIONS_CHANGED` | Reactions on a message changed. |
| 156 | `NOTIF_MSG_YOU_REACTED` | Confirmation of your own reaction. |
| 159 | `NOTIF_PROFILE` | Your profile updated elsewhere. |
| 277 | `NOTIF_FOLDERS` | Folder list changed. |
| 292 | `NOTIF_BANNERS` | UI banners (announcements). |

## Status / command codes

Value of `cmd` byte in every packet:

| Value | Name | Meaning |
|---|---|---|
| 0 | `CMD_REQUEST` | Client request or server push. |
| 1 | `CMD_OK` | Successful reply. |
| 2 | `CMD_NOT_FOUND` | Resource not found (rare). |
| 3 | `CMD_ERROR` | Error reply. Payload contains `error`, `message`, `localizedMessage`. After ERROR the server usually closes the TCP connection. |
