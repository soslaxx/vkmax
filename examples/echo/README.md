# echo

Minimal example: echoes every incoming private message.

```bash
python login.py main
python main.py
```

Key ideas demonstrated:

- `Client("main")` — reuses the existing session file.
- `@app.on_message(filters.incoming & filters.private & filters.text)`
  — combined filters, only DMs with non-empty text from other people.
- `message.reply(text)` — replies in the same chat.
- `app.run()` — connect + login + listen forever.
