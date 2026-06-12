from __future__ import annotations

import asyncio
import logging
import sys

from vkmax import MaxClient, Opcode, Packet

logging.basicConfig(
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.INFO,
)


async def get_code() -> str:
    return input("SMS code: ").strip()


async def main() -> None:
    client = MaxClient("main")

    if client.device.token:
        await client.start(token=client.device.token)
    else:
        phone = input("Phone (+7...): ").strip()
        result = await client.start(phone=phone, code_callback=get_code)
        if not getattr(result, "token", None):
            print("Login failed:", result)
            return

    print(f"Logged in as account_id={client.account_id}")

    @client.on_message
    async def on_message(packet: Packet) -> None:
        payload = packet.payload if isinstance(packet.payload, dict) else {}
        message = payload.get("message") if isinstance(payload.get("message"), dict) else None
        if not message:
            return
        chat_id = payload.get("chatId")
        text = message.get("text")
        sender = message.get("sender")
        if sender == client.account_id:
            return
        print(f"[chat={chat_id} from={sender}] {text!r}")

        if isinstance(text, str) and text.startswith(".ping"):
            await client.send_message(chat_id, "pong", reply_to=message.get("id"))

    print("Listening for messages. Send '.ping' from another account to test.")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
