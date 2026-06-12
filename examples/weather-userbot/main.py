import asyncio
import ssl
import time
from urllib.parse import quote

from vkmax import Client, MessageType, filters

app = Client("main")

WEATHER_HOST = "wttr.in"
DEFAULT_CITY = "Moscow"

SPINNER = ["\U0001f50d", "\U0001f50e", "\U0001f30d", "\U0001f30e", "\U0001f30f"]
BAR_FULL = "\u25cf"
BAR_EMPTY = "\u25cb"
BAR_WIDTH = 8

WEATHER_EMOJI = {
    "Sunny": "\u2600\ufe0f",
    "Clear": "\U0001f31f",
    "Partly cloudy": "\U0001f324\ufe0f",
    "Cloudy": "\u2601\ufe0f",
    "Overcast": "\U0001f325\ufe0f",
    "Mist": "\U0001f32b\ufe0f",
    "Fog": "\U0001f32b\ufe0f",
    "Smog": "\U0001f32b\ufe0f",
    "Rain": "\U0001f327\ufe0f",
    "Light rain": "\U0001f326\ufe0f",
    "Heavy rain": "\u26c8\ufe0f",
    "Thunder": "\u26c8\ufe0f",
    "Snow": "\u2744\ufe0f",
    "Light snow": "\U0001f328\ufe0f",
    "Blizzard": "\U0001f328\ufe0f",
    "Sleet": "\U0001f328\ufe0f",
}

HELP = (
    "\U0001f916 **vkmax userbot**\n"
    "**`.weather [город]`** — погода\n"
    "**`.ping`** — проверить связь\n"
    "**`.id`** — мой account_id\n"
    "**`.help`** — это сообщение"
)


def weather_emoji(cond: str) -> str:
    if not cond:
        return "\U0001f30d"
    for key, value in WEATHER_EMOJI.items():
        if key.lower() in cond.lower():
            return value
    return "\U0001f30d"


async def fetch_weather(city: str) -> dict | None:
    path = f"/{quote(city)}?format=j1&lang=ru"
    ctx = ssl.create_default_context()
    reader, writer = await asyncio.open_connection(WEATHER_HOST, 443, ssl=ctx)
    try:
        writer.write(
            (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {WEATHER_HOST}\r\n"
                "User-Agent: vkmax-weather-bot/1.0\r\n"
                "Connection: close\r\n\r\n"
            ).encode()
        )
        await writer.drain()
        data = await asyncio.wait_for(reader.read(-1), timeout=15)
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
    if b"\r\n\r\n" not in data:
        return None
    headers, body = data.split(b"\r\n\r\n", 1)
    head = headers.decode(errors="replace")
    parts = head.split("\r\n", 1)[0].split(" ", 2)
    if len(parts) < 2 or parts[1] != "200":
        return None
    if "transfer-encoding: chunked" in head.lower():
        body = _dechunk(body)
    import json
    try:
        return json.loads(body.decode("utf-8", errors="replace"))
    except Exception:
        return None


def _dechunk(body: bytes) -> bytes:
    out = bytearray()
    pos = 0
    while pos < len(body):
        nl = body.find(b"\r\n", pos)
        if nl < 0:
            break
        size_str = body[pos:nl].split(b";", 1)[0].strip()
        try:
            size = int(size_str, 16)
        except ValueError:
            break
        pos = nl + 2
        if size == 0:
            break
        out.extend(body[pos:pos + size])
        pos += size + 2
    return bytes(out)


def format_weather(payload: dict, city: str) -> str:
    nearest = (payload.get("nearest_area") or [{}])[0]
    area = (nearest.get("areaName") or [{}])[0].get("value") or city.title()
    country = (nearest.get("country") or [{}])[0].get("value")
    location = f"{area}, {country}" if country else area
    current = (payload.get("current_condition") or [{}])[0]
    temp = current.get("temp_C", "?")
    feels = current.get("FeelsLikeC", "?")
    cond_en = (current.get("weatherDesc") or [{}])[0].get("value", "")
    desc_list = current.get("lang_ru") or []
    desc = (desc_list[0].get("value") if desc_list else "") or cond_en
    wind = current.get("windspeedKmph", "?")
    humidity = current.get("humidity", "?")
    today = (payload.get("weather") or [{}])[0]
    max_t = today.get("maxtempC", "?")
    min_t = today.get("mintempC", "?")
    emoji = weather_emoji(cond_en)
    return (
        f"{emoji} **Погода в {location}**\n"
        f"**Сейчас:** {desc} \u2022 **{temp}\u00b0C** (ощущается как {feels}\u00b0)\n"
        f"\U0001f4ca **Сегодня:** от {min_t}\u00b0 до {max_t}\u00b0C\n"
        f"\U0001f4a8 **Ветер:** {wind} км/ч\n"
        f"\U0001f4a7 **Влажность:** {humidity}%"
    )


async def animate(message: MessageType, city: str, stop: asyncio.Event) -> None:
    frame = 0
    while not stop.is_set():
        spinner = SPINNER[frame % len(SPINNER)]
        fill = (frame % BAR_WIDTH) + 1
        bar = BAR_FULL * fill + BAR_EMPTY * (BAR_WIDTH - fill)
        try:
            await message.edit_markdown(
                f"{spinner} **Ищу погоду в {city.title()}…**\n{bar}"
            )
        except Exception:
            pass
        frame += 1
        try:
            await asyncio.wait_for(stop.wait(), timeout=0.4)
        except asyncio.TimeoutError:
            continue


@app.on_message(filters.outgoing & filters.command("weather"))
async def cmd_weather(client: Client, message: MessageType) -> None:
    args = message.command[1:] if message.command else []
    city = " ".join(args) or DEFAULT_CITY
    await message.edit_markdown(f"\U0001f50d **Ищу погоду в {city.title()}…**")
    stop = asyncio.Event()
    animator = asyncio.create_task(animate(message, city, stop))
    try:
        payload = await asyncio.wait_for(fetch_weather(city), timeout=20)
    except Exception:
        payload = None
    stop.set()
    try:
        await animator
    except Exception:
        pass
    if payload is None:
        await message.edit_markdown(f"\u26a0\ufe0f **Нет данных для** *{city.title()}*")
        return
    await message.edit_markdown(format_weather(payload, city))


@app.on_message(filters.outgoing & filters.command("ping"))
async def cmd_ping(client: Client, message: MessageType) -> None:
    started = time.perf_counter()
    await message.edit_markdown("\U0001f3d3 *понг…*")
    await client.ping()
    elapsed = (time.perf_counter() - started) * 1000
    await message.edit_markdown(f"\U0001f3d3 **pong** — `{elapsed:.0f} мс`")


@app.on_message(filters.outgoing & filters.command("id"))
async def cmd_id(client: Client, message: MessageType) -> None:
    await message.edit_markdown(f"\U0001f194 **account id:** `{client.account_id}`")


@app.on_message(filters.outgoing & filters.command("help"))
async def cmd_help(client: Client, message: MessageType) -> None:
    await message.edit_markdown(HELP)


if __name__ == "__main__":
    print("vkmax userbot starting…")
    app.run()
