# vkmax — documentation

Async Python client for the MAX messenger mobile API
(`api.oneme.ru:443`, binary protocol).

Two API tiers ship in the same package:

- **Pyrogram-style** (recommended): `vkmax.Client`, `filters`, typed
  `Message` with `.reply()` / `.edit()` / `.react()` / `.delete()`.
  Pick this when writing a userbot.
- **Low-level**: `vkmax.MaxClient` — direct method-per-opcode wrapper.
  Use this when you need raw access.

## Languages

- [English](en/README.md)
- [Русский](ru/README.md)

## Protocol reference

- [en/protocol.md](en/protocol.md) — binary framing, msgpack, LZ4.
- [en/opcodes.md](en/opcodes.md) / [ru/opcodes.md](ru/opcodes.md) —
  full opcode catalogue (≈ 90 opcodes).
