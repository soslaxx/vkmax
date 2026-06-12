import asyncio

from vkmax import Client, MessageType, filters

app = Client("main")


@app.on_message(filters.incoming & filters.private & filters.text)
async def echo(client: Client, message: MessageType) -> None:
    await message.reply(message.text or "")


@app.on_message(filters.outgoing & filters.command("start"))
async def start(client: Client, message: MessageType) -> None:
    await message.edit_markdown(
        "**echo bot online**\n"
        f"my id: `{client.account_id}`"
    )


if __name__ == "__main__":
    app.run()
