# Security

Two-factor authentication, password-checked operations, and live
login sessions.

## Two-factor authentication

MAX 2FA is a server-side password gate that protects destructive
operations (delete account, change password, etc.) and the
login-by-SMS flow itself.

### Status

```python
await client.get_2fa_details()
# {"enabled": True, "hint": "...", "hasEmail": True, ...}
```

### Enable

```python
track_id = await client.create_auth_track()
await client.set_2fa(
    track_id,
    password="strong_password",
    hint="my hint",
    expected_capabilities=None,
)
```

### Disable

```python
track_id = await client.create_auth_track()
await client.remove_2fa(track_id, password="strong_password")
```

### Validate the current password

Useful before destructive ops:

```python
track_id = await client.create_auth_track()
await client.validate_password(track_id, password)
await client.validate_password_hint(track_id, "hint to display")
```

### Password challenge during SMS login

If SMS sign-in returns a `passwordChallenge`, complete it:

```python
result = await client.sign_in(code, sms_token)
if result.requires_password:
    login_token = await client.check_password(
        result.challenge_track_id, my_password
    )
    await client.login(login_token)
```

`client.start(..., password_callback=...)` does this automatically.

## Sessions

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

There is no per-session terminate over the wire; the server only
supports "current" and "all others".

## QR login

Approve a QR-login request shown on another device:

```python
await client.approve_qr_login("https://max.ru/auth/qr/...")
```

## OK token (Odnoklassniki SSO)

```python
await client.get_ok_token()
```

Returns a short-lived token used by the OK integration. Rarely needed.
