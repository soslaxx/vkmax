# Безопасность

2FA, проверки пароля, активные сессии.

## Двухфакторная аутентификация

2FA в MAX — серверная проверка пароля, защищающая деструктивные
операции (удаление аккаунта, смена пароля и т.п.) и сам процесс
SMS-логина.

### Статус

```python
await client.get_2fa_details()
# {"enabled": True, "hint": "...", "hasEmail": True, ...}
```

### Включить

```python
track_id = await client.create_auth_track()
await client.set_2fa(
    track_id,
    password="strong_password",
    hint="подсказка",
    expected_capabilities=None,
)
```

### Отключить

```python
track_id = await client.create_auth_track()
await client.remove_2fa(track_id, password="strong_password")
```

### Проверить текущий пароль

Полезно перед опасными операциями:

```python
track_id = await client.create_auth_track()
await client.validate_password(track_id, password)
await client.validate_password_hint(track_id, "подсказка")
```

### Password challenge во время SMS-логина

Если `sign_in` вернул `passwordChallenge`, доверши:

```python
result = await client.sign_in(code, sms_token)
if result.requires_password:
    login_token = await client.check_password(
        result.challenge_track_id, my_password
    )
    await client.login(login_token)
```

`client.start(..., password_callback=...)` делает это автоматически.

## Активные сессии

```python
sessions = await client.get_sessions()
# [
#   {"id": ..., "time": ms, "client": "MAX Android",
#    "info": "TECNO TECNO LE7n, Android 11",
#    "location": "Russia, Moscow, IP ...",
#    "current": True},
#   ...
# ]

await client.terminate_other_sessions()
```

По-сессионное завершение по протоколу не поддерживается; сервер
умеет только «текущую» и «все кроме текущей».

## QR-вход

Подтвердить QR-логин с другого устройства:

```python
await client.approve_qr_login("https://max.ru/auth/qr/...")
```

## OK token (Одноклассники SSO)

```python
await client.get_ok_token()
```

Короткоживущий токен для интеграции с OK. Используется редко.
