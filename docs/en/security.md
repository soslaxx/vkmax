# Security

Two-factor authentication, password-checked operations, and live
login sessions.

## Two-factor authentication

MAX 2FA is a server-side password gate that protects destructive
operations (delete account, change password, etc.) and the SMS
sign-in flow itself.

### Status

```python
await app.get_2fa_details()
# {"enabled": True, "hint": "...", "hasEmail": True, ...}
```

### Enable

```python
track_id = await app.create_auth_track()
await app.set_2fa(
    track_id,
    password="strong_password",
    hint="my hint",
    expected_capabilities=None,
)
```

### Disable

```python
track_id = await app.create_auth_track()
await app.remove_2fa(track_id, password="strong_password")
```

### Validate the current password

Useful before destructive ops:

```python
track_id = await app.create_auth_track()
await app.validate_password(track_id, password)
await app.validate_password_hint(track_id, "hint to display")
```

### Password challenge during SMS login

If SMS sign-in returns a `passwordChallenge`, complete it:

```python
result = await app.sign_in(code, sms_token)
if result.requires_password:
    login_token = await app.check_password(
        result.challenge_track_id, my_password
    )
    await app.login(login_token)
```

`app.start(..., password_callback=...)` does this automatically.

## Sessions

```python
sessions = await app.get_sessions()
# [
#   {"id": ..., "time": ms, "client": "MAX Android",
#    "info": "TECNO TECNO LE7n, Android 11",
#    "location": "Russia, Moscow, IP ...",
#    "current": True},
#   ...
# ]

await app.terminate_other_sessions()
```

There is no per-session terminate over the wire; the server only
supports "current" and "all others".

## QR login

Approve a QR-login request shown on another device:

```python
await app.approve_qr_login("https://max.ru/auth/qr/...")
```

## OK token (Odnoklassniki SSO)

```python
await app.get_ok_token()
```

Returns a short-lived token used by the OK integration. Rarely
needed outside Odnoklassniki integrations.
