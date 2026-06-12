import asyncio
from vkmax import Client, dm_chat_id

PEER = 123456789  # id пользователя, которому нужно отправить сообщение


async def main():
    app = Client("main")
    await app.start_session()
    chat_id = dm_chat_id(app.account_id, PEER)
    msg = await app.send_message(chat_id, "Пошел нахуй пидор")
    print(f"sent id={msg.id} chat_id={chat_id}")
    await app.disconnect()

asyncio.run(main()) 