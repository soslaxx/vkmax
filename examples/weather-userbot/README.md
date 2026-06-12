# weather-userbot

A minimal vkmax userbot in pyrogram-style. Reacts only to **your own**
outgoing messages thanks to `filters.outgoing & filters.command(...)`.

## Commands

- `.weather` — погода в Moscow.
- `.weather Питер` — погода в указанном городе.
- `.ping` — RTT до сервера MAX.
- `.id` — твой `account_id`.
- `.help` — список команд.

Каждое сообщение редактируется на месте: сначала анимированный
спиннер, потом итоговая карточка с **жирными** метками.

## Setup

1. Install vkmax:

   ```bash
   pip install vkmax
   ```

2. Создай файл сессии:

   ```bash
   python login.py main
   ```

3. Запусти бота:

   ```bash
   python main.py
   ```

## Notes

- Никаких токенов в исходниках — используется `~/.vkmax/main.json`.
- Погода с [wttr.in](https://wttr.in/), без API-ключа.
- Бот вызывает `message.edit_markdown(...)` — MAX рендерит **bold**.
