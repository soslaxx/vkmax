from __future__ import annotations

import sys

from vkmax import Client, MessageType, filters

app = Client("main")

_cache: dict[int, dict] = {}
_CACHE_LIMIT = 5000


def _remember(message: MessageType) -> None:
    if len(_cache) >= _CACHE_LIMIT:
        for stale in list(_cache.keys())[: _CACHE_LIMIT // 5]:
            _cache.pop(stale, None)
    _cache[int(message.id)] = {
        "chat_id": int(message.chat_id),
        "sender_id": int(message.sender_id),
        "text": message.text or "",
    }


@app.on_message(filters.incoming)
async def stash(client: Client, message: MessageType) -> None:
    if message.is_edited or message.is_removed:
        return
    _remember(message)


@app.on_deleted_message()
async def on_deleted(client: Client, message: MessageType) -> None:
    cached = _cache.pop(int(message.id), None)
    if not cached or cached["sender_id"] == client.account_id:
        return
    text = cached["text"]
    if not text:
        return
    await client.send_message(
        message.chat_id,
        f"\U0001f5d1\ufe0f **ты удалил сообщение:**\n__{text}__",
        markdown=True,
    )


if __name__ == "__main__":
    print("ayumax online \u2014 \u043b\u043e\u0432\u0438\u043c \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u044f")
    app.run()
