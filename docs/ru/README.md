# vkmax — документация (русский)

## Pyrogram-стиль (рекомендуется)

Высокоуровневое API для юзерботов: `Client`, декораторы, фильтры,
типизированные `Message`/`Chat`/`User`.

- [getting-started.md](getting-started.md) — установка, вход, первый
  бот в 10 строк.
- [client.md](client.md) — `Client`, `run()`, прокси, реконнекты.
- [handlers.md](handlers.md) — `@app.on_message`, `on_reaction`,
  `on_typing`, группы.
- [filters.md](filters.md) — комбинируемые фильтры, кастомные,
  `filters.command`, `filters.regex`.
- [message.md](message.md) — объект `Message`: `.reply()`,
  `.edit_markdown()`, `.react()`, `.delete()`, `.forward_to()`.
- [formatting.md](formatting.md) — Markdown и HTML-парсеры, raw
  `elements`.

## Сообщения

- [messages.md](messages.md) — отправка, редактирование, удаление,
  ответ, пересылка, история, поиск.
- [reactions.md](reactions.md) — поставить / убрать реакцию, алиасы.
- [uploads.md](uploads.md) — фото, **видео**, файлы, голосовые,
  скачивание, прогресс.

## Чаты и пользователи

- [chats.md](chats.md) — список, группы, каналы, участники, админы,
  mute, join links.
- [contacts.md](contacts.md) — поиск, по номеру, блок/разблок.
- [folders.md](folders.md) — папки чатов.

## Аккаунт

- [profile.md](profile.md) — имя, аватар, preset-аватары.
- [privacy.md](privacy.md) — все ключи приватности.
- [notifications.md](notifications.md) — mute, транскрипция.
- [account.md](account.md) — удалить аккаунт, сменить телефон, email.
- [security.md](security.md) — 2FA, сессии, QR-вход.

## Низкоуровневое

- [low-level.md](low-level.md) — `MaxClient.invoke()`, свои опкоды,
  `Packet`.
- [proxy.md](proxy.md) — HTTP CONNECT и SOCKS5.
- [protocol.md](protocol.md) — бинарный формат, msgpack, LZ4.
- [opcodes.md](opcodes.md) — полный список опкодов с описанием.
