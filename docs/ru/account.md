# Управление аккаунтом

Деструктивные операции. **Все три** необратимы со стороны сервера —
осторожно.

## Запланировать удаление

Аккаунт удаляется отложенно через `days` дней; вход в этот период
отменяет удаление.

```python
await client.set_account_delete_timer(days=7)
await client.set_account_delete_timer(delete_time=1799999999999)  # ms
```

Сервер возвращает результирующий `deleteTime`.

Отменить:

```python
await client.cancel_account_delete_timer()
```

## Удалить немедленно

Опкод 199 (`PROFILE_DELETE`). Точный требуемый payload не
документирован komet, поэтому хелпер шлёт ровно то что передал:

```python
await client.delete_account()
await client.delete_account(password="...", track_id="...", reason="...")
```

Если сервер ждёт `auth_track` flow (создать track + validate password),
сделай это сначала:

```python
track_id = await client.create_auth_track()
await client.validate_password(track_id, "my_2fa_password")
await client.delete_account(password="my_2fa_password", track_id=track_id)
```

## Сменить номер телефона

Два опкода: `PHONE_BIND_REQUEST` (98) + `PHONE_BIND_CONFIRM` (99):

```python
start = await client.request_phone_change("+79991234567")
# на новый номер уходит SMS; start['token'] — токен привязки
await client.confirm_phone_change(start["token"], input("код: "))
```

Новый номер заменяет старый при успехе. Текущий токен сессии
остаётся валидным.

## Привязать / подтвердить email

```python
track_id = await client.create_auth_track()
await client.request_email_verify(track_id, "user@example.com")
# на почту приходит код
await client.check_email_code(track_id, input("email-код: "))
```

## Logout

```python
await client.logout()                       # текущая сессия
await client.logout(push_token="<fcm>")     # ещё и push-токен сбросить
```

Logout очищает кэшированный токен с диска.
