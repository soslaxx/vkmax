# vkmax docs — English

## Pyrogram-style (recommended)

These cover the high-level userbot API: `Client`, decorators,
filters, typed `Message`/`Chat`/`User`.

- [getting-started.md](getting-started.md) — install, log in, first
  bot in 10 lines.
- [client.md](client.md) — `Client` lifecycle, `run()`, proxy,
  reconnects.
- [handlers.md](handlers.md) — `@app.on_message`, `on_reaction`,
  `on_typing`, `on_event`, handler groups.
- [filters.md](filters.md) — combinable filters, custom filters,
  `filters.command`, `filters.regex`.
- [message.md](message.md) — `Message` object: `.reply()`,
  `.edit_markdown()`, `.react()`, `.delete()`, `.forward_to()`.
- [formatting.md](formatting.md) — Markdown and HTML parsers, raw
  `elements` payload.

## Messaging features

- [messages.md](messages.md) — `send_message`, edit, delete, reply,
  forward, history, search.
- [reactions.md](reactions.md) — react / unreact, emoji aliases,
  chat-level reaction settings.
- [uploads.md](uploads.md) — photos, **videos**, files, voice,
  downloads, progress callbacks.

## Chats & users

- [chats.md](chats.md) — list, groups, channels, members, admins,
  mute, join links.
- [contacts.md](contacts.md) — fetch users, by phone, block/unblock.
- [folders.md](folders.md) — chat folders.

## Account

- [profile.md](profile.md) — name, avatar, preset avatars.
- [privacy.md](privacy.md) — all privacy keys + helpers.
- [notifications.md](notifications.md) — chat-level mute,
  transcription.
- [account.md](account.md) — delete account, change phone, bind
  email.
- [security.md](security.md) — 2FA, sessions, QR login.

## Low-level / advanced

- [low-level.md](low-level.md) — `MaxClient.invoke()`, custom
  opcodes, `Packet`.
- [proxy.md](proxy.md) — HTTP CONNECT and SOCKS5 support.
- [protocol.md](protocol.md) — binary framing, msgpack, LZ4, the
  exact bytes on the wire.
- [opcodes.md](opcodes.md) — full opcode list with descriptions.
